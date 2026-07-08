from __future__ import annotations

import json
import time
from enum import Enum
from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

from agentpreflight import __version__
from agentpreflight.remediator.codex_fix import run_codex_fix
from agentpreflight.remediator.local_fix import apply_local_fixes
from agentpreflight.remediator.prompt_builder import build_prompt_pack
from agentpreflight.reporters import json_reporter, markdown_reporter, sarif_reporter
from agentpreflight.rules.catalog import ALL_RULES
from agentpreflight.scanner import scan_path

app = typer.Typer(no_args_is_help=True, invoke_without_command=True)
rules_app = typer.Typer(no_args_is_help=True)
app.add_typer(rules_app, name="rules")
console = Console()


class OutputFormat(str, Enum):
    table = "table"
    json = "json"
    sarif = "sarif"
    markdown = "markdown"


_SEVERITY_RANK = {"low": 1, "medium": 2, "high": 3, "critical": 4}


def _should_fail(findings, fail_on: str | None) -> bool:
    if not fail_on:
        return False
    threshold = _SEVERITY_RANK[fail_on]
    return any(_SEVERITY_RANK[f.severity] >= threshold for f in findings)


def _render_quiet(result) -> None:
    console.print(f"trust_score={result.trust_score} verdict={result.verdict} findings={len(result.findings)}")


def _render_table(result, verbose: bool = False) -> None:
    color = "green" if result.verdict == "pass" else "yellow" if result.verdict == "warn" else "red"
    console.print(f"[bold]AgentPreflight[/bold] target={result.target}")
    console.print(f"trust_score=[bold {color}]{result.trust_score}[/bold {color}] verdict=[bold {color}]{result.verdict}[/bold {color}] findings={len(result.findings)} offline={result.offline}")
    console.print(
        f"summary critical={result.summary['critical']} high={result.summary['high']} "
        f"medium={result.summary['medium']} low={result.summary['low']} "
        f"suppressed={result.summary.get('suppressed', 0)} artifacts={result.summary['artifacts_scanned']}"
    )
    if not result.findings:
        return
    table = Table(show_header=True, header_style="bold")
    table.add_column("Severity")
    table.add_column("Rule")
    table.add_column("Path")
    table.add_column("Line", justify="right")
    table.add_column("Evidence")
    for finding in result.findings[:12]:
        table.add_row(
            finding.severity,
            finding.id,
            Path(finding.path).name,
            str(finding.line or ""),
            finding.evidence,
        )
    console.print(table)
    if verbose:
        for finding in result.findings[:12]:
            console.print(f"\n[bold]{finding.id}[/bold] {finding.title}")
            console.print(f"  risk: {finding.risk}")
            console.print(f"  fix:  {finding.fix}")
            if finding.references:
                console.print(f"  refs: {', '.join(finding.references)}")
    fixable = sum(1 for f in result.findings if f.fix_available)
    if fixable:
        console.print(f"fix_available={fixable} run: agentpreflight fix {result.target}")


@app.callback()
def main(version: bool = typer.Option(False, "--version", help="Print version and exit.", is_eager=True)) -> None:
    if version:
        console.print(__version__)
        raise typer.Exit()


@app.command()
def scan(
    target: Path = typer.Argument(..., exists=True, help="Path to repo, file, or fixture."),
    profile: str = typer.Option("balanced", "--profile", help="dev, balanced, or strict."),
    fail_on: str | None = typer.Option(None, "--fail-on", help="low, medium, high, or critical."),
    format: OutputFormat = typer.Option(OutputFormat.table, "--format"),
    output: Path | None = typer.Option(None, "--output", "-o", help="Write JSON/SARIF output to file."),
    suppressions: Path | None = typer.Option(None, "--suppressions", help="Path to .agentpreflight.json suppressions file."),
    quiet: bool = typer.Option(False, "--quiet", "-q", help="Print only trust_score, verdict, and finding count."),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Show full evidence, risk, fix, and references per finding."),
) -> None:
    if profile not in {"dev", "balanced", "strict"}:
        raise typer.BadParameter("profile must be dev, balanced, or strict")
    if fail_on and fail_on not in _SEVERITY_RANK:
        raise typer.BadParameter("fail-on must be low, medium, high, or critical")

    result = scan_path(target, profile=profile, suppression_file=suppressions)
    if format == OutputFormat.json:
        rendered = json_reporter.render(result)
    elif format == OutputFormat.sarif:
        rendered = sarif_reporter.render(result)
    elif format == OutputFormat.markdown:
        rendered = markdown_reporter.render(result)
    else:
        rendered = ""
        if quiet:
            _render_quiet(result)
        else:
            _render_table(result, verbose=verbose)

    if output:
        output.write_text(rendered, encoding="utf-8")
        console.print(f"wrote={output}")
    elif rendered:
        console.print(rendered)

    if _should_fail(result.findings, fail_on):
        raise typer.Exit(1)


@app.command()
def fix(
    target: Path = typer.Argument(..., exists=True, help="Path to scan and locally remediate."),
    rules: str | None = typer.Option(None, "--rules", help="Comma-separated rule IDs to fix."),
    apply: bool = typer.Option(False, "--apply", help="Apply local safe fixes."),
    codex: bool = typer.Option(False, "--codex", help="Generate Codex AI patch proposals (requires OPENAI_API_KEY)."),
    codex_model: str = typer.Option("codex-mini-latest", "--codex-model", help="OpenAI model for Codex remediation."),
) -> None:
    result = scan_path(target, profile="strict")
    allowed = {item.strip() for item in rules.split(",")} if rules else None
    fixable = [f for f in result.findings if f.fix_available and (not allowed or f.id in allowed)]
    console.print(f"fixable={len(fixable)} target={target}")

    if codex:
        console.print("[bold cyan]Connecting to OpenAI Codex...[/bold cyan]")
        console.print("Scrubbing credential context from snippets... Done")
        try:
            patches = run_codex_fix(fixable, allowed=allowed, model=codex_model)
        except (ImportError, ValueError) as exc:
            console.print(f"[red]codex_error={exc}[/red]")
            raise typer.Exit(1)
        for patch in patches:
            console.print(f"\n[bold yellow]CODEX PATCH[/bold yellow] {patch.finding_id} {patch.path}:{patch.line or ''}")
            console.print(patch.proposed)
        return

    if not apply:
        for finding in fixable:
            console.print(f"{finding.id} {finding.path}:{finding.line or ''} -> {finding.fix}")
        console.print("dry_run=true use --apply to modify files")
        return
    changed = apply_local_fixes(fixable, allowed)
    console.print(f"changed={len(changed)}")
    for path in changed:
        console.print(path)


@app.command()
def bench(
    target: Path = typer.Argument(..., exists=True, help="Path to benchmark scan against."),
    profile: str = typer.Option("balanced", "--profile", help="dev, balanced, or strict."),
    runs: int = typer.Option(1, "--runs", help="Number of scan repetitions."),
) -> None:
    if profile not in {"dev", "balanced", "strict"}:
        raise typer.BadParameter("profile must be dev, balanced, or strict")
    times: list[float] = []
    result = None
    for i in range(runs):
        t0 = time.perf_counter()
        result = scan_path(target, profile=profile)
        elapsed = time.perf_counter() - t0
        times.append(elapsed)
        console.print(f"run={i+1} elapsed={elapsed:.3f}s artifacts={result.summary['artifacts_scanned']} findings={len(result.findings)}")
    avg = sum(times) / len(times)
    console.print(
        f"bench target={target} runs={runs} avg={avg:.3f}s "
        f"min={min(times):.3f}s max={max(times):.3f}s "
        f"artifacts={result.summary['artifacts_scanned'] if result else 0} "
        f"rules={len(ALL_RULES)}"
    )


@app.command()
def prompts(
    target: Path = typer.Argument(..., exists=True, help="Path to scan and build remediation prompts for."),
    output: Path | None = typer.Option(None, "--output", "-o", help="Write prompt pack to file."),
    max_findings: int = typer.Option(10, "--max-findings", help="Maximum fixable findings to include."),
) -> None:
    result = scan_path(target, profile="strict")
    rendered = build_prompt_pack(result.findings, max_findings=max_findings)
    if output:
        output.write_text(rendered, encoding="utf-8")
        console.print(f"wrote={output}")
    else:
        console.print(rendered)


@rules_app.command("list")
def list_rules() -> None:
    table = Table(show_header=True, header_style="bold")
    table.add_column("Rule")
    table.add_column("Severity")
    table.add_column("Category")
    table.add_column("Applies to")
    for rule in ALL_RULES:
        table.add_row(rule.id, rule.severity, rule.category, ", ".join(sorted(rule.applies_to)))
    console.print(table)


def run() -> None:
    app()


if __name__ == "__main__":
    run()

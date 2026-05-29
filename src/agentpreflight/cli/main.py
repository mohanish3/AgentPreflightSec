from __future__ import annotations

import sys
import time
from enum import Enum
from pathlib import Path

import typer
from rich.console import Console
from rich.markup import escape
from rich.table import Table

from agentpreflight import __version__
from agentpreflight.cli.repl import run_repl
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

_MAX_TABLE_ROWS = 20


class OutputFormat(str, Enum):
    table = "table"
    json = "json"
    sarif = "sarif"
    markdown = "markdown"


_SEVERITY_RANK = {"low": 1, "medium": 2, "high": 3, "critical": 4}

_SEVERITY_COLOR = {
    "critical": "bold red",
    "high": "bold yellow",
    "medium": "yellow",
    "low": "dim",
}


def _should_fail(findings, fail_on: str | None) -> bool:
    if not fail_on:
        return False
    threshold = _SEVERITY_RANK[fail_on]
    return any(_SEVERITY_RANK[f.severity] >= threshold for f in findings)


def _render_table(result) -> None:
    verdict_color = "green" if result.verdict == "pass" else "yellow" if result.verdict == "warn" else "red"
    console.print(f"[bold]AgentPreflight[/bold] target={result.target}")
    console.print(
        f"trust_score=[bold {verdict_color}]{result.trust_score}[/bold {verdict_color}]"
        f" verdict=[bold {verdict_color}]{result.verdict}[/bold {verdict_color}]"
        f" findings={len(result.findings)} offline={result.offline}"
    )
    console.print(
        f"summary critical={result.summary['critical']} high={result.summary['high']} "
        f"medium={result.summary['medium']} low={result.summary['low']} "
        f"suppressed={result.summary.get('suppressed', 0)} artifacts={result.summary['artifacts_scanned']}"
    )
    if not result.findings:
        console.print("[bold green]PASS: no issues found[/bold green]")
        return
    sorted_findings = sorted(result.findings, key=lambda f: _SEVERITY_RANK[f.severity], reverse=True)
    shown = sorted_findings[:_MAX_TABLE_ROWS]
    hidden = len(sorted_findings) - len(shown)
    table = Table(show_header=True, header_style="bold")
    table.add_column("Severity", min_width=8)
    table.add_column("Rule")
    table.add_column("Path")
    table.add_column("Line", justify="right")
    table.add_column("Evidence")
    for finding in shown:
        sev_color = _SEVERITY_COLOR.get(finding.severity, "")
        table.add_row(
            f"[{sev_color}]{finding.severity}[/{sev_color}]",
            finding.id,
            Path(finding.path).name,
            str(finding.line or ""),
            escape(finding.evidence),
        )
    console.print(table)
    if hidden:
        console.print(f"[dim]...and {hidden} more finding{'s' if hidden > 1 else ''} - use --format json for full output[/dim]")
    fixable = sum(1 for f in result.findings if f.fix_available)
    if fixable:
        console.print(f"[cyan]fix_available={fixable}[/cyan] run: agentpreflight fix {result.target}")


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
) -> None:
    if profile not in {"dev", "balanced", "strict"}:
        raise typer.BadParameter("profile must be dev, balanced, or strict")
    if fail_on and fail_on not in _SEVERITY_RANK:
        raise typer.BadParameter("fail-on must be low, medium, high, or critical")

    try:
        if format == OutputFormat.table:
            with console.status(f"[dim]scanning {target} (profile={profile})...[/dim]"):
                result = scan_path(target, profile=profile, suppression_file=suppressions)
        else:
            result = scan_path(target, profile=profile, suppression_file=suppressions)
    except PermissionError as exc:
        console.print(f"[red]error:[/red] permission denied: {exc}")
        raise typer.Exit(2)
    except OSError as exc:
        console.print(f"[red]error:[/red] could not read target: {exc}")
        raise typer.Exit(2)

    if format == OutputFormat.json:
        rendered = json_reporter.render(result)
    elif format == OutputFormat.sarif:
        rendered = sarif_reporter.render(result)
    elif format == OutputFormat.markdown:
        rendered = markdown_reporter.render(result)
    else:
        rendered = ""
        _render_table(result)

    if output:
        output.write_text(rendered, encoding="utf-8")
        console.print(f"wrote={output}")
    elif rendered:
        sys.stdout.write(rendered)
        if not rendered.endswith("\n"):
            sys.stdout.write("\n")

    if _should_fail(result.findings, fail_on):
        raise typer.Exit(1)


@app.command()
def fix(
    target: Path = typer.Argument(..., exists=True, help="Path to scan and locally remediate."),
    rules: str | None = typer.Option(None, "--rules", help="Comma-separated rule IDs to fix."),
    apply: bool = typer.Option(False, "--apply", help="Apply local safe fixes."),
    prove: bool = typer.Option(False, "--prove", help="Rescan after --apply to show before/after score."),
    codex: bool = typer.Option(False, "--codex", help="Generate Codex AI patch proposals (requires OPENAI_API_KEY)."),
    codex_model: str = typer.Option("codex-mini-latest", "--codex-model", help="OpenAI model for Codex remediation."),
) -> None:
    with console.status(f"[dim]scanning {target} (profile=strict)...[/dim]"):
        result = scan_path(target, profile="strict")
    score_before = result.trust_score
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
        dry_table = Table(show_header=True, header_style="bold")
        dry_table.add_column("Severity", min_width=8)
        dry_table.add_column("Rule")
        dry_table.add_column("Path")
        dry_table.add_column("Line", justify="right")
        dry_table.add_column("Fix")
        for finding in fixable:
            sev_color = _SEVERITY_COLOR.get(finding.severity, "")
            dry_table.add_row(
                f"[{sev_color}]{finding.severity}[/{sev_color}]",
                finding.id,
                Path(finding.path).name,
                str(finding.line or ""),
                escape(finding.fix),
            )
        console.print(dry_table)
        console.print("[dim]dry_run=true - use --apply to modify files[/dim]")
        return
    changed = apply_local_fixes(fixable, allowed)
    console.print(f"changed={len(changed)}")
    for path in changed:
        console.print(path)

    if prove and changed:
        with console.status("[dim]rescanning to verify fixes...[/dim]"):
            after = scan_path(target, profile="strict")
        verdict_color = "green" if after.verdict == "pass" else "yellow" if after.verdict == "warn" else "red"
        delta = after.trust_score - score_before
        delta_str = f"[bold green]+{delta}[/bold green]" if delta > 0 else f"[bold red]{delta}[/bold red]" if delta < 0 else "0"
        console.print(
            f"rescan trust_score=[bold {verdict_color}]{after.trust_score}[/bold {verdict_color}]"
            f" verdict=[bold {verdict_color}]{after.verdict}[/bold {verdict_color}]"
            f" delta={delta_str} findings={len(after.findings)}"
        )


def _collect_mtimes(target: Path) -> dict[Path, float]:
    paths = list(target.rglob("*")) if target.is_dir() else [target]
    result: dict[Path, float] = {}
    for p in paths:
        try:
            if p.is_file():
                result[p] = p.stat().st_mtime
        except OSError:
            pass
    return result


@app.command()
def watch(
    target: Path = typer.Argument(..., exists=True, help="Path to watch and rescan on change."),
    profile: str = typer.Option("balanced", "--profile", help="dev, balanced, or strict."),
    fail_on: str | None = typer.Option(None, "--fail-on", help="low, medium, high, or critical."),
    interval: int = typer.Option(3, "--interval", help="Poll interval in seconds."),
    suppressions: Path | None = typer.Option(None, "--suppressions", help="Path to suppressions file."),
) -> None:
    """Watch target for changes and rescan automatically."""
    if profile not in {"dev", "balanced", "strict"}:
        raise typer.BadParameter("profile must be dev, balanced, or strict")
    if fail_on and fail_on not in _SEVERITY_RANK:
        raise typer.BadParameter("fail-on must be low, medium, high, or critical")

    console.print(f"[bold]AgentPreflight watch[/bold] target={target} interval={interval}s profile={profile}")
    console.print("[dim]Press Ctrl+C to stop.[/dim]\n")

    mtimes: dict[Path, float] = {}
    scan_count = 0

    try:
        while True:
            current = _collect_mtimes(target)
            changed = current != mtimes

            if changed:
                mtimes = current
                scan_count += 1
                ts = time.strftime("%H:%M:%S")

                if scan_count > 1:
                    console.rule(f"[dim]{ts} change detected -rescanning[/dim]")
                else:
                    console.rule(f"[dim]{ts} initial scan[/dim]")

                with console.status(f"[dim]scanning (profile={profile})...[/dim]"):
                    result = scan_path(target, profile=profile, suppression_file=suppressions)

                _render_table(result)

                if _should_fail(result.findings, fail_on):
                    console.print(f"[bold red]FAIL[/bold red] threshold={fail_on} exceeded")
                else:
                    console.print(f"[dim]watching... next poll in {interval}s[/dim]")

            time.sleep(interval)
    except KeyboardInterrupt:
        console.print("\n[dim]watch stopped[/dim]")


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
    table.add_column("Severity", min_width=8)
    table.add_column("Category")
    table.add_column("Applies to")
    for rule in ALL_RULES:
        sev_color = _SEVERITY_COLOR.get(rule.severity, "")
        table.add_row(
            rule.id,
            f"[{sev_color}]{rule.severity}[/{sev_color}]",
            rule.category,
            ", ".join(sorted(rule.applies_to)),
        )
    console.print(table)


@app.command()
def shell(
    target: Path | None = typer.Argument(None, help="Optional path to scan immediately on entry."),
    profile: str = typer.Option("balanced", "--profile", help="Default profile for session."),
    fail_on: str | None = typer.Option(None, "--fail-on", help="Fail threshold for session."),
) -> None:
    """Start interactive shell with session state and command history."""
    if profile not in {"dev", "balanced", "strict"}:
        raise typer.BadParameter("profile must be dev, balanced, or strict")
    run_repl(initial_target=target, profile=profile, fail_on=fail_on)


_SUPPRESSION_TEMPLATE = """{
  "version": "1.0",
  "suppressions": []
}
"""

_SUPPRESSION_EXAMPLE = """\
Example suppression entry:
  {
    "rule": "AP-SEC-003",
    "path": ".env",
    "reason": "env file intentionally included for local dev only",
    "owner": "appsec",
    "expires": "2026-12-31"
  }

Fields:
  rule    - rule ID or "*" to suppress all rules for the path
  path    - filename or glob (e.g. "*.env", "tests/*")
  reason  - required human description
  owner   - team or person responsible
  expires - ISO date; suppression becomes inactive after this date
"""


@app.command()
def init(
    target: Path = typer.Argument(Path("."), help="Directory to create suppression file in."),
    force: bool = typer.Option(False, "--force", help="Overwrite existing file."),
) -> None:
    """Create a .agentpreflight.json suppression template in target directory."""
    if not target.is_dir():
        console.print(f"[red]error:[/red] {target} is not a directory")
        raise typer.Exit(1)
    out = target / ".agentpreflight.json"
    if out.exists() and not force:
        console.print(f"[yellow]exists:[/yellow] {out} (use --force to overwrite)")
        raise typer.Exit(0)
    out.write_text(_SUPPRESSION_TEMPLATE, encoding="utf-8")
    console.print(f"[green]created:[/green] {out}")
    console.print()
    console.print(_SUPPRESSION_EXAMPLE)


def run() -> None:
    app()


if __name__ == "__main__":
    run()

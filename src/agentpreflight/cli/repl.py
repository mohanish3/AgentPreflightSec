"""Interactive shell for AgentPreflight -persistent session with command history."""
from __future__ import annotations

import shlex
from pathlib import Path

from rich.console import Console
from rich.table import Table

from agentpreflight import __version__
from agentpreflight.remediator.local_fix import apply_local_fixes
from agentpreflight.reporters import json_reporter, sarif_reporter
from agentpreflight.rules.catalog import ALL_RULES
from agentpreflight.scanner import scan_path

_HISTORY_FILE = Path.home() / ".agentpreflight_history"

console = Console()

_SEVERITY_RANK = {"low": 1, "medium": 2, "high": 3, "critical": 4}
_SEVERITY_COLOR = {
    "critical": "bold red",
    "high": "bold yellow",
    "medium": "yellow",
    "low": "dim",
}

_COMMANDS = ["scan", "fix", "rescan", "rules", "export", "clear", "help", "exit", "quit"]

_HELP = """\
[bold]AgentPreflight shell[/bold] -available commands

  [cyan]scan[/cyan] [path] [--profile dev|balanced|strict] [--fail-on low|medium|high|critical]
      Scan a target. Omit path to rescan the last target.

  [cyan]fix[/cyan] [path] [--apply] [--rules AP-MCP-001,...]
      Show (or apply) local safe fixes. Omit path to use last target.

  [cyan]rescan[/cyan]
      Rescan last target with same profile.

  [cyan]export[/cyan] [json|sarif] [output-file]
      Export last scan result. Prints to stdout if no file given.

  [cyan]rules[/cyan]
      List all rules.

  [cyan]clear[/cyan]
      Clear the screen.

  [cyan]help[/cyan] / [cyan]?[/cyan]
      Show this help.

  [cyan]exit[/cyan] / [cyan]quit[/cyan] / [bold]Ctrl-D[/bold]
      Exit shell.
"""


def _try_enable_readline(history_file: Path = _HISTORY_FILE) -> None:
    try:
        import readline

        if history_file.exists():
            readline.read_history_file(str(history_file))
        readline.set_history_length(500)

        commands = _COMMANDS
        readline.set_completer(lambda text, state: (
            [c for c in commands if c.startswith(text)] + [None]
        )[state])
        readline.parse_and_bind("tab: complete")
    except (ImportError, OSError):
        pass


def _save_readline_history(history_file: Path = _HISTORY_FILE) -> None:
    try:
        import readline
        history_file.parent.mkdir(parents=True, exist_ok=True)
        readline.write_history_file(str(history_file))
    except (ImportError, OSError):
        pass


def _render_result(result: ScanResult) -> None:
    from agentpreflight.cli.main import _render_table
    _render_table(result)


def _cmd_scan(args: list[str], session: dict) -> None:
    profile = session["profile"]
    fail_on = session["fail_on"]
    path_arg = None

    i = 0
    while i < len(args):
        token = args[i]
        if token == "--profile" and i + 1 < len(args):
            profile = args[i + 1]
            i += 2
        elif token == "--fail-on" and i + 1 < len(args):
            fail_on = args[i + 1]
            i += 2
        elif not token.startswith("--"):
            path_arg = token
            i += 1
        else:
            i += 1

    target = Path(path_arg) if path_arg else session.get("last_target")
    if target is None:
        console.print("[red]error:[/red] no target -provide a path or run scan after a previous target was set")
        return
    if not target.exists():
        console.print(f"[red]error:[/red] path does not exist: {target}")
        return
    if profile not in {"dev", "balanced", "strict"}:
        console.print(f"[red]error:[/red] profile must be dev, balanced, or strict")
        return

    with console.status(f"[dim]scanning {target} (profile={profile})...[/dim]"):
        result = scan_path(target, profile=profile)

    session["last_result"] = result
    session["last_target"] = target
    session["profile"] = profile
    session["fail_on"] = fail_on

    _render_result(result)

    if fail_on and fail_on in _SEVERITY_RANK:
        threshold = _SEVERITY_RANK[fail_on]
        if any(_SEVERITY_RANK[f.severity] >= threshold for f in result.findings):
            console.print(f"[bold red]FAIL[/bold red] threshold={fail_on} exceeded")


def _cmd_fix(args: list[str], session: dict) -> None:
    apply = False
    rules_filter = None
    path_arg = None

    i = 0
    while i < len(args):
        token = args[i]
        if token == "--apply":
            apply = True
            i += 1
        elif token == "--rules" and i + 1 < len(args):
            rules_filter = {r.strip() for r in args[i + 1].split(",")}
            i += 2
        elif not token.startswith("--"):
            path_arg = token
            i += 1
        else:
            i += 1

    target = Path(path_arg) if path_arg else session.get("last_target")
    if target is None:
        console.print("[red]error:[/red] no target")
        return

    result = session.get("last_result")
    if result is None or str(result.target) != str(target.resolve()):
        with console.status(f"[dim]scanning {target} (profile=strict)...[/dim]"):
            result = scan_path(target, profile="strict")
        session["last_result"] = result
        session["last_target"] = target

    fixable = [f for f in result.findings if f.fix_available and (not rules_filter or f.id in rules_filter)]
    console.print(f"fixable={len(fixable)} target={target}")

    if not fixable:
        console.print("[dim]no fixable findings[/dim]")
        return

    if not apply:
        table = Table(show_header=True, header_style="bold")
        table.add_column("Severity", min_width=8)
        table.add_column("Rule")
        table.add_column("Path")
        table.add_column("Line", justify="right")
        table.add_column("Fix")
        for finding in fixable:
            sev_color = _SEVERITY_COLOR.get(finding.severity, "")
            table.add_row(
                f"[{sev_color}]{finding.severity}[/{sev_color}]",
                finding.id,
                Path(finding.path).name,
                str(finding.line or ""),
                finding.fix,
            )
        console.print(table)
        console.print("[dim]dry_run=true -use --apply to modify files[/dim]")
        return

    score_before = result.trust_score
    changed = apply_local_fixes(fixable, rules_filter)
    console.print(f"changed={len(changed)}")
    for p in changed:
        console.print(p)
    session["last_result"] = None  # invalidate -rescan needed

    if changed:
        with console.status("[dim]rescanning to verify fixes...[/dim]"):
            after = scan_path(target, profile="strict")
        session["last_result"] = after
        session["last_target"] = target
        verdict_color = "green" if after.verdict == "pass" else "yellow" if after.verdict == "warn" else "red"
        delta = after.trust_score - score_before
        delta_str = f"+{delta}" if delta > 0 else str(delta)
        console.print(
            f"rescan trust_score=[bold {verdict_color}]{after.trust_score}[/bold {verdict_color}]"
            f" verdict=[bold {verdict_color}]{after.verdict}[/bold {verdict_color}]"
            f" delta=[{'bold green' if delta > 0 else 'bold red'}]{delta_str}[/{'bold green' if delta > 0 else 'bold red'}]"
            f" findings={len(after.findings)}"
        )


def _cmd_export(args: list[str], session: dict) -> None:
    result = session.get("last_result")
    if result is None:
        console.print("[red]error:[/red] no scan result -run scan first")
        return

    fmt = args[0] if args else "json"
    out_path = Path(args[1]) if len(args) >= 2 else None

    if fmt == "json":
        rendered = json_reporter.render(result)
    elif fmt == "sarif":
        rendered = sarif_reporter.render(result)
    else:
        console.print(f"[red]error:[/red] unknown format {fmt!r} -use json or sarif")
        return

    if out_path:
        out_path.write_text(rendered, encoding="utf-8")
        console.print(f"wrote={out_path}")
    else:
        console.print(rendered)


def _cmd_rules() -> None:
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


def _build_prompt(session: dict) -> str:
    parts = ["agentpreflight"]
    last_result = session.get("last_result")
    last_target = session.get("last_target")
    if last_target:
        parts.append(f"({Path(last_target).name}")
        if last_result:
            score = last_result.trust_score
            verdict = last_result.verdict
            color_open = "\033[32m" if verdict == "pass" else "\033[33m" if verdict == "warn" else "\033[31m"
            color_close = "\033[0m"
            parts[-1] += f" {color_open}{score}{color_close}"
        parts[-1] += ")"
    return " ".join(parts) + "> "


def run_repl(initial_target: Path | None = None, profile: str = "balanced", fail_on: str | None = None) -> None:
    _try_enable_readline()

    session: dict = {
        "last_result": None,
        "last_target": initial_target,
        "profile": profile,
        "fail_on": fail_on,
    }

    console.print(f"[bold]AgentPreflight[/bold] {__version__} -type [cyan]help[/cyan] for commands, [cyan]exit[/cyan] to quit")
    if initial_target:
        console.print(f"[dim]target={initial_target}[/dim]")

    # Auto-scan initial target if provided
    if initial_target:
        _cmd_scan([], session)

    while True:
        try:
            line = input(_build_prompt(session)).strip()
        except (EOFError, KeyboardInterrupt):
            console.print("\n[dim]bye[/dim]")
            _save_readline_history()
            break

        if not line:
            continue

        try:
            tokens = shlex.split(line)
        except ValueError as exc:
            console.print(f"[red]parse error:[/red] {exc}")
            continue

        cmd = tokens[0].lower()
        args = tokens[1:]

        if cmd in ("exit", "quit"):
            console.print("[dim]bye[/dim]")
            _save_readline_history()
            break
        elif cmd == "help" or cmd == "?":
            console.print(_HELP)
        elif cmd == "clear":
            console.clear()
        elif cmd == "scan":
            _cmd_scan(args, session)
        elif cmd == "rescan":
            if not session.get("last_target"):
                console.print("[red]error:[/red] no previous target")
            else:
                _cmd_scan([], session)
        elif cmd == "fix":
            _cmd_fix(args, session)
        elif cmd == "export":
            _cmd_export(args, session)
        elif cmd == "rules":
            _cmd_rules()
        else:
            console.print(f"[yellow]unknown command:[/yellow] {cmd!r} -type [cyan]help[/cyan]")

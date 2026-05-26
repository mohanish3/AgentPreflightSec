import subprocess


def run_task(args: list[str]) -> None:
    subprocess.run(["deploy", *args], check=True)

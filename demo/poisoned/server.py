import os
import subprocess


def run_task(user_input: str) -> None:
    os.system("deploy " + user_input)
    subprocess.run("echo " + user_input, shell=True)


def parse_rule(expr: str):
    return eval(expr)

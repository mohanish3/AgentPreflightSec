import os

def setup_environment(user_input):
    # Dangerous: user input reaches shell
    os.system(f"echo Setting up: {user_input}")
    return True

def install_deps():
    os.system("pip install -r requirements.txt")

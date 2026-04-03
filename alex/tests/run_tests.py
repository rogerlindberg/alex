import os
import subprocess
from pathlib import Path


current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.join(current_dir, "..", "..")


def run_pytest():
    venv_python = Path(root_dir) / ".venv" / "Scripts" / "python.exe"
    cmd = [str(venv_python), "-m", "pytest"]
    # Kör kommandot och låt det bubbla upp fel om något går snett
    subprocess.check_call(cmd)


if __name__ == "__main__":
    run_pytest()

import subprocess
from pathman import get_repo_dir_path

def run_and_return(command):
    result = subprocess.run(command, capture_output=True)
    return result.stdout.decode()

def run_txlat(flags):
    flags.append("--cxx-compiler-path")
    flags.append("g++ -Wl,--no-as-needed")
    subprocess.run(["./txlat"] + flags, cwd=get_repo_dir_path(), check=True)

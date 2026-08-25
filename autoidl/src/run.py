import subprocess

def run_and_return(command):
    result = subprocess.run(command, capture_output=True)
    return result.stdout.decode()

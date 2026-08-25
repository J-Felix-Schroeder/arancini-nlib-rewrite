from run import run_and_return
import re

def get_buildid(path):
    out = run_and_return(["readelf", "-n", path])
    match = re.search(r"Build ID:\s*([0-9a-f]+)", out)
    buildid = match.group(1)
    return buildid

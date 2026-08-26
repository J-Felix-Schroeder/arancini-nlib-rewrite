#fake lib maker
import subprocess, os
from pathman import get_flib_c_path, get_flib_path, get_translated_path
from run import run_txlat

def build_flib(library): 
    soname = library.soname
    flib_c_path = get_flib_c_path(soname)
    flib_c = open(flib_c_path, "w")
    for sig in library.signatures:
        if not sig.is_supported():
            continue # yeah so there will be a bunch of missing functions
        flib_c.write("void " + sig.name + "(void){}\n")
    flib_c.close()

    out = get_flib_path(soname)
    subprocess.run(["x86_64-linux-gnu-gcc", "-shared", "-nostdlib", "-fno-builtin", "-Wl,-soname," + soname, "-o", out, flib_c_path])
    return out

def translate_flib(soname, flibpath, idlpath):
    outpath = get_translated_path(soname)
    flags = []
    flags.append("-I")
    flags.append(flibpath)
    flags.append("-O")
    flags.append(outpath)
    flags.append("--nlib")
    flags.append(idlpath)
    run_txlat(flags)
    return outpath

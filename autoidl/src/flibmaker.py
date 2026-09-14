#fake lib maker
import subprocess, os
from pathman import get_flib_c_path, get_flib_path, get_translated_path, get_musl_libc_path, get_musl_lid_path
from run import run_txlat

def build_flib(soname, idl_path):
    flib_c_path = get_flib_c_path(soname)
    flib_c = open(flib_c_path, "w")
    for line in open(idl_path):
        if line.startswith("#") or line.startswith("library") or "(" not in line:
            continue
        name = line.split("(")[0].split()[-1]
        flib_c.write("void " + name + "(void){}\n")
    flib_c.close()

    out = get_flib_path(soname)
    subprocess.run(["x86_64-linux-gnu-gcc", "-shared", "-nostdlib", "-fno-builtin", "-Wl,-soname," + soname, "-o", out, flib_c_path])
    return out

def translate_libc():
    outpath = get_translated_path("libc.so")
    flags = []
    flags.append("-I")
    flags.append(get_musl_libc_path())
    flags.append("-O")
    flags.append(outpath)
    flags.append("--nlib")
    flags.append(get_musl_lid_path())
    run_txlat(flags)
    return outpath

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

import ctypes, os, glob
from elfhelper import get_buildid
from run import run_and_return
from pathman import get_amd64_cache_path

def debuginfod_find(buildid):
    os.environ["DEBUGINFOD_URLS"] = "https://debuginfod.debian.net https://debuginfod.elfutils.org"
    path = run_and_return(["debuginfod-find", "debuginfo", buildid]).strip()
    if not os.path.isfile(path):
        return None
    return path

def get_dwarf_path(soname, arch):
    path = get_path_from_soname(soname)
    buildid = get_buildid(path)
    dwarf_path = "/usr/lib/debug/.build-id/"+buildid[:2] + "/" + buildid[2:] + ".debug"
    if os.path.isfile(dwarf_path):
        return dwarf_path
    return debuginfod_find(buildid)

class _LinkMap(ctypes.Structure):
    _fields_ = [("l_addr", ctypes.c_void_p), ("l_name", ctypes.c_char_p)]

def get_path_from_soname(soname):
    lib = ctypes.CDLL(soname)
    libc = ctypes.CDLL(None)
    libc.dlinfo.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.c_void_p]
    lm = ctypes.POINTER(_LinkMap)()
    if libc.dlinfo(ctypes.c_void_p(lib._handle), 2, ctypes.byref(lm)) == 0:
        return lm.contents.l_name.decode() or None

def package_line(dpkg_out):
    for line in dpkg_out.splitlines():
        line = line.strip()
        if not line or line.startswith("diversion by"):
            continue
        return line.split(":", 1)[0].strip()
    return None

def get_packagename(lib_path):
    dpkg_out = run_and_return(["dpkg", "-S", os.path.realpath(lib_path)])
    pkg = package_line(dpkg_out)
    if pkg:
        return pkg
    for line in dpkg_out.splitlines():
        if line.startswith("diversion by") and " from: " in line:
            return package_line(run_and_return(["dpkg", "-S", line.split(" from: ", 1)[1].strip()]))
    return None

def find_lib(cachedir, native_path):
    lib_filename = os.path.basename(native_path)
    realname = os.path.basename(os.path.realpath(native_path))
    for pattern in [lib_filename, realname, lib_filename + ".*", realname + "*"]:
        found = glob.glob(os.path.join(cachedir, "**/" + pattern), recursive=True)
        found = [m for m in found if os.path.isfile(m)]
        if found:
            return found[0]
    return None

def debian_version(pkgname):
    for line in run_and_return(["apt-cache", "madison", pkgname + ":amd64"]).splitlines():
        if "deb.debian.org" in line:
            return line.split("|")[1].strip()
    return None

def amd64_so_path(soname, native_path):
    cachedir = get_amd64_cache_path(soname)
    found = find_lib(cachedir, native_path)
    if found:
        return found
    package = get_packagename(native_path)
    if package is None:
        return None
    version = debian_version(package)
    if version is None:
        return None
    os.makedirs(cachedir, exist_ok=True)
    run_and_return(["apt", "download", package + ":amd64=" + version], cachedir)
    matches = glob.glob(os.path.join(cachedir, "*.deb"))
    if not matches:
        return None
    run_and_return(["dpkg-deb", "-x", os.path.abspath(matches[0]), cachedir], cachedir)
    return find_lib(cachedir, native_path)

def get_amd64_dwarf_path(soname):
    x86_lib_path = amd64_so_path(soname, get_path_from_soname(soname))
    if x86_lib_path is None:
        return None
    buildid = get_buildid(x86_lib_path)
    if buildid is None:
        return None
    return debuginfod_find(buildid)

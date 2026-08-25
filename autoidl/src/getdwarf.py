import ctypes, os
from elfhelper import get_buildid

def get_dwarf_path(soname, arch):
    path = get_path_from_soname(soname)
    buildid = get_buildid(path)
    dwarf_path = "/usr/lib/debug/.build-id/"+buildid[:2] + "/" + buildid[2:] + ".debug"
    if not os.path.isfile(dwarf_path):
        return None
    return dwarf_path

class _LinkMap(ctypes.Structure):
    _fields_ = [("l_addr", ctypes.c_void_p), ("l_name", ctypes.c_char_p)]

def get_path_from_soname(soname):
    lib = ctypes.CDLL(soname)
    libc = ctypes.CDLL(None)
    libc.dlinfo.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.c_void_p]
    lm = ctypes.POINTER(_LinkMap)()
    if libc.dlinfo(ctypes.c_void_p(lib._handle), 2, ctypes.byref(lm)) == 0:
        return lm.contents.l_name.decode() or None

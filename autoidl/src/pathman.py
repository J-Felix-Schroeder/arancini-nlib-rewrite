#path manager
import os

def get_aidl_dir_path():
    file_dir_path = os.path.dirname(os.path.abspath(__file__))
    aidl_dir_path = os.path.abspath(os.path.join(file_dir_path, ".."))
    return aidl_dir_path

def get_repo_dir_path():
    aidl_dir_path = get_aidl_dir_path()
    repo_dir_path = os.path.abspath(os.path.join(aidl_dir_path, ".."))
    return repo_dir_path

def get_out_dir_path():
    aidl_dir_path = get_aidl_dir_path()
    out_dir_path = os.path.join(aidl_dir_path, "out")
    return out_dir_path

def get_idl_dir_path():
    return os.path.join(get_out_dir_path(), "idl")

def get_flib_dir_path():
    return os.path.join(get_out_dir_path(), "flib")

def get_translated_dir_path():
    return os.path.join(get_out_dir_path(), "translated")

def get_musl_dir_path():
    return os.path.join(get_aidl_dir_path(), "musl")

def get_musl_libc_path():
    return os.path.join(get_musl_dir_path(), "musl-x86_64", "lib", "libc.so")

def get_musl_lid_path():
    return os.path.join(get_musl_dir_path(), "libc.lid")

def get_musl_auto_lid_path():
    return os.path.join(get_musl_dir_path(), "libc.auto.lid")

def get_testsets_dir_path():
    return os.path.join(get_aidl_dir_path(), "testsets")

def get_box64_sonames_path():
    return os.path.join(get_testsets_dir_path(), "box64_sonames.txt")

def get_box64_trimmed_path():
    return os.path.join(get_testsets_dir_path(), "box64_trimmed.txt")

def get_idl_path(soname):
    return os.path.join(get_idl_dir_path(), soname + ".lid")

def get_flib_c_path(soname):
    return os.path.join(get_flib_dir_path(), soname + ".c")

def get_flib_path(soname):
    return os.path.join(get_flib_dir_path(), soname)

def get_translated_path(soname):
    return os.path.join(get_translated_dir_path(), soname)

def setup_dirs():
    os.makedirs(get_idl_dir_path(), exist_ok=True)
    os.makedirs(get_flib_dir_path(), exist_ok=True)
    os.makedirs(get_translated_dir_path(), exist_ok=True)

setup_dirs()

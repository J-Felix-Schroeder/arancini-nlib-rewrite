import argparse
from getdwarf import get_dwarf_path, get_path_from_soname
from elfhelper import get_exported_symbols, get_dtneeded
from dwarfhelper import get_signatures
from aidlsig import AidlLibrary, AidlSignature
from flibmaker import build_flib, translate_flib, translate_libc
from pathman import get_idl_path, get_musl_auto_lid_path
from run import run_txlat

def merge(soname, path, symbols, signatures):
    sigs = []
    for addr, names in symbols.items():
        if addr not in signatures:
            continue
        sig = signatures[addr]
        for name in names:
            sigs.append(AidlSignature(name, sig.return_type, sig.arguments))
    return AidlLibrary(soname, path, sigs)

def process_libc():
    # so we can copy libc idl easily to the lid file used for translation
    path = get_path_from_soname("libc.so.6")
    dwarf_path = get_dwarf_path("libc.so.6", None)
    symbols = get_exported_symbols(path)
    signatures = get_signatures(dwarf_path)
    library = merge("libc.so.6", path, symbols, signatures)
    with open(get_musl_auto_lid_path(), "w") as f:
        f.write(str(library))
    return translate_libc()

def translate_elf(elf_path, libs, out_path):
    flags = []
    flags.append("-I")
    flags.append(elf_path)
    for lib in libs:
        flags.append("-l")
        flags.append(lib)
    flags.append("-O")
    flags.append(out_path)
    run_txlat(flags)
    return out_path

def process_soname(soname):
    print("processing", soname)
    if soname == "libc.so" or soname == "libc.so.6":
        return process_libc()
    path = get_path_from_soname(soname)
    dwarf_path = get_dwarf_path(soname, None)
    print("dwarf path:", dwarf_path)
    symbols = get_exported_symbols(path)
    signatures = get_signatures(dwarf_path)
    library = merge(soname, path, symbols, signatures)
    idl_path = get_idl_path(soname)
    with open(idl_path, "w") as f:
        f.write(str(library))
    flib_path = build_flib(library)
    return translate_flib(soname, flib_path, idl_path)

def main():
    p = argparse.ArgumentParser(prog="autoidl", description="automatic idl generation")
    p.add_argument("-s", "--soname", nargs="?")
    p.add_argument("-i", "--input",  nargs="?")
    p.add_argument("-o", "--output", nargs="?")
    args = p.parse_args()
    
    sonames = []
    
    if args.soname:
        sonames.append(args.soname)
    if args.input:
        sonames = sonames + get_dtneeded(args.input)

    if not sonames:
        print("no sonames provided")

    libs = []
    for soname in sonames:
        libs.append(process_soname(soname))

    if args.input and args.output:
        translate_elf(args.input, libs, args.output)

if __name__ == "__main__":
    main()


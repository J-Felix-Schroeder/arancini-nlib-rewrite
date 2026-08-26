import argparse
from getdwarf import get_dwarf_path, get_path_from_soname
from elfhelper import get_exported_symbols
from dwarfhelper import get_signatures
from aidlsig import AidlLibrary, AidlSignature
from flibmaker import build_flib, translate_flib
from pathman import get_idl_path

def merge(soname, path, symbols, signatures):
    sigs = []
    for addr, names in symbols.items():
        if addr not in signatures:
            continue
        sig = signatures[addr]
        for name in names:
            sigs.append(AidlSignature(name, sig.return_type, sig.arguments))
    return AidlLibrary(soname, path, sigs)

def process_soname(soname):
    print("processing", soname)
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
    args = p.parse_args()
    
    sonames = []
    
    if args.soname:
        sonames.append(args.soname)

    if not sonames:
        print("no sonames provided")

    for soname in sonames:
        process_soname(soname)

if __name__ == "__main__":
    main()


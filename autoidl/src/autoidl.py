import argparse
import os
from getdwarf import get_dwarf_path, get_path_from_soname, get_amd64_dwarf_path
import structchecker
from elfhelper import get_exported_symbols, get_ifuncs, get_dtneeded
from dwarfhelper import get_signatures
import dwarfhelper
from aidlsig import AidlLibrary, AidlSignature
from flibmaker import build_flib, translate_flib, translate_libc
from pathman import get_idl_path, get_auto_idl_path, get_lib_path, get_musl_auto_lid_path, get_translated_path
from run import run_txlat
import analytics

analyze = False
struct_check = True
libc = False

def analyze_lib(library, symbols):
    analytics.start()
    analytics.fill("soname", library.soname)
    seen = []
    for names in symbols.values():
        for name in names:
            if name in seen:
                continue
            seen.append(name)
    exported = len(seen)
    supported = 0
    for sig in library.signatures:
        reasons = set(sig.unsupported_reasons())
        if not reasons:
            supported = supported + 1
            for tag in sig.features_used():
                analytics.fill_feature(tag)
        for reason in reasons:
            analytics.fill_record(reason)
    analytics.fill("total_fn_count", exported)
    analytics.fill("described_fn_count", len(library.signatures))
    analytics.fill("supported_fn_count", supported)

def merge(soname, path, symbols, ifuncs, signatures, declarations):
    sigs = []
    seen = []
    for addr, names in symbols.items():
        sig = signatures.get(addr)
        for name in names:
            if sig is None or name in ifuncs:
                sig = declarations.get(name)
        if sig is None:
            continue
        for name in names: 
            if name in seen:
                continue  
            seen.append(name)
            sigs.append(AidlSignature(name, sig.return_type, sig.arguments))
    return AidlLibrary(soname, path, sigs)

def process_libc():
    # so we can copy libc idl easily to the lid file used for translation
    path = get_path_from_soname("libc.so.6")
    dwarf_path = get_dwarf_path("libc.so.6", None)
    dwarfhelper.structmap = None
    if struct_check:
        dwarfhelper.structmap = structchecker.build_structmap(dwarf_path, get_amd64_dwarf_path("libc.so.6"))
    symbols = get_exported_symbols(path)
    ifuncs = get_ifuncs(path)
    signatures, declarations = get_signatures(dwarf_path)
    library = merge("libc.so.6", path, symbols, ifuncs, signatures, declarations)
    analyze_lib(library, symbols)
    with open(get_musl_auto_lid_path(), "w") as f:
        f.write(str(library))
    if analyze:
        return None
    if libc:
        return translate_libc()
    return get_translated_path("libc.so")

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
    analytics.record("libs_attempted")
    if soname == "libc.so" or soname == "libc.so.6":
        return process_libc()
    path = get_path_from_soname(soname)
    dwarf_path = get_dwarf_path(soname, None)
    print("dwarf path:", dwarf_path)
    if dwarf_path is None:
        analytics.record("no_debug_info")
        return None
    dwarfhelper.structmap = None
    if struct_check:
        amd64_dwarf_path = get_amd64_dwarf_path(soname)
        dwarfhelper.structmap = structchecker.build_structmap(dwarf_path, amd64_dwarf_path)
    symbols = get_exported_symbols(path)
    ifuncs = get_ifuncs(path)
    signatures, declarations = get_signatures(dwarf_path)
    library = merge(soname, path, symbols, ifuncs, signatures, declarations)
    analyze_lib(library, symbols)
    with open(get_auto_idl_path(soname), "w") as f:
        f.write(str(library))
    if analyze:
        return None
    idl_path = get_idl_path(soname)
    if not os.path.isfile(idl_path):
        idl_path = get_auto_idl_path(soname)
    lib_path = get_lib_path(soname)
    if not os.path.isfile(lib_path): # only do fakelib if not real lib exist
        lib_path = build_flib(soname, idl_path)
    return translate_flib(soname, lib_path, idl_path)

def main():
    p = argparse.ArgumentParser(prog="autoidl", description="automatic idl generation")
    p.add_argument("-s", "--soname", help="soname input", nargs="+")
    p.add_argument("-f", "--file", help="file with one soname per line", nargs="?")
    p.add_argument("-i", "--input", help="input binary to translate", nargs="?")
    p.add_argument("-o", "--output", help="output path", nargs="?")
    p.add_argument("--anal", help="only run analytics, dont translate", action="store_true")
    p.add_argument("--no-struct-check", help="skip struct check and whitelist all structs", action="store_true")
    p.add_argument("--translate-libc", help="(re-)translate libc", action="store_true")
    args = p.parse_args()
    global struct_check
    struct_check = not args.no_struct_check
    global libc
    libc = args.translate_libc
    global analyze
    analyze = args.anal
    
    sonames = []
    
    if args.soname:
        sonames = sonames + args.soname
    if args.file:
        sonames = sonames + open(args.file).read().split()
    if args.input:
        sonames = sonames + get_dtneeded(args.input)

    if not sonames:
        print("no sonames provided")

    libs = []
    for soname in sonames:
        lib = process_soname(soname)
        if lib is not None:
            libs.append(lib)

    analytics.summarize()

    if args.input and args.output:
        translate_elf(args.input, libs, args.output)

if __name__ == "__main__":
    main()


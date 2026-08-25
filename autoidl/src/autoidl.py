import argparse
from getdwarf import get_dwarf_path

def process_soname(soname):
    print("processing", soname)
    print("dwarf path:", get_dwarf_path(soname, None))

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


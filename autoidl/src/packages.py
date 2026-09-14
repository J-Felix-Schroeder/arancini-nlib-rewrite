from getdwarf import get_path_from_soname, get_packagename, get_dwarf_path
from pathman import get_box64_trimmed_path

def main():
    sonames = open(get_box64_trimmed_path()).read().split()
    processed = []
    unprocessed = []
    for soname in sonames:
        try:
            path = get_path_from_soname(soname)
        except Exception:
            continue
        package = get_packagename(path)
        if get_dwarf_path(soname, None) is None:
            if package not in unprocessed:
                unprocessed.append(package)
        elif package not in processed:
            processed.append(package)
    for package in processed:
        if package in unprocessed:
            unprocessed.remove(package)
    print("processed")
    for package in processed:
        print(package)
    print("unprocessed")
    for package in unprocessed:
        print(package)

if __name__ == "__main__":
    main()

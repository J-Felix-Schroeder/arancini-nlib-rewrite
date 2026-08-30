import os
from getdwarf import get_path_from_soname
from pathman import get_box64_sonames_path, get_box64_trimmed_path

def main():
    sonames = open(get_box64_sonames_path()).read().split()
    trimmed = []
    seen_paths = []
    not_installed = 0
    duplicates = 0
    for soname in sonames:
        try:
            path = os.path.realpath(get_path_from_soname(soname))
        except OSError:
            print(soname, "not installed")
            not_installed = not_installed + 1
            continue
        if path in seen_paths:
            print(soname, "duplicate")
            duplicates = duplicates + 1
            continue
        seen_paths.append(path)
        trimmed.append(soname)
    with open(get_box64_trimmed_path(), "w") as f:
        f.write("\n".join(trimmed) )
    print("total", len(sonames))
    print("untrimmed", len(trimmed))
    print("trimmed (not installed)", not_installed)
    print("trimmed (duplicate)", duplicates)

if __name__ == "__main__":
    main()

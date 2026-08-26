from elftools.elf.elffile import ELFFile

def get_buildid(path):
    f = open(path, "rb")
    elf = ELFFile(f)
    buildid = None
    for note in elf.get_section_by_name(".note.gnu.build-id").iter_notes():
        if note["n_type"] == "NT_GNU_BUILD_ID":
            buildid = note["n_desc"]
    f.close()
    return buildid

def get_exported_symbols(path):
    f = open(path, "rb")
    elf = ELFFile(f)
    dynsym = elf.get_section_by_name(".dynsym")
    symbols = {}
    for sym in dynsym.iter_symbols():
        if not sym.name:
            continue
        if sym['st_info']['type'] not in ('STT_FUNC', 'STT_GNU_IFUNC'):
            continue
        if sym['st_shndx'] == 'SHN_UNDEF':
            continue
        if sym['st_value'] == 0:
            continue
        if not symbols.get(sym["st_value"]):
            symbols[sym["st_value"]] = []
        symbols[sym["st_value"]].append(sym.name)
    f.close()

    return symbols

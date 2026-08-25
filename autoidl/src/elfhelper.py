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

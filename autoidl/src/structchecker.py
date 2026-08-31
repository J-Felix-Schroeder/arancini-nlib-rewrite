from structrepack import StructRepack, InstructionType
from aidlsig import AidlInt, AidlFnptr
from elftools.elf.elffile import ELFFile
from aidlstruct import AidlStruct, AidlMember
from dwarfhelper import get_type, load_supplementary, name_of, strip, attr

def get_structs(debug_path):
    f = open(debug_path, "rb")
    elf = ELFFile(f)
    dwarf = elf.get_dwarf_info()
    load_supplementary(debug_path, elf, dwarf)

    dwarfs = [dwarf]
    if dwarf.supplementary_dwarfinfo is not None:
        dwarfs.append(dwarf.supplementary_dwarfinfo)
    structs = []
    for unit in [unit for d in dwarfs for unit in d.iter_CUs()]:
        for die in unit.iter_DIEs():
            name = name_of(die, None)
            if die.tag == "DW_TAG_typedef":
                die = strip(die)
                if die is None or die.tag != "DW_TAG_structure_type" or "DW_AT_name" in die.attributes:
                    continue
            if die.tag != "DW_TAG_structure_type" or "DW_AT_declaration" in die.attributes:
                continue
            size = attr(die, "DW_AT_byte_size")
            if name is None or size is None:
                continue
            members = []
            for member in die.iter_children():
                if member.tag != "DW_TAG_member":
                    continue
                mname = name_of(member, None)
                moff = attr(member, "DW_AT_data_member_location")
                mtarget = strip(member)
                if mname is None or not isinstance(moff, int) or mtarget is None:
                    continue
                msize = attr(mtarget, "DW_AT_byte_size")
                if msize is None:
                    continue
                members.append(AidlMember(mname, moff, msize, get_type(member)))
            structs.append(AidlStruct(name, size, frozenset(members)))
    f.close()
    return frozenset(structs)

def _find_member(struct, name):
    for m in struct.members:
        if m.name == name:
            return m
    return None

def generate_repack(structa, structb):
    repack = StructRepack(structa.name, structa.size, structb.size)
    if structa.size != structb.size:
        repack.mark_cant_repack()
        repack.add_reason("struct_size_mismatch")
    for bmember in structb.members:
        if _find_member(structa, bmember.name) is None:
            repack.mark_cant_repack()
            repack.add_reason("struct_member_missing")
    for amember in structa.members:
        bmember = _find_member(structb, amember.name)
        if bmember is None:
            repack.mark_cant_repack()
            repack.add_reason("struct_member_missing")
            continue
        if type(amember.mtype) == AidlFnptr or type(bmember.mtype) == AidlFnptr:
            repack.mark_needs_repack()
            repack.add_reason("struct_member_fnptr")
            repack.add_instruction(InstructionType.COPY_FNPTR, amember.name, amember.offset, bmember.offset) #fixed size 8 bit
            continue
        if amember.size != bmember.size:
            if type(amember.mtype) == AidlInt and type(bmember.mtype) == AidlInt:
                repack.mark_needs_repack()
                repack.add_reason("struct_int_size_mismatch")
                repack.add_instruction(InstructionType.COPY_INT, amember.name, amember.offset, bmember.offset, amember.size, bmember.size) 
            else:
                repack.mark_cant_repack()
                repack.add_reason("struct_member_size_mismatch")
            continue
        if amember.offset != bmember.offset:
            repack.mark_needs_repack()
            repack.add_reason("struct_offset_mismatch")
        repack.add_instruction(InstructionType.COPY, amember.name, amember.offset, bmember.offset, amember.size)
    return repack

def _index_by_name(structs):
    by_name = {}
    for s in structs:
        if s.name not in by_name:
            by_name[s.name] = s
    return by_name

def build_structmap(arm64_path, amd64_path):
    arm_structs = get_structs(arm64_path)
    x86_structs = frozenset()
    if amd64_path is not None:
        x86_structs = get_structs(amd64_path)
    x86_by_name = _index_by_name(x86_structs)
    structmap = {}
    for s in arm_structs:
        other = x86_by_name.get(s.name)
        if other is None:
            structmap[s.name] = StructRepack(s.name, s.size, 0)
            structmap[s.name].mark_cant_repack()
            structmap[s.name].add_reason("struct_missing_on_amd64")
            continue
        structmap[s.name] = generate_repack(s, other)
    return structmap

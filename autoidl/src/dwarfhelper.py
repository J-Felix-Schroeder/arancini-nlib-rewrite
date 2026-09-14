import os
from elftools.elf.elffile import ELFFile
from elftools.dwarf.enums import ENUM_DW_ATE, ENUM_DW_LANG
from getdwarf import debuginfod_find
from aidlsig import AidlBasicType, AidlInt, AidlFloat, AidlPointer, AidlFnptr, AidlStructptr, AidlUnsupported, AidlArgument, AidlSignature

AGGREGATE_TAGS = ["DW_TAG_structure_type", "DW_TAG_union_type", "DW_TAG_class_type"]

structmap = None

def origin(die):
    if "DW_AT_abstract_origin" in die.attributes:
        return die.get_DIE_from_attribute("DW_AT_abstract_origin")
    if "DW_AT_specification" in die.attributes:
        return die.get_DIE_from_attribute("DW_AT_specification")
    return None

def attr(die, name):
    while die is not None:
        if name in die.attributes:
            return die.attributes[name].value
        die = origin(die)
    return None

def name_of(die, default):
    raw = attr(die, "DW_AT_name")
    if isinstance(raw, bytes):
        return raw.decode()
    return default

def strip(die):
    while True:
        while "DW_AT_type" not in die.attributes:
            die = origin(die)
            if die is None:
                return None
        die = die.get_DIE_from_attribute("DW_AT_type")
        if die.tag not in ["DW_TAG_const_type", "DW_TAG_volatile_type", "DW_TAG_restrict_type", "DW_TAG_atomic_type", "DW_TAG_typedef"]:
            return die

def struct_name(die):
    typedef = None
    while "DW_AT_type" in die.attributes:
        die = die.get_DIE_from_attribute("DW_AT_type")
        if die.tag == "DW_TAG_typedef":
            typedef = name_of(die, None)
        if die.tag not in ["DW_TAG_const_type", "DW_TAG_volatile_type", "DW_TAG_restrict_type", "DW_TAG_atomic_type", "DW_TAG_typedef"]:
            break
    return name_of(die, typedef)

def base_type(die):
    size = attr(die, "DW_AT_byte_size")
    enc = attr(die, "DW_AT_encoding")
    if size is None or enc is None:
        return AidlUnsupported("base_type_no_size_or_encoding")
    if enc in [ENUM_DW_ATE["DW_ATE_signed"], ENUM_DW_ATE["DW_ATE_signed_char"]]:
        return AidlInt(size * 8, True)
    if enc in [ENUM_DW_ATE["DW_ATE_unsigned"], ENUM_DW_ATE["DW_ATE_unsigned_char"], ENUM_DW_ATE["DW_ATE_boolean"], ENUM_DW_ATE["DW_ATE_UTF"]]:
        return AidlInt(size * 8, False)
    if enc == ENUM_DW_ATE["DW_ATE_float"]:
        if size > 8:
            return AidlUnsupported("long_double")
        return AidlFloat(size * 8)
    return AidlUnsupported("encoding_" + str(enc))

def pointer_type(die):
    target = strip(die)
    if target is None:
        return AidlPointer(AidlBasicType.VOID)
    if target.tag == "DW_TAG_subroutine_type":
        if not attr(target, "DW_AT_prototyped"):
            return AidlUnsupported("unprototyped_fnptr")
        return AidlFnptr(get_signature(target))
    if target.tag in ["DW_TAG_structure_type", "DW_TAG_union_type"]:
        name = struct_name(die)
        if name is None:
            return AidlUnsupported("struct_noname")
        return AidlStructptr(name, struct_reasons(name))
    if target.tag in AGGREGATE_TAGS:
        return AidlUnsupported("aggregate_ptr")
    return AidlPointer(get_type(die))

def struct_reasons(name):
    if structmap is None:
        return ()
    if name not in structmap:
        return () 
    return tuple(structmap[name].reasons())

def get_type(die):
    die = strip(die)
    if die is None:
        return AidlBasicType.VOID
    if die.tag == "DW_TAG_base_type":
        return base_type(die)
    if die.tag in ["DW_TAG_pointer_type", "DW_TAG_reference_type", "DW_TAG_rvalue_reference_type"]:
        return pointer_type(die)
    if die.tag == "DW_TAG_enumeration_type":
        size = attr(die, "DW_AT_byte_size")
        if size is None:
            return AidlUnsupported("enum_without_size")
        return AidlInt(size * 8, True)
    if die.tag in AGGREGATE_TAGS:
        return AidlUnsupported("aggregate_by_val")
    return AidlUnsupported(die.tag)

def get_signature(die):
    name = name_of(die, "nonamefn")
    fortran = attr(die.cu.get_top_DIE(), "DW_AT_language") == ENUM_DW_LANG["DW_LANG_Fortran08"] # fortran has "pointers" for everything so we need to treat it different
    args = []
    for child in die.iter_children():
        if child.tag == "DW_TAG_unspecified_parameters":
            args.append(AidlArgument(AidlBasicType.VARARG, ""))
        elif child.tag == "DW_TAG_formal_parameter":
            argname = name_of(child, "arg" + str(len(args)))
            if argname in ["library", "string", "fd", "ptr"]:
                argname = argname + "_arg"
            target = strip(child)
            if fortran and "DW_AT_artificial" not in child.attributes and (target is None or target.tag != "DW_TAG_pointer_type"):
                args.append(AidlArgument(AidlBasicType.PTR, argname))
            else:
                args.append(AidlArgument(get_type(child), argname))
    return AidlSignature(name, get_type(die), tuple(args))

def load_supplementary(dwarf_path, elf, dwarf):
    section = elf.get_section_by_name(".gnu_debugaltlink")
    if section is None:
        return
    name, buildid = section.data().split(b"\x00", 1)
    sup_path = os.path.join(os.path.dirname(dwarf_path), name.decode())
    if not os.path.isfile(sup_path):
        sup_path = debuginfod_find(buildid.hex())
    if sup_path is None:
        return
    dwarf.supplementary_dwarfinfo = ELFFile(open(sup_path, "rb")).get_dwarf_info()

def get_signatures(dwarf_path):
    f = open(dwarf_path, "rb")
    elf = ELFFile(f)
    dwarf = elf.get_dwarf_info()
    load_supplementary(dwarf_path, elf, dwarf)
    signatures = {}
    declarations = {}
    for cu in dwarf.iter_CUs():
        if attr(cu.get_top_DIE(), "DW_AT_language") == ENUM_DW_LANG["DW_LANG_Mips_Assembler"]: # yes assembler is named so though its not really mips
            continue
        for die in cu.iter_DIEs():
            if die.tag != "DW_TAG_subprogram":
                continue
            if "DW_AT_low_pc" in die.attributes:
                lowpc = die.attributes["DW_AT_low_pc"].value
                if lowpc not in signatures:
                    signatures[lowpc] = get_signature(die)
            name = name_of(die, None)
            if name is not None and name not in declarations:
                declarations[name] = get_signature(die)
    f.close()
    return signatures, declarations

# struct repacking type definitions

from enum import Enum
from dataclasses import dataclass
from typing import Any
class InstructionType(Enum):
    STRUCTDEF = "structdef" #structdef struct_name size_from size_to
    COPY = "copy" #copy member_name off_from off_to size
    COPY_INT = "copy_int"
    COPY_FNPTR = "copy_fnptr"

    def __str__(self):
        return self.value

@dataclass
class Instruction:
    instruction_type : Any
    args : Any

    def __str__(self):
        return str(self.instruction_type) + " " + str(self.args)

class StructRepack:

    def __init__(self, name, sizea, sizeb):
        self.name = name
        self.instructions = []
        self.reason_tags = []
        self.can_repack = True
        self.needs_repack = False
        self.add_instruction(InstructionType.STRUCTDEF, name, sizea, sizeb)

    def add_instruction(self, instruction_type, *args):
        self.instructions.append(Instruction(instruction_type, args))

    def add_reason(self, reason):
        if reason not in self.reason_tags:
            self.reason_tags.append(reason)

    def mark_needs_repack(self):
        self.needs_repack = True

    def mark_cant_repack(self):
        self.can_repack = False

    def reasons(self):
        if self.can_repack and not self.needs_repack:
            return []
        if self.reason_tags:
            return self.reason_tags
        if not self.can_repack:
            return ["struct_unrepackable"]
        return ["struct_needs_repack"]

    def __str__(self):
        res = ""
        for i in self.instructions:
            res += str(i) + "\n"
        return res

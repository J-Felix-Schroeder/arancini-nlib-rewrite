from dataclasses import dataclass
from typing import Any

class AidlType:
    def idl_name(self):
        return "I have no name and I must scream"

    def unsupported_reasons(self):
        return []

    def is_supported(self):
        return not self.unsupported_reasons()

    def __str__(self):
        return self.idl_name()

@dataclass(frozen=True)
class AidlVoid(AidlType):
    def idl_name(self):
        return "void"

@dataclass(frozen=True)
class AidlInt(AidlType):
    bits: Any
    signed: Any

    def idl_name(self):
        return ("i" if self.signed else "u") + str(self.bits)

    def unsupported_reasons(self):
        if self.bits not in (8, 16, 32, 64):
            return ["unsupported_int_width_" + str(self.bits)]
        return []

@dataclass(frozen=True)
class AidlFloat(AidlType):
    bits: Any

    def idl_name(self):
        return "f" + str(self.bits)

    def unsupported_reasons(self):
        return ["float"]

@dataclass(frozen=True)
class AidlVararg(AidlType):
    def idl_name(self):
        return "..."

    def unsupported_reasons(self):
        return ["vararg"]

@dataclass(frozen=True)
class AidlUnsupported(AidlType):
    detail: Any

    def idl_name(self):
        return "unsupported"

    def unsupported_reasons(self):
        return ["unsupported_" + self.detail]

@dataclass(frozen=True)
class AidlPointer(AidlType):
    type: Any

    def idl_name(self):
        return "ptr"

@dataclass(frozen=True)
class AidlFnptr(AidlPointer):
    def signature(self):
        return self.type

    def idl_name(self):
        return "fnptr"

    def unsupported_reasons(self):
        return ["fnptr"]

@dataclass(frozen=True)
class AidlStructptr(AidlType):
    name: Any
    reasons: Any

    def idl_name(self):
        return "i64"

    def unsupported_reasons(self):
        return list(self.reasons)

class AidlBasicType:
    VOID = AidlVoid()
    VARARG = AidlVararg()
    I8, I16, I32, I64 = AidlInt(8, True), AidlInt(16, True), AidlInt(32, True), AidlInt(64, True)
    U8, U16, U32, U64 = AidlInt(8, False), AidlInt(16, False), AidlInt(32, False), AidlInt(64, False)
    F32, F64 = AidlFloat(32), AidlFloat(64)
    PTR = AidlPointer(None)

@dataclass(frozen=True)
class AidlArgument:
    type: Any
    name: Any

    def __str__(self):
        return (str(self.type) + " " + self.name).strip()

@dataclass(frozen=True)
class AidlSignature:
    name: Any
    return_type: Any
    arguments: Any

    def unsupported_reasons(self):
        reasons = list(self.return_type.unsupported_reasons())
        for arg in self.arguments:
            reasons += arg.type.unsupported_reasons()
        return reasons

    def is_supported(self):
        return not self.unsupported_reasons()

    def __str__(self):
        args = ", ".join(str(arg) for arg in self.arguments)
        return str(self.return_type) + " " + self.name + "(" + args + ")"

@dataclass(frozen=True)
class AidlLibrary:
    soname: Any
    path: Any
    signatures: Any

    def __str__(self):
        lines = ['library "' + self.path + '";']
        for sig in self.signatures:
            prefix = ""
            if not sig.is_supported():
                prefix = "#" 
            lines.append(prefix + str(sig) + ";")
        return "\n".join(lines)

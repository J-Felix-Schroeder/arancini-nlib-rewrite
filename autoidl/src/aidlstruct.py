from dataclasses import dataclass
from typing import Any

@dataclass(frozen=True)
class AidlStruct:
    name : Any
    size : Any
    members : Any

@dataclass(frozen=True)
class AidlMember:
    name : Any
    offset : Any
    size : Any
    mtype : Any

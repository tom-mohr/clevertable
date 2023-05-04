from __future__ import annotations

from .Function import Function


class Const(Function):

    def __init__(self, val: any):
        self.__val = val
        super().__init__(lambda _: val)

    def __repr__(self):
        return f"Const({self.__val})"

#!/usr/bin/env python3
# coding=utf-8

import bitarray
from .consts import *
from .utils import *


class Bits(bitarray.bitarray):
    DEFAULT_BYTE_ORDER = BYTE_ORDER

    def __init__(self, initial=None, clean=True, **kwargs):
        super().__init__()

        if clean and isinstance(initial, int):
            self.setall(0)

    # def __init__(self, *args, byte_order=DEFAULT_BYTE_ORDER, **kwargs):


    def __bytes__(self) -> bytes:
        return self.tobytes()

    def __int__(self) -> int:
        delta = ceil8(len(self)) - len(self)
        if delta:
            bits = Bits(delta) + self
        else:
            bits = self
        return int.from_bytes(bytes(bits), BYTE_ORDER)

    def __bool__(self) -> bool:
        return all(self.tolist())

    @classmethod
    def fromint(cls, value: int, length: int, byte_order=DEFAULT_BYTE_ORDER):
        return cls.frombytes(value.to_bytes((length + 7) // 8, byte_order))[-length:]

    @classmethod
    def frombytes(cls, value: bytes, byte_order=DEFAULT_BYTE_ORDER):
        c = cls()
        super(cls, c).frombytes(value)
        return c  # type:Bits

    def tobits(self):
        return self

    def __repr__(self):
        return "{}<{},{}>".format(self.__class__.__name__, self.hex(), len(self))

    def ljust(self, length):
        delta = length - len(self)
        if delta <= 0:
            return self
        else:
            return self + Bits(delta)

    def rjust(self, length):
        delta = length - len(self)
        if delta <= 0:
            return self
        else:
            return Bits(delta) + self

    def __hash__(self):
        return hash((len(self), bytes(self)))

    def hex(self):
        return bytes(self).hex()

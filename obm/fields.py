#!/usr/bin/env python3
# coding=utf-8
from .datastruct import Bits
from .fields_base import FieldBase


class IntField(FieldBase):
    def bits2py(self, bits: Bits) -> int:
        return int(bits)

    def py2bits(self, value: int, length: int, **kwargs) -> Bits:
        return Bits.fromint(value, length)


class BytesField(FieldBase):
    def bits2py(self, bits: Bits) -> bytes:
        return bytes(bits)

    def py2bits(self, value: bytes, length: int, **kwargs) -> Bits:
        return Bits.frombytes(value)


class BitsField(FieldBase):
    def bits2py(self, bits: Bits) -> Bits:
        return bits

    def py2bits(self, value: Bits, length: int, **kwargs) -> Bits:
        if isinstance(value, Bits):
            return value
        elif isinstance(value, (bool, tuple, list, str)):
            if len(value) == length:
                return Bits(value)
            else:
                return Bits(value) + Bits(length - len(value))
        elif value in (0, 1):
            b = Bits(length)
            b.setall(value)
            return b
        else:
            raise ValueError()

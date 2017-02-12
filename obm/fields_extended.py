#!/usr/bin/env python3
# coding=utf-8
import collections
from .datastruct import Bits
from .fields_base import FieldBase
from .model_base import PackageBase


class PrefixedOptionsField(FieldBase):
    def __init__(self, length, options: dict, name=None, default=0):
        super().__init__(length, name, default)
        self.options = {}
        lengths = set()
        for key, value in options.items():
            if isinstance(key, (bytes, bytearray)):
                key = Bits.frombytes(key)

            self.options[key] = value

            lengths.add(len(key))

        self._options_key_length_choices = sorted(lengths)

    def bits2py(self, bits: Bits) -> list:
        length = len(bits)
        i = 0
        offset = self._options_key_length_choices[0]
        result = list()
        while i + offset <= length:
            for offset in self._options_key_length_choices:
                if i + offset > length:
                    continue

                piece = bits[i:i + offset]
                if piece not in self.options:
                    continue

                opt = self.options[piece]

                if not isinstance(opt, (bytes, bytearray)) and issubclass(opt, PackageBase):
                    if opt.variable_fields:
                        opt = opt.frombits(bits[i:], drop_payload=True)
                    else:
                        opt = opt.frombits(bits[i:i + opt.solid_length], drop_payload=True)

                result.append(opt)
                if isinstance(opt, (bytearray, bytes)):
                    i += len(Bits.frombytes(opt))
                else:
                    i += len(opt)

                break

            else:
                raise ValueError("unable to decode")

        return result

    def py2bits(self, value: list, length: int, **kwargs) -> Bits:
        # instance._varfields[self.attr_name]=self._bits_walk()
        buffer = Bits()
        for v in value:
            if isinstance(v, PackageBase):
                buffer += v.tobits()
            elif isinstance(v, Bits):
                buffer += v
            elif isinstance(v, (bytes, bytearray)):
                buffer += Bits.frombytes(v)
            else:
                raise ValueError()
        return buffer.ljust(length)

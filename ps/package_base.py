#!/usr/bin/env python3
# coding=utf-8

import inspect
import collections
from .datastruct import Bits
from .fields import FieldBase


class MetaPackage(type):
    @classmethod
    def __prepare__(mcs, name, bases, **kwargs):
        return collections.OrderedDict()

    def __new__(cls, name, bases, attrs):
        # print(name, bases, attrs)
        if name == "PackageBase":
            return super().__new__(cls, name, bases, attrs)

        fields = collections.OrderedDict()
        solid_fields = collections.OrderedDict()
        variable_fields = collections.OrderedDict()
        solid_length = 0
        variable_length = 0
        for k, v in attrs.items():
            if isinstance(v, FieldBase):
                fields[k] = v
                v.attr_name = k
                if v.variable:
                    variable_fields[k] = v
                else:
                    solid_fields[k] = v
                    v.offset = solid_length
                    v._byte_start = solid_length // 8
                    head_spare = v.offset - 8 * v._byte_start
                    v._first_byte_trail_spare = min(8 - head_spare - v.length, 0)
                    v._byte_end = max((v.length + head_spare - 1) // 8, 0)
                    v._first_byte_mask = cls.calc_first_byte_mask(
                        head_spare, v._first_byte_trail_spare
                    )

                    solid_length += v.length

        attrs["fields"] = fields
        attrs["solid_fields"] = solid_fields
        attrs["solid_length"] = solid_length
        attrs["variable_fields"] = variable_fields
        attrs["variable_length"] = variable_length

        return super().__new__(cls, name, bases, attrs)

    @staticmethod
    def calc_first_byte_mask(head_spare, tail_spare):
        if not head_spare and not tail_spare:
            return 0xff
        mask = 0x00
        pointer = 0x80
        for i in range(8):
            if head_spare <= i < 8 - tail_spare:
                mask |= pointer
            pointer >>= 1
        return mask


class PackageBase(metaclass=MetaPackage):
    # fields = collections.OrderedDict()  # placeholder
    # solid_fields = collections.OrderedDict()  # placeholder
    # variable_fields = collections.OrderedDict()  # placeholder
    # solid_length = 0  # placeholder

    def __init__(self, parent=None, payload=None, _blank_init=False, **kwargs):
        self.payload = payload if payload is not None else Bits()
        self.parent = parent

        if _blank_init:
            return

        self.solid_data = Bits(self.solid_length)
        for fname, field in self.solid_fields.items():  # type: str,FieldBase
            setattr(self, fname, kwargs.get(fname, field.default))

        if self.variable_fields:
            self.alloc_variable_fields()
            for fname, field in self.variable_fields.items():
                setattr(self, fname, kwargs.get(fname, field.default))
        else:
            self.variable_data = Bits()

    def alloc_variable_fields(self):
        self._varfields = collections.OrderedDict()
        self.variable_length = 0
        self.variable_data = Bits()
        for fname, field in self.variable_fields.items():  # type:str,FieldBase
            field.var_alloc(self)

        self.variable_length = len(self.variable_data)

    def __len__(self):
        return self.solid_length + self.variable_length + len(self.payload)

    def tobytes(self):
        return bytes(self.solid_data) + bytes(self.variable_data) + bytes(self.payload)

    __bytes__ = tobytes

    def hex(self) -> str:
        return bytes(self).hex()

    def tobits(self):
        return self.solid_data + self.variable_data + Bits(self.payload)

    @classmethod
    def frombytes(cls, bytes: bytes, drop_payload=False, parent=None):
        c = cls(_blank_init=True)
        c.parent = parent
        bits = Bits.frombytes(bytes)
        c.solid_data = bits[:c.solid_length]
        c.alloc_variable_fields()
        c.variable_data = bits[c.solid_length:c.solid_length + c.variable_length]
        if not drop_payload:
            c.payload = bits[c.solid_length + c.variable_length:]
            payload_type = c.payload_type()
            if payload_type is not None:
                # noinspection PyTypeChecker
                if inspect.isclass(payload_type) and issubclass(payload_type, PackageBase):
                    c.payload = payload_type.frombits(c.payload, parent=c)
                else:
                    # noinspection PyCallingNonCallable
                    c.payload = payload_type(c.payload, parent=c)
        else:
            c.payload = Bits()
        return c

    @classmethod
    def frombits(cls, bits: Bits, drop_payload=False, parent=None):
        return cls.frombytes(bytes(bits), drop_payload=drop_payload, parent=parent)

    def payload_type(self):
        return None

    @property
    def header_data(self):
        return self.solid_data + self.variable_data

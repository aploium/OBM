#!/usr/bin/env python3
# coding=utf-8
from .datastruct import Bits


class FieldBase:
    def __init__(self, length, name=None, default=0):
        self.length = length
        self.variable = callable(self.length)
        self.name = name
        self.default = default

        # they will be auto-generated
        self.offset = 0
        self.default = default
        self.attr_name = None
        self._byte_start = 0
        self._byte_end = 0
        self._first_byte_trail_spare = 0
        self._first_byte_mask = 0xff

    def getter(self, instance, owner=None):
        """
        :type instance: PackageBase
        """
        if instance is None:
            return self

        if not self.variable:
            buff = instance.solid_data
            bits = buff[self.offset: self.offset + self.length]
        else:
            buff = instance.variable_data
            offset = instance._varfields[self.attr_name]["offset"]
            length = instance._varfields[self.attr_name]["length"]
            bits = buff[offset: offset + length]

        # if self._first_byte_mask != 0xff:
        #     data_bytes[0] &= self._first_byte_mask

        return self.bits2py(bits)

    __get__ = getter

    def setter(self, instance, value):
        """

        :type instance: PackageBase
        """
        if instance is None:
            raise ValueError()

        if not self.variable:
            if value is None:
                dec = 0
            else:
                dec = self.py2bits(value, self.length, instance=instance).tobits()
            instance.solid_data[self.offset: self.offset + self.length] = dec
        else:
            offset = instance._varfields[self.attr_name]["offset"]
            length = instance._varfields[self.attr_name]["length"]
            if value is None:
                dec = 0
            else:
                dec = self.py2bits(value, length, instance=instance).tobits()
            instance.variable_data[offset: offset + length] = dec

    def var_alloc(self, instance):
        """

        :type instance: PackageBase
        """
        length = self.length(instance)

        instance._varfields[self.attr_name] = dict(
            length=length,
            offset=len(instance.variable_data),
        )

        instance.variable_data.extend(Bits(length))
        return length

    __set__ = setter

    def bits2py(self, bits: Bits) -> Bits:
        # if self.ftype == self.FTYPE_INT:
        #     if self._first_byte_trail_spare:
        #         data_bytes[0] >>= self._first_byte_trail_spare
        #     return int.from_bytes(data_bytes, BYTE_ORDER)
        # else:
        #     return data_bytes

        return bits

    def py2bits(self, value: Bits, length: int, instance=None) -> Bits:
        return value

    def __repr__(self):
        return "{}<{} {}>".format(
            self.__class__.__name__,
            self.attr_name,
            self.length if isinstance(self.length, int) else "variable"
        )

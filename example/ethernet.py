#!/usr/bin/env python3
# coding=utf-8
from obm import Model, IntField, BytesField
from example.ipv4 import IP


class Ethernet(Model):
    dst_mac = BytesField(48)
    src_mac = BytesField(48)
    type = IntField(16)

    def payload_type(self):
        if self.type == 0x0800:
            # TODO: add more protocols
            return IP
        else:
            return None

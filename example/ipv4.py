#!/usr/bin/env python3
# coding=utf-8
from ps import Package, IntField, BitsField
from ps.utils import one_complement_checksum

from example.tcp import TCP


class IP(Package):
    version = IntField(4, default=4)
    ihl = IntField(4, default=5)
    dscp = IntField(6)
    ecn = IntField(2)

    total_length = IntField(16)

    identification = IntField(16)

    flags = BitsField(3)
    fragment_offset = IntField(13)

    ttl = IntField(8)
    protocol = IntField(8)

    checksum = IntField(16)

    src_ip = IntField(32)
    dst_ip = IntField(32)

    options = BitsField(lambda self: max(0, (self.ihl - 5) * 32))

    def fill_checksum(self):
        self.checksum = 0
        self.checksum = one_complement_checksum(bytes(self.solid_data))

    def payload_type(self):
        if self.protocol == 0x06:
            return TCP
        else:
            # TODO: add more
            return None


def send_ipv4():
    import socket
    ip = IP()

    s = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_RAW)


if __name__ == '__main__':
    send_ipv4()

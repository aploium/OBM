#!/usr/bin/env python3
# coding=utf-8
from ps import Package, IntField, BitsField, PrefixedOptionsField
from ps.utils import one_complement_checksum


class TCP(Package):
    src_port = IntField(16)
    dst_port = IntField(16)

    seq_number = IntField(32)
    ack_number = IntField(32)

    data_offset = IntField(4, default=5)
    reserved = BitsField(3)
    ns = IntField(1)
    cwr = IntField(1)
    ece = IntField(1)
    urg = IntField(1)
    ack = IntField(1)
    psh = IntField(1)
    rst = IntField(1)
    syn = IntField(1)
    fin = IntField(1)

    window_size = IntField(16)
    checksum = IntField(16)
    urgent_pointer = IntField(16)

    class OptionMaxSegmentSize(Package):
        prefix = IntField(8, default=2)
        length = IntField(8, default=4)
        value = IntField(16)

    class OptionWindowScale(Package):
        prefix = IntField(8, default=3)
        length = IntField(8, default=3)
        value = IntField(8)

    class OptionSelectiveAckPermitted(Package):
        prefix = IntField(8, default=4)
        length = IntField(8, default=2)

    class OptionSACK(Package):
        prefix = IntField(8, default=5)
        length = IntField(8)
        value = BitsField(length=lambda self: 8 * (self.length - 2))

    class OptionTimestamp(Package):
        prefix = IntField(8, default=8)
        length = IntField(8, default=10)
        value = IntField(64)

    options = PrefixedOptionsField(
        length=lambda self: max(0, 32 * (self.data_offset - 5)),
        options={
            b'\x00': b'\x00',
            b'\x01': b'\x01',
            b'\x02': OptionMaxSegmentSize,
            b'\x03': OptionWindowScale,
            b'\x04': OptionSelectiveAckPermitted,
            b'\x05': OptionSACK,
            b'\x08': OptionTimestamp,
        }
    )

    def fill_checksum(self):
        self.checksum = 0
        ip = self.parent
        placebo_head = ip.src_ip.to_bytes(4, "big") + \
                       ip.dst_ip.to_bytes(4, "big") + \
                       b'\x00\x06' + \
                       len(bytes(self)).to_bytes(2, "big")

        self.checksum = one_complement_checksum(placebo_head + bytes(self))

#!/usr/bin/env python3
# coding=utf-8
import struct
import array
import socket

from .consts import *


def ceil8(num):
    return (num + 7) // 8 * 8


if struct.pack("H", 1) == b"\x00\x01":  # big endian
    def one_complement_checksum(pkt):
        if len(pkt) % 2 == 1:
            pkt += b"\x00"
        s = sum(array.array("H", pkt))
        s = (s >> 16) + (s & 0xffff)
        s += s >> 16
        s = ~s
        return s & 0xffff
else:
    def one_complement_checksum(pkt):
        if len(pkt) % 2 == 1:
            pkt += b"\x00"
        s = sum(array.array("H", pkt))
        s = (s >> 16) + (s & 0xffff)
        s += s >> 16
        s = ~s
        return (((s >> 8) & 0xff) | s << 8) & 0xffff


def ip2int(ip):
    return int.from_bytes(socket.inet_aton(ip), BYTE_ORDER)


def int2ip(integer):
    return socket.inet_ntoa(integer.to_bytes(4, BYTE_ORDER))

#!/usr/bin/env python3
# coding=utf-8
from ps import Package, IntField, BytesField
from example.ipv4 import IP


class Ethernet(Package):
    dst_mac = BytesField(48)
    src_mac = BytesField(48)
    type = IntField(16)

    def payload_type(self):
        if self.type == 0x0800:
            return IP
        else:
            return None


def main():
    raw = bytes.fromhex(
        '000c29ba6742005056c0000808004500'
        '003447124000800627dfc0a88501c0a8'
        '8580b70a1e61ee3bd3cb000000008002'
        '20002bca0000020405b4010303080101'
        '0402'
    )

    ethernet = Ethernet.frombytes(raw)
    pass


if __name__ == '__main__':
    main()

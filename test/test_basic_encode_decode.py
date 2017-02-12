#!/usr/bin/env python3
# coding=utf-8
import unittest
from obm.datastruct import Bits
from obm.fields_base import FieldBase
from example.ethernet import Ethernet
from example.ipv4 import IP
from example.tcp import TCP


class TestBasicDecodeEncode(unittest.TestCase):
    def setUp(self):
        super().setUp()
        self.raw_hex_ethernet = (
            "000c29ba6742" "005056c00008"
            "0800"  # TCP
        )
        self.raw_hex_ip = (
            "450000344712" "4000800627df"
            "c0a88501c0a8" "8580"
        )
        self.raw_hex_tcp = (
            "b70a1e61ee3b" "d3cb00000000"
            "800220002bca" "0000020405b4"
            "010303080101" "0402"
        )
        self.raw_byte_ethernet = bytes.fromhex(self.raw_hex_ethernet)
        self.raw_byte_ip = bytes.fromhex(self.raw_hex_ip)
        self.raw_byte_tcp = bytes.fromhex(self.raw_hex_tcp)

        self.raw_bytes_entire_frame = self.raw_byte_ethernet + self.raw_byte_ip + self.raw_byte_tcp

        self.ethernet = Ethernet.frombytes(self.raw_bytes_entire_frame)

    def test_ethernet_decode(self):
        ethernet = self.ethernet
        self.assertIsInstance(ethernet, Ethernet)

        self.assertEqual(ethernet.dst_mac, bytes.fromhex("000c29ba6742"))
        self.assertEqual(ethernet.src_mac, bytes.fromhex("005056c00008"))
        self.assertEqual(ethernet.type, 0x0800)

        self.assertEqual(bytes(ethernet), self.raw_bytes_entire_frame)
        self.assertEqual(bytes(ethernet.solid_data), self.raw_byte_ethernet)
        self.assertEqual(ethernet.solid_length, len(self.raw_byte_ethernet) * 8)

        self.assertEqual(Ethernet.dst_mac.attr_name, "dst_mac")
        self.assertEqual(Ethernet.src_mac.attr_name, "src_mac")
        self.assertEqual(Ethernet.type.attr_name, "type")

        self.assertIn("dst_mac", Ethernet.fields)
        self.assertIn("src_mac", Ethernet.fields)
        self.assertIn("type", Ethernet.fields)

        self.assertIn("dst_mac", Ethernet.solid_fields)
        self.assertIn("src_mac", Ethernet.solid_fields)
        self.assertIn("type", Ethernet.solid_fields)

        self.assertIs(Ethernet.dst_mac, Ethernet.solid_fields["dst_mac"])
        self.assertIs(Ethernet.src_mac, Ethernet.solid_fields["src_mac"])
        self.assertIs(Ethernet.type, Ethernet.solid_fields["type"])

        self.assertFalse(Ethernet.variable_fields)
        self.assertEqual(Ethernet.variable_length, 0)
        self.assertEqual(ethernet.variable_data, Bits())

        self.assertEqual(Ethernet.dst_mac.length, 48)
        self.assertEqual(Ethernet.src_mac.length, 48)
        self.assertEqual(Ethernet.type.length, 16)

        self.assertEqual(Ethernet.dst_mac.offset, 0)
        self.assertEqual(Ethernet.src_mac.offset, 48)
        self.assertEqual(Ethernet.type.offset, 96)

        self.assertFalse(Ethernet.dst_mac.variable)
        self.assertFalse(Ethernet.src_mac.variable)
        self.assertFalse(Ethernet.type.variable)

    def test_ip_decode(self):
        # ----------- IPv4 -----------
        self.assertIsInstance(self.ethernet.payload, IP)
        ip = self.ethernet.payload  # type: IP

        self.assertEqual(ip.checksum, 0x27df)
        ip.fill_checksum()
        self.assertEqual(ip.checksum, 0x27df)
        ip.checksum = 0x233
        self.assertEqual(ip.checksum, 0x233)
        ip.fill_checksum()
        self.assertEqual(ip.checksum, 0x27df)

        self.assertIs(ip.parent, self.ethernet)

        self.assertEqual(bytes(ip), self.raw_byte_ip + self.raw_byte_tcp)
        self.assertEqual(bytes(ip.solid_data), self.raw_byte_ip)

        self.assertEqual(ip.version, 4)
        self.assertEqual(ip.ihl, 5)
        self.assertEqual(ip.dscp, 0)
        self.assertEqual(ip.ecn, 0)
        self.assertEqual(ip.total_length, 52)
        self.assertEqual(ip.identification, 0x4712)
        self.assertEqual(ip.flags, Bits('010'))
        self.assertEqual(ip.fragment_offset, 0)
        self.assertEqual(ip.ttl, 128)
        self.assertEqual(ip.protocol, 0x06)
        self.assertEqual(ip.src_ip, 0xc0a88501)
        self.assertEqual(ip.dst_ip, 0xc0a88580)
        self.assertEqual(ip.options, Bits())

        for k, v in IP.fields.items():
            self.assertIsInstance(v, FieldBase)
            if v.variable:
                self.assertIn(k, IP.variable_fields)
                self.assertIs(v, IP.variable_fields[k])
            else:
                self.assertIn(k, IP.solid_fields)
                self.assertIs(v, IP.solid_fields[k])

        for k in ("version", "ihl", "dscp", "ecn", "total_length",
                  "identification", "flags", "fragment_offset", "ttl",
                  "protocol", "checksum", "src_ip", "dst_ip"):
            field = getattr(IP, k)
            self.assertIsInstance(field, FieldBase)
            self.assertIs(field, IP.solid_fields[k])
            self.assertEqual(field.attr_name, k)
            self.assertIn(k, IP.fields)
            self.assertIn(k, IP.solid_fields)
            self.assertIn(k, IP.fields)
            self.assertNotIn(k, IP.variable_fields)
            self.assertFalse(field.variable)
            self.assertIsInstance(field.length, int)

        for k in ("options",):
            field = getattr(IP, k)
            self.assertIsInstance(field, FieldBase)
            self.assertIn(k, IP.variable_fields)
            self.assertTrue(callable(field.length))
            self.assertTrue(field.variable)

    def test_tcp_decode(self):
        ethernet = self.ethernet
        ip = ethernet.payload  # type: IP
        self.assertIsInstance(ip.payload, TCP)

        tcp = ip.payload  # type: TCP
        self.assertEqual(tcp.checksum, 0x2bca)
        tcp.fill_checksum()
        self.assertEqual(tcp.checksum, 0x2bca)
        tcp.checksum = 0x2333
        self.assertEqual(tcp.checksum, 0x2333)
        tcp.fill_checksum()
        self.assertEqual(tcp.checksum, 0x2bca)

        self.assertEqual(bytes(tcp), self.raw_byte_tcp)

        self.assertEqual(tcp.src_port, 46858)
        self.assertEqual(tcp.dst_port, 7777)
        self.assertEqual(tcp.seq_number, 0xee3bd3cb)
        self.assertEqual(tcp.ack_number, 0x00000000)
        self.assertEqual(tcp.data_offset, 8)
        self.assertEqual(tcp.reserved, Bits('000'))
        self.assertEqual(tcp.ns, 0)
        self.assertEqual(tcp.cwr, 0)
        self.assertEqual(tcp.ece, 0)
        self.assertEqual(tcp.urg, 0)
        self.assertEqual(tcp.ack, 0)
        self.assertEqual(tcp.psh, 0)
        self.assertEqual(tcp.rst, 0)
        self.assertEqual(tcp.syn, 1)
        self.assertEqual(tcp.fin, 0)
        self.assertEqual(tcp.window_size, 8192)
        self.assertEqual(tcp.urgent_pointer, 0x0000)

        from obm.fields_extended import PrefixedOptionsField
        self.assertIsInstance(TCP.options, PrefixedOptionsField)
        options = tcp.options
        self.assertIsInstance(options, list)
        self.assertIn("options", TCP.fields)
        self.assertIn("options", TCP.variable_fields)
        self.assertIs(TCP.options, TCP.fields["options"])
        self.assertIs(TCP.options, TCP.variable_fields["options"])

        self.assertTrue(TCP.options.variable)
        self.assertTrue(callable(TCP.options.length))

        self.assertEqual(len(options), 6)

        self.assertIsInstance(options[0], TCP.OptionMaxSegmentSize)
        self.assertEqual(options[0].prefix, 2)
        self.assertEqual(options[0].length, 4)
        self.assertEqual(options[0].value, 1460)

        self.assertEqual(options[1], b'\x01')

        self.assertIsInstance(options[2], TCP.OptionWindowScale)
        self.assertEqual(options[2].prefix, 3)
        self.assertEqual(options[2].length, 3)
        self.assertEqual(options[2].value, 8)

        self.assertEqual(options[3], b'\x01')
        self.assertEqual(options[4], b'\x01')

        self.assertIsInstance(options[5], TCP.OptionSelectiveAckPermitted)
        self.assertEqual(options[5].prefix, 4)
        self.assertEqual(options[5].length, 2)

    def test_combined_decode(self):
        self.test_ethernet_decode()
        self.test_tcp_decode()
        self.test_ip_decode()

    def test_tcp_encode_inplace(self):
        tcp = self.ethernet.payload.payload  # type: TCP
        for k, field in TCP.fields.items():
            value = getattr(tcp, k)
            setattr(tcp, k, value)

        self.test_combined_decode()

    def test_ip_encode_inplace(self):
        ip = self.ethernet.payload  # type: IP

        for k, field in IP.fields.items():
            value = getattr(ip, k)
            setattr(ip, k, value)

        self.test_combined_decode()

    def test_ethernet_encode_inplace(self):
        ethernet = self.ethernet  # type: Ethernet

        for k, field in Ethernet.fields.items():
            value = getattr(ethernet, k)
            setattr(ethernet, k, value)

        self.test_combined_decode()

    def test_tcp_encode_new(self):
        tcp = self.ethernet.payload.payload  # type: TCP

        kwargs = {}
        for k, field in TCP.fields.items():
            value = getattr(tcp, k)
            kwargs[k] = value

        tcp = TCP(self.ethernet.payload, **kwargs)
        self.ethernet.payload.payload = tcp

        self.test_combined_decode()

    def test_ip_encode_new(self):
        tcp = self.ethernet.payload.payload  # type: TCP
        ip = self.ethernet.payload  # type: IP

        kwargs = {}
        for k, field in IP.fields.items():
            value = getattr(ip, k)
            kwargs[k] = value

        ip = IP(self.ethernet, payload=tcp, **kwargs)
        self.ethernet.payload = ip

        self.test_combined_decode()

    def test_ethernet_encode_new(self):
        ethernet = self.ethernet  # type: Ethernet
        ip = self.ethernet.payload  # type: IP

        kwargs = {}
        for k, field in Ethernet.fields.items():
            value = getattr(ethernet, k)
            kwargs[k] = value

        ethernet = Ethernet(payload=ip, **kwargs)
        self.ethernet = ethernet
        ip.parent = ethernet

        self.test_combined_decode()

    def test_combined_encode(self):
        self.test_ethernet_encode_new()
        self.test_ip_encode_new()
        self.test_tcp_encode_new()

        self.test_ethernet_encode_new()
        self.test_tcp_encode_new()
        self.test_ip_encode_new()

        self.test_tcp_encode_new()
        self.test_ethernet_encode_new()
        self.test_ip_encode_new()

        self.test_tcp_encode_new()
        self.test_ip_encode_new()
        self.test_ethernet_encode_new()

        self.test_ip_encode_new()
        self.test_tcp_encode_new()
        self.test_ethernet_encode_new()

        self.test_ip_encode_new()
        self.test_ethernet_encode_new()
        self.test_tcp_encode_new()

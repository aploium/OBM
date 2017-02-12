# OBM - Object Bits Mapping
OBM for bits(binary) is like the ORM for database  
Define, encode and decode binary protocol or format in the human way.

## Installation
because this project is in early development status, so pip install is not available yet.
Python3.4+ only, no Py2.x support yet

1. install bitarray
    * linux: `pip3 install bitarray`
    * windows: go and download it here: http://www.lfd.uci.edu/~gohlke/pythonlibs/#bitarray

5. download OBM itself and use it.  
　　`git clone https://github.com/aploium/obm`


## Examples

```python
# define a Ethernet model
# ref https://en.wikipedia.org/wiki/Ethernet_frame
from obm import Model, IntField, BytesField

class Ethernet(Model):
    dst_mac = BytesField(48) # field length is 48bits, not 48bytes
    src_mac = BytesField(48)
    type = IntField(16)

# That's all! All we need to do is define it's structure
#   and the model will do the rest dirty job
# notice: obm itself knows nothing about the Ethernet definition,  
#   you defined it here




# ------ encode a ethernet model ------
ethernet = Ethernet(
    dst_mac=bytes.fromhex("005056c00001"),
    src_mac=bytes.fromhex("000c29ba674c"),
    type=0x0800, # IPv4
)
print(ethernet) # Ethernet<dst_mac=b'\x00PV\xc0\x00\x01' src_mac=b'\x00\x0c)\xbagL' type=2048>
print(bytes(ethernet)) # some bytes...

# ------ decode a ethernet model ------
ethernet = Ethernet.fromhex("005056c00001000c29ba674c0800")
print(ethernet.dst_mac.hex()) # 005056c00001
print(ethernet.src_mac.hex()) # 000c29ba674c
print(ethernet.type) # 2048
print(bytes(ethernet))
```

Let's see a little more complex example:
```python
# define a IPv4 model
# ref https://en.wikipedia.org/wiki/IPv4
from obm import Model, IntField, BitsField

class IP(Model):
    # here, see the `version` field, 
    #   we defined a 4-bits length integer
    #   the bit operation is handled by obm itself
    # the 4-bits integer has the same behavior as normal int
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
    # the options is a variable length field,
    #   so we define how it's length was calculated,
    #   instead of a specified length,
    options = BitsField(lambda self: max(0, (self.ihl - 5) * 32))
    
# ------- definition completed -----
    
ip = IP.fromhex("4500003c055940004006438fc0a8b881c0a8b801")
print(ip)
# IP<version=4 ihl=5 dscp=0 ecn=0 total_length=60 identification=1369 \
#   flags=Bits<40,3> fragment_offset=0 ttl=64 protocol=6 checksum=17295 \
#   src_ip=3232282753 dst_ip=3232282625 options=Bits<,0>
# >
```

The third example of models chaining
Ethernet->IPv4->TCP->real_data
```python
# chaining several models (import from example)
from example.ethernet import Ethernet
ethernet = Ethernet.fromhex(
    "005056c00001000c29ba674c08004500"
    "0040d6c840004006721bc0a8b881c0a8"
    "b801a90004d23c02fd3597ca24818018"
    "00e5f20600000101080a00773265026b"
    "7a2b68656c6c6f776f726c64210a"
)
print(ethernet)
# Ethernet<dst_mac=b'\x00PV\xc0\x00\x01' src_mac=b'\x00\x0c)\xbagL' type=2048
#
#   #---- following the IP payload of Ethernet ---
#   #payload: IP<version=4 ihl=5 dscp=0 ecn=0 total_length=64 \
#     identification=54984 flags=Bits<40,3> fragment_offset=0 \
#     ttl=64 protocol=6 checksum=29211 \
#     src_ip=3232282753 dst_ip=3232282625 \
#     options=Bits<,0> 
#
#   #---- following the TCP payload of IP package ---
#   #payload: TCP<src_port=43264 dst_port=1234 seq_number=1006828853 \
#     ack_number=2546607233 data_offset=8 reserved=Bits<00,3> ns=0 \
#     cwr=0 ece=0 urg=0 ack=1 psh=1 rst=0 syn=0 fin=0 window_size=229 \
#     checksum=61958 urgent_pointer=0 \
#     options=[b'\x01', b'\x01', \
#       OptionTimestamp<prefix=8 length=10 value=33550931642251819 #payload: Bits<,0>>]
#
#   #---- following the real payload of TCP package ---
#   #payload: Bits<68656c6c6f776f726c64210a,96>>>>
#             b'helloworld!\n'

print(type(ethernet.payload)) # <class 'example.ipv4.IP'>
print(type(ethernet.payload.payload)) # <class 'example.tcp.TCP'>
print(bytes(ethernet.payload.payload.payload)) # b'helloworld!\n'
```

for full examples, such as model payload,  
please see the `example` folder.

## Why OBM?

* Direct bits/binary operation is hard and dirty
* To ease your pain dealing with protocol or formats which are not covered by specified libraries.
* Fast prototyping new protocol/format
* Exploiting private protocols
* Upgrade or change protocols syntax with no pain
* Learning the low-level but avoid the dirty bits operation

## Warning
This project is under EARLY development stage,  
　if you think it may be useful, please star it and come back after several weeks :)

import socket

# region Packet constants
# PN = 0xf0
# SOM = 0x1c
# EOM = 0xfa
PREAMBLE = 0xAA  # 170
SOM = 0xC5  # 197
EOM = 0x5C  # 92
POSTAMBLE = 0x3A  # 58
POLYNOMIAL = 0x8C  # 140

PROTO_RAW = 0x0
PROTO_ICMP = 0x1
PROTO_RES1 = 0x2
PROTO_RES2 = 0x4
OPT_FORWARD = 0x8
ICMP_PING = 0x0
ICMP_PONG = 0x1

LOCAL_ADDRESS = int(socket.gethostbyname(socket.gethostname()).split('.')[-1])
print 'LOCAL_ADDRESS is %d' % LOCAL_ADDRESS

# endregion

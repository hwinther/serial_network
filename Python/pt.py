# region Imports
import time
import datetime
import socket
from threading import Thread, Event
import serial

# endregion Imports


"""
TODO:
actually validate packet constructor input to avoid integer overflow
"""

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


# region Packet classes


class Packet(object):
    def __init__(self, data=None):
        # for raw creation
        if not data:
            self.checksum = 0
            self.rawData = ''
            return

        # this does not belong here
        self.rawData = data

        som_pos = data.find(chr(SOM))
        data = data[som_pos + 1:som_pos + 9]
        # end this nonsense <:

        dlenopt = ord(data[0])
        ttlchk = ord(data[1])
        pidseq = ord(data[2])

        self.dataLength = dlenopt >> 4
        self.options = dlenopt & 0xF

        self.timeToLive = ttlchk >> 4
        self.checksum = ttlchk & 0xF

        self.id = pidseq >> 4
        self.sequence = pidseq & 0xF

        self.source = ord(data[3])
        self.destination = ord(data[4])

        self.data = ''
        if self.dataLength:
            self.data = data[5:5 + self.dataLength]

    def calculate_checksum(self):
        chk = 0
        i = 0
        for b in self.all_bytes():
            first = b >> 4
            last = b & 0xF
            # we have to skip the checksum itself when creating a checksum, duh
            if i != 0:
                chk ^= first
            chk ^= last
            i += 1
        return chk

    def all_bytes(self):
        l = list()
        l.append(self.calculate_dlenopt())
        l.append(self.calculate_ttlchk())
        l.append(self.calculate_pidseq())
        l.append(self.source)
        l.append(self.destination)
        for c in self.data:
            l.append(ord(c))
        return l

    def is_valid_checksum(self):
        chk = self.calculate_checksum()
        print 'self.checksum = %d chk = %d' % (self.checksum, chk)
        return self.checksum == chk

    def __str__(self):
        option_list = list()
        if not self.options & 1:
            option_list.append('proto:raw')
        if self.options & 1:
            option_list.append('proto:icmp')
        if self.options & 2:
            option_list.append('proto:res1')
        if self.options & 4:
            option_list.append('proto:res2')
        if self.options & 8:
            option_list.append('opt:forward')
        return 'datalength: %d\noptions: %s (%s)\nttl: %d\nchecksum: %d\nid: %d\nsequence: %d\nsource: %s\ndestination: %s\ndata: %s' \
               % (self.dataLength, self.options, ', '.join(option_list), self.timeToLive, self.checksum, self.id,
                  self.sequence,
                  self.source, self.destination, repr(self.data))

    @classmethod
    def convert_to_class(cls, obj):
        obj.__class__ = cls

    @staticmethod
    def craft_packet(dst, src=LOCAL_ADDRESS, opt=0, ttl=0, pid=0, seq=0, data=''):
        # type: (int, int, int, int, int, int, str) -> Packet
        packet = Packet()
        packet.source = src
        packet.destination = dst
        packet.options = opt
        packet.timeToLive = ttl
        packet.id = pid
        packet.sequence = seq
        packet.data = data
        packet.dataLength = len(data)
        packet.checksum = packet.calculate_checksum()
        return packet

    def calculate_dlenopt(self):
        return self.dataLength * 16 + self.options

    def calculate_ttlchk(self):
        # print 'calc_ttlchk: ttl=%d chk=%d res=%d' % (self.timeToLive, self.checksum, self.timeToLive * 16 + self.checksum)
        return self.timeToLive * 16 + self.checksum

    def calculate_pidseq(self):
        return self.id * 16 + self.sequence

    def get_packet_data(self):
        return chr(self.calculate_dlenopt()) + chr(self.calculate_ttlchk()) + chr(self.calculate_pidseq()) + \
               chr(self.source) + chr(self.destination) + self.data

    def print_raw(self):
        dlenopt = self.calculate_dlenopt()
        ttlchk = self.calculate_ttlchk()
        pidseq = self.calculate_pidseq()
        print 'dlenopt\t%s\t0x%x\t%d' % (bin(dlenopt), dlenopt, dlenopt)
        print 'ttlchk\t%s\t0x%x\t%d' % (bin(ttlchk), ttlchk, ttlchk)
        print 'pidseq\t%s\t0x%x\t%d' % (bin(pidseq), pidseq, pidseq)
        print 'source\t%s\t0x%x\t%d' % (bin(self.source), self.source, self.source)
        print 'dest\t%s\t0x%x\t%d' % (bin(self.destination), self.destination, self.destination)
        i = 0
        for c in self.data:
            print 'data%d\t%s' % (i, bin(ord(c)))
            i += 1

    def __eq__(self, other):
        """Override the default Equals behavior"""
        if isinstance(other, self.__class__):
            return self.calculate_dlenopt() == other.calculate_dlenopt() and \
                   self.calculate_ttlchk() == other.calculate_ttlchk() and \
                   self.calculate_pidseq() == other.calculate_pidseq() and \
                   self.source == other.source and self.destination == other.destination and \
                   self.data == other.data
        return NotImplemented

    def __ne__(self, other):
        """Define a non-equality test"""
        if isinstance(other, self.__class__):
            return not self.__eq__(other)
        return NotImplemented

        # def __hash__(self):
        #     """Override the default hash behavior (that returns the id or the object)"""
        #     return hash(tuple(sorted(self.__dict__.items())))


class IcmpPingPacket(Packet):
    def __init__(self, data=None):
        super(IcmpPingPacket, self).__init__(data)

    @staticmethod
    def craft_packet(dst, src=LOCAL_ADDRESS, opt=0, ttl=0, pid=0, seq=0, data='', packet=None):
        opt |= PROTO_ICMP  # add icmp protocol in case its missing
        # return packet with ICMP_PING data, that's it
        packet = Packet.craft_packet(dst=dst, src=src, opt=opt, ttl=ttl, pid=pid, seq=seq, data=chr(ICMP_PING))
        IcmpPingPacket.convert_to_class(packet)
        return packet

    def craft_pong_response(self):
        return IcmpPongPacket.craft_packet(src=LOCAL_ADDRESS, dst=self.source,
                                           opt=self.options | PROTO_ICMP, ttl=15, pid=self.id,
                                           seq=self.sequence + 1, data=chr(ICMP_PING) + self.data[1:])


class IcmpPongPacket(Packet):
    def __init__(self, data=None):
        super(IcmpPongPacket, self).__init__(data)

    @staticmethod
    def craft_packet(dst, src=LOCAL_ADDRESS, opt=0, ttl=0, pid=0, seq=0, data=''):
        opt |= PROTO_ICMP  # add icmp protocol in case its missing
        # return packet with ICMP_PING data, that's it
        packet = Packet.craft_packet(dst=dst, src=src, opt=opt, ttl=ttl, pid=pid, seq=seq, data=chr(ICMP_PONG))
        IcmpPongPacket.convert_to_class(packet)
        return packet


# endregion Packet classes


class ReceiveHandler(Thread):
    def __init__(self, packet_handler):
        # super(Thread, self).__init__()
        # TODO: what is the difference?
        Thread.__init__(self)
        self.StopEvent = Event()
        self.packetHandler = packet_handler

    def run(self):
        while not self.StopEvent.is_set():
            for packet in self.packetHandler.ReceiveBuffer:
                self.packetHandler.handle_packet(packet)
                # TOOD: assuming we want to remove it after for now
                self.packetHandler.ReceiveBuffer.remove(packet)


class PacketHandler(Thread):
    def __init__(self):
        Thread.__init__(self)
        self.ReceiveBuffer = list()
        self.StopEvent = Event()
        self.receiveHandler = ReceiveHandler(self)
        self.receiveHandler.start()
        self.StopEvents = list()
        self.StopEvents.append(self.StopEvent)
        self.StopEvents.append(self.receiveHandler.StopEvent)
        # protocol related variables
        self.pingTime = datetime.datetime.now()  # assigning a value purely for IDE type recognition

    def recv(self, packet):
        # type: (Packet) -> None
        # the difference between recv and handle_packet is that recv is blocking further reads
        # handle_packet runs in its own thread and can take all the time it wants to process
        if packet.source == LOCAL_ADDRESS:
            print 'Ignoring packet from self'
            packet.print_raw()
        elif packet.destination in [LOCAL_ADDRESS, 255]:
            print 'Received', str(packet)
            self.ReceiveBuffer.append(packet)
        else:
            print 'Ignoring packet that isn\'t for me'
            packet.print_raw()

    def send(self, packet):
        # type: (Packet) -> None
        print 'sending:'
        packet.print_raw()

    def send_ping(self, dst):
        # type: (int) -> None
        self.pingTime = datetime.datetime.now()
        self.send(IcmpPingPacket.craft_packet(dst=dst, opt=PROTO_ICMP, ttl=15))

    def run(self):
        # i know this breaks the inheritance override principle
        raise Exception('Cannot use packethandler as a thread by itself (its a base class)')

    def handle_packet(self, packet):
        # type: (Packet) -> None
        if packet.options & PROTO_ICMP and packet.dataLength == 1 and ord(packet.data[0]) == ICMP_PING:
            IcmpPingPacket.convert_to_class(packet)
            self.recv_icmp_ping(packet)
        elif packet.options & PROTO_ICMP and packet.dataLength == 1 and ord(packet.data[0]) == ICMP_PONG:
            IcmpPongPacket.convert_to_class(packet)
            self.recv_icmp_pong(packet)

    def recv_icmp_ping(self, packet):
        # type: (IcmpPingPacket) -> None
        print 'ping packet detected'
        self.send(packet.craft_pong_response())

    def recv_icmp_pong(self, packet):
        # type: (IcmpPongPacket) -> None
        print 'pong packet detected'
        delta = datetime.datetime.now() - self.pingTime
        print 'roundtrip time %d' % delta.microseconds, delta


class SocketPacketHandler(PacketHandler):
    def __init__(self):
        super(SocketPacketHandler, self).__init__()
        self.Sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.Sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        self.Sock.bind(('', 5151))
        self.PacketParser = PacketParser()

    def run(self):
        # TODO: split this up so that base actually holds execution and calls override methods?
        print 'listening on *:5151'
        while not self.StopEvent.is_set():
            self.Sock.settimeout(1.0)
            try:
                received_data, client_address = self.Sock.recvfrom(1024)
            except socket.timeout:
                continue
            # TODO: handle buffer assembly for multiple clients
            # print 'repr', repr(received_data), address
            # TODO: handle packet content parsing (start at SOM, end at EOM, maybe also do a checksum)
            self.PacketParser.parse_buffer(received_data)
            for packet in self.PacketParser.Packets:
                self.recv(packet)
                self.PacketParser.Packets.remove(packet)

    def handle_packet(self, packet):
        # type: (Packet) -> None
        super(SocketPacketHandler, self).handle_packet(packet)

    def send(self, packet):
        # type: (Packet) -> None
        super(SocketPacketHandler, self).send(packet)
        self.Sock.sendto(packet.get_packet_data(), ('255.255.255.255', 5151))


class SerialPacketHandler(PacketHandler):
    def __init__(self, port=None, baud=None):
        super(SerialPacketHandler, self).__init__()
        if port is None:
            port = 'COM3'
        if baud is None:
            baud = 2400
        self.Serial = serial.Serial(port, baud, timeout=1)
        self.PacketParser = PacketParser()

    def run(self):
        print 'reading data from serial port ' + self.Serial.port
        while not self.StopEvent.is_set():
            received_data = self.Serial.read(100)
            self.PacketParser.parse_buffer(received_data)
            for packet in self.PacketParser.Packets:
                self.recv(packet)
                self.PacketParser.Packets.remove(packet)

    def handle_packet(self, packet):
        # type: (Packet) -> None
        super(SerialPacketHandler, self).handle_packet(packet)

    def send(self, packet):
        # type: (Packet) -> None
        super(SerialPacketHandler, self).send(packet)
        self.Serial.write(chr(POLYNOMIAL)*5 + chr(PREAMBLE)*2 + chr(SOM) + packet.get_packet_data() + chr(EOM) + chr(POSTAMBLE)*4)


class PacketParser:
    """
    :type packetBuffer: str
    :type Packets: list(Packet)
    """
    splitChars = chr(PREAMBLE) + chr(PREAMBLE) + chr(SOM)
    endChars = chr(EOM) + chr(POSTAMBLE) + chr(POSTAMBLE)

    def __init__(self):
        """
        :rtype: PacketParser
        """
        self.packetBuffer = ''
        self.Packets = list()

    def parse_buffer(self, packetdata):
        # type: (packetdata) -> str
        if packetdata == '':
            return

        self.packetBuffer += packetdata
        # print repr(packetData)
        rest = ''
        for segment in self.packetBuffer.split(PacketParser.splitChars):
            if segment == '' or segment == len(segment) * chr(POLYNOMIAL):
                # the segment empty or only POLYNOMIAL, ignore it
                pass
            elif segment.find(PacketParser.endChars) != -1:
                # print len(segment), 'segment', ' '.join([str(ord(x)) for x in list(segment)])
                s = segment.split(PacketParser.endChars)[0]  # discard everything after
                # print repr(segment.split(endChars))
                # print len(s), 's', ' '.join([str(ord(x)) for x in list(s)])
                packet = Packet(s)
                self.Packets.append(packet)
            else:
                # print len(segment), 'rest segment', ' '.join([str(ord(x)) for x in list(segment)])
                rest += PacketParser.splitChars + segment
        # if rest != '':
        #     print len(rest), 'rest is', ' '.join([str(ord(x)) for x in list(rest)])
        self.packetBuffer = rest


class Test:
    def __init__(self):
        # self.packetHandler = SocketPacketHandler()
        self.packetHandler = SerialPacketHandler()
        self.StopEvents = list()
        self.StopEvents.extend(self.packetHandler.StopEvents)

    def run(self):
        self.packetHandler.start()
        time.sleep(0.2)
        while True:
            self.packetHandler.send_ping(255)
            print 'ping'
            try:
                raw_input('> ')
            except:
                break

        print 'exiting'
        for stopEvent in self.StopEvents:
            stopEvent.set()


def run_tests():
    print '\nGenerating packet from string'
    p = Packet(chr(PREAMBLE) + chr(PREAMBLE) + chr(SOM) + chr(0b00000001) + chr(0b00000010) + chr(0b00000000) +
               chr(1) + chr(2) + chr(EOM) + chr(POSTAMBLE) + chr(POSTAMBLE) + chr(POSTAMBLE) + chr(POSTAMBLE) +
               chr(POSTAMBLE))
    # print p
    # print p.is_valid_checksum()
    p.print_raw()

    print '\nGenerating packet by param input'
    p2 = Packet.craft_packet(src=1, dst=2, opt=PROTO_ICMP, data='')
    # print p2
    # print p2.is_valid_checksum()
    p2.print_raw()

    print '\np1 == p2?', p == p2
    # print p is p2

    print '\nCreating sample ping packet'
    ping = IcmpPingPacket.craft_packet(src=1, dst=2, ttl=15)
    ping.print_raw()

    print '\nCreating sample pong packet'
    # Consider making this craft_response and override it where relevant
    pong = ping.craft_pong_response()
    pong.print_raw()


if __name__ == '__main__':
    test = Test()
    test.run()
    # run_tests()
    sys.exit(0)

    ser = serial.Serial('COM3', 2400, timeout=1)
    ping = IcmpPingPacket.craft_packet(src=LOCAL_ADDRESS, dst=10, ttl=15)
    # ping.print_raw()
    data = chr(POLYNOMIAL) + chr(POLYNOMIAL) + chr(POLYNOMIAL) + chr(POLYNOMIAL) + chr(POLYNOMIAL) + chr(PREAMBLE) + \
           chr(PREAMBLE) + chr(SOM) + ping.get_packet_data() + chr(EOM) + chr(POSTAMBLE) + chr(POSTAMBLE) + \
           chr(POSTAMBLE) + chr(POSTAMBLE) + chr(POSTAMBLE)
    # packetBuffer = ''
    pp = PacketParser()
    while True:
        # print 'repr', repr(data)
        # print 'sending ping packet via serial'
        # ser.write(data)
        # regex that might do the same: \xAA{2}\xC5(.{10})\x5C\x3A
        packetData = ser.read(100)
        pp.parse_buffer(packetData)
        for p in pp.Packets:
            p.print_raw()
            print ord(p.rawData[9])
            # pop it
            pp.Packets.remove(p)

        try:
            time.sleep(1)
        except:
            pass
    ser.close()
    print 'exit'

    # 17 25 20 17 02 02 50 24 02 40 24 0

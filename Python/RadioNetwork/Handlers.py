from threading import Thread, Event
import datetime
import socket
import serial
from Protocol import *
from Packet import Packet, IcmpPingPacket, IcmpPongPacket, ADDRESS_LOCAL
import logging
import time


class ReceiveHandler(Thread):
    def __init__(self, packet_handler):
        # super(Thread, self).__init__()
        # TODO: what is the difference?
        """

        :type packet_handler: PacketHandler
        """
        Thread.__init__(self)
        self.StopEvent = Event()
        self.packetHandler = packet_handler

    def run(self):
        while not self.StopEvent.is_set():
            for packet in self.packetHandler.ReceiveBuffer:
                self.packetHandler.handle_packet(packet)
                # TODO: assuming we want to remove it after for now
                self.packetHandler.ReceiveBuffer.remove(packet)

            time.sleep(0.01)  # to reduce cpu usage


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
        self.pingTime = dict()  # assigning a value purely for IDE type recognition

    def recv(self, packet):
        # type: (Packet) -> None
        # the difference between recv and handle_packet is that recv is blocking further reads
        # handle_packet runs in its own thread and can take all the time it wants to process
        if packet.is_valid_checksum() == False:
            logging.warn('Ignoring packet with invalid checksum')
            packet.print_raw(logging.DEBUG)
        elif packet.source == ADDRESS_LOCAL:
            logging.debug('Ignoring packet from self')
            packet.print_raw(logging.DEBUG)
        elif packet.destination in [ADDRESS_LOCAL, ADDRESS_BROADCAST]:
            logging.debug('Received: ' + str(packet))
            self.ReceiveBuffer.append(packet)
        else:
            logging.debug('Ignoring packet that isn\'t for me')
            packet.print_raw(logging.DEBUG)

    def send(self, packet):
        # type: (Packet) -> None
        logging.debug('sending:')
        packet.print_raw(logging.DEBUG)

    def send_ping(self, dst, pid=0):
        # type: (int) -> None
        self.pingTime[pid] = datetime.datetime.now()
        self.send(IcmpPingPacket.craft_packet(dst=dst, proto=PROTO_ICMP, ttl=15, pid=pid))

    def run(self):
        # i know this breaks the inheritance override principle
        raise Exception('Cannot use packethandler as a thread by itself (its a base class)')

    def handle_packet(self, packet):
        # type: (Packet) -> None
        """
Override this to implement custom packet handling
        :param packet: Packet
        """
        if packet.protocol == PROTO_ICMP and packet.dataLength == 1 and ord(packet.data[0]) == ICMP_PING:
            IcmpPingPacket.convert_to_class(packet)
            self.recv_icmp_ping(packet)
        elif packet.protocol == PROTO_ICMP and packet.dataLength == 1 and ord(packet.data[0]) == ICMP_PONG:
            IcmpPongPacket.convert_to_class(packet)
            self.recv_icmp_pong(packet)

    def recv_icmp_ping(self, packet):
        # type: (IcmpPingPacket) -> None
        logging.debug('ping packet detected, sending pong reply')
        self.send(packet.craft_pong_response())

    def recv_icmp_pong(self, packet):
        # type: (IcmpPongPacket) -> None
        logging.debug('pong packet detected')
        if self.pingTime[packet.id] is None:
            # pong retransmission?
            return
        delta = datetime.datetime.now() - self.pingTime[packet.id]
        self.pingTime[packet.id] = None
        print('pong: roundtrip time for %d was %ss' % (packet.id, delta.total_seconds()))

    def stop(self):
        for event in self.StopEvents:
            event.set()


class SocketPacketHandler(PacketHandler):
    def __init__(self):
        super(SocketPacketHandler, self).__init__()
        self.Sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.Sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        self.Sock.bind(('', 5151))
        self.PacketParser = PacketParser()

    def run(self):
        # TODO: split this up so that base actually holds execution and calls override methods?
        logging.info('listening on *:5151')
        while not self.StopEvent.is_set():
            self.Sock.settimeout(1.0)
            try:
                received_data, client_address = self.Sock.recvfrom(1024)
            except socket.timeout:
                continue
            # TODO: handle buffer assembly for multiple clients
            logging.debug('repr: ' + repr(received_data) + ' ' + str(client_address))
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
        packet_data = packet.get_packet_data()  # to get the checksum corrected before printing it out in supers debug
        super(SocketPacketHandler, self).send(packet)
        self.Sock.sendto(chr(PREAMBLE)*2 + chr(SOM) + packet_data + chr(EOM) + chr(POSTAMBLE)*4, ('192.168.1.255', 5151))


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
        logging.info('Reading data from serial port ' + self.Serial.port)
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
        packet_data = packet.get_packet_data()  # to get the checksum corrected before printing it out in supers debug
        super(SerialPacketHandler, self).send(packet)
        self.Serial.write(chr(POLYNOMIAL)*5 + chr(PREAMBLE)*2 + chr(SOM) + packet_data + chr(EOM) + chr(POSTAMBLE)*4)


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
        # logging.debug(repr(packetData))
        rest = ''
        for segment in self.packetBuffer.split(PacketParser.splitChars):
            if segment == '' or segment == len(segment) * chr(POLYNOMIAL):
                # the segment empty or only POLYNOMIAL, ignore it
                pass
            elif segment.find(PacketParser.endChars) != -1:
                # print len(segment), 'segment', ' '.join([str(ord(x)) for x in list(segment)])
                s = segment.split(PacketParser.endChars)[0]  # discard everything after
                # print repr(segment.split(PacketParser.endChars))
                # print 's detail', len(s), ' '.join([str(ord(x)) for x in list(s)])
                packet = Packet(s)
                self.Packets.append(packet)
            else:
                # print len(segment), 'rest segment', ' '.join([str(ord(x)) for x in list(segment)])
                rest += PacketParser.splitChars + segment
        # if rest != '':
        #     print len(rest), 'rest is', ' '.join([str(ord(x)) for x in list(rest)])
        self.packetBuffer = rest

from Protocol import *
import socket
import logging

# TODO: this cant happen here if we want it logged
ADDRESS_LOCAL = int(socket.gethostbyname(socket.gethostname()).split('.')[-1])
# logging.info('ADDRESS_LOCAL is %d' % ADDRESS_LOCAL)
print('ADDRESS_LOCAL is %d' % ADDRESS_LOCAL)

# region Packet classes


class Packet(object):
    def __init__(self, data=None):
        # for raw creation
        if not data:
            self.dataLength = 0
            self.protocol = 0
            self.options = 0
            self.timeToLive = 0
            self.checksum = 0
            self.id = 0
            self.sequence = 0
            self.source = 0
            self.destination = 0
            self.data = ''
            self.rawData = ''  # TODO: rawdata should probably not be set, instead call the method that gets all bytes?
            return

        self.rawData = data
        # TODO: proper handling of datalength?

        dlenopt = ord(data[0])
        ttlchk = ord(data[1])
        pidseq = ord(data[2])

        # rev 1.1 - the split is now 3 / 5
        # rev 1.2 - dlen proto opt
        #           000  000   00
        # split is now 3 / 3 / 2
        self.dataLength = dlenopt >> 5
        # self.options = dlenopt & 0x1F
        self.protocol = (dlenopt & 0x1C) >> 2
        self.options = dlenopt & 0x3

        # the others are still 4 / 4
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
        bytes = self.all_bytes()
        for b in bytes:
            # this totally ignores dlen/opt structure, but afaik thats ok
            hnibble = b >> 4
            lnibble = b & 0xF
            # we have to skip the checksum itself when creating a checksum, duh
            chk ^= hnibble
            if i != 1:
                chk ^= lnibble
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
        proto = ''
        if self.protocol == PROTO_RAW:
            proto = 'proto:raw'
        elif self.protocol & PROTO_ICMP:
            proto = 'proto:icmp'
        elif self.protocol & PROTO_ACKREQ:
            proto = 'proto:acqreq'
        elif self.protocol & PROTO_SYN:
            proto = 'proto:syn'
        elif self.protocol & PROTO_SYNACK:
            proto = 'proto:synack'
        elif self.protocol & PROTO_FIN:
            proto = 'proto:fin'
        elif self.protocol & PROTO_FINACK:
            proto = 'proto:finack'
        elif self.protocol & PROTO_RES1:
            proto = 'proto:res1'

        option_list = list()
        if self.options & OPT_ACK:
            option_list.append('opt:ack')
        if self.options & OPT_RST:
            option_list.append('opt:rst')

        return 'datalength: %d\nprotocol: %d (%s)\noptions: %d (%s)\nttl: %d\nchecksum: %d\nid: %d\nsequence: %d\n' \
               'source: %s\ndestination: %s\ndata: %s' \
               % (self.dataLength, self.protocol, proto, self.options, ', '.join(option_list), self.timeToLive,
                  self.checksum, self.id, self.sequence, self.source, self.destination, repr(self.data))

    @classmethod
    def convert_to_class(cls, obj):
        obj.__class__ = cls

    @staticmethod
    def craft_packet(dst, src=ADDRESS_LOCAL, proto=0, opt=0, ttl=0, pid=0, seq=0, data=''):
        # type: (int, int, int, int, int, int, int, str) -> Packet
        packet = Packet()
        packet.source = src
        packet.destination = dst
        packet.protocol = proto
        packet.options = opt
        packet.timeToLive = ttl
        packet.id = pid
        packet.sequence = seq
        packet.data = data
        packet.dataLength = len(data)
        packet.checksum = packet.calculate_checksum()
        return packet

    def calculate_dlenopt(self):
        # return self.dataLength * 32 + self.options  # rev 1.1
        return self.dataLength * 32 + (self.protocol << 2) + self.options  # rev 1.2

    def calculate_ttlchk(self):
        return self.timeToLive * 16 + self.checksum

    def calculate_pidseq(self):
        return self.id * 16 + self.sequence

    def get_packet_data(self):
        self.checksum = self.calculate_checksum()
        return chr(self.calculate_dlenopt()) + chr(self.calculate_ttlchk()) + chr(self.calculate_pidseq()) + \
               chr(self.source) + chr(self.destination) + self.data

    def print_raw(self, loglevel=None):
        dlenopt = self.calculate_dlenopt()
        ttlchk = self.calculate_ttlchk()
        pidseq = self.calculate_pidseq()
        if not loglevel:
            print 'dlenopt\t%s\t0x%x\t%d' % (bin(dlenopt), dlenopt, dlenopt)
            print 'ttlchk\t%s\t0x%x\t%d' % (bin(ttlchk), ttlchk, ttlchk)
            print 'pidseq\t%s\t0x%x\t%d' % (bin(pidseq), pidseq, pidseq)
            print 'source\t%s\t0x%x\t%d' % (bin(self.source), self.source, self.source)
            print 'dest\t%s\t0x%x\t%d' % (bin(self.destination), self.destination, self.destination)
            i = 0
            for c in self.data:
                print 'data%d\t%s' % (i, bin(ord(c)))
                i += 1
        else:
            logging.debug('dlenopt\t%s\t0x%x\t%d' % (bin(dlenopt), dlenopt, dlenopt))
            logging.debug('ttlchk\t%s\t0x%x\t%d' % (bin(ttlchk), ttlchk, ttlchk))
            logging.debug('pidseq\t%s\t0x%x\t%d' % (bin(pidseq), pidseq, pidseq))
            logging.debug('source\t%s\t0x%x\t%d' % (bin(self.source), self.source, self.source))
            logging.debug('dest\t%s\t0x%x\t%d' % (bin(self.destination), self.destination, self.destination))
            i = 0
            for c in self.data:
                logging.debug('data%d\t%s' % (i, bin(ord(c))))
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
    def craft_packet(dst, src=ADDRESS_LOCAL, proto=0, opt=0, ttl=0, pid=0, seq=0, data='', packet=None):
        opt |= PROTO_ICMP  # add icmp protocol in case its missing
        # return packet with ICMP_PING data, that's it
        packet = Packet.craft_packet(dst=dst, src=src, proto=proto, opt=opt, ttl=ttl, pid=pid, seq=seq,
                                     data=chr(ICMP_PING))
        IcmpPingPacket.convert_to_class(packet)
        return packet

    def craft_pong_response(self):
        return IcmpPongPacket.craft_packet(src=ADDRESS_LOCAL, dst=self.source,
                                           proto=PROTO_ICMP, opt=0, ttl=15, pid=self.id,
                                           seq=self.sequence + 1, data=chr(ICMP_PING) + self.data[1:])


class IcmpPongPacket(Packet):
    def __init__(self, data=None):
        super(IcmpPongPacket, self).__init__(data)

    @staticmethod
    def craft_packet(dst, src=ADDRESS_LOCAL, proto=0, opt=0, ttl=0, pid=0, seq=0, data=''):
        opt |= PROTO_ICMP  # add icmp protocol in case its missing
        # return packet with ICMP_PING data, that's it
        packet = Packet.craft_packet(dst=dst, src=src, proto=proto, opt=opt, ttl=ttl, pid=pid, seq=seq,
                                     data=chr(ICMP_PONG))
        IcmpPongPacket.convert_to_class(packet)
        return packet


# endregion Packet classes

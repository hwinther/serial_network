from Protocol import *
import socket

LOCAL_ADDRESS = int(socket.gethostbyname(socket.gethostname()).split('.')[-1])
print 'LOCAL_ADDRESS is %d' % LOCAL_ADDRESS

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

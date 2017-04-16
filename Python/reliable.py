from RadioNetwork.Handlers import SerialPacketHandler, SocketPacketHandler
from RadioNetwork.Packet import Packet, ADDRESS_LOCAL
from RadioNetwork.Protocol import *
from threading import Thread, Event
import time
import logging
import datetime
import sys

# state values
STATE_IDLE = 0
STATE_QUEUE = 1

# seconds to wait before sending packet again
RETRANSMISSION_WAIT = 2
# maximum amount of received packets to buffer - this is done to avoid exposing retransmitted packets
INPUTCACHE_LENGTH = 10
# max amount of retransmissions - after this we raise an exception
RETRANSMISSION_MAX = 10


class RetransmissionThread(Thread):
    def __init__(self, reliable_handler):
        """
        :type reliable_handler: ReliablePacketHandler
        """
        Thread.__init__(self)
        self.StopEvent = Event()
        self.ReliablePacketHandler = reliable_handler

    def run(self):
        while not self.StopEvent.is_set():
            # handle retransmissions
            self.ReliablePacketHandler.handle_queue()

            # print received data
            while True:
                r = self.ReliablePacketHandler.receive()
                if not r:
                    break
                # write data from other end on top of our prompt and then recreate the prompt on the next line
                sys.stdout.write('\r< %s     \n> ' % r.data)
                sys.stdout.flush()

            time.sleep(0.01)  # to reduce cpu usage


class ReliablePacketHandler(SerialPacketHandler):
    def __init__(self, port=None):
        super(ReliablePacketHandler, self).__init__(port=port)

        self.sendBuffer = list()
        self.state = STATE_IDLE
        self.recvBuffer = list()
        self.recvCache = list()
        self.retransmissionThread = RetransmissionThread(self)
        self.retransmissionThread.start()
        self.StopEvents.append(self.retransmissionThread.StopEvent)
        self.sequence = 0

    def handle_packet(self, packet):
        super(ReliablePacketHandler, self).handle_packet(packet)

        if packet.protocol != PROTO_ACKREQ:
            return

        # is this an ACK for a packet we sent?
        if packet.options & OPT_ACK:
            # try to find a packet in the buffer that this belongs to
            for p in self.sendBuffer:
                if packet.source == p.destination and packet.id == p.id and packet.sequence == p.sequence:
                    # this should be the right packet
                    # TODO: compare them via class method?
                    logging.info('ACK discharged packet from buffer, transmissions: %d' % len(p.sendTimes))
                    self.sendBuffer.remove(p)
                    # TODO: recipience transition/event?

            if len(self.sendBuffer) == 0 and self.state == STATE_QUEUE:
                self.state = STATE_IDLE
                # TODO: from queued to state idle transition

            return

        # send ACK
        ack = Packet()
        ack.protocol = PROTO_ACKREQ
        ack.options = OPT_ACK
        ack.source = ADDRESS_LOCAL
        ack.destination = packet.source
        ack.id = packet.id
        ack.sequence = packet.sequence
        super(ReliablePacketHandler, self).send(ack)

        # maintain max length of inputCache list
        while len(self.recvCache) > INPUTCACHE_LENGTH:
            self.recvCache.pop(0)

        # don't append to inputBuffer if its a retransmitted packet (destination received the ACK after retransmitting)
        for p in self.recvCache:
            if packet.source == p.source and packet.destination == p.destination and packet.id == p.id and \
                    packet.sequence == p.sequence:
                return

        self.recvCache.append(packet)
        self.recvBuffer.append(packet)

    def send(self, packet):
        packet.sequence = self.sequence
        # this will cause the packet to be sent on the wire
        super(ReliablePacketHandler, self).send(packet)

        # mmm python stuff
        packet.sendTimes = list()
        packet.sendTimes.append(datetime.datetime.now())

        self.sendBuffer.append(packet)

        if self.state == STATE_IDLE:
            self.state = STATE_QUEUE
            # TODO: from idle to queued transition

        # increment sequence
        # TODO: this should be on a per pid & destination level, not global like now
        self.sequence += 1
        if self.sequence > 15:
            self.sequence = 0
            # reset

    def receive(self):
        if len(self.recvBuffer) == 0:
            return None

        p = self.recvBuffer[0]
        self.recvBuffer.remove(p)
        return p

    def handle_queue(self):
        # here we will go over the queue and resend packets
        # if self.state == STATE_IDLE:
        #     return

        for p in self.sendBuffer:
            if (datetime.datetime.now() - p.sendTimes[-1]).total_seconds() > RETRANSMISSION_WAIT:
                if len(p.sendTimes) > RETRANSMISSION_MAX:
                    # TODO: raise exception? for now just dropping packet
                    logging.info('dropping packet after %d retransmissions' % RETRANSMISSION_MAX)
                    self.sendBuffer.remove(p)
                    continue

                # resend the packet
                logging.info('retransmission of packet')
                super(ReliablePacketHandler, self).send(p)
                p.sendTimes.append(datetime.datetime.now())


class Client:
    def __init__(self, destination, port=None):
        self.packetHandler = ReliablePacketHandler(port)
        # self.StopEvents = list()
        # self.StopEvents.extend(self.packetHandler.StopEvents)
        self.destination = destination

    def run(self):
        self.packetHandler.start()
        time.sleep(0.2)
        try:
            print('reliable comm with %d started' % self.destination)
            while True:
                i = raw_input('> ')
                if len(i) > 5:
                    print('Larger than 5, truncating to 5')
                    i = i[0:5]
                if len(i) == 0:
                    continue
                # TODO: wrap this up in an alternate packetHandler method?
                packet = Packet()
                packet.destination = self.destination
                packet.source = ADDRESS_LOCAL
                packet.dataLength = len(i)
                packet.data = i
                packet.protocol = PROTO_ACKREQ  # specifies that we require an ack to be sent back
                packet.options = OPT_NONE
                self.packetHandler.send(packet)
        finally:
            self.stop()

    def stop(self):
        print('exiting')
        self.packetHandler.stop()
        # for stopEvent in self.StopEvents:
        #     stopEvent.set()


if __name__ == '__main__':
    log_level = logging.INFO

    logFormatter = logging.Formatter("%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s")
    rootLogger = logging.getLogger()
    rootLogger.setLevel(log_level)

    consoleHandler = logging.StreamHandler()
    consoleHandler.setFormatter(logFormatter)
    rootLogger.addHandler(consoleHandler)

    dest = int(sys.argv[1])
    # dest = 5
    port = 'COM3'
    if len(sys.argv) == 3:
        port = sys.argv[2]
    if dest < 0 or dest >= 255:
        print('Destination %d out of range' % dest)
        sys.exit(1)
    c = Client(dest, port)
    c.run()

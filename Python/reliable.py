from RadioNetwork.Handlers import SerialPacketHandler, SocketPacketHandler
from RadioNetwork.Packet import Packet, ADDRESS_LOCAL
from RadioNetwork.Protocol import *
from threading import Thread, Event
import time
import logging
import datetime
import sys

STATE_IDLE = 0
STATE_QUEUE = 0


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

        self.buffer = list()
        self.state = STATE_IDLE
        self.inputBuffer = list()
        self.retransmissionThread = RetransmissionThread(self)
        self.retransmissionThread.start()
        self.StopEvents.append(self.retransmissionThread.StopEvent)

    def handle_packet(self, packet):
        super(ReliablePacketHandler, self).handle_packet(packet)

        if packet.options == OPT_ACK:
            # try to find a packet in the buffer that this belongs to
            for p in self.buffer:
                if packet.source == p.destination and packet.id == p.id and packet.sequence == p.sequence:
                    # this should be the right packet
                    logging.debug('ACK discharged packet from buffer, transmissions: %d' % len(p.sendTimes))
                    self.buffer.remove(p)
                    # recipience event call?

            if len(self.buffer) == 0 and self.state == STATE_QUEUE:
                self.state = STATE_IDLE
                # TODO: from queued to state idle transition

            return

        if packet.options == 0:
            # send ACK
            ack = Packet()
            ack.options = OPT_ACK
            ack.source = ADDRESS_LOCAL
            ack.destination = packet.source
            ack.id = packet.id
            ack.sequence = packet.sequence
            super(ReliablePacketHandler, self).send(ack)
            self.inputBuffer.append(packet)
            return

    def send(self, packet):
        # this will cause the packet to be sent on the wire
        super(ReliablePacketHandler, self).send(packet)
        # mmm python stuff
        packet.sendTimes = list()
        packet.sendTimes.append(datetime.datetime.now())
        self.buffer.append(packet)
        if self.state == STATE_IDLE:
            self.state = STATE_QUEUE
            # TODO: from idle to queued transition

    def receive(self):
        if len(self.inputBuffer) != 0:
            p = self.inputBuffer[0]
            self.inputBuffer.remove(p)
            return p
        return None

    def handle_queue(self):
        # here we will go over the queue and resend packets
        # if self.state == STATE_IDLE:
        #     return

        for p in self.buffer:
            if (datetime.datetime.now() - p.sendTimes[-1]).total_seconds() > 1:
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
                packet = Packet()
                packet.destination = self.destination
                packet.source = ADDRESS_LOCAL
                packet.dataLength = len(i)
                packet.data = i
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

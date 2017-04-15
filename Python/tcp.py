from RadioNetwork.Handlers import SerialPacketHandler, SocketPacketHandler
from RadioNetwork.Packet import Packet, ADDRESS_LOCAL
from RadioNetwork.Protocol import *
import time
import logging
import datetime

STATE_IDLE = 0
STATE_SYNRECEIVED = 1
STATE_SYNACKRECEIVED = 2
STATE_SYNSENT = 3
STATE_OPEN = 8
STATE_x = 9


class TcpServer(SocketPacketHandler):
    def __init__(self):
        super(TcpServer, self).__init__()

        self.state = STATE_IDLE

    def handle_packet(self, packet):
        super(TcpServer, self).handle_packet(packet)
        if packet.id != 10:
            return

        # TODO: support multiple clients through state dict

        # TODO: switch?

        if self.state == STATE_IDLE and \
                        packet.options == OPT_SYN:
            self.state = STATE_SYNRECEIVED
            synack = Packet()
            synack.options = OPT_SYN | OPT_ACK
            synack.source = ADDRESS_LOCAL
            synack.destination = packet.source
            synack.id = packet.id
            self.send(synack)
            return

        if self.state == STATE_SYNRECEIVED and \
                        packet.options == OPT_ACK:
            self.state = STATE_OPEN
            return

        if self.state == STATE_SYNSENT and \
                        packet.options == OPT_SYN | OPT_ACK:
            self.state = STATE_SYNACKRECEIVED
            ack = Packet()
            ack.options = OPT_ACK
            ack.source = ADDRESS_LOCAL
            ack.destination = packet.source
            ack.id = packet.id
            self.send(ack)
            return

        if self.state == STATE_OPEN and \
                        packet.options == 0:
            # data to service
            # testing as clock service, send ack and the time
            ack = Packet()
            ack.options = OPT_ACK
            ack.source = ADDRESS_LOCAL
            ack.destination = packet.source
            ack.id = packet.id
            self.send(ack)

            p = Packet()
            p.options = 0
            p.source = ADDRESS_LOCAL
            p.destination = packet.source
            p.id = packet.id
            # obviously this could've been compressed down to 2 bytes and even contain a decade relative date value
            p.data = datetime.datetime.now().strftime('%H:%M')
            p.dataLength = 5
            self.send(p)


class Client:
    def __init__(self, destination, pid):
        # self.packetHandler = SocketPacketHandler()
        self.packetHandler = TcpServer()
        self.StopEvents = list()
        self.StopEvents.extend(self.packetHandler.StopEvents)
        self.destination = destination
        self.pid = pid

    def run(self):
        self.packetHandler.start()
        time.sleep(0.2)
        # tcp handshake, syn -> syn|ack -> ack
        syn = Packet()
        syn.options = OPT_SYN
        syn.source = ADDRESS_LOCAL
        syn.destination = self.destination
        syn.id = self.pid
        self.packetHandler.state = STATE_SYNSENT
        self.packetHandler.send(syn)

        time.sleep(2)

        # re-send syn
        if self.packetHandler.state == STATE_SYNSENT:
            self.packetHandler.send(syn)
            time.sleep(2)

        if self.packetHandler.state == STATE_SYNSENT:
            print('Did not receive reply to syn')
            self.stop()
            return

        if self.packetHandler.state != STATE_SYNACKRECEIVED:
            print('Wrong state: %d' % self.packetHandler.state)
            self.stop()
            return

        # state is SYNACKRECEIVED as far as we're concerned its opened
        # TODO: its possible that the ack was not received, perhaps it should be sent one more time regardless after 1s

        self.packetHandler.state = STATE_OPEN
        #

    def stop(self):
        print('exiting')
        for stopEvent in self.StopEvents:
            stopEvent.set()


if __name__ == '__main__':
    log_level = logging.INFO

    logFormatter = logging.Formatter("%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s")
    rootLogger = logging.getLogger()
    rootLogger.setLevel(log_level)

    consoleHandler = logging.StreamHandler()
    consoleHandler.setFormatter(logFormatter)
    rootLogger.addHandler(consoleHandler)

    c = Client(250, 10)
    c.run()

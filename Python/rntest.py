from RadioNetwork.Handlers import SerialPacketHandler
import time
import logging


class App:
    def __init__(self):
        # self.packetHandler = SocketPacketHandler()
        self.packetHandler = SerialPacketHandler()
        self.StopEvents = list()
        self.StopEvents.extend(self.packetHandler.StopEvents)

    def run(self):
        self.packetHandler.start()
        time.sleep(0.2)
        ping_id = 0
        total_pings = 0
        while True:
            self.packetHandler.send_ping(255, ping_id)
            ping_id += 1
            total_pings += 1
            if ping_id == 16:
                break
                ping_id = 0
            # from RadioNetwork.Packet import IcmpPingPacket
            # from RadioNetwork.Protocol import PROTO_ICMP
            # p = IcmpPingPacket.craft_packet(dst=255, opt=PROTO_ICMP, ttl=15)
            # p.print_raw()
            # print p.is_valid_checksum()
            # print('ping')
            try:
                # raw_input('> ')
                time.sleep(2)
            except:
                break

        pong_count = 0
        for x in self.packetHandler.pingTime.keys():
            if self.packetHandler.pingTime[x] is None:
                pong_count += 1
        print('out of %d ping packets sent %d were replied to, %d%% loss' %(total_pings, pong_count,
                                                                            100 - (float(pong_count) / float(total_pings) * 100)))

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

    app = App()
    app.run()

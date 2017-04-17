from RadioNetwork.Handlers import SerialPacketHandler, SocketPacketHandler
import time
import logging
import sys


class App:
    def __init__(self, dest, dev=None):
        # TODO: implement interface binding for SocketPacketHandler
        # if not dev:
            # default to network/eth0
        #    dev = 'eth0'
        if dev and dev.lower().find('com') != -1 or dev.find('/dev/') != -1:
            self.packetHandler = SerialPacketHandler(port=dev)
        else:
            self.packetHandler = SocketPacketHandler()

        self.destination = dest

    def run(self):
        self.packetHandler.start()
        time.sleep(0.2)
        try:
            ping_id = 0
            total_pings = 0
            print('pinging %s' % self.destination)
            while True:
                self.packetHandler.send_ping(self.destination, ping_id)
                ping_id += 1
                total_pings += 1
                if ping_id == 16:
                    break

                try:
                    time.sleep(2)
                except:
                    break

            pong_count = 0
            for x in self.packetHandler.pingTime.keys():
                if self.packetHandler.pingTime[x] is None:
                    pong_count += 1
            print('out of %d ping packets sent %d were replied to, %d%% loss' % (total_pings, pong_count,
                                                                                100 - (float(pong_count) / float(total_pings) * 100)))
        finally:
            self.packetHandler.stop()


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print 'Usage: ping.py <destination> [interface/serialport]'
        sys.exit(0)

    destination = int(sys.argv[1])
    if destination <= 0 or destination > 255:
        print('Invalid destination: %d' % destination)
        sys.exit(0)

    device = None
    if len(sys.argv) == 3:
        device = sys.argv[2]

    log_level = logging.WARN

    logFormatter = logging.Formatter("%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s")
    rootLogger = logging.getLogger()
    rootLogger.setLevel(log_level)

    consoleHandler = logging.StreamHandler()
    consoleHandler.setFormatter(logFormatter)
    rootLogger.addHandler(consoleHandler)

    app = App(destination, device)
    app.run()

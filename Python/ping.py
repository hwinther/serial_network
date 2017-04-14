from RadioNetwork.Handlers import SerialPacketHandler
import time
import logging
import sys


class App:
    def __init__(self, destination):
        # self.packetHandler = SocketPacketHandler()
        self.packetHandler = SerialPacketHandler()
        self.StopEvents = list()
        self.StopEvents.extend(self.packetHandler.StopEvents)
        self.destination = destination

    def run(self):
        self.packetHandler.start()
        time.sleep(0.2)
        try:
            ping_id = 0
            total_pings = 0
            print('pinging %s' %(self.destination))
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
            for stopEvent in self.StopEvents:
                stopEvent.set()


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print 'Usage: ping.py <destination>'
        sys.exit(0)

    destination = int(sys.argv[1])
    if destination <= 0 or destination > 255:
        print 'Invalid destination: ' + destination
        sys.exit(0)

    log_level = logging.WARN

    logFormatter = logging.Formatter("%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s")
    rootLogger = logging.getLogger()
    rootLogger.setLevel(log_level)

    consoleHandler = logging.StreamHandler()
    consoleHandler.setFormatter(logFormatter)
    rootLogger.addHandler(consoleHandler)

    app = App(destination)
    app.run()

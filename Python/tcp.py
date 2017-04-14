from RadioNetwork.Handlers import SerialPacketHandler
from RadioNetwork.Packet import Packet
from RadioNetwork.Protocol import *
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
        destination = 99
        pid = 10
        syn = Packet()
        syn.options = 0
        self.packetHandler.send(syn)

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

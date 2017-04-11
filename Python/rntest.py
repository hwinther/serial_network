from RadioNetwork.Handlers import SerialPacketHandler
import time
import sys


class Test:
    def __init__(self):
        # self.packetHandler = SocketPacketHandler()
        self.packetHandler = SerialPacketHandler()
        self.StopEvents = list()
        self.StopEvents.extend(self.packetHandler.StopEvents)

    def run(self):
        self.packetHandler.start()
        time.sleep(0.2)
        while True:
            self.packetHandler.send_ping(255)
            print 'ping'
            try:
                raw_input('> ')
            except:
                break

        print 'exiting'
        for stopEvent in self.StopEvents:
            stopEvent.set()


if __name__ == '__main__':
    test = Test()
    test.run()

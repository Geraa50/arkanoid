import threading
import time
import json
import itertools

from loguru import logger

logger.add("file.log", backtrace=True, diagnose=True) 

DISCONNECT_TIMEOUT = 1

from settings import PACKAGE_SIZE


class BrickManager:
    def __init__(self, startState):
        self.state = startState

    def getState(self):
        return self.state

    def updateState(self, arrivedState):
        if arrivedState:
            self.state.update(arrivedState)


# brickManager = BrickManager({"0 0": "+", "1 1": "+", "3 2": "+", "3 4": "+", "2 3": "+"})


class GameConnectionPull:
    def __init__(self):
        self.ids = {_: False for _ in range(10)}

    def prepareData(self):
        data = {}
        for _ in self.ids:
            if self.ids[_] != False:
                data[_] = self.ids[_].data
        # data["s"] = {"BrickManager": {"state": brickManager.getState()} }
        return json.dumps(data)


connections = GameConnectionPull()

    
class GameConnection(threading.Thread):
    def __init__(self, client_socket, addressInfo):
        super().__init__(target=self)
        global connections
        self.client_socket = client_socket
        self.addressInfo = addressInfo
        self.id = self.setId()
        self.data = None

    def run(self):
        logger.info(self.getAddressInfo())
        self.runPackageCycle()

    def getAddressInfo(self):
        return self.addressInfo
        
    def runPackageCycle(self):
        self.client_socket.send(f"{self.id}".encode())
        while True:
            try:
                package = self.client_socket.recv(PACKAGE_SIZE).decode()
                if package == b"":
                    break   
                try:
                    self.data = json.loads(package)
                except:
                    logger.info(package)
                # logger.info(package)
                # if "BrickManager" in self.data:
                    # brickManager.updateState(self.data["BrickManager"])
                    # self.data.pop("BrickManager")
                self.client_socket.sendall(connections.prepareData().encode())
            except ConnectionAbortedError:
                break
            except ConnectionResetError:
                break
            except BrokenPipeError:
                break
            except KeyboardInterrupt:
                break
        self.close()

    def setId(self):
        global connections
        for _ in connections.ids:
            if connections.ids[_] == False:
                connections.ids[_] = self
                return _

    def close(self):
        global connections
        self.client_socket.close()
        self.data = "closed"
        time.sleep(DISCONNECT_TIMEOUT)
        connections.ids[self.id] = False
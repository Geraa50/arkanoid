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
        data["s"] = {"Ball": ball.getCoords()}
        return json.dumps(data)


connections = GameConnectionPull()


WIDTH, HEIGHT = 1200, 600
PLATFORM_H = 35
PLATFORM_W = 330
PLATFORM_OFFSET_Y = 10

class Ball:
    def __init__(self, coords, r, s):
        self.coords = coords
        self.radius = r
        self.speed = s
        self.dx = 1
        self.dy = 1

    def move(self):
        self.coords[0] += self.speed * self.dx
        self.coords[1] += self.speed * self.dy

    def getCoords(self):
        if self.coords[0] > WIDTH - 2 * self.radius or self.coords[0] < 0 + 2 * self.radius:
            self.dx = -self.dx
        if self.coords[1] < 0:
            self.dy = -self.dy
        
        self.move()
        
        return self.coords

    def isPointCollide(self, point, rect):
        # logger.debug(point)
        # logger.debug(rect)
        if point[0] > rect[0] and point[0] < (rect[0] + rect[2]) and point[1] > rect[1] and point[1] < (rect[1] + rect[3]):
            return True
        return False

    def detectCollision(self, dx, dy, rect):
        ballX, ballY = self.coords
        radius = self.radius 
        if dx > 0:
            delta_x = (ballX + 2 * radius) - rect[0]
        else:
            delta_x = (rect[0] + rect[2]) - ballX
        if dy > 0:
            delta_y = (ballY + 2 * radius) - rect[1]
        else:
            delta_y = (rect[1] + rect[3]) - ballY

        if abs(delta_x - delta_y) < 10:
            dx, dy = -dx, -dy
        elif delta_x > delta_y:
            dy = -dy
        elif delta_y > delta_x:
            dx = -dx
        return dx, dy

    def collideRect(self, rect):
        coords = self.coords
        radius = self.radius
        points = [(coords[0], coords[1]), (coords[0] + 2 * radius, coords[1]), (coords[0] + 2 * radius, coords[1] + 2 * radius), (coords[0], coords[1] + 2 * radius)]
        for _ in points:
            if self.isPointCollide(_, rect):
                return True
        return False

    def collidePlatform(self, platformX):
        rect = (platformX, HEIGHT - PLATFORM_H - PLATFORM_OFFSET_Y, PLATFORM_W, PLATFORM_H)
        if self.collideRect(rect):
            self.dx, self.dy = self.detectCollision(self.dx, self.dy, rect)
        # logger.debug(rect)

ball = Ball([200, 200], 20, 6)


    
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
                    data = json.loads(package)
                except:
                    logger.info(package)
                # logger.info(package)
                for _ in data:
                    if _.startswith("Platform"):
                        ball.collidePlatform(data[_]["x"])
                self.data = data
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
import threading
import socket

from GameConnection import GameConnection, connections

from settings import HOST
from settings import PACKAGE_SIZE


class GameTCPServer:
    def __init__(self, host, port):
        self.host = host
        self.port = port

    def input(self):
        while True:
            command = input()
            if command == "exit":
                print("Server closed")
                self.server_socket.close()
                break
            elif command == "get":
                data = connections.prepareData().replace(";", "\n")
                if data:
                    print("Данные о клиентах:\n" + data)
                else:
                    print("Данных о клиентах нет")

    def run(self):
        self.raiseServer()

    def raiseServer(self):
        print("Server raised")
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(5)
        while True:
            client_socket, addr = self.server_socket.accept()
            GameConnection(client_socket, addr).start()


if __name__ == "__main__":
    server = GameTCPServer(*HOST)
    inputThread = threading.Thread(target=server.input)
    inputThread.start()
    server.run()
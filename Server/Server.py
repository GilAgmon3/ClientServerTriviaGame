import socket
import struct
import threading
import time

from Game import Game
from Player import Player


class Server:
    def __init__(self):
        self.__is_alive = False
        self.__is_broadcasting = False
        self.local_ip = socket.gethostbyname(socket.gethostname())
        self.udp_socket = None
        self.udp_ip = "255.255.255.255"
        self.udp_port = 13117
        self.udp_format = ">IB32sH"
        # self.tcp_socket, self.tcp_port = self.__find_available_port(1024)
        self.tcp_socket = None
        self.tcp_port = 55566
        self.buffer_size = 1024
        self.magic_cookie = 0xabcddcba
        self.message_type = 0x2
        self.server_name="Smelly Cat Squad"
        self.players=[]

    def __find_available_port(self, start_port):
        port=start_port
        while(True):
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    # TODO: check if keep localhost or empty
                    s.bind(('localhost', port))
                    return s, port
            except OSError as e:
                port += 1

    def start(self):
        self.is_alive = True
        # open udp connection
        self.udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        # open tcp connection
        self.tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.tcp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        self.tcp_socket.bind(("", self.tcp_port))  # TODO: "" was self.local_ip
        self.tcp_socket.settimeout(10)  # TODO: need it?
        self.tcp_socket.listen()

        print("Server started, listening on IP address " + self.local_ip)
        # start strategy
        self.__strategy()

    def __start_broadcast(self):
        self.is_broadcasting = True
        threading.Thread(target=self.__send_broadcast).start()

    def __send_broadcast(self):

        # Encode the server name string into bytes using UTF-8 encoding
        server_name_bytes = self.server_name.encode('utf-8')
        # print(f'udp_format: {self.udp_format}, magic_cookie: {self.magic_cookie}, message_type: {self.message_type}, server_name: {self.server_name},  tcp_port:  {self.tcp_port}')
        message = struct.pack(self.udp_format, self.magic_cookie, self.message_type, server_name_bytes, self.tcp_port)
        while self.is_broadcasting:
            self.udp_socket.sendto(message, (self.udp_ip, self.udp_port))
            time.sleep(1)

    def __stop_broadcast(self):
        self.is_broadcasting = False

    def stop(self):
        self.is_alive = False
        self.__stop_broadcast()
        # kill tcp
        self.tcp_socket.close()
        # Kill UDP
        self.udp_socket.close()

    def __strategy(self):

        while self.is_alive:
            # start sending udp broadcast messages
            self.__start_broadcast()
            # Wait for players to join or 10 seconds to elapse
            while True:
                try:
                    # Accept incoming TCP connections
                    new_client = self.tcp_socket.accept()  # (connection socket, address)
                    name = new_client[0].recv(self.buffer_size).decode()
                    print(f"name: {name}")
                    player = Player(new_client[0], new_client[1], name)
                    self.players.append(player)
                    print(f"Time number 1: {time.time()}")
                    continue
                except socket.timeout:
                    if not self.is_alive:
                        break
                    if len(self.players) >= 2:
                        self.__stop_broadcast()
                        print(f"Time number 2: {time.time()}")
                        Game(self.players)
                    # TODO what if only one player and timed out?


def main():
    s = Server()
    s.start()


main()
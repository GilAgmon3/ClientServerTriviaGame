import errno
import socket
import struct
import threading
import time

from Game import Game
from Client.Player import Player


class Server:
    def __init__(self):
        self.is_broadcasting = False
        # self.local_ip = socket.gethostbyname(socket.gethostname())
        self.local_ip = self.get_local_ip()
        self.udp_socket = None
        self.udp_ip = "255.255.255.255"
        self.udp_port = 13117
        self.udp_format = ">IB32sH"
        # self.tcp_socket, self.tcp_port = self.__find_available_port(1024)
        self.tcp_socket = None
        self.tcp_port = None
        self.buffer_size = 1024
        self.magic_cookie = 0xabcddcba
        self.message_type = 0x2
        self.server_name = "Smelly Cat Squad"
        self.players = []

    def __find_available_port(self, start_port):
        port = start_port
        while True:
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    # TODO: check if keep localhost or empty
                    # s.bind(("", port))
                    s.bind(('localhost', port))
                    # TODO i changed to returning only port
                    return port
            except OSError as e:
                port += 1

    # NOAM AND LINOY
    # def get_local_ip(self):
    #     while True:
    #         try:
    #             time.sleep(0.2)
    #             temp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    #             temp_socket.connect(("8.8.8.8", 80))
    #             ip_address = temp_socket.getsockname()[0]
    #             temp_socket.close()
    #             return ip_address
    #         except OSError as e:
    #             print(f"Error in get_local_ip: {e}")
    #             continue

    def get_local_ip(self):
        while True:
            try:
                time.sleep(0.2)
                with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
                    # Connect to a public DNS server to get the local IP
                    sock.connect(('8.8.8.8', 80))
                    local_ip = sock.getsockname()[0]
                    return local_ip
            except OSError as error:
                print(f"Error obtaining local IP: {error}")
                # Continue trying until a successful IP retrieval

    def start(self):
        print("Server started, listening on IP address " + self.local_ip)

        while True:
            print("started server again")
            # open udp connection
            self.udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            self.udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.udp_socket.bind((self.local_ip, self.udp_port))

            # open tcp connection
            self.tcp_port = self.__find_available_port(1025)
            self.tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.tcp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.tcp_socket.bind((self.local_ip, self.tcp_port))  # TODO: self.local_ip was ""
            # self.tcp_socket.bind(("", self.tcp_port))  # TODO: "" was self.local_ip
            self.tcp_socket.settimeout(10)  # TODO: need it?
            self.tcp_socket.listen()

            #self.tcp_socket.settimeout(10)  # TODO: need it? GPT DIDNT USE IT

            # start strategy

            self.__strategy()

    # def start(self):
    #     # open udp connection
    #     self.udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    #     self.udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    #     # open tcp connection
    #     self.tcp_port = self.__find_available_port(1025)
    #     self.tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    #     self.tcp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    #
    #     # self.tcp_socket.bind((self.local_ip, self.tcp_port))  # TODO: self.local_ip was ""
    #     self.tcp_socket.bind(("", self.tcp_port))  # TODO: "" was self.local_ip
    #     self.tcp_socket.settimeout(10)  # TODO: need it?
    #     self.tcp_socket.listen()
    #
    #     print("Server started, listening on IP address " + self.local_ip)
    #     # start strategy
    #
    #     self.__strategy()

    def __start_broadcast(self):
        self.is_broadcasting = True
        threading.Thread(target=self.__send_broadcast).start()

    def __send_broadcast(self):

        # Encode the server name string into bytes using UTF-8 encoding
        server_name_bytes = self.server_name.encode('utf-8')
        # print(f'udp_format: {self.udp_format}, magic_cookie: {self.magic_cookie}, message_type: {self.message_type}, server_name: {self.server_name},  tcp_port:  {self.tcp_port}')
        message = struct.pack(self.udp_format, self.magic_cookie, self.message_type, server_name_bytes, self.tcp_port)
        # print(f'len message {len(message)}')
        while self.is_broadcasting:
            self.udp_socket.sendto(message, (self.udp_ip, self.udp_port))
            # print(f'Broadcasting: message: {message}, udp- ip+port: {self.udp_ip}, {self.udp_port}')
            time.sleep(1)

    def __stop_broadcast(self):
        self.is_broadcasting = False

    def stop(self):
        # kill tcp
        self.tcp_socket.close()
        self.tcp_socket = None
        # Kill UDP
        self.udp_socket.close()
        self.udp_socket = None
        # for c in self.clients:
        #     c.stop()
        self.players.clear()  # Clear the players list

        # TODO: added killing clients threads, check if its ok and needed
        # for player in self.players:
        #     player.kill()

    # TODO: added this method, need to check it. This method is for checking clients connections while server is alive
    # this implementation printed pings non-stop at client's console
    # def __manage_clients(self):
    #     while self.__is_alive:
    #         disconnected_players = []
    #         for player in self.players:
    #             try:
    #                 player.get_socket().send(b'ping')  # Sending a ping to check if the connection is alive
    #             except (socket.error, BrokenPipeError):
    #                 disconnected_players.append(player)
    #
    #         # Remove disconnected players
    #         for disconnected_player in disconnected_players:
    #             self.players.remove(disconnected_player)
    #             disconnected_player.close()
    #
    #         # if len(self.players) < 2:
    #         #     print("Game need at least two players, restarting...")
    #         #     self.__strategy()

    def __manage_clients(self):
        # TODO: 1. Add handling situation with one player or less, 2. Check that its working properly
        while True:
            disconnected_players = []
            for player in self.players:
                try:
                    # Attempt to receive data from the socket without blocking
                    player.get_socket().settimeout(0.1)  # Set a timeout for the receive operation
                    data = player.get_socket().recv(1)
                    if not data:
                        # No data received, socket is likely closed
                        raise socket.error("Socket closed")
                except socket.error as e:
                    if e.errno != errno.EWOULDBLOCK:
                        # Socket error other than EWOULDBLOCK (non-blocking operation would block)
                        disconnected_players.append(player)
                except Exception as e:
                    # Handle other exceptions (e.g., connection reset)
                    disconnected_players.append(player)
                finally:
                    # Reset socket timeout
                    player.get_socket().settimeout(None)

            # Remove disconnected players
            for disconnected_player in disconnected_players:
                self.players.remove(disconnected_player)

            if len(self.players) <= 1:
                self.stop()

    def broadcast_to_players(self, message):
        for player in self.players:
            try:
                player.get_socket().send(message.encode())
            except Exception as e:
                print(f"Failed to send message to {player.get_name()}: {e}")
                self.players.remove(player)

    # TODO: this is the same function but with different approach for the implementation. Need to check and decide
    def __strategy(self):
        # TODO: 1. remove all the printings 2. check if lines before loop should stay there or not 3. manage
        # TODO: instead of inside
        # self.__start_broadcast()
        # Start sending UDP broadcast messages
        self.__start_broadcast()
        # Wait for players to join or 10 seconds to elapse
        self.tcp_socket.settimeout(10)  # Set socket timeout to 10 seconds
        # TODO: remove time handling and prints later
        start_time = time.time()
        self.players = []
        while True:
            try:
                # Accept incoming TCP connections
                new_client, addr = self.tcp_socket.accept()  # (connection socket, address)
                name = new_client.recv(self.buffer_size).decode()
                print(f"Client accepted. Client's name: {name}")
                player = Player(new_client, addr, name)
                self.players.append(player)
                print(f"Time from the beginning of count: {time.time() - start_time}")
                start_time = time.time()
            except socket.timeout:
                if len(self.players) == 0:
                    continue
                    # No players connected
                    # break  # Back to step 1
                elif len(self.players) == 1:
                    # One player connected, cannot start the game
                    print("Only one player connected, waiting for more players...")
                    continue
                    # self.players.clear()  # Clear the players list
                    # break  # Back to step 1
                else:
                    # Two or more players connected, start the game
                    self.__stop_broadcast()
                    print("Starting the game...")
                    Game(self.players)
                    self.stop()
                    # TODO: Statistics
                    break  # Proceed to the next game


if __name__ == '__main__':
    s = Server()
    s.start()

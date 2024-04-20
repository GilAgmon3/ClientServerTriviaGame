import errno
import socket
import struct
import threading
import time
import random

from Game import Game
from Client.Player import Player
from GameView import print_colored
from Constants import server_names, udp_format


class Server:
    def __init__(self):
        self.is_broadcasting = False
        # self.local_ip = socket.gethostbyname(socket.gethostname())
        self.local_ip = self.__get_local_ip()
        self.udp_socket = None
        self.udp_ip = "255.255.255.255"
        self.udp_port = 13117
        self.udp_format = udp_format
        # self.tcp_socket, self.tcp_port = self.__find_available_port(1024)
        self.tcp_socket = None
        self.tcp_port = None
        self.buffer_size = 1024
        self.magic_cookie = 0xabcddcba
        self.message_type = 0x2
        self.server_name = random.choice(server_names)
        self.players = []
        self.game = False
        self.players_names = []

    def __find_available_port(self, start_port: int) -> int:
        """ Finds the first port available staring start_port and returns it"""
        port = start_port
        while True:
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    # s.bind(("", port))
                    s.bind(('localhost', port))
                    return port
            except OSError as e:
                port += 1


    def __get_local_ip(self):
        while True:
            try:
                time.sleep(0.2)
                with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
                    # Connect to a public DNS server to get the local IP
                    sock.connect(('8.8.8.8', 80))
                    local_ip = sock.getsockname()[0]
                    return local_ip
            except OSError as error:
                #print(f"Error obtaining local IP: {error}")
                print_colored(text=f"Error obtaining local IP: {error}", color='yellow')
                # Continue trying until a successful IP retrieval

    def start(self):

        # print("\033[31mThis is red text\033[0m")
        #print("\033[31mServer started, listening on IP address " + self.local_ip + "\033[0m")
        print_colored(text=f"Server started, listening on IP address {self.local_ip}", color='magenta')

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
            self.tcp_socket.bind((self.local_ip, self.tcp_port))
            # self.tcp_socket.bind(("", self.tcp_port))
            self.tcp_socket.settimeout(10)
            self.tcp_socket.listen()

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
            # print(self.udp_socket)
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

    def __manage_clients(self):
        while not self.game:
            disconnected_players = []
            for player in self.players:
                try:
                    # Attempt to send data in a non-blocking way
                    player.get_socket().setblocking(0)  # Set socket to non-blocking mode
                    player.get_socket().send(b'')  # Send a ping to check if the connection is alive
                except OSError as e:
                    if e.errno in [errno.EWOULDBLOCK, errno.EAGAIN]:
                        # These errors are expected non-blocking operation errors
                        continue
                    else:
                        # For any other socket error, assume the connection is broken
                        disconnected_players.append(player)
                except Exception as e:
                    # Handle unexpected exceptions
                    disconnected_players.append(player)
                finally:
                    # Reset socket to blocking mode
                    player.get_socket().setblocking(1)

                # Remove disconnected players
                for disconnected_player in disconnected_players:
                    self.players.remove(disconnected_player)
                    self.player_names.remove(disconnected_player.get_name())
                    disconnected_player.kill()  # Ensure the socket is closed


    def __strategy(self):
        # Start sending UDP broadcast messages
        self.__start_broadcast()
        # Wait for players to join or 10 seconds to elapse
        self.tcp_socket.settimeout(10)  # Set socket timeout to 10 seconds
        start_time = time.time()
        self.players = []
        manage_thread = threading.Thread(target=self.__manage_clients)
        manage_thread.start()
        while True:
            try:
                # Accept incoming TCP connections
                new_client = self.tcp_socket.accept()  # (connection socket, address)
                name = new_client[0].recv(self.buffer_size).decode()

                suffix = 0  # Initialize a suffix to add to the name
                while True:
                    if suffix > 0:  # Only modify name after the first check
                        modified_name = f"{name}{suffix}"  # Format the name with the current suffix
                    else:
                        modified_name = name  # Use the original name initially

                    if modified_name not in self.players_names:
                        name = modified_name  # Update name to the unique modified_name
                        break  # Exit loop once a unique name is found

                    suffix += 1  # Increment suffix for the next iteration if needed

                self.players_names.append(name)  # Append the unique name to the list

                print_colored(text=f"Client accepted. Client's name: {name}", color='magenta')
                player = Player(new_client[0], new_client[1], name)
                self.players.append(player)
                print_colored(text=f"Time from the beginning of count: {time.time() - start_time}", color='magenta')
                start_time = time.time()
            except socket.timeout:
                if len(self.players) == 0:
                    continue
                elif len(self.players) == 1:
                    # One player connected, cannot start the game
                    print_colored(text="Only one player connected, waiting for more players...", color='magenta')
                    continue
                else:
                    # Two or more players connected, start the game
                    self.__stop_broadcast()
                    print_colored(text="Starting the game...", color='magenta')
                    self.game = True
                    manage_thread.join()
                    Game(self.players, self.server_name)
                    self.players_names.clear()
                    self.stop()
                    break  # Proceed to the next game


if __name__ == '__main__':
    s = Server()
    s.start()

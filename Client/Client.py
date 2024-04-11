import socket
import struct
import threading

class Client:
    def __init__(self, client_name):
        self.client_name = client_name

        # >: Indicates big-endian byte order.
        # 4s: Represents a 4-byte string for the magic cookie.
        # B: Represents a single byte for the message type.
        # 32s: Represents a 32-byte string for the server name.
        # H: Represents a 2-byte unsigned short integer for the server port.
        self.udp_format = ">4sB32sH"

        self.local_ip = socket.gethostbyname(socket.gethostname())
        self.is_alive = False
        self.is_playing = False
        self.udp_socket = None
        self.udp_port = 13117
        self.server_ip = None
        self.tcp_socket = None
        self.tcp_port = 0
        self.buffer_size = 1024
        self.magic_cookie = 0xabcddcba
        self.message_type = 0x2


    def start(self):
        self.is_alive = True
        # Open UDP listener
        self.udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        #self.udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
        self.udp_socket.bind(("", self.udp_port))
        print("“Client started, listening for offer requests...")

        while self.is_alive:
            self.server_ip, self.tcp_port = self.__find_server()
            try:
                self.connect_to_server()
            except:
                print("Connection failed...")
                continue
            self.__game()

    def stop(self):
        self.is_alive = False

    def __find_server(self):
        while self.is_alive:
            try:
                data, address = self.udp_socket.recvfrom(self.buffer_size)
                magic_cookie, message_type, server_name, server_port = struct.unpack(self.udp_format, data)
            except struct.error:
                continue
            if magic_cookie == self.magic_cookie and message_type == self.message_type:
                print(f"Received offer from server {server_name} at address {address[0]}, attempting to connect...")
                return address[0], int(server_port)

    def connect_to_server(self):

        # TODO: do we need this?
        # if not self.is_alive:
        #    raise Exception
        self.tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.tcp_socket.connect((self.server_ip, self.tcp_port))
        self.__send_message(self.client_name + "\n")

    def __game(self):
        self.is_playing = True
        receiver = threading.Thread(target=self.__receive_message)
        receiver.start()
        self.__handle_user_inputs()
        receiver.join()

    def __receive_message(self):
        while self.is_alive and self.is_playing:
            try:
                message = self.tcp_socket.recv(self.buffer_size)
                if message:
                    print(message.decode())
                else:
                    print("Server disconnected, listening for offer requests...")
                    self.is_playing = False
            except socket.timeout:
                continue
            except:
                print("Server disconnected, listening for offer requests...")
                self.is_playing = False
                return

    def __handle_user_inputs(self):
        # TODO: do we need a while here?
        while self.is_alive and self.is_playing:
            message = input()
            self.__send_message(str(message))

    def __send_message(self, message):
        try:
            self.tcp_socket.send(message.encode())
        except:
            print("Server disconnected, listening for offer requests...")
            self.is_playing = False


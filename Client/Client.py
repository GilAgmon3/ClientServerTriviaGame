import msvcrt
import socket
import struct
import sys
import threading
import queue
import time

import select


# Hello Tlaten, this is a test to see if GitHub works correctly.

class Client:
    def __init__(self, client_name: str):
        self.client_name = client_name

        # >: Indicates big-endian byte order.
        # 4s: Represents a 4-byte string for the magic cookie.
        # B: Represents a single byte for the message type.
        # 32s: Represents a 32-byte string for the server name.
        # H: Represents a 2-byte unsigned short integer for the server port.
        self.udp_format = ">IB32sH"

        self.local_ip = socket.gethostbyname(socket.gethostname())
        self.is_alive = False
        self.is_playing = False
        self.udp_socket = None
        self.udp_port = 13117
        self.server_ip = None
        self.tcp_socket = None
        self.tcp_port_server = 0
        self.buffer_size = 1024
        self.magic_cookie = 0xabcddcba
        self.message_type = 0x2

    def start(self):
        self.is_alive = True
        print("Client started, listening for offer requests...")
        while True:
            # Open UDP listener
            self.udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            # self.udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
            self.udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.udp_socket.bind(("", self.udp_port))
            # self.udp_socket.bind((self.local_ip, self.udp_port))
            # print(f'local_ip: {self.local_ip}, udp_port: {self.udp_port}')
            while self.is_alive:
                self.server_ip, self.tcp_port_server = self.__find_server()
                try:
                    self.create_tcp_connection()
                except:
                    print("Connection failed...")
                    continue
                self.__game()
                print("Client finished game")
                break

    # def connect_to_server(self):

    def listening_for_offers(self):
        # Open UDP listener
        self.udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # self.udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
        self.udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.udp_socket.bind(("", self.udp_port))
        # self.udp_socket.bind((self.local_ip, self.udp_port))
        # print(f'local_ip: {self.local_ip}, udp_port: {self.udp_port}')

    def __find_server(self):
        while self.is_alive:
            try:

                data, address = self.udp_socket.recvfrom(self.buffer_size)
                magic_cookie, message_type, server_name, server_port = struct.unpack(self.udp_format, data)

                # Decode the server_name_bytes into a string and strip any trailing null characters
                server_name = server_name.decode('utf-8').rstrip('\x00')

            except struct.error as e:
                print("inside error in __find_server: ", e)  # TODO: delete at end
                continue

            if magic_cookie == self.magic_cookie and message_type == self.message_type:
                print(f"Received offer from server {server_name} at address {address[0]}, attempting to connect...")
                return address[0], int(server_port)

    def create_tcp_connection(self):
        """
        Connecting to server by TCP
        """
        # TODO: do we need this?
        if not self.is_alive:
            raise Exception

        self.tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.tcp_socket.connect((self.server_ip, self.tcp_port_server))
        # self.__send_message(self.client_name + "\n")
        self.__send_message(self.client_name)

    def __game(self):
        self.is_playing = True
        receiver = threading.Thread(target=self.__receive_message)
        receiver.start()
        self.__handle_user_inputs()
        # TODO: need to change the call to handle_user_input to new thread instead of main thread ?
        # sender = threading.Thread(target=self.__handle_user_inputs)
        # sender.start()
        receiver.join()
        print("After receiver join")
        # sender.join()

    def __receive_message(self):
        while self.is_alive and self.is_playing:
            try:
                # timeout is for rcv will not block input handling
                self.tcp_socket.settimeout(1)
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
                # return

    import msvcrt
    import time

    def __handle_user_inputs(self):
        while self.is_alive and self.is_playing:
         #   print(f"inside __handle_user_inputs, is_alive is {self.is_alive} and is playing is {self.is_playing}")
            try:
                message = ""
                print("Please type a message: (press Enter to send)")
                while True:
                    if msvcrt.kbhit():  # Check if key was pressed
                        char = msvcrt.getch()  # Get the key press
                        print(f"key that pressed: {char}")
                        if char == b'\r':  # Carriage return means Enter was pressed
                            print("inside if statement")
                            break
                        message += char.decode()  # Add character to message
                        sys.stdout.write(char.decode())  # Echo character back to console
                        sys.stdout.flush()
                    time.sleep(0.1)  # Sleep briefly to reduce CPU load

                if message:  # If a message was collected, send it
                    self.__send_message(str(message))
                    print(f"\nMessage sent: {message}")
            except Exception as e:
                # Handle exceptions, possibly specific ones
                print(f"Exception in __handle_user_inputs: {e}")
                continue
            print("Checking game status...")

        print(f'Finished handling inputs, self.is_playing is {self.is_playing}')

    def __handle_user_inputs(self):
        while self.is_alive and self.is_playing:
            try:
                input_thread = threading.Thread(target=self.__get_input)
                input_thread.start()

                input_thread.join(timeout=10)  # Wait for 1 second for the input thread to finish
                if input_thread.is_alive():
                    raise TimeoutError("Input timeout reached")
            except TimeoutError as te:
                continue
            except Exception as e:
                continue

    def __get_input(self):
        try:
            message = input()
            self.__send_message(str(message))
        except EOFError:
            pass  # Handle end-of-file error if necessary


    # def __handle_user_inputs(self):
    #     # TODO: do we need a while here?
    #     print(
    #         f"at the start of __handle_user_inputs when is_alive is {self.is_alive} and is playing is {self.is_playing}")
    #     while self.is_alive and self.is_playing:
    #         try:
    #             print(f"inside __handle_user_inputs, is_alive is {self.is_alive} and is playing is {self.is_playing}")
    #             message = input()
    #             self.__send_message(str(message))
    #
    #             print(f"inside __handle_user_inputs, sent message, is_alive is {self.is_alive} and is playing is {self.is_playing}")
    #
    #         except Exception as e:
    #             # TODO: decide how to handle
    #             print("exception in __handle_user_inputs")
    #             continue
    #     print(f'Finished handling inputs, self.is_playing is {self.is_playing}')



    def __send_message(self, message):
        try:
            self.tcp_socket.send(message.encode())
        except:
            # print("Server disconnected, listening for offer requests...")
            self.is_playing = False

    def stop(self):
        self.is_playing = False
        self.udp_socket.close()
        self.tcp_socket.close()
        self.udp_socket = None
        self.tcp_socket = None

# def main():
#     c = Client("Giler & Tlaten")
#     c.start()
#
# main()

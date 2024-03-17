import Protocol
import threading
import socket
import csv

class Client:
    def __init__(self):
        self.buffer = bytearray()
        self.host, self.port = Protocol.read_config()
        self.stop_thread = False
        self.is_in_room = False
        self.username = None
        self.password = None

    def run(self):
            
        # Connection to the server
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            client.connect((self.host, self.port))
        except Exception as e:
            print(f"Error connecting to the server: {e}")
            input("Press Enter to exit")
            return
        
        # Receive message from the server and send it to the server
        receive_thread = threading.Thread(target=self.receive, args=(client,))
        receive_thread.start()

    def receive(self, client):
        while not self.stop_thread:
            try:
                self.buffer += client.recv(Protocol.BufferSize)
                while (message := Protocol.process_buffer(self.buffer)):
                    message_type = message[0]

                    if message_type == Protocol.MsgType.FailLogin:
                        print("Invalid username or password")
                        message_type = Protocol.MsgType.Login

                    if message_type == Protocol.MsgType.Login:
                        self.username = input("Enter username: ")
                        self.password = input("Enter password: ")
                        client.send(Protocol.serialize(f'{Protocol.MsgType.Login}{self.username} {self.password}'))
                    elif message_type == Protocol.MsgType.SuccessLogin:
                        print("Login successful")
                        client.send(Protocol.serialize(Protocol.MsgType.ListRooms))
                    elif message_type == Protocol.MsgType.ListRooms:
                        print(f"Rooms:\n{message[1:]}")
                        room_choice = input("Choose your room:")
                        client.send(Protocol.serialize(f"{Protocol.MsgType.JoinRoom}{room_choice}"))
                    elif message_type == Protocol.MsgType.JoinRoom:
                        print(f"Welcome to {message[1:]}\n")
                        self.is_in_room = True
                    elif message_type == Protocol.MsgType.InvalidRoom:
                        print("input is not valid please try again")
                    elif message_type == Protocol.MsgType.RegularMessage:
                        print(f"{message[1:]}")
                    elif message_type == Protocol.MsgType.Notification:
                        print(f"{message[1:]}")
                    elif message_type == Protocol.MsgType.SuccessRoom:
                        write_thread = threading.Thread(target=self.write, args=(client,))
                        write_thread.start()
            except Exception as e:
                print(f"An exception occurred2: {e}")
                client.close()
                break

    def write(self, client):
        while not self.stop_thread:
            message = input("")
            message = Protocol.MsgType.RegularMessage + message
            client.send(Protocol.serialize(message))

if __name__ == "__main__":
    client = Client()
    client.run()

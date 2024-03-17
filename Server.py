import Protocol
from User import User
from Room import Room
import threading
import socket
import csv
import time

class Server:
    def __init__(self):
        self.buffer = bytearray()
        self.host, self.port = Protocol.read_config()
        self.bans = self.read_bans('bans.txt')
        self.format = Protocol.Format
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.rooms = [Room("room0"), Room("room1"), Room("room2"), Room("room3")]
        self.users = []

    def start(self):
        self.server.bind((self.host, self.port))
        self.server.listen()
        print("Server is listening...")
        self.receive_connections()

    def receive_connections(self):
        print("Server is waiting for connection...")
        while True:
            client, address = self.server.accept()
            print(f'Connected with {str(address)}')
            threading.Thread(target=self.handle_new_client, args=(client,)).start()

    def handle_new_client(self, client):
        try:
            client.send(Protocol.serialize(Protocol.MsgType.Login)) # Send login request

            threading.Thread(target=self.handle_user, args=(client,)).start()

        except Exception as e:
            print(f"An exception occurred1: {e}")

    def handle_user(self, client):
        user = None
        while True:
            try:
                self.buffer += client.recv(Protocol.BufferSize)
                while (message := Protocol.process_buffer(self.buffer)):
                    message_type = message[0]
                    msg = message[1:]
                    if not user:
                        if message_type == Protocol.MsgType.Login:
                            usr_psw = msg.split()
                            if self.check_user(usr_psw[0], usr_psw[1]):
                                user = User(usr_psw[0], client)
                                self.users.append(user)
                                print(f'The name of the client is {usr_psw[0]}.')
                                client.send(Protocol.serialize(Protocol.MsgType.SuccessLogin))
                            else:
                                client.send(Protocol.serialize(Protocol.MsgType.FailLogin))
                    else: # logged in
                        if message_type == Protocol.MsgType.ListRooms:
                            self.send_room_list(user)
                        elif message_type == Protocol.MsgType.JoinRoom:
                            self.join_room(user, message)
                        elif message_type == Protocol.MsgType.RegularMessage:
                            self.broadcast_message(msg, user)
            except Exception as e:
                print(f"An exception occurred2: {e}")
                self.remove_user(user)
                break

    def join_room(self, user, buf):
        valid_room = False
        for room in self.rooms:
            if room.get_id() == buf[1:]:
                valid_room = True
                user.join_room(room)
        if valid_room:
            user.get_client().send(Protocol.serialize(buf))
            user.get_client().send(Protocol.serialize(Protocol.MsgType.SuccessRoom))
            self.broadcast_notification(f"{user.get_uid()} joined the chat!", user)
        else:
            self.send_room_list(user)

    def broadcast_message(self, message, sender):
        try:
            for user in sender.get_room().get_users():
                user.get_client().send(Protocol.serialize(f'{Protocol.MsgType.RegularMessage}{sender.get_uid()} : {message}'))
        except Exception as e:
            print(f"An exception occurred3: {e}")

    def broadcast_notification(self, message, sender):
        try:
            for user in sender.get_room().get_users():
                user.get_client().send(Protocol.serialize(f'{Protocol.MsgType.Notification}{message}'))
        except Exception as e:
            print(f"An exception occurred4: {e}")

    def remove_user(self, user):
        if user in self.users:
            user.get_client().close()
            self.broadcast_notification(f'{user.get_uid()} left the chat.', user)
            self.users.remove(user)

    def send_room_list(self, user):
        roomList = Protocol.MsgType.ListRooms
        for room in self.rooms:
            roomList = roomList + room.get_id() + "\n"
        
        try:
            user.get_client().send(Protocol.serialize(roomList))
        except Exception as e:
            print(f"An exception occurred5: {e}")

    def check_user(self, name, psw, file_path='users.csv'):
        with open(file_path, 'r') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                if (row['username'] == name) and (row['password'] == psw):
                    return True
            return False
    
    @staticmethod
    def read_bans(file):
        with open(file, 'r') as f:
            bans = f.readlines()
        return bans

if __name__ == "__main__":
    server = Server()
    server.start()
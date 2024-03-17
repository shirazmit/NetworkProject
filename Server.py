import Protocol
from User import User
from Room import Room
import threading
import socket
import csv
import time
import datetime

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
            sock, address = self.server.accept()
            print(f'Connected with {str(address)}')
            threading.Thread(target=self.handle_new_client, args=(sock,)).start()

    def handle_new_client(self, sock):
        try:
            sock.send(Protocol.serialize(Protocol.MsgType.Login, "")) # Send login request

            threading.Thread(target=self.handle_user, args=(sock,)).start()

        except Exception as e:
            print(f"An exception occurred: {e}")

    def handle_user(self, sock):
        user = None
        while True:
            try:
                self.buffer += sock.recv(Protocol.BufferSize)
                while (message := Protocol.process_buffer(self.buffer)):
                    msg_type = message[0]
                    msg_data = message[1:]
                    if not user:
                        if msg_type == Protocol.MsgType.Login:
                            uid_psw = msg_data.split()
                            if self.check_user(uid_psw[0], uid_psw[1]):
                                user = User(uid_psw[0], sock, uid_psw[0] == 'admin')
                                self.users.append(user)
                                print(f'The name of the user is {uid_psw[0]}.')
                                sock.send(Protocol.serialize(Protocol.MsgType.SuccessLogin, ""))
                            else:
                                sock.send(Protocol.serialize(Protocol.MsgType.FailLogin, ""))
                    else: # logged in
                        if msg_type == Protocol.MsgType.ListRooms:
                            self.send_room_list(user)
                        elif msg_type == Protocol.MsgType.JoinRoom:
                            self.join_room(user, msg_data)
                        elif msg_type == Protocol.MsgType.RegularMessage:
                            if str(msg_data).lower() == Protocol.MsgCommands.LeaveRoom:
                                sock.send(Protocol.serialize(Protocol.MsgType.LeaveRoom, ""))
                                self.send_room_list(user)
                            else:
                                self.broadcast_message(msg_data, user)
            except Exception as e:
                print(f"An exception occurred: {e}")
                self.remove_user(user)
                break

    def join_room(self, user, choice):
        valid_room = False
        for room in self.rooms:
            if room.get_id() == choice:
                valid_room = True
                user.join_room(room)
                
        if valid_room:
            user.get_socket().send(Protocol.serialize(Protocol.MsgType.JoinRoom, choice))
            chatlog = user.get_room().load_chat_messages()
            user.get_socket().send(Protocol.serialize(Protocol.MsgType.RegularMessage, chatlog))
            self.broadcast_notification(f"{user.get_uid()} joined the chat!", user)
        else:
            self.send_room_list(user)

    def broadcast_message(self, message, sender):
        try:
            msg = f'{datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")} {sender.get_uid()} : {message}'
            sender.get_room().log_chat_message(msg)
            for user in sender.get_room().get_users():
                user.get_socket().send(Protocol.serialize(Protocol.MsgType.RegularMessage, msg))
        except Exception as e:
            print(f"An exception occurred: {e}")

    def broadcast_notification(self, message, sender):
        try:
            for user in sender.get_room().get_users():
                user.get_socket().send(Protocol.serialize(Protocol.MsgType.Notification, message))
        except Exception as e:
            print(f"An exception occurred: {e}")

    def remove_user(self, user):
        if user in self.users:
            user.get_socket().close()
            self.broadcast_notification(f'{user.get_uid()} left the chat.', user)
            self.users.remove(user)

    def send_room_list(self, user):
        roomList = ""
        for room in self.rooms:
            roomList = roomList + room.get_id() + "\n"
        
        try:
            user.get_socket().send(Protocol.serialize(Protocol.MsgType.ListRooms, roomList))
        except Exception as e:
            print(f"An exception occurred: {e}")

    @staticmethod
    def check_user(name, psw, file_path='users.csv'):
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
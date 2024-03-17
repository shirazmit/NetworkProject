import Protocol
from User import User
from Room import Room
import threading
import socket
import time

class Server:
    def __init__(self):
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
            client.send(Protocol.MsgType.SetUsername.encode('ascii'))
            username = client.recv(Protocol.BufferSize).decode('ascii')

            if username + '\n' in self.bans:
                client.send(Protocol.MsgType.RefuseBan.encode('ascii'))
                client.close()
                return

            if username == 'admin':
                client.send('PASS'.encode('ascii'))
                password = client.recv(Protocol.BufferSize).decode('ascii')
                if password != 'adminPass':
                    client.send('REFUSE'.encode('ascii'))
                    client.close()
                    return

            user = User(username, client)
            self.users.append(user)
            print(f'The name of the client is {username}.')

            threading.Thread(target=self.handle_user, args=(user,)).start()

        except Exception as e:
            print(f"An exception occurred: {e}")

    def handle_user(self, user):
        while True:
            try:
                buffer = user.get_client().recv(Protocol.BufferSize).decode('ascii')
                message_type = buffer[0]
                if message_type == Protocol.MsgType.ListRooms:
                    self.send_room_list(user)
                elif message_type == Protocol.MsgType.JoinRoom:
                    self.join_room(user, buffer)
                elif message_type == Protocol.MsgType.RegularMessage:
                    self.broadcast_message(buffer[1:], user)
            except Exception as e:
                print(f"An exception occurred: {e}")
                self.remove_user(user)
                break

    def join_room(self, user, buffer):
        valid_room = False
        for room in self.rooms:
            if room.get_id() == buffer[1:]:
                valid_room = True
                user.join_room(room)
        if valid_room:
            user.get_client().send(buffer.encode('ascii'))
            time.sleep(0.1)
            self.broadcast_notification(f"{user.get_uid()} joined the chat!", user)
        else:
            self.send_room_list(user)

    def broadcast_message(self, message, sender):
        try:
            for user in sender.get_room().get_users():
                user.get_client().send(f'{Protocol.MsgType.RegularMessage}{sender.get_uid()} : {message}'.encode('ascii'))
        except Exception as e:
            print(f"An exception occurred: {e}")

    def broadcast_notification(self, message, sender):
        try:
            for user in sender.get_room().get_users():
                user.get_client().send(f'{Protocol.MsgType.Notification}{message}'.encode('ascii'))
        except Exception as e:
            print(f"An exception occurred: {e}")

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
            user.get_client().send(roomList.encode('ascii'))
        except Exception as e:
            print(f"An exception occurred: {e}")
    
    @staticmethod
    def read_bans(file):
        with open(file, 'r') as f:
            bans = f.readlines()
        return bans

if __name__ == "__main__":
    server = Server()
    server.start()
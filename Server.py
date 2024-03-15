import socket
import threading
import json
import csv
import datetime
import os
from User import User
from Room import Room
import time

#from cryptography.hazmat.backends import default_backend
#from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
#from cryptography.hazmat.primitives import padding

#server side
#localhost

host = '127.0.0.1'
port = 8000
format = 'utf-8'

#connection
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((host ,port))
server.listen()

users = []
rooms = [Room("room0"), Room("room1"), Room("room2"), Room("room3")]

#broadcast message that sends to all the clients
def broadcast(message, user):
    try:
        for u in user.get_room().get_users():
            u.get_client().send(f'm{user.get_name()} : {message}'.encode('ascii'))
    except Exception as e:
        print(f"An exception occurred: {e}")

def handle(user):
    while True:
        try:
            buffer = user.get_client().recv(1024).decode('ascii')
            if buffer:
                if buffer.startswith('l'):
                    handle_list(user)
                elif buffer.startswith('r'):
                    valid_room = False
                    for room in rooms:
                        if room.get_name() == buffer[1:]:
                            valid_room = True
                            room.get_users().append(user)
                            user.set_room(room)
                    if valid_room:
                        user.get_client().send(buffer.encode('ascii'))
                        time.sleep(1)
                        broadcast("joined the chat!", user)
                    else:
                        handle_list(user)
                elif buffer.startswith('m'):
                    broadcast(buffer[1:], user)
                    user.get_room().log_chat_message(user.get_name(), buffer)
                
        except Exception as e:
            # Print the exception
            print(f"An exception occurred: {e}")
            if user in users:
                user.get_client().close()
                broadcast(f'left the chat.', user)
                users.remove(user)
                break
""""
        try:
        # Loop to receive and process each message from the client
            for i in range(total_messages):
                data_encrypted = conn.recv(1024)
                data = decrypt(data_encrypted)
                print(f"Received message #{i} from client: \"{data}\"")
                # Echo back the decrypted message to the client after encryption
                conn.send(encrypt(data))
            print("\n[CLIENT DISCONNECTED] on address: ", addr)
            print()
        except:
             print("[CLIENT CONNECTION INTERRUPTED] on address: ", addr)
"""

def receive():
    print("Server is waiting for connection...")
    while True:
        client, address = server.accept()
        print(f'Connected with {str(address)}')

        try:
            client.send('NICK'.encode('ascii'))
            username = client.recv(1024).decode('ascii')
        except Exception as e:
            print(f"An exception occurred: {e}")

        with open('bans.txt', 'r') as f:
            bans = f.readlines()

        if username+'\n' in bans:
            client.send('BAN'.encode('ascii'))
            client.close()
            continue

        if username == 'admin':
            client.send('PASS'.encode('ascii'))
            password = client.recv(1024).decode('ascii')
            #better to use hash
            if password != 'adminPass':
                client.send('REFUSE'.encode('ascii'))
                client.close()
                continue

        user = User(username, client)
        users.append(user)

        print(f'The name of the client is {username}.')

        thread = threading.Thread(target=handle, args=(user,))
        thread.start()

#kick user from the chat
def kick_user(name):
    for user in users:
        if user.get_name() == name:
            user.get_client().send('You were kicked by the admin!'.encode('ascii'))
            user.get_client().close()
            broadcast(f'{name} was kicked by the admin', user)
            users.remove(user)

def handle_list(user):
    roomList = "l"
    for room in rooms:
        roomList = roomList + room.get_name() + "\n"

    try:
        user.get_client().send(roomList.encode('ascii'))
    except Exception as e:
        print(f"An exception occurred: {e}")

print ("Server is listening...")
receive()





import socket
import threading
import json
import csv
import datetime
import os
from User import User
from Room import Room

#from cryptography.hazmat.backends import default_backend
#from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
#from cryptography.hazmat.primitives import padding

#server side
#localhost

host = '127.0.0.1'
port = 55555
format = 'utf-8'

#connection
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((host ,port))
server.listen()

users = []
rooms = [Room("room0"), Room("room1"), Room("room2"), Room("room3")]

#broadcast message that sends to all the clients
def broadcast(message):
    for user in users:
        user.get_client().send(message)

def handle(user):

    while True:
        try:
            buffer = user.get_client().recv(1024)
            msg = message = user.get_client().recv(1024)

            if buffer.startswith('r'):
                for room in rooms:
                    if room == buffer[1:]:
                        user.get_client().send(buffer.encode('ascii'))
                        room.get_users().append(user)
                user.get_client().send('f'.encode('ascii'))
                
            if msg.decode('ascii').startswith('KICK'):
                print("Test")
                if user.get_name() == 'admin':
                    kick_name = msg.decode('ascii')[5:]
                    kick_user(kick_name)
                else:
                    user.get_client().send('Command was refused!'.encode('ascii'))
            elif msg.decode('ascii').startswith('BAN'):
                if user.get_name() == 'admin':
                    ban_name = msg.decode('ascii')[4:]
                    kick_user(ban_name)
                    with open('bans.txt','a') as f:
                        f.write(f'{ban_name}\n')
                    print(f'{ban_name} was banned!')
                else:
                    user.get_client().send('Command was refused!'.encode('ascii'))
            else:
                broadcast(message)
                Room.log_chat_message(user.get_name(), message.decode('ascii'))
                
        except Exception as e:
            # Print the exception
            print(f"An exception occurred: {e}")
            if user in users:
                user.get_client().close()
                broadcast(f'{user.get_name()} left the chat.'.encode('ascii'))
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

        client.send('NICK'.encode('ascii'))
        username = client.recv(1024).decode('ascii')

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
        broadcast(f'{username} joined the chat!'.encode('ascii'))

        roomList = ""
        for room in rooms:
            roomList = roomList + room.get_name() + "\n"
        client.send(roomList.encode('ascii'))
        
        thread = threading.Thread(target=handle, args=(user,))
        thread.start()

#kick user from the chat
def kick_user(name):
    for user in users:
        if user.get_name() == name:
            user.get_client().send('You were kicked by the admin!'.encode('ascii'))
            user.get_client().close()
            users.remove(user)
            broadcast(f'{name} was kicked by the admin'.encode('ascii'))

print ("Server is listening...")
receive()







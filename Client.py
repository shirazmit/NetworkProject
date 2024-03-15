import socket
import threading
import json
import csv
import os
import time

# Comment
stopThread = False
is_in_room = False

def main():
    #if username == 'admin':
    #    password = input("Enter password: ")
    result = False

    while(result == False):
        username = input("Enter username: ")
        password = input("Enter password: ")
        result = check_user(username, password)
        
    #connection to the server
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client.connect(('127.0.0.1',8000))
    except Exception as e:
        print(f"Error connecting to the server: {e}")
        input("Press Enter to exit")
        return
    
    #receive message from the server and sent it to the server
    receive_thread = threading.Thread(target=receive, args=(client, username, password))
    receive_thread.start()
    
#receiving messages 
def receive(client, username, password):
    while True:
        global stopThread
        global is_in_room
        if stopThread:
            break
        try:
            buffer = client.recv(1024).decode('ascii')
            if buffer:
                if buffer.startswith('l'):
                    print(f"Rooms:\n{buffer[1:]}" )
                    room_choice = input ("Choose your room:")
                    client.send(f"r{room_choice}".encode('ascii'))
                elif buffer.startswith('r'):
                    print(f"Welcome to {buffer[1:]}\n" )
                    is_in_room = True
                elif buffer.startswith('f'):
                    print("input is not valid pls try again")
                if buffer.startswith('m'):
                    print(f"{buffer[1:]}" )
                elif buffer.startswith('NICK'):
                    client.send(username.encode('ascii'))
                    write_thread = threading.Thread(target=write, args=(client, username))
                    write_thread.start()
        except:
            print("Error - Houston, we have a problem")
            client.close()
            break

def write(client, username):
    while True:
        global stopThread
        global is_in_room
        if stopThread:
            break

        if not is_in_room:
            client.send("l".encode('ascii'))
            while not is_in_room:
                pass

        message = input("")
        message = 'm' + message
    
        if message[len(username)+2:].startswith('/'):
            if username == 'admin' :
                if message[len(username)+2:].startswith('/kick'):
                    client.send(f'KICK {message[len(username)+2+6:]}'.encode('ascii'))
                elif message[len(username)+2:].startswith('/ban'):
                    client.send(f'BAN {message[len(username)+2+5:]}'.encode('ascii'))
            else:
                 print("Only the admin allowed to send commends")
        else:
            client.send(message.encode('ascii'))

def check_user (name, psw, file_path = 'users.csv'):
    with open(file_path, 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            if (row['username'] == name) and (row['password'] == psw):
                return True
            
        print("Username or Password are not valid, \n Pls try again")
        return False


            
if __name__ == "__main__":
    main()

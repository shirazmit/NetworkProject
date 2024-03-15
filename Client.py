import socket
import threading
import csv
from MessageType import MessageType

# Helper method to read config file
def read_config(filename='config.txt'):
    with open(filename, 'r') as f:
        lines = f.readlines()
        host = lines[0].strip()
        port = int(lines[1].strip())
    return host, port

class Client:
    def __init__(self):
        self.host, self.port = read_config()
        self.stop_thread = False
        self.is_in_room = False
        self.username = None

    def run(self):
        result = False

        while not result:
            self.username = input("Enter username: ")
            password      = input("Enter password: ")
            result = self.check_user(self.username, password)
            
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
        while True:
            if self.stop_thread:
                break
            try:
                buffer = client.recv(1024).decode('ascii')
                message_type = buffer[0]
                if message_type == MessageType.ListRooms:
                    print(f"Rooms:\n{buffer[1:]}")
                    room_choice = input("Choose your room:")
                    client.send(f"{MessageType.JoinRoom}{room_choice}".encode('ascii'))
                elif message_type == MessageType.JoinRoom:
                    print(f"Welcome to {buffer[1:]}\n")
                    self.is_in_room = True
                elif message_type == MessageType.InvalidRoom:
                    print("input is not valid pls try again")
                elif message_type == MessageType.RegularMessage:
                    print(f"{buffer[1:]}")
                elif message_type == MessageType.SetUsername:
                    client.send(self.username.encode('ascii'))
                    write_thread = threading.Thread(target=self.write, args=(client,))
                    write_thread.start()
            except:
                print("Error - Houston, we have a problem")
                client.close()
                break

    def write(self, client):
        while True:
            if self.stop_thread:
                break

            if not self.is_in_room:
                client.send(MessageType.ListRooms.encode('ascii'))
                while not self.is_in_room:
                    pass

            message = input("")
            message = MessageType.RegularMessage + message

            if message[len(self.username) + 2:].startswith('/'):
                if self.username == 'admin':
                    if message[len(self.username) + 2:].startswith('/kick'):
                        client.send(f'KICK {message[len(self.username) + 2 + 6:]}'.encode('ascii'))
                    elif message[len(self.username) + 2:].startswith('/ban'):
                        client.send(f'BAN {message[len(self.username) + 2 + 5:]}'.encode('ascii'))
                else:
                    print("Only the admin allowed to send commands")
            else:
                client.send(message.encode('ascii'))

    def check_user(self, name, psw, file_path='users.csv'):
        with open(file_path, 'r') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                if (row['username'] == name) and (row['password'] == psw):
                    return True
            print("Username or Password are not valid, \n Pls try again")
            return False

if __name__ == "__main__":
    client = Client()
    client.run()

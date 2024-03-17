import Protocol
import threading
import socket
import csv

class Client:
    def __init__(self):
        self.host, self.port = Protocol.read_config()
        self.stop_thread = False
        self.is_in_room = False
        self.username = None

    def run(self):
        valid_user = False
        while not valid_user:
            self.username = input("Enter username: ")
            password      = input("Enter password: ")
            valid_user = self.check_user(self.username, password)
            
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
                buffer = client.recv(Protocol.BufferSize).decode('ascii')
                message_type = buffer[0]
                if message_type == Protocol.MsgType.ListRooms:
                    print(f"Rooms:\n{buffer[1:]}")
                    room_choice = input("Choose your room:")
                    client.send(f"{Protocol.MsgType.JoinRoom}{room_choice}".encode('ascii'))
                elif message_type == Protocol.MsgType.JoinRoom:
                    print(f"Welcome to {buffer[1:]}\n")
                    self.is_in_room = True
                elif message_type == Protocol.MsgType.InvalidRoom:
                    print("input is not valid please try again")
                elif message_type == Protocol.MsgType.RegularMessage:
                    print(f"{buffer[1:]}")
                elif message_type == Protocol.MsgType.Notification:
                    print(f"{buffer[1:]}")
                elif message_type == Protocol.MsgType.SetUsername:
                    client.send(self.username.encode('ascii'))
                    write_thread = threading.Thread(target=self.write, args=(client,))
                    write_thread.start()
            except:
                print("Error - Houston, we have a problem")
                client.close()
                break

    def write(self, client):
        while not self.stop_thread:

            if not self.is_in_room:
                client.send(Protocol.MsgType.ListRooms.encode('ascii'))
                while not self.is_in_room:
                    pass

            message = input("")
            message = Protocol.MsgType.RegularMessage + message

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
            print("Username or Password are not valid, \n Please try again")
            return False

if __name__ == "__main__":
    client = Client()
    client.run()

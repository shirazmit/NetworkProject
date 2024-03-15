import socket
import datetime
from User import User

class Room:
    def __init__(self, name, users=None):
        if users is None:
            users = []  # Create a new list for each instance
        self.users = users
        self.name = name

    def get_users(self):
        return self.users

    def get_name(self):
        return self.name
    
  #  def get_key(self):
   #     return self.key

    def set_user(self, user):
        self.user = user

    def set_name(self, name):
        self.name = name

    def log_chat_message(self, sender, message):
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(f'{self.name}.txt', 'a') as chat_log:
            chat_log.write(f'{timestamp} - {sender}: {message}\n')


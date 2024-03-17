import datetime

class Room:
    def __init__(self, id, users=None):
        if users is None:
            users = []
        self.users = users
        self.id = id

    def get_users(self):
        return self.users

    def get_id(self):
        return self.id
    
    def get_users(self):
        return self.users
    
    # Handled by User
    def __add_user(self, user):
        if user not in self.users:
            self.users.append(user)

    # Handled by User
    def __remove_user(self, user):
        if user in self.users:
            self.users.remove(user)

    def log_chat_message(self, sender, message):
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(f'{self.id}.txt', 'a') as chat_log:
            chat_log.write(f'{timestamp} - {sender}: {message}\n')


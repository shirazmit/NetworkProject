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

    def log_chat_message(self, message):
        try:
            with open(f'{self.id}.txt', 'a') as chat_log:
                chat_log.write(f'{message}\n')
        except FileNotFoundError:
            # If the file doesn't exist, create it and then write the message
            with open(f'{self.id}.txt', 'w') as chat_log:
                chat_log.write(f'{message}\n')

    def load_chat_messages(self):
        ret = ""
        try:
            with open(f'{self.id}.txt', 'r') as chat_log:
                for line in chat_log:
                    ret += line
            return ret
        except FileNotFoundError:
            print("Initial chat log not found.")
            return ""

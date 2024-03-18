import socket

class User:
    def __init__(self, uid, socket, is_admin=False):
        self.uid = uid
        self.socket = socket
        self.room = None
        self.is_admin = is_admin

    def get_uid(self):
        return self.uid

    def get_socket(self):
        return self.socket
    
    def get_room(self):
        return self.room

    def set_uid(self, uid):
        self.uid = uid

    def set_socket(self, socket):
        self.socket = socket

    def join_room(self, room):
        if self.room:
            self.leave_room()  # Make sure the user leaves any existing room
        self.room = room
        room._Room__add_user(self)

    def leave_room(self):
        if self.room:
            self.room._Room__remove_user(self)
            self.room = None
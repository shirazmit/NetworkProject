import socket

class User:
    def __init__(self, uid, client):
        self.uid = uid
        self.client = client
        self.room = None

    def get_uid(self):
        return self.uid

    def get_client(self):
        return self.client
    
    def get_room(self):
        return self.room

    def set_uid(self, uid):
        self.uid = uid

    def set_client(self, client):
        self.client = client

    def join_room(self, room):
        if self.room:
            self.leave_room()  # Make sure the user leaves any existing room
        self.room = room
        room._Room__add_user(self)

    def leave_room(self):
        if self.room:
            self.room._Room__remove_user(self)
            self.room = None
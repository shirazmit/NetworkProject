import socket

class User:
    def __init__(self, name, client):
        self.name = name
        self.client = client

    def get_name(self):
        return self.name

    def get_client(self):
        return self.client

    def set_name(self, name):
        self.name = name

    def set_client(self, client):
        self.client = client
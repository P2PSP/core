import socket

class blocking_socket(socket.socket):

    def __init__(self, *p):
        super(blocking_socket, self).__init__(*p)

    def brecv(self, size):
        data = super(blocking_socket, self).recv(size)
        while len(data) < size:
            data += super(blocking_socket, self).recv(size - len(data))
        return data

    def baccept(self):
        return super(blocking_socket, self).accept()

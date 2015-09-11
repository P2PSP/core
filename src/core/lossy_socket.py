# -*- coding: iso-8859-15 -*-

# The P2PSP.org project has been supported by the Junta de Andalucía
# through the Proyecto Motriz "Codificación de Vídeo Escalable y su
# Streaming sobre Internet" (P10-TIC-6548).

# Overwrites the "sendto" method of the socket library, in order to
# simulate packet loss.
  
#from __future__ import print_function
from socket import socket

# http://stackoverflow.com/questions/2833022/cant-overload-python-socket-send

class lossy_socket():

    def __init__(self, ratio, *p):
        self._sock = socket(*p)
        self.counter = 0
        self.ratio = ratio

    def sendto(self, *p):
        self.counter += 1
        if (self.counter % self.ratio) != 0:
            return self._sock.sendto(*p)
        else:
            print('lost chunk!')
            self.counter = 0

    def bind(self, *p):
        return self._sock.bind(*p)

    def settimeout(self, *p):
        return self._sock.settimeout(*p)

    def getsockname(self, *p):
        return self._sock.getsockname(*p)

    def recvfrom(self, *p):
        return self._sock.recvfrom(*p)

    def setsockopt(self, *p):
        return self._sock.setsockopt(*p)

# -*- coding: iso-8859-15 -*-

# The P2PSP.org project has been supported by the Junta de Andalucía
# through the Proyecto Motriz "Codificación de Vídeo Escalable y su
# Streaming sobre Internet" (P10-TIC-6548).

# Overwrites the "sendto" method of the socket library, in order to
# force sequential source port allocation.

import socket

# Proxy object for socket.socket
class symsp_socket(object):
    # {{{

    def __init__(self, port_step, *p):
        self._sock = socket.socket(*p)
        self.destinations = []
        self.port_step = port_step

    def sendto(self, message, destination):
        # {{{

        # For each destination endpoint that was not sent to yet, this socket
        # wrapper creates a temporary socket and connects to the destination a
        # specified number of times before sending from the original socket.
        # This forces the NAT to create a new mapping entry and therefore
        # to increment the source port of self._sock by self.port_step.

        if destination not in self.destinations:
            for _ in range(self.port_step):
                sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                sock.sendto(b'', destination)
                sock.close()
            self.destinations.append(destination)
        return self._sock.sendto(message, destination)

        # }}}

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

    def close(self, *p):
        return self._sock.close(*p)

    # }}}

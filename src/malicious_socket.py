#!/usr/bin/python -O
# -*- coding: iso-8859-15 -*-

# This code is distributed under the GNU General Public License (see
# THE_GENERAL_GNU_PUBLIC_LICENSE.txt for extending this information).
# Copyright (C) 2015, the P2PSP team.
# http://www.p2psp.org

import socket
import struct

class MaliciousSocket():

    def __init__(self, message_format, *p):
        self._sock = socket.socket(*p)
        self.message_format = message_format

    def sendto(self, string, address):
        if len(string) == struct.calcsize(self.message_format):
            return self._sock.sendto(self.get_poisoned_chunk(string), address)
        else:
            return self._sock.sendto(string, address)

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

    def get_poisoned_chunk(self, message):
        chunk_number, chunk = struct.unpack(self.message_format, message)
        return struct.pack(self.message_format, chunk_number, '0')

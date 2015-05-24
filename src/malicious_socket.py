#!/usr/bin/python -O
# -*- coding: iso-8859-15 -*-

# This code is distributed under the GNU General Public License (see
# THE_GENERAL_GNU_PUBLIC_LICENSE.txt for extending this information).
# Copyright (C) 2015, the P2PSP team.
# http://www.p2psp.org

from socket import socket

class MaliciousSocket():

    def __init__(self, chunk_message_length, *p):
        self._sock = socket(*p)
        self.chunk_message_length = chunk_message_length

    def sendto(self, string, address):
        if len(string) == self.chunk_message_length:
            return self._sock.sendto(self.get_poisoned_chunk(), address)
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

    def get_poisoned_chunk(self):
        return bytes('0' * self.chunk_message_length, 'utf-8')

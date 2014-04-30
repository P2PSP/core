# -*- coding: iso-8859-15 -*-

# {{{ GNU GENERAL PUBLIC LICENSE

# This is part of the P2PSP (Peer-to-Peer Simple Protocol)
# <https://launchpad.net/p2psp>.
#
# Copyright (C) 2013 Vicente González Ruiz.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

# }}}

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
            print('Lost chunk!')
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

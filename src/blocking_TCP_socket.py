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

import socket

class blocking_TCP_socket(socket.socket):

    def __init__(self, *p):
        super(blocking_TCP_socket, self).__init__(*p)

    def brecv(self, size):
        data = super(blocking_TCP_socket, self).recv(size)
        while len(data) < size:
            data += super(blocking_TCP_socket, self).recv(size - len(data))
        return data

    def baccept(self):
        return super(blocking_TCP_socket, self).accept()

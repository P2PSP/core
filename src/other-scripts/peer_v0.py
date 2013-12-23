#!/usr/bin/python -O
# -*- coding: iso-8859-15 -*-

# Recibe el stream desde el servidor fuente (Icecast) y lo env'ia al
# player.

import os
import sys
import socket
import struct
import time
from config import Config

IP_ADDR = 0
PORT = 1

buffer_size = Config.buffer_size
peer_port = Config.peer_port
header_size = Config.header_size

# Estas cuatro variables las debería indicar el splitter
source_hostname = Config.source_hostname
source_port = Config.source_port
channel = Config.channel
block_size = Config.block_size
block_format_string = Config.block_format_string

source = (source_hostname, source_port)

def get_player_socket():
    # {{{

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    try:
        # In Windows systems this call doesn't work!
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    except:
        pass
    sock.bind(('', peer_port))
    sock.listen(0)

    print sock.getsockname(), 'Waiting for the player at port:', peer_port

    sock, player = sock.accept()
    sock.setblocking(0)

    print sock.getsockname(), 'Player is', sock.getpeername()

    return sock

    # }}}

player_sock = get_player_socket() # The peer is blocked until the
                                  # player establish a connection.

def communicate_the_header():
    # {{{ 
    source_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    source_sock.connect(source)
    GET_message = 'GET /' + channel + ' HTTP/1.1\r\n'
    GET_message += '\r\n'
    source_sock.sendall(GET_message)

    print source_sock.getsockname(), \
        'Requesting the stream header to http://' + \
        str(source_sock.getpeername()[0]) + \
        ':' + str(source_sock.getpeername()[1]) + \
        '/'+str(channel)
    # {{{ Receive the video header from the source and send it to the player

    # Nota: este proceso puede fallar si durante la recepción de los
    # bloques el stream se acaba. Habría que realizar de nuevo la
    # petición HTTP (como hace el servidor).

    data = source_sock.recv(header_size)
    total_received = len(data)
    player_sock.sendall(data)
    while total_received < header_size:
        data = source_sock.recv(header_size - len(data))
        player_sock.sendall(data)
        total_received += len(data)
        print "Received bytes:", total_received, "\r",

    # }}}

    print source_sock.getsockname(), 'Got', total_received, 'bytes'

    source_sock.close()
    # }}}

communicate_the_header() # Retrieve the header of the stream from the
                         # source and send it to the player.

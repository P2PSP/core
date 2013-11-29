#!/usr/bin/python -O

# Servir captura usando "netcat -l".

import time
import sys
import socket
from blocking_TCP_socket import blocking_TCP_socket

source_hostname='150.214.150.68'
source_port=4551

source = (source_hostname, source_port)
source_sock = blocking_TCP_socket(socket.AF_INET, socket.SOCK_STREAM)
print source_sock.getsockname(), 'Connecting to the source ', source, '...',

source_sock.connect(source)

print source_sock.getsockname(), 'Connected to ', source, '!'

channel='480.ogg'
GET_message = 'GET /' + channel + ' HTTP/1.1\r\n'
GET_message += '\r\n'
source_sock.sendall(GET_message)

of = open('prueba.dat', 'wb')

block_size = 1024

while True:

    # Receive data from the source
    def receive_next_block():
        # {{{

        global source_sock

        block = source_sock.recv(block_size)
        tries = 0
        while len(block) < block_size:
            tries += 1
            if tries > 3:
                tries = 0

                print '\b!',
                sys.stdout.flush()

                time.sleep(1)
                source_sock.close()
                source_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                source_sock.connect(source)
                source_sock.sendall(GET_message)
            block += source_sock.recv(block_size - len(block))
        return block

        # }}}

    block = receive_next_block()

    print '\b.',
    sys.stdout.flush()

    of.write(block)

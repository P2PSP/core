#!/usr/bin/python
# -*- coding: iso-8859-15 -*-

'''
python peer.py 150.214.150.68 4552 9999
vlc http://localhost:9999
'''

# No solicita retransmisión de bloques perdidos. Avisa al nodo fuente
# de los peers eliminados de la lista de peers. Posee un buffer para
# acomodar el jitter.

import sys
import socket
from blocking_socket import blocking_socket
from colors import Color
import struct

IP_ADDR = 0
PORT = 1

source_name = sys.argv[1]
source_port = int(sys.argv[2])
player_port = int(sys.argv[3])

peer_list = []
peer_insolidarity = {}

player_listen_socket = blocking_socket(socket.AF_INET, socket.SOCK_STREAM)
player_listen_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
player_listen_socket.bind(("localhost", player_port))
player_listen_socket.listen(1)
print player_listen_socket.getsockname(), "Waiting for the player ...",
player_serve_socket, player = player_listen_socket.baccept()
player_listen_socket.setblocking(0)
print player_serve_socket.getsockname(), "accepted connection from", player

if len(sys.argv) > 4:
    source_socket = socket.create_connection((source_name, source_port),1000,('',int(sys.argv[4])))
else:
    source_socket = blocking_socket(socket.AF_INET, socket.SOCK_STREAM)
    source_socket.connect((source_name, source_port))

print source_socket.getsockname(), "Connected to", source_socket.getpeername()

print source_socket.getsockname(), \
    "My IP address is" , source_socket.getsockname(), "->", \
    source_socket.getpeername()
payload = struct.pack("4sH",
                      socket.inet_aton(source_socket.getsockname()[IP_ADDR]),
                      socket.htons(source_socket.getsockname()[PORT]))
source_socket.sendall(payload)

buffer_size = 32

number_of_peers = socket.ntohs(
    struct.unpack(
        "H", source_socket.recv(
                struct.calcsize("H")))[0])
print source_socket.getsockname(), "<- Cluster size =", number_of_peers+1
print source_socket.getsockname(), "Retrieving the list of peers ..."
while number_of_peers > 0:
    payload = source_socket.recv(struct.calcsize("4sH"))
    peer_IPaddr, port = struct.unpack("4sH", payload)
    peer_IPaddr = socket.inet_ntoa(peer_IPaddr)
    port = socket.ntohs(port)
    peer = (peer_IPaddr, port)
    print source_socket.getsockname(), "<- peer", peer
    peer_list.append(peer)
#    peer_insolidarity[peer] = -32768 # To avoid removing peers during
#                                     # the buffering
    peer_insolidarity[peer] = 0
    number_of_peers -= 1

print source_socket.getsockname(), "<- ", source_socket, "[Video header",
video_header_size = socket.ntohs(
    struct.unpack(
        "H", source_socket.recv(
            struct.calcsize("H")))[0])
for i in xrange (video_header_size):
    block = source_socket.recv(1024)
    player_serve_socket.sendall(block)
    print "\b.",
print "] done"

stream_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
stream_socket.bind(source_socket.getsockname())

# This should create a working entry in the NAT if the peer is in a
# private network
payload = struct.pack("4sH", "aaaa", 0)
(source_ip, unbound_port) = (source_socket.getpeername()[0], 80)
print source_socket.getpeername(), (source_ip, unbound_port)
for i in xrange(2):
    #stream_socket.sendto(payload, (source_ip, unbound_port))
    stream_socket.sendto(payload, source_socket.getpeername())

class Block_buffer_element:
    def block(self):
        return self[0]
    def number(self):
        return self[1]
    def empty(self):
        return self[2]

block_buffer = [Block_buffer_element() for i in xrange(buffer_size)]
for i in xrange(buffer_size):
    block_buffer[i].empty = True # Nothing useful inside

print "Buffering ..."

def receive_and_feed_the_cluster():
    
    payload, addr = stream_socket.recvfrom(struct.calcsize("H1024s"))
    number, block = struct.unpack("H1024s", payload)
    number = socket.ntohs(number)
    '''
    print source_socket.getsockname(),
    if block_buffer[number % buffer_size].requested:
        print Color.red + "<~" + Color.none,
    else:
        print Color.green + "<-" + Color.none, 
    print number, addr
    '''
    print source_socket.getsockname(),
    print Color.green + "<-" + Color.none,
    print number, addr

    if addr == source_socket.getpeername():
        counter = 0
        for peer in peer_list:
            print source_socket.getsockname(), \
                number, Color.green + "->" + Color.none, peer, "(", counter, "/", len(peer_list),")"
            counter += 1
            stream_socket.sendto(payload, peer)
            peer_insolidarity[peer] += 1
            if peer_insolidarity[peer] > 32: # <- Important parameter!!
                index_of_peer_to_remove = peer_list.index(peer)
                peer_list.remove(peer)
                del peer_insolidarity[peer]
                print Color.blue
                print "Removing", peer
                print Color.none

                payload = struct.pack("4sH",
                                      socket.inet_aton(peer[IP_ADDR]),
                                      socket.htons(peer[PORT]))
                stream_socket.sendto(payload, source_socket.getpeername())

                # Si este paquete se pierde, en principio no ocurre
                # nada porque el o los super-peers van a hacer lo
                # mismo con el nodo fuente y es prácticamente
                # imposible que los mensajes que se envían desde los
                # super-peers hacia el nodo fuente se pierdan (en
                # ancho de banda entre ellos está garantizado).

    else:
        if not addr in peer_list:
            peer_list.append(addr)
        peer_insolidarity[addr] = 0

    block_buffer[number % buffer_size].block = block
    block_buffer[number % buffer_size].number = number
    block_buffer[number % buffer_size].empty = False

    return number

block_to_play = receive_and_feed_the_cluster()
for i in xrange(buffer_size/2):
    receive_and_feed_the_cluster()

# Now, reset the solidarity of the peers
for p in peer_list:
    peer_insolidarity[p] = 0

print "... buffering done"

def send_a_block_to_the_player():

    global block_to_play

    # Only if the block has something useful inside ...
    if block_buffer[(block_to_play % buffer_size)].empty == False:
        print player_serve_socket.getsockname(), \
            block_buffer[block_to_play % buffer_size].number, \
            Color.blue + "=>" + Color.none, \
            player_serve_socket.getpeername()
        sent_bytes = player_serve_socket.sendall(str(block_buffer[block_to_play % buffer_size].block))
        
        # buffer[block_to_play.number].empty = True
        block_buffer[block_to_play % buffer_size].empty = True

    # Increment the block_to_play
    block_to_play = (block_to_play + 1) % 65536

while True:
    send_a_block_to_the_player()
    receive_and_feed_the_cluster()

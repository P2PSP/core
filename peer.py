#!/usr/bin/python
# -*- coding: iso-8859-15 -*-

# No solicita retransmisión de bloques perdidos. Avisa al nodo fuente
# de los peers eliminados de la lista de peers. Posee un buffer para
# acomodar el jitter.

import getopt
import sys
import socket
from blocking_socket import blocking_socket
from colors import Color
import struct

IP_ADDR = 0
PORT = 1

source_name = "150.214.150.68"
source_port = 4552
player_port = 9999
peer_port = 0 # OS default behavior will be used

def usage():
    print "This is " + sys.argv[0] + ", the peer node of a P2PSP network"
    print
    print "Parameters (and default values):"
    print
    print " -[-l]listening_port=the port that this peer uses to listen to the player (" + str(player_port) + ")"
    print " -[-p]eer_port=the port that this peer uses to connect to the source (" + str(peer_port) + ", "
    print "               where 0 means that this port will be selected using the OS default behavior)"
    print " -[-s]ource=host name and port of the source node ((" + source_name + ":" + str(source_port) + "))"
    print
    print "Typical usage:"
    print
    print "python peer.py -s 150.214.150.68:4552 -l 9999 &"
    print "  |       |                  |             |"
    print "  |       |                  |             +- Listening port"
    print "  |       |                  +--------------- Source's end-point"
    print "  |       +---------------------------------- The peer code"
    print "  +------------------------------------------ The Python interpreter"
    print
    print "vlc http://localhost:9999"
    print " |          |"
    print " |          +-------------------------------- Peer's end-point"
    print " +------------------------------------------- The VLC player"

opts = ""

try:
    opts, extraparams = getopt.getopt(sys.argv[1:],"l:p:s:h",
                                      ["listening_port=",
                                       "peer_port=",
                                       "server=",
                                       "help"
                                       ])

except getopt.GetoptError, exc:
    sys.stderr.write(sys.argv[0] + ": " + exc.msg + "\n")
    sys.exit(2)

for o, a in opts:
    if o in ("-l", "--listening_port"):
        player_port = int(a)
        print sys.argv[0] + ": listening_port=" + str(player_port)
    if o in ("-p", "--peer_port"):
        peer_port = int(a)
        print sys.argv[0] + ": peer_port=" + str(peer_port)
    if o in ("-s", "--source"):
        source_name = a.split(":")[0]
        source_port = int(a.split(":")[1])
        print sys.argv[0] + ": source=" + "(" + source_name + ":" + str(source_port) + ")" 
    if o in ("-h", "--help"):
	usage()
	sys.exit()

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

if peer_port > 0:
    source_socket = socket.create_connection((source_name, source_port),1000,('',peer_port))
else:
    # Maybe this is redundant
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
    
    #superpeers ip control            
    if peer[0].startswith('127.'):
        peer=(source_socket.getpeername()[IP_ADDR],port)
        
    print source_socket.getsockname(), "<- peer", peer
    peer_list.append(peer)
#    peer_insolidarity[peer] = -32768 # To avoid removing peers during
#                                     # the buffering
    peer_insolidarity[peer] = 0
    number_of_peers -= 1

print source_socket.getsockname(), "<- ", source_socket.getpeername(), "[Video header",
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
stream_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
stream_socket.bind(('',source_socket.getsockname()[PORT]))

# This should create a working entry in the NAT if the peer is in a
# private network
payload = struct.pack("4sH", "aaaa", 0)
for i in xrange(2):
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

counter=0
lastpayload=None
def receive_and_feed_the_cluster():
    global counter
    global lastpayload
    
    try:
        payload, addr = stream_socket.recvfrom(struct.calcsize("H1024s"))
    except socket.timeout:
        sys.stderr.write("Lost connection to the source") 
        sys.exit(-1)
        
    number, block = struct.unpack("H1024s", payload)
    number = socket.ntohs(number)
    '''
    print source_socket.getsockname(),
    if block_buffer[number % buffer_size].requested:
        print Color.red + "<~" + Color.none,
    else:
        print Color.green + "<-" + Color.none, 
    print number, addr
    
    print source_socket.getsockname(),
    print Color.green + "<-" + Color.none,
    print number, addr
    '''
    print "recive from ", addr, " number ", number
    
    if addr == source_socket.getpeername():        
    
        while((counter<len(peer_list))&(counter>0)):
            peer=peer_list[counter]
            '''
            print source_socket.getsockname(), \
                number, Color.green + "->" + Color.none, peer_list[counter], "(", counter+1, "/", len(peer_list),")"
            '''
            stream_socket.sendto(lastpayload, peer)
            peer_insolidarity[peer] += 1
            if peer_insolidarity[peer] > 64: # <- Important parameter!!
                del peer_insolidarity[peer]
                print Color.blue
                print "Removing", peer
                print Color.none
                
                payload = struct.pack("4sH",
                                      socket.inet_aton(peer[IP_ADDR]),
                                      socket.htons(peer[PORT]))
                stream_socket.sendto(payload, source_socket.getpeername())
                peer_list.remove(peer)
            counter += 1
            
        counter=0
        lastpayload=payload
                # Si este paquete se pierde, en principio no ocurre
                # nada porque el o los super-peers van a hacer lo
                # mismo con el nodo fuente y es prácticamente
                # imposible que los mensajes que se envían desde los
                # super-peers hacia el nodo fuente se pierdan (en
                # ancho de banda entre ellos está garantizado).
    else:
        
        if addr not in peer_list:
            peer_list.append(addr)
            
        peer_insolidarity[addr] = 0
        
    if(counter<len(peer_list)): 
        peer=peer_list[counter]
        
        '''
        print source_socket.getsockname(), \
            number, Color.green + "->" + Color.none, peer_list[counter], "(", counter+1, "/", len(peer_list),")"
        '''
        stream_socket.sendto(lastpayload, peer)
        peer_insolidarity[peer] += 1
        if peer_insolidarity[peer] > 64: # <- Important parameter!!
            del peer_insolidarity[peer]
            print Color.blue
            print "Removing", peer
            print Color.none
                        
            payload = struct.pack("4sH",
                                  socket.inet_aton(peer[IP_ADDR]),
                                  socket.htons(peer[PORT]))
            stream_socket.sendto(payload, source_socket.getpeername())
            peer_list.remove(peer)
        counter += 1
        
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
        '''
        print player_serve_socket.getsockname(), \
            block_buffer[block_to_play % buffer_size].number, \
            Color.blue + "=>" + Color.none, \
            player_serve_socket.getpeername()
        '''
        try:
            player_serve_socket.sendall(block_buffer[block_to_play % buffer_size].block)
        except socket.error:
            sys.stderr.write("Conection closed by the player")
            sys.exit(-1)
        
        # buffer[block_to_play.number].empty = True
        block_buffer[block_to_play % buffer_size].empty = True
    #else:
       # print ("------------------------- missing block ---------------------")
    # Increment the block_to_play
    block_to_play = (block_to_play + 1) % 65536

while True:
    send_a_block_to_the_player()
    receive_and_feed_the_cluster()

#!/usr/bin/python -O
# -*- coding: iso-8859-15 -*-

# Recibe bloques desde el splitter y los reenv'ia a resto de peers.

import os
import sys
import socket
import struct
import time
from threading import Thread
from config import Config

IP_ADDR = 0
PORT = 1

buffer_size = Config.buffer_size
peer_port = Config.peer_port
splitter_hostname = Config.splitter_hostname
splitter_port = Config.splitter_port
header_size = Config.header_size
#trusted_peer_port = Config.trusted_peer_port

# Estas cuatro variables las debería indicar el splitter
source_hostname = Config.source_hostname
source_port = Config.source_port
channel = Config.channel
block_size = Config.block_size
block_format_string = Config.block_format_string

trusted_peer_port = splitter_port + 1
I_am_a_trusted_peer = False

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
    source = (source_hostname, source_port)
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

# We need to connecto to the splitter in order to retrieve the list of
# peers and blocks of video.
splitter = (splitter_hostname, splitter_port)
def connect_to_the_splitter(splitter_hostname, splitter_port):
    # {{{

    sock = ''

    try:
        if trusted_peer_port > 0:
            print "Connecting to the splitter at", splitter, "using the port", trusted_peer_port, "..."
            sock = socket.create_connection((splitter_hostname, splitter_port), \
                                       1000,('127.0.0.1',trusted_peer_port))
        else:
            print "Connecting to the splitter ..."
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect(splitter)

        print "Connected to the splitter", splitter, "using", sock.getsockname()
    except:
        sys.exit("Sorry. Can't connect with the splitter at " + str(splitter))
    return sock

    # }}}
splitter_sock = connect_to_the_splitter(splitter_hostname, splitter_port)

# Now, on the same end-point than splitter_sock, we create a UDP
# socket to communicate with the peers.
def create_cluster_sock():
    # {{{

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # In Windows systems this call doesn't work!
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    except:
        pass
    #sock.bind(('',splitter_sock.getsockname()[PORT]))
    sock.bind(('', splitter_port))
    return sock

   # }}}
cluster_sock = create_cluster_sock()
cluster_sock.settimeout(Config.cluster_timeout) # This is the maximum
                                                # time the peer will
                                                # wait for a block
                                                # (from the splitter
                                                # or from another
                                                # peer).

print "Joining to the cluster ..."
sys.stdout.flush()

# This is the list of peers of the cluster. Each peer uses this
# structure to resend the blocks received from the splitter to these
# nodes.
peer_list = []

# This store the insolidarity/unreliability of the peers of the
# cluster. When the insolidarity exceed a threshold, the peer is
# deleted from the list of peers.
unreliability = {}

# The list of peers is retrieved from the splitter in a different
# thread because in this way, if the retrieving takes a long time, the
# peer can receive the blocks that other peers are sending to it.
class retrieve_the_list_of_peers(Thread):
    # {{{

    def __init__(self):
        Thread.__init__(self)

    def run(self):

        # Request the list of peers
        print splitter_sock.getsockname(), \
            '->', splitter_sock.getpeername(), \
            'Requesting the list of peers'

        number_of_peers = socket.ntohs(\
            struct.unpack("H",splitter_sock.recv(struct.calcsize("H")))[0])

        print splitter_sock.getpeername(), \
            '->', splitter_sock.getsockname(), \
            'The number of peers is:', number_of_peers

        while number_of_peers > 0:
            message = splitter_sock.recv(struct.calcsize("4sH"))
            IP_addr, port = struct.unpack("4sH", message)
            IP_addr = socket.inet_ntoa(IP_addr)
            port = socket.ntohs(port)
            peer = (IP_addr, port)
            if peer != splitter_sock.getsockname():
                peer_list.append(peer)
                unreliability[peer] = 0

                # Say hello to the peer
                cluster_sock.sendto('', peer) # Send a empty block (this
                                              # should be fast).
            else:
                I_am_a_trusted_peer = True

            number_of_peers -= 1

            print splitter_sock.getsockname(), \
                '->', splitter_sock.getpeername(), \
                'Received peer', peer

    # }}}
retrieve_the_list_of_peers().start()

# Now it is time to define the buffer of blocks, a structure that is used
# to delay the playback of the blocks in order to accommodate the
# network jittter. Two components are needed: (1) the "blocks" buffer
# that stores the received blocks and (2) the "received" buffer that
# stores if a block has been received or not. Notice that each peer
# can use a different buffer_size: the smaller the buffer size, the
# lower start-up time, the higher block-loss ratio. However, for the
# sake of simpliticy, all peers will use the same buffer size.
blocks = [None]*buffer_size
received = [False]*buffer_size
numbers = [0]*buffer_size

def receive_and_feed():
    # {{{

    # This variable holds the last block received from the
    # splitter. It is used below to send the last received block in
    # the congestion avoiding mode. In that mode, the peer sends a
    # block only when it received a block from another peer or om the
    # splitter.
    last = ''

    # Number of times that the last received block has been sent to
    # the cluster. If this counter is smaller than the number of peers
    # in the cluster, the last block must be sent in the burst mode
    # because a new block from the splitter has arrived and the last
    # received block has not been sent to all the peers of the
    # cluster. This can happen when one o more blocks that were routed
    # towards this peer have been lost.
    counter = 0

    try:
        # {{{ Receive and send
        message, sender = cluster_sock.recvfrom(\
            struct.calcsize(block_format_string))
        if len(message) == struct.calcsize(block_format_string):
            # {{{ A video block has been received

            number, block = struct.unpack(block_format_string, message)
            block_number = socket.ntohs(number)

            # Insert the received block into the buffer.
            blocks[block_number % buffer_size] = block
            received[block_number % buffer_size] = True
            numbers[block_number % buffer_size] = block_number

            if sender == splitter:
                # {{{ The burst sending mode.

                # A new block has arrived from the splitter and we
                # must check if the last block was sent fo the rest of
                # peers of the cluster.
                while( (counter > 0) & (counter < len(peer_list)) ):
                    peer = peer_list[counter]
                    cluster_sock.sendto(last, peer)

                    # Each time we send a block to a peer, the
                    # unreliability of that peer is incremented. Each
                    # time we receive a block from a peer, the
                    # unreliability of that peer is decremented.
                    unreliability[peer] += 1

                    # If the unreliability of a peer exceed a
                    # threshold, the peer is removed from the list of
                    # peers.
                    if unreliability[peer] > Config.peer_unreliability_threshold:
                        del unreliability[peer]
                        peer_list.remove(peer)
                        print 'Removing the unsupportive peer', peer
                    counter += 1
                counter = 0
                last = message

               # }}}
            else:
                # {{{ The sender is a peer, check if the peer is new.
                if sender not in peer_list:
                    # The peer is new
                    peer_list.append(sender)
                    unreliability[sender] = 0                
                    print 'Added', sender, 'by data block'
                # }}}
                
            # A new block has arrived and it must be forwarded to the
            # rest of peers of the cluster.
            if counter < len(peer_list):
                # {{{ Send the last block in congestion avoiding mode.
                peer = peer_list[counter]
                cluster_sock.sendto(last, peer)

                unreliability[peer] += 1        
                if unreliability[peer] > Config.peer_unreliability_threshold:
                    del unreliability[peer]
                    peer_list.remove(peer)
                    print 'Removing the unsupportive peer', peer 
                counter += 1        
                # }}}

            return block_number

            # }}}
        else:
            # {{{ A control block has been received
            if sender not in peer_list:
                peer_list.append(sender)
                print 'Added', sender, 'by \"hello\" message'
                unreliability[sender] = 0
            else:
                peer_list.remove(sender)
                print 'Removed', sender, 'by \"goodbye\" message'
            return -1
            # }}}
        # }}}
    except socket.timeout:
        return -2

    # }}}

start_latency = time.time() # Wall time (execution time plus waiting
                            # time).
# {{{ Buffering

# We will send a block to the player when a new block is
# received. Besides, those slots in the buffer that have not been
# filled by a new block will not be send to the player. Moreover,
# blocks can be delayed an unknown time. This means that (due to the
# jitter) after block X, the block X+Y can be received (instead of the
# block X+1). Alike, the block X-Y could follow the block X. Because
# we implement the buffer as a circular queue, in order to minimize
# the probability of a delayed block overwrites a new block that is
# waiting for traveling the player, we wil fill only the half of the
# circular queue.

# Retrieve the first block to play.
block_number = receive_and_feed()

# The receive_and_feed() procedure returns if a packet has been
# received or if a time-out exception has been arised. In the first
# case, the returned value is -1 if the packet contains a
# hello/goodbyte message and in the second one, -2. None of these
# situations inserts a block of video in the buffer and therefore, the
# must be ignored.
while block_number<=0:
    block_number = receive_and_feed()

# The range of the block index uses to be much larger than the buffer
# size. Therefore, a simple hash operation (in the case, the modulo
# operation) has been used. Because we expect that video blocks come
# in order and the blocks are sent to the player also in order, this
# hashing should work fine.
block_to_play = block_number % buffer_size

# Fill up to the half of the buffer.
for x in xrange(buffer_size/2):
    while receive_and_feed()<=0:
        # Again, w discard control messages (hello and goodbye
        # messages).
        pass

# }}}

end_latency = time.time()
latency = end_latency - start_latency
print 'Latency (buffering) =', latency, 'seconds'

player_connected = True

def send_a_block_to_the_player():
    # {{{

    global block_to_play
    global player_sock
    global player_connected

    if not received[block_to_play]:

        # Lets complain to the splitter.
        message = struct.pack("!H", block_to_play)
        cluster_sock.sendto(message, splitter)

    # Ojo, probar a no enviar nada!!!
    try:
        player_sock.sendall(blocks[block_to_play])
        print player_sock.getsockname(), "->", numbers[block_to_play], player_sock.getpeername()
 
    except socket.error:
        print 'Player disconected'
        player_connected = False
        return
    except Exception as detail:
        print 'unhandled exception', detail
        return

    # We have fired the block.
    received[block_to_play] = False

    # }}}

while player_connected:
    
    block_number = receive_and_feed()
    if block_number>=0:
        if (block_number % 256) == 0:
            for i in unreliability:
                unreliability[i] /= 2
        send_a_block_to_the_player()
        block_to_play = (block_to_play + 1) % buffer_size

# The player has gone. Lets do a polite farewell.
print 'No player, goodbye!'
goodbye = ''
cluster_sock.sendto(goodbye, splitter)
for x in xrange(3):
    receive_and_feed()
for peer in peer_list:
    cluster_sock.sendto(goodbye, peer)

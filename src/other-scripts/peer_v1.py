#!/usr/bin/python -O
# -*- coding: iso-8859-15 -*-

# Recibe bloques desde el splitter y los reenv'ia a resto de peers.

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
splitter_hostname = Config.splitter_hostname
splitter_port = Config.splitter_port
header_size = Config.header_size

# Estas cuatro variables las debería indicar el splitter
source_hostname = Config.source_hostname
source_port = Config.source_port
channel = Config.channel
block_size = Config.block_size
block_format_string = Config.block_format_string

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


# COMIENZO DE BUFFERING TIME (incluye acceso al cluster). time.time()
# measures wall time, this means execution time plus waiting time.
print "Joining to the cluster ..."
sys.stdout.flush()
start_latency = time.time()
    
def connect_to_the_splitter():
    # {{{
    
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    splitter = (splitter_hostname, splitter_port)
    sock.connect(splitter)
    return sock

    # }}}
splitter_sock = connect_to_the_splitter()

def create_cluster_sock():
    # {{{

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # In Windows systems this call doesn't work!
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    except:
        pass
    sock.bind(('',splitter_sock.getsockname()[PORT]))
    return sock

   # }}}
cluster_sock = create_cluster_sock()

# This is the maximum time the peer will wait for a block (from the
# splitter or from another peer).
cluster_sock.settimeout(Config.cluster_timeout)

# This is the list of peers of the cluster. Each peer uses this
# structure to resend the blocks received from the splitter to these
# nodes.
peer_list = []

# This store the insolidarity/unreliability of the peers of the
# cluster. When the insolidarity exceed a threshold, the peer is
# deleted from the list of peers.
unreliability = {}

def retrieve_the_list_of_peers():
    # {{{

    print splitter_sock.getsockname(), '->', splitter_sock.getpeername(), 'Requesting the list of peers'

    number_of_peers = socket.ntohs(\
        struct.unpack("H",splitter_sock.recv(struct.calcsize("H")))[0])

    print splitter_sock.getpeername(), '->', splitter_sock.getsockname(), 'The number of peers is:', number_of_peers

    while number_of_peers > 0:
        message = splitter_sock.recv(struct.calcsize("4sH"))
        IP_addr, port = struct.unpack("4sH", message)
        IP_addr = socket.inet_ntoa(IP_addr)
        port = socket.ntohs(port)
        peer = (IP_addr, port)
        peer_list.append(peer)
        unreliability[peer] = 0

        # Say hello to the peer
        cluster_sock.sendto('', peer) # Send a empty block (this
                                      # should be fast).

        number_of_peers -= 1

        print splitter_sock.getsockname(), '->', splitter_sock.getpeername(), 'Received peer', peer

    # }}}

retrieve_the_list_of_peers()
splitter_sock.close()

# In this momment, the rest of peers of the cluster are sending (or
# going to send) blocks to the new peer.

# Now it is time to define the buffer of blocks, a structure that used
# to delay the playback of the blocks in order to accommodate the
# network jittter. Two components are needed: (1) the "blocks" buffer
# that stores the received blocks and (2) the "received" buffer that
# stores if a block has been received or not. Notice that each peer
# can use a different buffer_size: the smaller the buffer size, the
# lower start-up time, the higher block-loss ratio. However, for the
# sake of simpliticy, all peers will use the same buffer size.
blocks = [None]*buffer_size
received = [False]*buffer_size

def receive_and_feed():
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
            # {{{ Received a video block
            number, block = struct.unpack(block_format_string, message)
            block_number = socket.ntohs(number)

            # Insert the received block into the buffer.
            blocks[block_number % buffer_size] = block
            received[block_number % buffer_size] = True

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
                    if unreliability[peer] > peer_unreliability_threshold:
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
                if unreliability[peer] > peer_unreliability_threshold:
                    del unreliability[peer]
                    peer_list.remove(peer)
                    print 'Removing the unsupportive peer', peer 
                counter += 1        
                # }}}

            return block_number
            # }}}
        else:
            # {{{ Received a control block

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

last_block_number = 0
error_counter = 0

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
# buffer (the beginning of the circular queue).
for x in xrange(buffer_size/2): # Fill half buffer
    while receive_and_feed()<=0:
        # We discard control messages (hello and goodbye messages).
        pass

# }}}

# FIN DE BUFFERING TIME
end_latency = time.time()
latency = end_latency - start_latency

print 'Latency (joining to the cluster + buffering) =', latency, 'seconds'

player_connected = True

def send_a_block_to_the_player():
    # {{{

    global block_to_play
    global player_sock
    global player_connected

    if not received[block_to_play]:
        message = struct.pack("!H", block_to_play)
        cluster_sock.sendto(message, splitter)

        if __debug__:
            logger.info(Color.cyan +
                        str(cluster_sock.getsockname()) +
                        ' complaining about lost block ' +
                        str(block_to_play) + Color.none)

        # Parece que la mayoría de los players se sincronizan antes,
        # si en lugar de no enviar nada se envía un bloque vacío,
        # aunque esto habría que probarlo.

    try:
        player_sock.sendall(blocks[block_to_play])

        # {{{ debug
        if __debug__:
            logger.debug('{}'.format(player_sock.getsockname()) +
                         ' ' +
                         str(block_to_play) +
                         ' -> (player) ' +
                         '{}'.format(player_sock.getpeername()))

        # }}}

    except socket.error:
        if __debug__:
            logger.error(Color.red + 'player disconected!' + Color.none)
        player_connected = False
        return
    except Exception as detail:
        if __debug__:
            logger.error(Color.red + 'unhandled exception ' + str(detail) + Color.none)
        return

    received[block_to_play] = False

    # }}}

if __debug__:    
    #get a death time
    #death_time = churn.new_death_time(20)
    death_time = churn.new_death_time(weibull_scale)

'''
#Once the buffer is half-filled, then start operating normally
'''
#while player_connected and not blocks_exhausted:
while player_connected:
    
    if __debug__:
        if churn.time_to_die(death_time):
            break;

    if __debug__ and death_time != churn.NEVER:
        current_time = time.localtime()
        logger.debug(Color.green +
                     'Current time is ' +
                     str(current_time.tm_hour).zfill(2) +
                     ':' +
                     str(current_time.tm_min).zfill(2) +
                     ':' +
                     str(current_time.tm_sec).zfill(2) +
                     Color.none)
        logger.debug(Color.green +
                     'Scheduled death time is ' +
                     str(time.localtime(death_time).tm_hour).zfill(2) +
                     ':' +
                     str(time.localtime(death_time).tm_min).zfill(2) +
                     ':' +
                     str(time.localtime(death_time).tm_sec).zfill(2) +
                     Color.none)
    
    block_number = receive_and_feed()
    if block_number>=0:
        if (block_number % 256) == 0:
            for i in unreliability:
                unreliability[i] /= 2
        if _PLAYER_:
            send_a_block_to_the_player()
            block_to_play = (block_to_play + 1) % buffer_size
    #elif block_number == -2:    #this stops the peer after only one cluster timeout
    #    break
    if __debug__:
        logger.debug('NUM PEERS '+str(len(peer_list)))

print 'No player, goodbye!'
if __debug__:
    logger.info(Color.cyan + 'Goodbye!' + Color.none)
#goodbye = 'bye'
goodbye = ''
cluster_sock.sendto(goodbye, splitter)
for x in xrange(3):
    receive_and_feed()
for peer in peer_list:
    cluster_sock.sendto(goodbye, peer)

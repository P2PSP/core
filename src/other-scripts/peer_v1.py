#!/usr/bin/python -O
# -*- coding: iso-8859-15 -*-

# Recibe bloques desde el splitter y los reenv'ia a resto de peers.

# Problemas:
# 1. Los goodbyes no llegan al splitter.
# 2. Los nuevos peers no pueden contactar con los antiguos a causa del NAT.

# {{{ Imports

import os
import sys
import socket
import struct
import time
import argparse
from threading import Thread
#from config import Config
from color import Color

# }}}

print "Peer running in",
if __debug__:
    print "debug mode"
else:
    print "release mode"

IP_ADDR = 0
PORT = 1

peer_unreliability_threshold = 12800

# {{{ Args parsing

parser = argparse.ArgumentParser(
    description='This is a peer node of a P2PSP network.')

player_port = 9999
parser.add_argument('--player_port',
                    help='Port used to communicate with the player.\
 (Default = {})'.format(player_port))

#splitter_host = "127.0.0.1" # Don't use "localhost"
splitter_host = "150.214.150.68"
#splitter_host = "192.168.1.137"
parser.add_argument('--splitter_host',
                    help='Host of the splitter.\
 (Default = {})'.format(splitter_host))

splitter_port = 4552
parser.add_argument('--splitter_port',
                    help='Listening port of the splitter.\
 (Default = {})'.format(splitter_port))

cluster_port = 0
# Port that the peer uses to communicate the cluster. 0 means that, by
# default, the peer uses the port that the OS will select as a typical
# client application.
parser.add_argument('--cluster_port',
                    help='The local port that this peer uses\
 to communcate to the cluster. (Default = {})'.format(cluster_port))

args = parser.parse_known_args()[0]
if args.player_port:
    player_port = int(args.player_port)
if args.splitter_host:
    splitter_host = socket.gethostbyname(args.splitter_host)
if args.splitter_port:
    splitter_port = int(args.splitter_port)
if args.cluster_port:
    cluster_port = int(args.cluster_port)

# }}}

def get_player_socket():
    # {{{

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    try:
        # In Windows systems this call doesn't work!
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    except:
        pass
    sock.bind(('', player_port))
    sock.listen(0)

    print sock.getsockname(), "\b: waiting for the player ..."

    sock, player = sock.accept()
    #sock.setblocking(0)

    print sock.getsockname(), "\b: the player is", sock.getpeername()

    return sock

    # }}}

# The peer is blocked until the player establish a connection.
player_sock = get_player_socket() 

# We need to connect to the splitter in order to retrieve
# configuration information, the list of peers and chunks of video.
splitter = (splitter_host, splitter_port)
def connect_to_the_splitter(splitter_host, splitter_port):
    # {{{

    #sock = ''

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print sock.getsockname(), "\b: connecting to the splitter at", splitter
    if cluster_port != 0:
        #sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind(("", cluster_port))
        #print "hola"
        #sock.bind(("192.168.1.130", cluster_port))
        #sock.bind((splitter_host, cluster_port))
        #sock.bind((source_sock.getsockname()[0], cluster_port))
    try:
        sock.connect(splitter)
    except:
        sys.exit("Sorry. Can't connect to the splitter at " + str(splitter))
    print sock.getsockname(), "\b: connected to the splitter at", splitter
    return sock

    # }}}
splitter_socket = connect_to_the_splitter(splitter_host, splitter_port)

# Now, on the same end-point than splitter_socket, we create a UDP
# socket to communicate with the peers.
def create_cluster_socket():
    # {{{

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # In Windows systems this call doesn't work!
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    except:
        pass
    sock.bind(('',splitter_socket.getsockname()[PORT]))
    return sock

   # }}}
cluster_socket = create_cluster_socket()

# This is the maximum time the peer will
# wait for a chunk (from the splitter or from another peer).
cluster_socket.settimeout(1) 

#print cluster_socket.getsockname(), "\b: joining to the cluster ..."
#sys.stdout.flush()

# This is the list of peers of the cluster. Each peer uses this
# structure to resend the chunks received from the splitter to these
# nodes.
peer_list = []

# This store the insolidarity/unreliability of the peers of the
# cluster. When the insolidarity exceed a threshold, the peer is
# deleted from the list of peers.
unreliability = {}

# The list of peers is retrieved from the splitter in a different
# thread because in this way, if the retrieving takes a long time, the
# peer can receive the chunks that other peers are sending to it.
class retrieve_the_list_of_peers(Thread):
    # {{{

    def __init__(self):
        Thread.__init__(self)

    def run(self):

        # Request the list of peers.
        sys.stdout.write(Color.green)
        print splitter_socket.getsockname(), "\b: requesting the list of peers to", splitter_socket.getpeername()

        number_of_peers = socket.ntohs(struct.unpack("H",splitter_socket.recv(struct.calcsize("H")))[0])

        print splitter_socket.getpeername(), "\b: the size of the list of peers is", number_of_peers

        while number_of_peers > 0:
            message = splitter_socket.recv(struct.calcsize("4sH"))
            IP_addr, port = struct.unpack("4sH", message)
            IP_addr = socket.inet_ntoa(IP_addr)
            port = socket.ntohs(port)
            peer = (IP_addr, port)

            print "[%5d]" % number_of_peers, peer

            peer_list.append(peer)
            unreliability[peer] = 0
            #print Color.green, cluster_socket.getsockname(), \
            #    "-", '"hello"', "->", peer, Color.none
            # Say hello to the peer
            cluster_socket.sendto('', peer) # Send a empty chunk (this
                                          # should be fast).
            number_of_peers -= 1

        print 'done'
        sys.stdout.write(Color.none)

    # }}}

# Receive from the splitter the IP address of the source node.
message = splitter_socket.recv(struct.calcsize("4s"))
source_host = struct.unpack("4s", message)[0]
source_host = socket.inet_ntoa(source_host)
print splitter_socket.getpeername(), "\b: source_host =", source_host

# Receive from the splitter the port of the source node.
message = splitter_socket.recv(struct.calcsize("H"))
source_port = struct.unpack("H", message)[0]
source_port = socket.ntohs(source_port)
print splitter_socket.getpeername(), "\b: source_port =", source_port

# Rececive from the splitter the channel name.
message = splitter_socket.recv(struct.calcsize("H"))
channel_size = struct.unpack("H", message)[0]
channel_size = socket.ntohs(channel_size)
channel = splitter_socket.recv(channel_size)
print splitter_socket.getpeername(), "\b: channel =", channel

# Receive from the splitter the buffer size.
message = splitter_socket.recv(struct.calcsize("H"))
buffer_size = struct.unpack("H", message)[0]
buffer_size = socket.ntohs(buffer_size)
print splitter_socket.getpeername(), "\b: buffer_size =", buffer_size

# Receive fron the splitter the chunk size.
message = splitter_socket.recv(struct.calcsize("H"))
chunk_size = struct.unpack("H", message)[0]
chunk_size = socket.ntohs(chunk_size)
print splitter_socket.getpeername(), "\b: chunk_size =", chunk_size

retrieve_the_list_of_peers().start()

#payload = struct.pack("4sH", "0.0.0.0", 0)
#cluster_socket.sendto(payload, splitter)
message = struct.pack("!H", 0)
cluster_socket.sendto(message, splitter)

# The video header is requested directly to the source node, mainly,
# because in a concatenation of videos served by the source each video
# has a different header (another reason is that part of the load is
# translated from the splitter to the source, which can also perform
# managing operations such as collecting statistics about the
# peers). This implies that, if the header of the currently streamed
# video is served by the splitter, it must be aware of the end of a
# video and the start of the next, and record the header to serve it
# to the peers. Notice that, only the header of the first recived
# video is transmitted over the TCP. The headers of the rest of videos
# of the received sequence is transmitted over the UDP. It is
# expectable that, if one of these headers are corrupted by
# transmission errors, the users will manually restart the conection
# with the streaming service, using again the TCP.

def get_source_socket():
    source_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    source = (source_host, source_port)
    print source_socket.getsockname(), "\b: connecting to the source at", source, "..."
    sys.stdout.flush()
    source_socket.connect(source)
    print source_socket.getsockname(), "\b: connected to", source
    return source_socket

source_sock = get_source_socket()

def communicate_the_header():
    # {{{ 

    GET_message = 'GET ' + channel + ' HTTP/1.1\r\n'
    GET_message += '\r\n'
    source_sock.sendall(GET_message)

    print source_sock.getsockname(), "\b: requesting the stream header via http://" + str(source_sock.getpeername()[0]) + ':' + str(source_sock.getpeername()[1]) + str(channel)
    # {{{ Receive the video header from the source and send it to the player

    # Nota: este proceso puede fallar si durante la recepción de los
    # bloques el stream se acaba. Habría que realizar de nuevo la
    # petición HTTP (como hace el servidor).

    # Esta(s) variable(s) la(s) deberia determinar el peer
    header_size = 1024*100

    received = 0
    data = ""

    while received < header_size:
        data = source_sock.recv(header_size - received)
        received += len(data)
        try:
            player_sock.sendall(data)
        except:
            print "error sending data to the player"
            print "len(data) =", len(data)
        print "received bytes:", received, "\r",
    '''
    data = source_sock.recv(header_size)
    total_received = len(data)
    player_sock.sendall(data)
    while total_received < header_size:
        data = source_sock.recv(header_size - len(data))
        player_sock.sendall(data)
        total_received += len(data)
        print "received bytes:", total_received, "\r",
    '''
    # }}}

    print source_sock.getsockname(), '\b: sent', received, 'bytes'


    # }}}
communicate_the_header() # Retrieve the header of the stream from the
                         # source and send it to the player.
source_sock.close()

# Now it is time to define the buffer of chunks, a structure that is used
# to delay the playback of the chunks in order to accommodate the
# network jittter. Two components are needed: (1) the "chunks" buffer
# that stores the received chunks and (2) the "received" buffer that
# stores if a chunk has been received or not. Notice that each peer
# can use a different buffer_size: the smaller the buffer size, the
# lower start-up time, the higher chunk-loss ratio. However, for the
# sake of simpliticy, all peers will use the same buffer size.
chunks = [None]*buffer_size
received = [True]*buffer_size
numbers = [0]*buffer_size
for i in xrange(0, buffer_size):
    numbers[i] = i

total_chunks = 0L

# This variable holds the last chunk received from the
# splitter. It is used below to send the last received chunk in
# the congestion avoiding mode. In that mode, the peer sends a
# chunk only when it received a chunk from another peer or om the
# splitter.
last = ''

# Number of times that the last received chunk has been sent to
# the cluster. If this counter is smaller than the number of peers
# in the cluster, the last chunk must be sent in the burst mode
# because a new chunk from the splitter has arrived and the last
# received chunk has not been sent to all the peers of the
# cluster. This can happen when one o more chunks that were routed
# towards this peer have been lost.
counter = 0

def receive_and_feed():
    # {{{

    global total_chunks
    global last
    global counter

    try:
        chunk_format_string = "H" + str(chunk_size) + "s"

        # {{{ Receive and send
        message, sender = cluster_socket.recvfrom(\
            struct.calcsize(chunk_format_string))
        if __debug__:
            print Color.cyan, "Received a message from", sender, \
                "of length", len(message), Color.none
        if len(message) == struct.calcsize(chunk_format_string):
            # {{{ A video chunk has been received

            number, chunk = struct.unpack(chunk_format_string, message)
            chunk_number = socket.ntohs(number)

            total_chunks += 1

            # Insert the received chunk into the buffer.
            chunks[chunk_number % buffer_size] = chunk
            received[chunk_number % buffer_size] = True
            numbers[chunk_number % buffer_size] = chunk_number

            if sender == splitter:
                # {{{ Send the last chunk in burst sending mode

                if __debug__:
                    print cluster_socket.getsockname(), \
                        Color.red, "<-", Color.none, chunk_number, "-", sender

                # A new chunk has arrived from the splitter and we
                # must check if the last chunk was sent fo the rest of
                # peers of the cluster.
                while( (counter < len(peer_list)) and (counter > 0) ):
                    peer = peer_list[counter]
                    cluster_socket.sendto(last, peer)
                    if __debug__:
                        print cluster_socket.getsockname(), "-", chunk_number, \
                            Color.green, "->", Color.none, peer

                    # Each time we send a chunk to a peer, the
                    # unreliability of that peer is incremented. Each
                    # time we receive a chunk from a peer, the
                    # unreliability of that peer is decremented.
                    unreliability[peer] += 1

                    # If the unreliability of a peer exceed a
                    # threshold, the peer is removed from the list of
                    # peers.
                    if unreliability[peer] > peer_unreliability_threshold:
                        sys.stdout.write(Color.red)
                        print 'removing the unsupportive peer', peer
                        sys.stdout.write(Color.none)
                        del unreliability[peer]
                        peer_list.remove(peer)
                    counter += 1
                counter = 0
                last = message

               # }}}
            else:
                # {{{ The sender is a peer, check if the peer is new.

                if __debug__:
                    print cluster_socket.getsockname(), \
                        Color.green, "<-", Color.none, chunk_number, "-", sender

                if sender not in peer_list:
                    # The peer is new
                    peer_list.append(sender)
                    unreliability[sender] = 0                
                    print Color.green, sender, 'added by data chunk', \
                        chunk_number, Color.none
                else:
                    unreliability[sender] -= 1;
                    if unreliability[sender] < 0:
                        unreliability[sender] = 0

                # }}}
                
            # A new chunk has arrived and it must be forwarded to the
            # rest of peers of the cluster.
            if ( counter < len(peer_list) and ( last != '') ):
                # {{{ Send the last chunk in congestion avoiding mode.

                peer = peer_list[counter]
                cluster_socket.sendto(last, peer)
                if __debug__:
                    print cluster_socket.getsockname(), "-", chunk_number,\
                        Color.green, "->", Color.none, peer

                unreliability[peer] += 1        
                if unreliability[peer] > peer_unreliability_threshold:
                    sys.stdout.write(Color.red)
                    print peer, 'Removed by unsupportive', "(unreliability[", "\b", peer, "\b] = ", unreliability[peer], ">", peer_unreliability_threshold
                    sys.stdout.write(Color.none)  
                    del unreliability[peer]
                    peer_list.remove(peer)
                counter += 1        

                # }}}

            return chunk_number

            # }}}
        else:
            # {{{ A control chunk has been received

            if sender not in peer_list:
                print Color.green, sender, 'added by \"hello\" message', Color.none
                peer_list.append(sender)
                unreliability[sender] = 0
            else:
                sys.stdout.write(Color.red)
                print cluster_socket.getsockname(), '\b: received "goodbye" from', sender
                sys.stdout.write(Color.none)
                peer_list.remove(sender)
            return -1

            # }}}
        # }}}
    except socket.timeout:
        return -2

    # }}}

start_latency = time.time() # Wall time (execution time plus waiting
                            # time).
# {{{ Buffering

# We will send a chunk to the player when a new chunk is
# received. Besides, those slots in the buffer that have not been
# filled by a new chunk will not be send to the player. Moreover,
# chunks can be delayed an unknown time. This means that (due to the
# jitter) after chunk X, the chunk X+Y can be received (instead of the
# chunk X+1). Alike, the chunk X-Y could follow the chunk X. Because
# we implement the buffer as a circular queue, in order to minimize
# the probability of a delayed chunk overwrites a new chunk that is
# waiting for traveling the player, we wil fill only the half of the
# circular queue.

print cluster_socket.getsockname(), "\b: buffering ",
sys.stdout.flush()

# Retrieve the first chunk to play.
#print "Primer receive_and_feed"
chunk_number = receive_and_feed()
#print chunk_number,
#sys.stdout.flush()

# The receive_and_feed() procedure returns if a packet has been
# received or if a time-out exception has been arised. In the first
# case, the returned value is -1 if the packet contains a
# hello/goodbyte message or a number >= 0 if a chunk has been
# received. A -2 is returned if a time-out is has happened.
while chunk_number < 0:
    #print "Segundos receive_and_feed"
    chunk_number = receive_and_feed()
    #print chunk_number,
    #sys.stdout.flush()

#print "------------------>", chunk_number

# In this moment, the variable chunk_number stores the first chunk to
# be sent to the player. Notice that the range of the chunk index uses
# to be much larger than the buffer size. Therefore, a simple hash
# operation (in the case, the modulo operation) has been used. Because
# we expect that video chunks come in order and the chunks are sent to
# the player also in order, this hashing should work fine.
chunk_to_play = chunk_number % buffer_size

# Fill up to the half of the buffer.
for x in xrange(buffer_size/2):
    print "\b.",
    sys.stdout.flush()
    #print "Terceros receive_and_feed", x, buffer_size/2
    while receive_and_feed()<=0:
        #print "Terceros receive_and_feed < 0"
        #print "\bo",
        #sys.stdout.flush()
        # Again, discard control messages (hello and goodbye
        # messages).
        pass

# }}}

end_latency = time.time()
latency = end_latency - start_latency
print 'latency =', latency, 'seconds'

# This is used to stop the child threads. They will be alive only
# while the main thread is alive.
main_alive = True

if not __debug__:
    kbps = 0
    class print_info(Thread):
        # {{{

        def __init__(self):
            Thread.__init__(self)

        def run(self):
            global kbps
            #global total_chunks
            last_total_chunks = 0
            while main_alive:
                print "[%3d] " % len(peer_list),
                kbps = (total_chunks - last_total_chunks) * \
                    chunk_size * 8/1000
                last_total_chunks = total_chunks
                '''
                print "#\tPeer\tUnreliability\t% loss"
                counter = 0
                for p in peer_list:
                    loss_percentage = float(unreliability[p]*100)/float(total_chunks)
                    print counter, '\t', p, '\t', unreliability[p], \
                        ' ({:.2}%)'.format(loss_percentage)
                    counter += 1
                '''
                #print '\r', "%8d" % total_chunks, "chunks/s,", "%8d kbps." % kbps,
                for x in xrange(0,kbps/10):
                    print "\b#",
                print kbps, "kbps"

                time.sleep(1)

        # }}}
    print_info().start()

player_connected = True

def send_a_chunk_to_the_player():
    # {{{

    global chunk_to_play
    global player_sock
    global player_connected

    if not received[chunk_to_play]:

        # Lets complain to the splitter.
        message = struct.pack("!H", chunk_to_play)
        cluster_socket.sendto(message, splitter)

        sys.stdout.write(Color.blue)
        print "lost chunk:", numbers[chunk_to_play]
        sys.stdout.write(Color.none)

    # Ojo, probar a no enviar nada!!!
    try:
        player_sock.sendall(chunks[chunk_to_play])
        #print player_sock.getsockname(), "->", numbers[chunk_to_play], player_sock.getpeername(), '\r',
    except socket.error:
        print 'Player disconected, ...',
        player_connected = False
        return
    finally:
        print "finally"
        return
    # We have fired the chunk.
    received[chunk_to_play] = False

    # }}}

while player_connected:
    try:
        chunk_number = receive_and_feed()
        if chunk_number>=0:
            if (chunk_number % 256) == 0:
                for i in unreliability:
                    unreliability[i] /= 2
            send_a_chunk_to_the_player()
            chunk_to_play = (chunk_to_play + 1) % buffer_size

    except KeyboardInterrupt:
        # Say to the daemon threads that the work has been finished,
        main_alive = False
        sys.exit('Keyboard interrupt detected ... Exiting!')

# The player has gone. Lets do a polite farewell.
main_alive = False
print 'goodbye!'
goodbye = ''
cluster_socket.sendto(goodbye, splitter)
print '"goodbye" message sent to the splitter', splitter
for x in xrange(3):
    receive_and_feed()
for peer in peer_list:
    cluster_socket.sendto(goodbye, peer)

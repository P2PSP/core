#!/usr/bin/python -O

# Recibe un stream y lo sirve v'ia UDP. Posee hilos de gesti'on del
# cluster.

# {{{ Imports

import time
import sys
import socket
from threading import Thread
import struct
#from config import Config
from color import Color
import argparse

# }}}
print "Splitter running in",
if __debug__:
    print "debug mode"
else:
    print "release mode"

# {{{ Args parsing

parser = argparse.ArgumentParser(
    description='This is the splitter node of a P2PSP network.')

source_host = "150.214.150.68"
parser.add_argument('--source_host',
                    help='The streaming server.\
 (Default = "{}")'.format(source_host))

source_port = 4551
parser.add_argument('--source_port',
                    help='Port where the streaming server is listening.\
 (Default = {})'.format(source_port))

channel = '134.ogg'
#channel = '480.ogg'
parser.add_argument('--channel',
                    help='Name of the channel served by the streaming source.\
 (Default = "{}")'.format(channel))

listening_host = "127.0.0.1"
parser.add_argument('--listening_host',
                    help='IP address to talk with the peers.\
 (Default = {})'.format(listening_host))

listening_port = 4552
parser.add_argument('--listening_port',
                    help='Port to talk with the peers.\
 (Default = {})'.format(listening_port))

# The buffer_size depends on the stream bit-rate and the maximun
# latency experimented by the users, and should be transmitted to the
# peers. The buffer_size is proportional to the bit-rate and the
# latency is proportional to the buffer_size.
buffer_size = 256
parser.add_argument('--buffer_size',
                    help='size of the video buffer in blocks.\
 (Default = {})'.format(buffer_size))

# The chunk_size depends mainly on the network technology and should
# be selected as big as possible, depending on the MTU and the
# bit-error rate.
chunk_size = 1024
parser.add_argument('--chunk_size',
                    help='Chunk size in bytes.\
 (Default = {})'.format(chunk_size))

args = parser.parse_known_args()[0]
if args.source_host:
    source_host = args.source_host
if args.source_port:
    source_port = int(args.source_port)
if args.channel:
    channel = args.channel
if args.listening_host:
    listening_host = args.listening_host
if args.listening_port:
    listening_port = int(args.listening_port)
if args.buffer_size:
    buffer_size = int(args.buffer_size)
if args.chunk_size:
    chunk_size = int(args.chunk_size)

# }}}

def get_peer_connection_socket():
    # {{{

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        # This does not work in Windows systems.
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    except:
        pass

    sock.bind((listening_host, listening_port))
    #sock.listen(5)
    sock.listen(socket.SOMAXCONN)   # Set the connection queue to the max!

    return sock

    # }}}
# Socket to manage the cluster (churn).
peer_connection_sock = get_peer_connection_socket()

def create_cluster_sock(listening_port):
    # {{{ 
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # This does not work in Windows systems !!
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    except:
        pass
    sock.bind((listening_host, listening_port))
    #peer_socket.bind(('',peer_connection_sock.getsockname()[PORT]))

    return sock
    # }}}
# Socket to send the media to the cluster.
cluster_sock = create_cluster_sock(listening_port)

# The list of peers in the cluster. There will be always a peer in the
# list of peers that, by default, is running in the same host than the
# splitter, listening to the port listening_port+1. Notice that you
# can replace this end-point by any other you want, for example, in a
# different host.
#peer_list = [('127.0.0.1',listening_port+1)]
peer_list = []

# Destination peers of the chunk, indexed by a chunk number. Used to
# find the peer to which a chunk has been sent.
destination_of_chunk = [('0.0.0.0',0) for i in xrange(buffer_size)]

# Unreliaility of the peers, indexed by (the end-point of) the
# peer. Counts the number of times a peer has not re-transmitted a
# packet.
unreliability = {}
#unreliability[('127.0.0.1',listening_port+1)] = 0

# Complaining rate of a peer. Sometimes the complaining peer has not
# enough bandwidth in his download link. In this case, the peevish
# peers should be rejected from the cluster.
complains = {}
#complains[('127.0.0.1',listening_port+1)] = 0

# Useful definitions.
IP_ADDR = 0
PORT = 1

# This is used to stop the child threads. They will be alive only
# while the main thread is alive.
main_alive = True

def arrival_handler(peer_serve_socket, peer, peer_list, unreliability):
    # {{{

    print Color.green, peer_serve_socket.getsockname(), \
        'accepted connection from peer', \
        peer

    # Send the source node IP address.
    message = struct.pack("4s", socket.inet_aton(source_host))
    peer_serve_socket.sendall(message)

    # Send the source node listening port.
    message = struct.pack("H", socket.htons(source_port))
    peer_serve_socket.sendall(message)

    # Send the name of the channel.
    message = struct.pack("H", socket.htons(len(channel)))    
    peer_serve_socket.sendall(message)
    peer_serve_socket.sendall(channel)

    # Send the buffer size.
    message = struct.pack("H", socket.htons(buffer_size))
    peer_serve_socket.sendall(message)

    # Send the chunk size.
    message = struct.pack("H", socket.htons(chunk_size))
    peer_serve_socket.sendall(message)

    print peer_serve_socket.getsockname(), \
        'sending the list of peers ...'

    # Sends the size of the list of peers.
    message = struct.pack("H", socket.htons(len(peer_list)))
    peer_serve_socket.sendall(message)

    # Send the list of peers.
    counter = 1
    for p in peer_list:
        message = struct.pack(
            "4sH", socket.inet_aton(p[IP_ADDR]),
            socket.htons(p[PORT]))
        peer_serve_socket.sendall(message)
        print "%5d" % counter, p

    print 'done', Color.none

    peer_serve_socket.close()
    peer_list.append(peer)
    unreliability[peer] = 0
    complains[peer] = 0

    # }}}

# The fist peer that contacts the splitter is a "monitor" peer that
# the cluster administrator can use to monitorize the performance of
# the streaming. This peer MUST run on the same host than the splitter
# to avoid bandwidth consumption and usually listen to the port
# splitter_port+1 (although this is configurable by the administrator
# selecting a different peer_port). This peer MUST also use the same
# public IP address that the splitter in order the rest of peers of
# the cluster communicate with it. The splitter will use its public IP
# address as the IP address of the monitor peer.
def wait_for_the_monitor_peer(peer_connection_sock, peer_list, unreliability):
    # {{{

    print peer_connection_sock.getsockname(),\
        "waiting for the monitor peer ..."
    sys.stdout.flush()
    peer_serve_socket, peer = peer_connection_sock.accept()
    print peer_serve_socket.getsockname(), "the monitor peer is", \
        peer_serve_socket.getpeername()

    peer = (listening_host, peer[1])
    arrival_handler(peer_serve_socket, peer, peer_list, unreliability)

    # }}}

wait_for_the_monitor_peer(peer_connection_sock, peer_list, unreliability)

# When a peer want to join a cluster, first it must establish a TCP
# connection with the splitter. In that connection, the splitter sends
# to the incomming peer the list of peers. Notice that the
# transmission of the list of peers (something that could need some
# time if the cluster is big or the peer is slow) is done in a
# separate thread. This helps to avoid a DoS (Denial-of-Service)
# attack.

# Handle the arrival of a peer.
class handle_one_arrival(Thread):
    # {{{

    peer_serve_socket = ""
    peer = ""
    
    def __init__(self, peer_serve_socket, peer):
        Thread.__init__(self)
        self.peer_serve_socket = peer_serve_socket
        self.peer = peer
        
    def run(self):
        global peer_list
        global unreliability

        if self.peer not in peer_list:
            arrival_handler(self.peer_serve_socket, self.peer, peer_list, unreliability)
            '''
        print self.peer_serve_socket.getsockname(), \
            'Accepted connection from peer', \
            self.peer

        print self.peer_serve_socket.getsockname(), \
            'sending the list of peers ...'

        # Sends the size of the list of peers.
        message = struct.pack("H", socket.htons(len(peer_list)))
        self.peer_serve_socket.sendall(message)

        # Send the list of peers.
        counter = 1
        for p in peer_list:
            message = struct.pack(
                "4sH", socket.inet_aton(p[IP_ADDR]),
                socket.htons(p[PORT]))
            self.peer_serve_socket.sendall(message)
            print "%5d" % counter, p

        print 'done'

        if self.peer not in peer_list:
            self.peer_serve_socket.close()
            peer_list.append(self.peer)
            unreliability[self.peer] = 0
            complains[self.peer] = 0
            '''
    # }}}

# The daemon which runs the "handle_one_arrival" threads. 
class handle_arrivals(Thread):
    # {{{

    def __init__(self):
        Thread.__init__(self)

    def run(self):
        print peer_connection_sock.getsockname(), "waiting for normal peers ..." 
        while main_alive:
            peer_serve_socket, peer = peer_connection_sock.accept()
            #if peer not in peer_list: # Puede que sobre
            handle_one_arrival(peer_serve_socket, peer).start()

    # }}}
handle_arrivals().start()

peer_index = 0

# A new daemon to administrate the cluster.
class listen_to_the_cluster(Thread):
    # {{{

    def __init__(self):
        Thread.__init__(self)

    def run(self):

        global peer_index

        print cluster_sock.getsockname(), "listening to the cluster ...", 
        while main_alive:
            # {{{

            # Peers complain about lost chunks, and a chunk index is
            # stored in a "H" (unsigned short) register.
            message, sender = cluster_sock.recvfrom(struct.calcsize("H"))

            # However, sometimes peers only want to exit. In this case,
            # they send a UDP datagram to the splitter with a
            # zero-length payload.
            if len(message) == 0:
                # An empty message is a goodbye message.
                if sender != peer_list[0]:
                    try:
                        peer_index -= 1
                        peer_list.remove(sender)
                        print Color.red, sender, 'removed by "goodbye" \
message', Color.none
                    except:
                        # Received a googbye message from a peer which is
                        # not in the list of peers.
                        pass
            else:
                # The sender of the packet complains, and the packet
                # comes with the index of a lost (non-received)
                # chunk. In this situation, the splitter counts the
                # number of times a peer has not achieved to send a
                # chunk to other peers. If this number exceeds a
                # threshold, the unsupportive peer is expelled from
                # the cluster. Moreover, if we receive too much
                # complains from the same peer, the problem could be
                # in that peer and it will be expelled from the
                # cluster.
                lost_chunk = struct.unpack("!H",message)[0]
                destination = destination_of_chunk[lost_chunk]
                print Color.blue, sender, \
                    'complains about lost chunk', lost_chunk, \
                    'sent to', destination, Color.none
                try:
                    unreliability[destination] += 1
                except:
                    print "the unsupportive peer does not exit"
                    pass
                else:
                    print Color.blue, "complains about", destination, \
                        "=", unreliability[destination], Color.none
                    if unreliability[destination] > 8:
                        print Color.red, 'too much complains about\
 unsupportive peer', \
                            destination, Color.none
                        peer_index -= 1
                        peer_list.remove(destination)
                        del unreliability[destination]
                        del complains[destination]

                if sender != peer_list[0]:
                    try:
                        complains[sender] += 1
                    except:
                        print "the complaining peer does not exit"
                        pass
                    else:
                        if complains[sender] > 8:
                            print Color.red, 'too much complains of a peevish peer', \
                                sender, Color.none
                            peer_index -= 1
                            peer_list.remove(sender)
                            del complains[sender]
                            del unreliability[sender]
            # }}}

    # }}}
listen_to_the_cluster().start()

chunk_number = 0
if not __debug__:

    kbps = 0
    class print_info(Thread):
        # {{{

        def __init__(self):
            Thread.__init__(self)

        def run(self):
            global kbps
            last_chunk_number = 0
            while main_alive:
                kbps = (chunk_number - last_chunk_number) * \
                    chunk_size * 8/1000
                last_chunk_number = chunk_number

                for x in xrange(0,kbps/10):
                    print "\b#",
                print kbps, "kbps", len(peer_list), "peers"

                time.sleep(1)

        # }}}
    print_info().start()

source = (source_host, source_port)
source_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
print source_sock.getsockname(), 'connecting to the source', source, '...'

source_sock.connect(source)

print source_sock.getsockname(), 'connected to', source

GET_message = 'GET /' + channel + ' HTTP/1.1\r\n'
GET_message += '\r\n'
source_sock.sendall(GET_message)

chunk_format_string = "H" + str(chunk_size) + "s" # "H1024s

# This is the main loop of the splitter
while True:
    try:
        # Receive data from the source
        def receive_next_chunk():
            global source_sock
            chunk = source_sock.recv(chunk_size)
            prev_chunk_size = 0
            while len(chunk) < chunk_size:
                if len(chunk) == prev_chunk_size:
                    print '\b!',
                    sys.stdout.flush()
                    time.sleep(1)
                    source_sock.close()
                    source_sock = socket.socket(socket.AF_INET,
                                                socket.SOCK_STREAM)
                    source_sock.connect(source)
                    source_sock.sendall(GET_message)
                prev_chunk_size = len(chunk)
                chunk += source_sock.recv(chunk_size - len(chunk))
            return chunk
        chunk = receive_next_chunk()
        chunk_number = (chunk_number + 1) % 65536

        # Send the chunk.
        '''
        try:
            peer = peer_list[peer_index]
        except:
            print "La lista de peers est'a vac'ia!!!"
        else:
            peer = peer_list[0]
        '''
        peer = peer_list[peer_index]
        message = struct.pack(chunk_format_string,
                              socket.htons(chunk_number),
                              chunk)
        cluster_sock.sendto(message, peer)
        destination_of_chunk[chunk_number % buffer_size] = peer
        peer_index = (peer_index + 1) % len(peer_list)

        # Decrement (dividing by 2) unreliability and complains after
        # every 256 sent chunks.
        if (chunk_number % 256) == 0:
            for i in unreliability:
                unreliability[i] /= 2
            for i in complains:
                complains[i] /= 2

        if __debug__:
            print '%5d' % chunk_number, Color.red, '->', Color.none, peer
            sys.stdout.flush()

    except KeyboardInterrupt:
        print 'Keyboard interrupt detected ... Exiting!'

        # Say to the daemon threads that the work has been finished,
        main_alive = False

        # Wake up the "listen_to_the_cluster" daemon, which is waiting
        # in a cluster_sock.recvfrom(...).
        cluster_sock.sendto('',('127.0.0.1',listening_port))

        # Wake up the "handle_arrivals" daemon, which is waiting in a
        # peer_connection_sock.accept().
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect(('127.0.0.1',listening_port))

        # Breaks this thread and returns to the parent process (usually,
        # the shell).
        break

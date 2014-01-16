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

class Splitter:

    # Some useful definitions.
    __IP_ADDR = 0
    __PORT = 1

    # A splitter runs 3 threads. The first one controls the peer
    # arrivals. The second one listen to the cluster, for example, to
    # resend lost blocks. The third one shows some information about
    # the transmission. This is used to stop the child threads. They
    # will be alive only while the main thread is alive.
    main_alive = True

    def __init__(self,

                 # The buffer_size depends on the stream bit-rate and
                 # the maximun latency experimented by the users, and
                 # should be transmitted to the peers. The buffer_size
                 # is proportional to the bit-rate and the latency is
                 # proportional to the buffer_size.
                 buffer_size = 256,

                 # The chunk_size depends mainly on the network
                 # technology and should be selected as big as
                 # possible, depending on the MTU and the bit-error
                 # rate.
                 chunk_size = 1024,

                 # Channel served by the streaming source.
                 channel = '134.ogg',

                 # The streaming server.
                 source_host = "150.214.150.68",

                 # Port where the streaming server is listening.
                 source_port = 4551,

                 # IP address to talk with the peers (a host can use
                 # several network adapters).
                 listening_host = "127.0.0.1",

                 # Port to talk with the peers.
                 listening_port = 4552

                 ):

        self.buffer_size = buffer_size
        self.chunk_size = chunk_size
        self.channel = channel
        self.source_host = source_host
        self.source_port = source_port
        self.listening_host = listening_host
        self.listening_port = listening_port

    def get_peer_connection_socket(host, port):
        # {{{

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        try:
            # This does not work in Windows systems.
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        except:
            pass

        sock.bind((host, port))
        #sock.listen(5)
        sock.listen(socket.SOMAXCONN)   # Set the connection queue to the max!

        return sock

        # }}}

    def create_cluster_sock(host, port):
        # {{{ 
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            # This does not work in Windows systems !!
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        except:
            pass
        sock.bind((host, port))
        #peer_socket.bind(('',peer_connection_sock.getsockname()[PORT]))

        return sock
        # }}}

    def __arrival_handler(peer_serve_socket, peer, peer_list, unreliability):
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
    def wait_for_the_monitor_peer(peer_connection_socket, peer_list, unreliability):
        # {{{

        print peer_connection_socket.getsockname(),\
            "waiting for the monitor peer ..."
        sys.stdout.flush()
        peer_serve_socket, peer = peer_connection_socket.accept()
        print peer_serve_socket.getsockname(), "the monitor peer is", \
            peer_serve_socket.getpeername()

        peer = (listening_host, peer[1])
        arrival_handler(peer_serve_socket, peer, peer_list, unreliability)

        # }}}

    #  Handle the arrival of a peer. When a peer want to join a cluster,
    # first it must establish a TCP connection with the splitter. In that
    # connection, the splitter sends to the incomming peer the list of
    # peers. Notice that the transmission of the list of peers (something
    # that could need some time if the cluster is big or the peer is slow)
    # is done in a separate thread. This helps to avoid a DoS
    # (Denial-of-Service) attack.
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

        def __init__(self, socket):
            Thread.__init__(self)
            self.socket = socket

        def run(self):
            global main_alive

            print socket.getsockname(), "waiting for normal peers ..." 
            while main_alive:
                peer_serve_socket, peer = self.socket.accept()
                #if peer not in peer_list: # Puede que sobre
                handle_one_arrival(peer_serve_socket, peer).start()

        # }}}

    # Daemon to administrate the cluster.
    class listen_to_the_cluster(Thread):
        # {{{

        def __init__(self):
            Thread.__init__(self)

        def run(self):

            global peer_index
            global main_alive

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
                            self.peer_index -= 1
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
                            self.peer_index -= 1
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
                                self.peer_index -= 1
                                peer_list.remove(sender)
                                del complains[sender]
                                del unreliability[sender]
                # }}}

        # }}}

    def run(self):

        print "Splitter running in",
        if __debug__:
            print "debug mode"
        else:
            print "release mode"

        # This is the list of peers in the cluster. There will be always a
        # peer in the list of peers that, by default, is running in the
        # same host than the splitter, listening to the port
        # listening_port+1. Notice that you can replace this end-point by
        # any other you want, for example, in a different host.
        peer_list = []
        # peer_list = [('127.0.0.1',listening_port+1)]

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

        # Socket to manage the cluster (churn).
        peer_connection_socket = self.get_peer_connection_socket()

        # Socket to send the media to the cluster.
        cluster_sock = create_cluster_sock(listening_port)

        wait_for_the_monitor_peer(peer_connection_socket, peer_list, unreliability)

        source = (source_host, source_port)
        source_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print source_sock.getsockname(), 'connecting to the source', source, '...'

        source_sock.connect(source)

        print source_sock.getsockname(), 'connected to', source

        GET_message = 'GET /' + channel + ' HTTP/1.1\r\n'
        GET_message += '\r\n'
        source_sock.sendall(GET_message)

        chunk_format_string = "H" + str(chunk_size) + "s" # "H1024s

        handle_arrivals().start()

        peer_index = 0
        listen_to_the_cluster(peer_index).start()

        chunk_number = 0

        #ifdef({{GRANULARITY_CHANGE}},
        #granularity_counter = 0
        #)

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

        #ifdef({{GRANULARITY_CHANGE}},
        #        granularity_counter += 1
        #        if granularity_counter == granularity:
        #            peer_index = (peer_index + 1) % len(peer_list)
        #            granularity_counter = 0
        #,
                peer_index = (peer_index + 1) % len(peer_list)
        #)

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


 #   @classmethod
    def start(self):
        self.run()

splitter = Splitter()

# {{{ Args parsing

parser = argparse.ArgumentParser(description='This is the splitter node of a P2PSP network.')
parser.add_argument('--source_host', help='The streaming server. (Default = "{}")'.format(splitter.source_host))
parser.add_argument('--source_port', help='Port where the streaming server is listening. (Default = {})'.format(splitter.source_port))
parser.add_argument('--channel', help='Name of the channel served by the streaming source. (Default = "{}")'.format(splitter.channel))
parser.add_argument('--listening_host', help='IP address to talk with the peers. (Default = {})'.format(splitter.listening_host))
parser.add_argument('--listening_port', help='Port to talk with the peers. (Default = {})'.format(splitter.listening_port))
parser.add_argument('--buffer_size', help='size of the video buffer in blocks. (Default = {})'.format(splitter.buffer_size))
parser.add_argument('--chunk_size', help='Chunk size in bytes. (Default = {})'.format(splitter.chunk_size))

#ifdef({{GRANULARITY_CHANGE}},
#granularity = 1
#parser.add_argument("--granularity",
#                    help="Round-Robing scheduling granularity.(Default = {})".format(granular#ity))
#)

args = parser.parse_known_args()[0]
if args.source_host:
    splitter.source_host = args.source_host
if args.source_port:
    splitter.source_port = int(args.source_port)
if args.channel:
    splitter.channel = args.channel
if args.listening_host:
    splitter.listening_host = args.listening_host
if args.listening_port:
    splitter.listening_port = int(args.listening_port)
if args.buffer_size:
    splitter.buffer_size = int(args.buffer_size)
if args.chunk_size:
    splitter.chunk_size = int(args.chunk_size)
# }}}

splitter.start()

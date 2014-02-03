#!/usr/bin/python -O

# This code implements the DBS of the P2PSP.

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

class Splitter(Thread):

     # The buffer_size depends on the stream bit-rate and
     # the maximun latency experimented by the users, and
     # must be transmitted to the peers. The buffer_size
     # is proportional to the bit-rate and the latency is
     # proportional to the buffer_size.
     buffer_size = 256

     # The chunk_size depends mainly on the network
     # technology and should be selected as big as
     # possible, depending on the MTU and the bit-error
     # rate.
     chunk_size = 1024

     # Channel served by the streaming source.
     channel = '/root/Videos/Big_Buck_Bunny_small.ogv',

     # The streaming server.
     source_host = "150.214.150.68"

     # Port where the streaming server is listening.
     source_port = 4551

     # IP address to talk with the peers (a host can use
     # several network adapters).
     team_host = "150.214.150.68"

     # Port to talk with the peers.
     listening_port = 4552

    # Some useful definitions.
    __IP_ADDR = 0
    __PORT = 1

    # A splitter runs 3 threads. The first one controls the peer
    # arrivals. The second one listens to the team, for example, to
    # re-sends lost blocks. The third one shows some information about
    # the transmission. This variable is used to stop the child
    # threads. They will be alive only while the main thread is alive.
    alive = True

    def __init__(self):
        Thread.__init__(self)

        print "Splitter running in",
        if __debug__:
            print "debug mode"
        else:
            print "release mode"

    def handle_peer_arrival(peer_connection_socket, peer_list, unreliability):
        # {{{

        # Handle the arrival of a peer. When a peer want to join a team,
        # first it must establish a TCP connection with the splitter. In that
        # connection, the splitter sends to the incomming peer the list of
        # peers. Notice that the transmission of the list of peers (something
        # that could need some time if the team is big or the peer is slow)
        # is done in a separate thread. This helps to avoid a DoS
        # (Denial-of-Service) attack.

        peer_serve_socket, peer = peer_connection_sock.accept()

        if self.peer not in peer_list:

            sys.stdout.write(Color.green)
            print peer_serve_socket.getsockname(), '\b: accepted connection from peer', peer

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

            print peer_serve_socket.getsockname(), '\b: sending the list of peers ...'

            # Sends the size of the list of peers.
            message = struct.pack("H", socket.htons(len(peer_list)))
            peer_serve_socket.sendall(message)

            # Send the list of peers.
            counter = 0
            for p in peer_list:
                message = struct.pack("4sH", socket.inet_aton(p[IP_ADDR]), socket.htons(p[PORT]))
                peer_serve_socket.sendall(message)
                print "[%5d]" % counter, p
                counter += 1

            print 'done'
            sys.stdout.write(Color.none)

            peer_serve_socket.close()
            peer_list.append(peer)

            unreliability[peer] = 0
            complains[peer] = 0

        # }}}

    class Handle_peer_arrival(Thread):
        # {{{

        #peer_connection_socket = ""
    
        def __init__(self, peer_connection_socket, peer_list, unreliability):
            Thread.__init__(self)
            self.peer_connection_socket = peer_connection_socket
            self.peer_list = peer_list
            self.unreliabilty = unreliability
        
            def run(self):
                handle_peer_arrival(self.peer_connection_socket, self.peer_list, self.unreliability)
        # }}}

    class Handle_arrivals(Thread):
        # {{{

        def __init__(self, peer_connection_socket, peer_list, unreliability):
            Thread.__init__(self)

        def run(self):
            while self.alive:
                Handle_peer_arrival(self.peer_connection_socket, self.peer_list, self.unreliability).start()

        # }}}

    class Moderate_the_team(Thread):
        # {{{

        def __init__(self):
            Thread.__init__(self)

        def run(self):

            global peer_index

            print team_sock.getsockname(), "\b: listening to the team (UDP messages) ...", 
            while self.alive:
                # {{{

                # Peers complain about lost chunks, and a chunk index is
                # stored in a "H" (unsigned short) register.
                message, sender = team_sock.recvfrom(struct.calcsize("H"))

                # However, sometimes peers only want to exit. In this case,
                # they send a UDP datagram to the splitter with a
                # zero-length payload.
                if len(message) == 0:
                    sys.stdout.write(Color.red)
                    print team_sock.getsockname(), '\b: received "goodbye" from', sender
                    sys.stdout.write(Color.none)
                    sys.stdout.flush()
                    # An empty message is a goodbye message.
                    if sender != peer_list[0]:
                        try:
                            peer_index -= 1
                            peer_list.remove(sender)
                            #print Color.red, "\b", sender, 'removed by "goodbye" message', Color.none
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
                    # the team. Moreover, if we receive too much
                    # complains from the same peer, the problem could be
                    # in that peer and it will be expelled from the
                    # team.
                    lost_chunk = struct.unpack("!H",message)[0]
                    destination = destination_of_chunk[lost_chunk]
                    sys.stdout.write(Color.blue)
                    print team_sock.getsockname(), "\b:", sender, "complains about lost chunk", lost_chunk, "sent to", destination, Color.none
                    sys.stdout.write(Color.none)
                    try:
                        unreliability[destination] += 1
                    except:
                        print "the unsupportive peer does not exit"
                        pass
                    else:
                        #print Color.blue, "complains about", destination, \
                        #    "=", unreliability[destination], Color.none
                        if unreliability[destination] > 128:
                            sys.stdout.write(Color.red)
                            print team_sock.getsockname(), "\b: too much complains about unsupportive peer", destination, "\b. Removing it"
                            peer_index -= 1
                            peer_list.remove(destination)
                            del unreliability[destination]
                            del complains[destination]
                            sys.stdout.write(Color.none)

                    if sender != peer_list[0]:
                        try:
                            complains[sender] += 1
                        except:
                            print "the complaining peer does not exit"
                            pass
                        else:
                            if complains[sender] > 128:
                                sys.stdout.write(Color.red)
                                print team_socket.getsockname(), "\b: too much complains of a peevish peer", sender
                                sys.stdout.write(Color.none)
                                peer_index -= 1
                                peer_list.remove(sender)
                                del complains[sender]
                                del unreliability[sender]
                # }}}

        # }}}

    def run(self):

        # {{{ Setup "peer_connection_socket"

        # peer_connection_socket is used to listen to the incomming peers.
        peer_connection_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            # This does not work in Windows systems.
            peer_connection_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        except:
            pass
        peer_connection_socket.bind((team_host, team_port))
        peer_connection_socket.listen(socket.SOMAXCONN) # Set the connection queue to the max!

        # }}}
        # {{{ Setup "team_socket"

        # "team_socket" is used to talk to the peers of the team.
        team_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            # This does not work in Windows systems !!
            team_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        except:
            pass
        team_socket.bind((team_host, team_port))

        # }}}
        # {{{ Setup "peer_list"

        # The list of peers in the team.
        #peer_list = [('127.0.0.1',team_port+1)]
        peer_list = []

        # }}}
        # {{{ Setup "destination_of_chunk"

        # Destination peers of the chunk, indexed by a chunk number. Used to
        # find the peer to which a chunk has been sent.
        destination_of_chunk = [('0.0.0.0',0) for i in xrange(buffer_size)]

        # }}}
        # {{{ Setup "unreliability"

        # Unreliaility of the peers, indexed by (the end-point of) the
        # peer. Counts the number of times a peer has not re-transmitted a
        # packet.
        unreliability = {}
        #unreliability[('127.0.0.1',team_port+1)] = 0

        # }}}
        # {{{ Setup "complains"

        # Complaining rate of a peer. Sometimes the complaining peer has not
        # enough bandwidth in his download link. In this case, the peevish
        # peers should be rejected from the team.
        complains = {}
        #complains[('127.0.0.1',team_port+1)] = 0

        # }}}
        # {{{ Wait for the monitor peer

        # The fist peer that contacts the splitter is a "monitor" peer that
        # the team administrator can use to monitorize the performance of
        # the streaming. This peer MUST run on the same host than the splitter
        # to avoid bandwidth consumption and usually listen to the port
        # team_port+1 (although this is configurable by the administrator
        # selecting a different peer_port). This peer MUST also use the same
        # public IP address that the splitter in order the rest of peers of
        # the team communicate with it. The splitter will use its public IP
        # address as the IP address of the monitor peer.

        handle_arrival(peer_connection_socket, peer_list, unreliability)

        # }}}
        Handle_arrivals(peer_connection_socket, peer_list, unreliability).start()
        peer_index = 0
        Moderate_the_team().start()

        source_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        def _():
            source = (source_host, source_port)
            print source_socket.getsockname(), 'connecting to the source', source, '...'
            source_socket.connect(source)
            print source_sock.getsockname(), 'connected to', source
            GET_message = 'GET ' + channel + ' HTTP/1.1\r\n'
            GET_message += '\r\n'
            source_socket.sendall(GET_message)
        _()

        chunk_format_string = "H" + str(chunk_size) + "s" # "H1024s
        chunk_number = 0

        while True:
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

            peer = peer_list[peer_index]
            message = struct.pack(chunk_format_string,
                                  socket.htons(chunk_number),
                                  chunk)
            chunk_number = (chunk_number + 1) % 65536
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

 #   @classmethod
    def start(self):
        self.run()

def main():
    splitter = Splitter()

    # {{{ Args parsing

    parser = argparse.ArgumentParser(description='This is the splitter node of a P2PSP network.')
    parser.add_argument('--source_host', help='The streaming server. (Default = "{}")'.format(splitter.source_host))
    parser.add_argument('--source_port', help='Port where the streaming server is listening. (Default = {})'.format(splitter.source_port))
    parser.add_argument('--channel', help='Name of the channel served by the streaming source. (Default = "{}")'.format(splitter.channel))
    parser.add_argument('--team_host', help='IP address to talk with the peers. (Default = "{}")'.format(splitter.team_host))
    parser.add_argument('--team_port', help='Port to talk with the peers. (Default = {})'.format(splitter.team_port))
    parser.add_argument('--buffer_size', help='size of the video buffer in blocks. (Default = {})'.format(splitter.buffer_size))
    parser.add_argument('--chunk_size', help='Chunk size in bytes. (Default = {})'.format(splitter.chunk_size))

    args = parser.parse_known_args()[0]
    if args.source_host:
        splitter.source_host = socket.gethostbyname(args.source_host)
    if args.source_port:
        splitter.source_port = int(args.source_port)
    if args.channel:
        splitter.channel = args.channel
    if args.listening_host:
        splitter.team_host = socket.gethostbyname(args.team_host)
    if args.team_port:
        splitter.listening_port = int(args.team_port)
    if args.buffer_size:
        splitter.buffer_size = int(args.buffer_size)
    if args.chunk_size:
        splitter.chunk_size = int(args.chunk_size)
    # }}}

    splitter.start()
    try:
        last_chunk_number = 0
        while splitter.alive:
            print "[%3d] " % len(peer_list),
            kbps = (chunk_number - last_chunk_number) * \
                chunk_size * 8/1000
            last_chunk_number = chunk_number

            for x in xrange(0,kbps/10):
                print "\b#",
            print kbps, "kbps"

            time.sleep(1)

    except KeyboardInterrupt:
        print 'Keyboard interrupt detected ... Exiting!'

        # Say to the daemon threads that the work has been finished,
        main_alive = False

        # Wake up the "listen_to_the_cluster" daemon, which is waiting
        # in a cluster_sock.recvfrom(...).
        cluster_sock.sendto('',('127.0.0.1',cluster_port))

        # Wake up the "handle_arrivals" daemon, which is waiting in a
        # peer_connection_sock.accept().
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect(('127.0.0.1',cluster_port))

        # Breaks this thread and returns to the parent process (usually,
        # the shell).
        break

if __name__ == "__main__":
    main()

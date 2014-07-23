from __future__ import print_function
import threading
import sys
import socket
import struct
from color import Color
import common
import time
from _print_ import _print_
from peer_ims import Peer_IMS

# Data Broadcasting Set of Rules
class Peer_DBS(Peer_IMS):
    # {{{

    # {{{ Class "constants"

    DEBT_MEMORY = 1024
    DEBT_THRESHOLD = 10 # This value depends on debt_memory

    # }}}

    def print_modulename(self):
        # {{{

        sys.stdout.write(Color.yellow)
        _print_("Peer DBS")
        sys.stdout.write(Color.none)

        # }}}

    def say_goodbye(self, node):
        # {{{

        self.team_socket.sendto('', node)

        # }}}

    def retrieve_the_list_of_peers(self):
        # {{{

        sys.stdout.write(Color.green)
        _print_("Requesting the list of peers to", self.splitter_socket.getpeername())
        tmp = number_of_peers = socket.ntohs(struct.unpack("H",self.splitter_socket.recv(struct.calcsize("H")))[0])
        _print_("The size of the team is", number_of_peers, "(apart from me)")

        while number_of_peers > 0:
            message = self.splitter_socket.recv(struct.calcsize("4sH"))
            IP_addr, port = struct.unpack("4sH", message) # Ojo, !H ????
            IP_addr = socket.inet_ntoa(IP_addr)
            port = socket.ntohs(port)
            peer = (IP_addr, port)
            #self.say_hello(peer, team_socket)
            if __debug__:
                _print_("[%5d]" % number_of_peers, peer)
            else:
                _print_("{:.2%}\r".format((tmp-number_of_peers)/tmp), end='')

            self.peer_list.append(peer)
            self.debt[peer] = 0
            number_of_peers -= 1

        _print_("List of peers received")
        sys.stdout.write(Color.none)

        # }}}

    def receive_the_debt_memory(self): # deprecated
        # {{{

        message = self.splitter_socket.recv(struct.calcsize("H"))
        debt_memory = struct.unpack("H", message)[0]
        self.debt_memory = socket.ntohs(debt_memory)
        if __debug__:
            print ("debt_memory =", self.debt_memory)

        # }}}
        
    def receive_the_debt_threshold(self): # deprecated
        # {{{

        message = self.splitter_socket.recv(struct.calcsize("H"))
        debt_threshold = struct.unpack("H", message)[0]
        self.debt_threshold = socket.ntohs(debt_threshold)
        if __debug__:
            print ("debt_threshold =", self.debt_threshold)

        # }}}
        
    def setup_team_socket(self): # LLamar listen_to_the_team ???
        # {{{ Create "team_socket" (UDP) as a copy of "splitter_socket" (TCP)

        self.team_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            # In Windows systems this call doesn't work!
            self.team_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        except Exception, e:
            print (e)
            pass
        self.team_socket.bind(('', self.splitter_socket.getsockname()[PORT]))

        # This is the maximum time the peer will wait for a chunk
        # (from the splitter or from another peer).
        self.team_socket.settimeout(1)

        # }}}

    def receive_and_feed(self): # LLamar process_a_chunk ???
        # {{{

        try:
            # {{{ Receive and send

            chunk_format_string = "H" + str(self.chunk_size) + "s"
            message, sender = self.team_socket.recvfrom(struct.calcsize(chunk_format_string))
            self.recvfrom_counter += 1
            #self.recvfrom_counter %= MAX_CHUNK_NUMBER

            # {{{ debug
            if __debug__:
                print (Color.cyan, "Received a message from", sender, \
                    "of length", len(message), Color.none)
            # }}}

            if len(message) == struct.calcsize(chunk_format_string):
                # {{{ A video chunk has been received

                number, chunk = struct.unpack(chunk_format_string, message)
                chunk_number = socket.ntohs(number)

                self.chunks[chunk_number % self.buffer_size] = chunk
                self.received[chunk_number % self.buffer_size] = True
                self.numbers[chunk_number % self.buffer_size] = chunk_number

                if sender == self.splitter:
                    # {{{ Send the previous chunk in burst sending

                    # mode if the chunk has not been sent to all
                    # the peers of the list of peers.

                    # {{{ debug

                    if __debug__:
                        print (self.team_socket.getsockname(), \
                            Color.red, "<-", Color.none, chunk_number, "-", sender)

                    # }}}

                    while( (self.receive_and_feed_counter < len(self.peer_list)) and (self.receive_and_feed_counter > 0) ):
                        peer = self.peer_list[self.receive_and_feed_counter]
                        self.team_socket.sendto(self.receive_and_feed_previous, peer)
                        self.sendto_counter += 1
                        #self.sendto_counter %= MAX_CHUNK_NUMBER

                        # {{{ debug

                        if __debug__:
                            print (self.team_socket.getsockname(), "-",\
                                socket.ntohs(struct.unpack(chunk_format_string, \
                                                               self.receive_and_feed_previous)[0]),\
                                Color.green, "->", Color.none, peer)

                        # }}}

                        self.debt[peer] += 1
                        if self.debt[peer] > self.DEBT_THRESHOLD:
                            del self.debt[peer]
                            self.peer_list.remove(peer)
                            print (Color.red, peer, 'removed by unsupportive', Color.none)

                        self.receive_and_feed_counter += 1

                    self.receive_and_feed_counter = 0
                    self.receive_and_feed_previous = message

                   # }}}
                else:
                    # {{{ The sender is a peer

                    # {{{ debug

                    if __debug__:
                        print (self.team_socket.getsockname(), \
                            Color.green, "<-", Color.none, chunk_number, "-", sender)

                    # }}}

                    if sender not in self.peer_list:
                        # The peer is new
                        self.peer_list.append(sender)
                        self.debt[sender] = 0
                        print (Color.green, sender, 'added by data chunk', \
                            chunk_number, Color.none)
                    else:
                        self.debt[sender] -= 1

                    # }}}

                # {{{ A new chunk has arrived from a peer and the
                # previous must be forwarded to next peer of the
                # list of peers.
                if ( self.receive_and_feed_counter < len(self.peer_list) and ( self.receive_and_feed_previous != '') ):
                    # {{{ Send the previous chunk in congestion avoiding mode.

                    peer = self.peer_list[self.receive_and_feed_counter]
                    self.team_socket.sendto(self.receive_and_feed_previous, peer)
                    self.sendto_counter += 1
                    #self.sendto_counter %= MAX_CHUNK_NUMBER

                    self.debt[peer] += 1
                    if self.debt[peer] > self.deft_threshold:
                        del self.debt[peer]
                        self.peer_list.remove(peer)
                        print (Color.red, peer, 'removed by unsupportive', Color.none)

                    # {{{ debug

                    if __debug__:
                        print (self.team_socket.getsockname(), "-", \
                            socket.ntohs(struct.unpack(chunk_format_string, self.receive_and_feed_previous)[0]),\
                            Color.green, "->", Color.none, peer)

                    # }}}

                    self.receive_and_feed_counter += 1

                    # }}}
                # }}}
                return chunk_number

                # }}}
            else:
                # {{{ A control chunk has been received
                '''
                try:
                    sys.stdout.write(Color.red)
                    print 'Received "goodbye" from', sender
                    sys.stdout.write(Color.none)
                    self.peer_list.remove(sender)
                    del self.debt[sender]
                except:
                    pass
                '''
                if sender in self.peer_list:
                    sys.stdout.write(Color.red)
                    print (self.team_socket.getsockname(), '\b: received "goodbye" from', sender)
                    sys.stdout.write(Color.none)
                    self.peer_list.remove(sender)
                    del self.debt[sender]
                return -1

                # }}}

            # }}}
        except socket.timeout:
            return -2

        # }}}

    def peers_life(self):
        # {{{

        while self.player_alive:
            self.keep_the_buffer_full()
            if (self.played_chunk % self.debt_memory) == 0:
                for i in self.debt:
                    self.debt[i] /= 2

            if __debug__:
                for i in xrange(self.buffer_size):
                    if self.received[i]:
                        sys.stdout.write(str(i%10))
                    else:
                        sys.stdout.write('.')
                print
                sys.stdout.write(Color.cyan)
                print ("Number of peers in the team:", len(self.peer_list)+1)
                print (self.team_socket.getsockname(),)
                for p in self.peer_list:
                    print (p,)
                print
                sys.stdout.write(Color.none)

        # }}}

    def polite_farewell(self):
        # {{{

        print('Goodbye!')
        for x in xrange(3):
            self.receive_and_feed()
            self.say_goodbye(self.splitter)
        for peer in self.peer_list:
            self.say_goodbye(peer)

        # }}}

    def run(self):
        # {{{

        self.wait_for_the_player()
        self.connect_to_the_splitter()
        self.receive_the_header()
        self.receive_the_buffersize()
        self.receive_the_chunksize()
        self.receive_the_debt_memory()
        self.receive_the_debt_threshold()
        self.setup_team_socket()
        self.retrieve_the_list_of_peers()
        self.splitter_socket.close()
        self.create_buffer()
        self.buffer_data()
        self.buffering.set()
        self.buffering = False
        self.peers_life()
        self.polite_farewell()

        # }}}

    def start(self):
        # {{{

        self.run()

        # }}}

    def __init__(self):
        # {{{

        threading.Thread.__init__(self)

        print("Running in", end=' ')
        if __debug__:
            print("debug mode")
        else:
            print("release mode")

        self.print_modulename()

        print("Player port =", self.PLAYER_PORT)
        #print("Splitter IP address =", self.SPLITTER_ADDR)
        #print("Splitter port =", self.SPLITTER_PORT)
        #print("(Team) Port =", self.TEAM_PORT)

        self.peer_list = []
#        self.buffer_size = 0
        self.player_alive = True
        self.played_chunk = 0
        self.chunk_size = 0

        # Number of times that the previous received chunk has been sent
        # to the team. If this counter is smaller than the number
        # of peers in the team, the previous chunk must be sent in the
        # burst mode because a new chunk from the splitter has arrived
        # and the previous received chunk has not been sent to all the
        # peers of the team. This can happen when one o more chunks
        # that were routed towards this peer have been lost.
        self.receive_and_feed_counter = 0

        # This "private and static" variable holds the previous chunk
        # received from the splitter. It is used to send the previous
        # received chunk in the congestion avoiding mode. In that
        # mode, the peer sends a chunk only when it received a chunk
        # from another peer or om the splitter.
        self.receive_and_feed_previous = ""
        self.received = []
        self.debt = {}

        self.sendto_counter = 0
        self.recvfrom_counter = 0

        #self.pipe_thread_end, self.pipe_main_end = Pipe()
        #self.buffering = True
        self.buffering = threading.Event()
        
        # }}}

    # }}}

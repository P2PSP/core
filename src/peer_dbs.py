# -*- coding: iso-8859-15 -*-

# {{{ GNU GENERAL PUBLIC LICENSE

# This is the splitter node of the P2PSP (Peer-to-Peer Simple Protocol)
# <https://launchpad.net/p2psp>.
#
# Copyright (C) 2014 Vicente González Ruiz,
#                    Cristóbal Medina López,
#                    Juan Alvaro Muñoz Naranjo.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

# }}}

# Data Broadcasting Set of Rules
class Peer_DBS(threading.Thread):
    # {{{

    # {{{ Class "constants"

    PLAYER_PORT = 9999
    SPLITTER_ADDR = "150.214.150.68"
    SPLITTER_PORT = 4552
    TEAM_PORT = 0
    DEBT_MEMORY = 1024
    DEBT_THRESHOLD = 10 # This value depends on debt_memory

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
        print("Splitter IP address =", self.SPLITTER_ADDR)
        print("Splitter port =", self.SPLITTER_PORT)
        print("(Team) Port =", self.TEAM_PORT)

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

    def print_modulename(self):
        # {{{

        sys.stdout.write(Color.yellow)
        print("Peer DBS")
        sys.stdout.write(Color.none)

        # }}}

    def say_goodbye(self, node):
        # {{{

        self.team_socket.sendto('', node)

        # }}}

    def retrieve_the_list_of_peers(self):
        # {{{

        sys.stdout.write(Color.green)
        print("Requesting the list of peers to", self.splitter_socket.getpeername())
        number_of_peers = socket.ntohs(struct.unpack("H",self.splitter_socket.recv(struct.calcsize("H")))[0])
        print("The size of the team is", number_of_peers, "(apart from me)")

        while number_of_peers > 0:
            message = self.splitter_socket.recv(struct.calcsize("4sH"))
            IP_addr, port = struct.unpack("4sH", message) # Ojo, !H ????
            IP_addr = socket.inet_ntoa(IP_addr)
            port = socket.ntohs(port)
            peer = (IP_addr, port)
            #self.say_hello(peer, team_socket)
            if __debug__:
                print("[%5d]" % number_of_peers, peer)
            self.peer_list.append(peer)
            self.debt[peer] = 0
            number_of_peers -= 1

        print(1, "List of peers received")
        sys.stdout.write(Color.none)

        # }}}

    # Tiene pinta de que los tres siguientes metodos pueden simplificarse

    def find_next_chunk(self):
        # {{{

        chunk_number = (self.played_chunk + 1) % common.MAX_CHUNK_NUMBER
        while not self.received[chunk_number % self.buffer_size]:
            chunk_number = (chunk_number + 1) % common.MAX_CHUNK_NUMBER
        return chunk_number

        # }}}

    def play_chunk(self, chunk):
        # {{{

        try:
            self.player_socket.sendall(self.chunks[chunk % self.buffer_size])
        except socket.error, e:
            print(e)
            print('Player disconected, ...', end=' ')
            self.player_alive = False

        # }}}

    def play_next_chunk(self):
        # {{{

        self.played_chunk = self.find_next_chunk()
        self.play_chunk(self.played_chunk)
        self.received[self.played_chunk % self.buffer_size] = False

        # }}}

    def wait_for_the_player(self):
        # {{{ Setup "player_socket" and wait for the player

        self.player_socket =  socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            # In Windows systems this call doesn't work!
            self.player_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        except Exception, e:
            print (e)
            pass
        self.player_socket.bind(('', self.PLAYER_PORT))
        self.player_socket.listen(0)
        print ("Waiting for the player at", self.player_socket.getsockname())
        self.player_socket = self.player_socket.accept()[0]
        #self.player_socket.setblocking(0)
        print("The player is", self.player_socket.getpeername())

        # }}}

    def connect_to_the_splitter(self):
        # {{{ Setup "splitter" and "splitter_socket"

        self.splitter_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.splitter = (self.SPLITTER_ADDR, self.SPLITTER_PORT)
        print ("Connecting to the splitter at", self.splitter)
        if self.TEAM_PORT != 0:
            try:
                self.splitter_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            except Exception, e:
                print (e)
                pass
            sys.stdout.write(Color.purple)
            print ("I'm using port the port", self.TEAM_PORT)
            sys.stdout.write(Color.none)
            self.splitter_socket.bind(("", self.TEAM_PORT))
        try:
            self.splitter_socket.connect(self.splitter)
        except Exception, e:
            print(e)
            sys.exit("Sorry. Can't connect to the splitter at " + str(self.splitter))
        print("Connected to the splitter at", self.splitter)

        # }}}

    def receive_the_header(self):
        # {{{

        header_size = 1024*10
        received = 0
        data = ""
        while received < header_size:
            data = self.splitter_socket.recv(header_size - received)
            received += len(data)
            try:
                self.player_socket.sendall(data)
            except Exception, e:
                print (e)
                print ("error sending data to the player")
                print ("len(data) =", len(data))
            print ("received bytes:", received, "\r", end=" ")

        print ("Received", received, "bytes of header")

        # }}}

    def receive_the_buffersize(self):
        # {{{

        message = self.splitter_socket.recv(struct.calcsize("H"))
        buffer_size = struct.unpack("H", message)[0]
        self.buffer_size = socket.ntohs(buffer_size)
        print ("buffer_size =", self.buffer_size)

        # }}}

    def receive_the_chunksize(self):
        # {{{

        message = self.splitter_socket.recv(struct.calcsize("H"))
        chunk_size = struct.unpack("H", message)[0]
        self.chunk_size = socket.ntohs(chunk_size)
        print ("chunk_size =", self.chunk_size)

        # }}}

    def setup_team_socket(self):
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

    def receive_and_feed(self):
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
                    if self.debt[peer] > self.DEBT_THRESHOLD:
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

    def create_buffer(self):
        # {{{

        # The buffer of chunks is a structure that is used to delay
        # the playback of the chunks in order to accommodate the
        # network jittter. Two components are needed: (1) the "chunks"
        # buffer that stores the received chunks and (2) the
        # "received" buffer that stores if a chunk has been received
        # or not. Notice that each peer can use a different
        # buffer_size: the smaller the buffer size, the lower start-up
        # time, the higher chunk-loss ratio. However, for the sake of
        # simpliticy, all peers will use the same buffer size.
        self.chunks = [""]*self.buffer_size
        self.received = [False]*self.buffer_size
        self.numbers = [0]*self.buffer_size

        # }}}

    def buffer_data(self):
        # {{{ Buffering

        #  Wall time (execution time plus waiting time).
        start_latency = time.time()

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

        print(self.team_socket.getsockname(), "\b: buffering ",)
        sys.stdout.flush()

        # First chunk to be sent to the player.
        chunk_number = self.receive_and_feed()

        # The receive_and_feed() procedure returns if a packet has been
        # received or if a time-out exception has been arised. In the first
        # case, the returned value is -1 if the packet contains a
        # hello/goodbyte message or a number >= 0 if a chunk has been
        # received. A -2 is returned if a time-out is has happened.
        while chunk_number < 0:
            chunk_number = self.receive_and_feed()
        self.played_chunk = chunk_number
        print ("First chunk to play", self.played_chunk)

        # Fill up to the half of the buffer
        for x in xrange(self.buffer_size/2):
            print("!", end='')
            sys.stdout.flush()
            while self.receive_and_feed() < 0:
                pass

        print()
        print('latency =', time.time() - start_latency, 'seconds')
        sys.stdout.flush()

        # }}}

    def keep_the_buffer_full(self):
        # {{{

        # Receive chunks while the buffer is not full
        chunk_number = self.receive_and_feed()
        while chunk_number < 0:
            chunk_number = self.receive_and_feed()
        while ((chunk_number - self.played_chunk) % self.buffer_size) < self.buffer_size/2:
            chunk_number = self.receive_and_feed()
            while chunk_number < 0:
                chunk_number = self.receive_and_feed()

        # Play the next chunk
        self.play_next_chunk()

        # }}}

    def peers_life(self):
        # {{{

        while self.player_alive:
            self.keep_the_buffer_full()
            if (self.played_chunk % self.DEBT_MEMORY) == 0:
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

    # }}}

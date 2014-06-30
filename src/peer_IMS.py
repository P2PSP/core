#!/usr/bin/python -O
# -*- coding: iso-8859-15 -*-

# Solo el peer monitor se queja al splitter. Si un peer no posee
# suficiente ancho de banda para recibir o transmitir, el monitor
# dejara de recibir sus chunks y el splitter lo descubrira a traves de
# las quejas del monitor al splitter. Un monitor es un peer que se
# queja y ademas el splitter le hace caso.

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

# {{{ Imports

from __future__ import print_function
import sys
import socket
import struct
import time
import argparse
from color import Color
import threading
from lossy_socket import lossy_socket
#from multiprocessing import Pipe

# }}}

ADDR = 0
PORT = 1
MAX_CHUNK_NUMBER = 65536
#MAX_CHUNK_NUMBER = 512

# IP Multicasting Set of Rules
class Peer_IMS(threading.Thread):
    # {{{

    # {{{ Class "constants"

    PLAYER_PORT = 9999
    SPLITTER_ADDR = "150.214.150.68"
    SPLITTER_PORT = 4552
    TEAM_PORT = 0
    HEADER_CHUNKS = 10
    TEAM_ADDR = "224.0.0.1"
    #MCAST_GRP = '224.1.1.1'
    
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

        # {{{ The peer dies if there is not a connected player
        # }}}
        self.player_alive = True

        # {{{ The last chunk sent to the player
        # }}}
        self.played_chunk = 0

        # {{{ The size of the chunk in bytes
        # }}}
        self.chunk_size = 0

        # {{{ Label the chunks in the buffer as "received" or "not received"
        # }}}
        self.received = []

        # {{{ Counts the number of executions of the recvfrom()
        # }}}
        self.recvfrom_counter = 0

        # {{{ "True" while buffering is being performed
        # }}}
        self.buffering = threading.Event()

        # }}}

    def print_modulename(self):
        # {{{

        sys.stdout.write(Color.yellow)
        print("Peer IMS")
        sys.stdout.write(Color.none)

        # }}}

    # Tiene pinta de que los tres siguientes metodos pueden simplificarse

    def find_next_chunk(self):
        # {{{

        chunk_number = (self.played_chunk + 1) % MAX_CHUNK_NUMBER
        while not self.received[chunk_number % self.buffer_size]:
            chunk_number = (chunk_number + 1) % MAX_CHUNK_NUMBER
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

        self.player_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
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

    def receive_and_send_the_header(self):
        # {{{

        header_size = self.HEADER_CHUNKS * self.chunk_size
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
        self.chunk_format_string = "H" + str(self.chunk_size) + "s"

        # }}}

    def setup_team_socket(self):
        # {{{ Create "team_socket" (UDP) for using the multicast channel

        #self.team_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.team_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        try:
            # In Windows systems this call doesn't work!
            self.team_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        except Exception, e:
            print (e)
            pass
        self.team_socket.bind(('', 5007))
#        self.team_socket.bind(('', self.splitter_socket.getsockname()[PORT]))

        mreq = struct.pack("4sl", socket.inet_aton(self.TEAM_ADDR), socket.INADDR_ANY)
        self.team_socket.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
        
        # This is the maximum time the peer will wait for a chunk
        # (from the splitter).
        self.team_socket.settimeout(1)

        # }}}

    def receive_a_chunk(self):
        # {{{
        print (".")
        try:
            # {{{ Receive a chunk

            message, sender = self.team_socket.recvfrom(struct.calcsize(self.chunk_format_string))
            self.recvfrom_counter += 1

            # {{{ debug
            if __debug__:
                print (Color.cyan, "Received a message from", sender, \
                    "of length", len(message), Color.none)
            # }}}

            number, chunk = struct.unpack(self.chunk_format_string, message)
            chunk_number = socket.ntohs(number)

            self.chunks[chunk_number % self.buffer_size] = chunk
            self.received[chunk_number % self.buffer_size] = True
            self.numbers[chunk_number % self.buffer_size] = chunk_number # Ojo

            return chunk_number

            # }}}
        except socket.timeout:
            return -2

        # }}}

    def create_buffer(self):
        # {{{ The buffer of chunks is a structure that is used to delay
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
        self.numbers = [0]*self.buffer_size # Ojo

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
        chunk_number = self.receive_a_chunk()

        # The receive_and_feed() procedure returns if a packet has been
        # received or if a time-out exception has been arised. In the first
        # case, the returned value is -1 if the packet contains a
        # hello/goodbyte message or a number >= 0 if a chunk has been
        # received. A -2 is returned if a time-out is has happened.
        while chunk_number < 0:
            chunk_number = self.receive_a_chunk()
        self.played_chunk = chunk_number
        print ("First chunk to play", self.played_chunk)

        # Fill up to the half of the buffer
        for x in xrange(self.buffer_size/2):
            print("!", end='')
            sys.stdout.flush()
            while self.receive_a_chunk() < 0:
                pass

        print()
        print('latency =', time.time() - start_latency, 'seconds')
        sys.stdout.flush()

        # }}}

    def keep_the_buffer_full(self):
        # {{{

        # Receive chunks while the buffer is not full
        chunk_number = self.receive_a_chunk()
        while chunk_number < 0:
            chunk_number = self.receive_a_chunk()
        while ((chunk_number - self.played_chunk) % self.buffer_size) < self.buffer_size/2:
            chunk_number = self.receive_a_chunk()
            while chunk_number < 0:
                chunk_number = self.receive_a_chunk()

        # Play the next chunk
        self.play_next_chunk()

        # }}}

    def peers_life(self):
        # {{{

        while self.player_alive:
            self.keep_the_buffer_full()

            if __debug__:
                for i in xrange(self.buffer_size):
                    if self.received[i]:
                        sys.stdout.write(str(i%10))
                    else:
                        sys.stdout.write('.')
                print
                print (self.team_socket.getsockname(),)
                sys.stdout.write(Color.none)

        # }}}

    def run(self):
        # {{{

        self.wait_for_the_player()
        self.connect_to_the_splitter()
        self.receive_the_chunksize()
        self.receive_and_send_the_header()
        self.receive_the_buffersize()
        self.setup_team_socket()
        self.splitter_socket.close()
        self.create_buffer()
        self.buffer_data()
        self.buffering.set()
        self.buffering = False
        self.peers_life()

        # }}}

    # }}}

def main():

    # {{{ Args parsing

    monitor_mode = False

    parser = argparse.ArgumentParser(description='This is the peer node of a P2PSP network.')

    parser.add_argument('--player_port', help='Port to communicate with the player. ({})'.format(Peer_IMS.PLAYER_PORT))

    parser.add_argument('--team_port', help='Port to communicate with the peers. ({})'.format(Peer_IMS.TEAM_PORT))

    parser.add_argument('--splitter_addr', help='IP address of the splitter. ({})'.format(Peer_IMS.SPLITTER_ADDR))

    parser.add_argument('--splitter_port', help='Listening port of the splitter. ({})'.format(Peer_IMS.SPLITTER_PORT))

    parser.add_argument('--monitor', help='Run the peer in the monitor mode.', action='store_true')

    args = parser.parse_known_args()[0]

    if args.player_port:
        Peer_IMS.PLAYER_PORT = int(args.player_port)
        print ('PLAYER_PORT = ', Peer_IMS.PLAYER_PORT)
    if args.splitter_addr:
        Peer_IMS.SPLITTER_ADDR = socket.gethostbyname(args.splitter_addr)
        print ('SPLITTER_ADDR = ', Peer_IMS.SPLITTER_ADDR)
    if args.splitter_port:
        Peer_IMS.SPLITTER_PORT = int(args.splitter_port)
        print ('SPLITTER_PORT = ', Peer_IMS.SPLITTER_PORT)
    if args.team_port:
        Peer_IMS.TEAM_PORT = int(args.team_port)
        print ('TEAM_PORT= ', Peer_IMS.TEAM_PORT)

    # }}}

    peer = Peer_IMS()
    peer.start()
    peer.buffering.wait()

    print("+-----------------------------------------------------+")
    print("| Received = Received kbps, including retransmissions |")
    print("|     Sent = Sent kbps                                |")
    print("|       (Expected values are between parenthesis)     |")
    print("+-----------------------------------------------------+")
    print()
    print("        Received |             Sent | Team description")
    print("-----------------+------------------+-----------------")

    last_chunk_number = peer.played_chunk
    last_recvfrom_counter = peer.recvfrom_counter
    while peer.player_alive:
        time.sleep(1)
        kbps_expected_recv = ((peer.played_chunk - last_chunk_number) * peer.chunk_size * 8) / 1000
        last_chunk_number = peer.played_chunk
        kbps_recvfrom = ((peer.recvfrom_counter - last_recvfrom_counter) * peer.chunk_size * 8) / 1000
        last_recvfrom_counter = peer.recvfrom_counter
        team_ratio = len(peer.peer_list) /(len(peer.peer_list) + 1.0)
        kbps_expected_sent = int(kbps_expected_recv*team_ratio)
        nice = 100.0/float((float(kbps_expected_recv)/kbps_recvfrom)*(len(peer.peer_list)+1))
        if kbps_expected_recv < kbps_recvfrom:
            sys.stdout.write(Color.red)
        elif kbps_expected_recv > kbps_recvfrom:
            sys.stdout.write(Color.green)
        print(repr(kbps_expected_recv).rjust(8), end=Color.none)
        print(('(' + repr(kbps_recvfrom) + ')').rjust(8), end=' | ')
        print()

if __name__ == "__main__":
     main()

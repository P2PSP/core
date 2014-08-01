#!/usr/bin/python -O
# -*- coding: iso-8859-15 -*-

# {{{ Imports

from __future__ import print_function
import time
import sys
import socket
import threading
import struct
import argparse
from color import Color
import common
from splitter_ims import Splitter_IMS
from splitter_dbs import Splitter_DBS
from _print_ import _print_

# }}}

class Splitter():

    def __init__(self):

        # {{{ Args parsing

        parser = argparse.ArgumentParser(description='This is the splitter node of a P2PSP team.')

        #parser.add_argument('--splitter_addr', help='IP address to serve (TCP) the peers. (Default = "{}")'.format(Splitter_IMS.SPLITTER_ADDR)) <- no ahora

        parser.add_argument('--buffer_size', help='size of the video buffer in blocks. Default = {}.'.format(Splitter_IMS.BUFFER_SIZE))

        parser.add_argument('--channel', help='Name of the channel served by the streaming source. Default = "{}".'.format(Splitter_IMS.CHANNEL))

        parser.add_argument('--chunk_size', help='Chunk size in bytes. Default = {}.'.format(Splitter_IMS.CHUNK_SIZE))

        parser.add_argument('--header_size', help='Size of the header of the stream in chunks. Default = {}.'.format(Splitter_IMS.HEADER_SIZE))

        #parser.add_argument('--losses_memory', help='Number of chunks to divide by two the losses counters. Makes sense only in unicast mode. Default = {}.'.format(Splitter_DBS.LOSSES_MEMORY))

        parser.add_argument('--max_chunk_loss', help='Maximum number of lost chunks for an unsupportive peer. Makes sense only in unicast mode. Default = {}.'.format(Splitter_DBS.MAX_CHUNK_LOSS))

        parser.add_argument("--mcast", action="store_true", help="Enables IP multicast.")

        parser.add_argument('--mcast_addr', help='IP multicast address used to serve the chunks. Makes sense only in multicast mode. Default = "{}".'.format(Splitter_IMS.MCAST_ADDR))

        parser.add_argument('--port', help='Port to serve the peers. Default = "{}".'.format(Splitter_IMS.PORT))

        parser.add_argument('--source_addr', help='IP address of the streaming server. Default = "{}".'.format(Splitter_IMS.SOURCE_HOST))

        parser.add_argument('--source_port', help='Port where the streaming server is listening. Default = {}.'.format(Splitter_IMS.SOURCE_PORT))

        args = parser.parse_known_args()[0]

        if args.buffer_size:
            Splitter_IMS.BUFFER_SIZE = int(args.buffer_size)

        if args.channel:
            Splitter_IMS.CHANNEL = args.channel

        if args.chunk_size:
            Splitter_IMS.CHUNK_SIZE = int(args.chunk_size)

        if args.header_size:
            Splitter_IMS.HEADER_SIZE = int(args.header_size)

        if args.port:
            Splitter_IMS.PORT = int(args.port)

        if args.source_addr:
            Splitter_IMS.SOURCE_HOST = socket.gethostbyname(args.source_addr)

        if args.source_port:
            Splitter_IMS.SOURCE_PORT = int(args.source_port)

        if args.mcast:
            splitter = Splitter_IMS()
            splitter.peer_list = []

            if args.mcast_addr:
                splitter.MCAST_ADDR = args.mcast_addr
        else:
            splitter = Splitter_DBS()

            if args.max_chunk_loss:
                splitter.MAX_CHUNK_LOSS = int(args.max_chunk_loss)

        # }}}

        # {{{ Run!

        splitter.start()

        # {{{ Prints information until keyboard interruption

        # #Chunk #peers { peer #losses period #chunks }

        #last_chunk_number = 0

        print("         | Received | Sent      |")
        print("    Time | (kbps)   | (kbps)    | Peers")
        print("---------+----------+-----------+------------+")

        last_sendto_counter = splitter.sendto_counter
        last_recvfrom_counter = splitter.recvfrom_counter

        while splitter.alive:
            try:
                time.sleep(1)
                kbps_sendto = ((splitter.sendto_counter - last_sendto_counter) * splitter.CHUNK_SIZE * 8) / 1000
                kbps_recvfrom = ((splitter.recvfrom_counter - last_recvfrom_counter) * splitter.CHUNK_SIZE * 8) / 1000
                last_sendto_counter = splitter.sendto_counter
                last_recvfrom_counter = splitter.recvfrom_counter
                sys.stdout.write(Color.white)
                _print_("|" + repr(kbps_recvfrom).rjust(10) + "|" + repr(kbps_sendto).rjust(10), end=" | ")
                #print('%5d' % splitter.chunk_number, end=' ')
                sys.stdout.write(Color.cyan)
                print(len(splitter.peer_list), end=' ')
                for p in splitter.peer_list:
                    sys.stdout.write(Color.blue)
                    print(p, end= ' ')
                    sys.stdout.write(Color.red)
                    print('%3d' % splitter.losses[p], '<', splitter.MAX_CHUNK_LOSS, end=' ')
                    try:
                        sys.stdout.write(Color.blue)
                        print('%3d' % splitter.period[p], end= ' ')
                        sys.stdout.write(Color.purple)
                        print('%4d' % splitter.number_of_sent_chunks_per_peer[p], end = ' ')
                        splitter.number_of_sent_chunks_per_peer[p] = 0
                    except AttributeError:
                        pass
                    sys.stdout.write(Color.none)
                    print('|', end=' ')
                print()
                '''
                print "[%3d] " % len(splitter.peer_list),
                kbps = (splitter.chunk_number - last_chunk_number) * \
                splitter.CHUNK_SIZE * 8/1000
                last_chunk_number = splitter.chunk_number

                for x in xrange(0,kbps/10):
                print "\b#",
                print kbps, "kbps"
                '''

            except KeyboardInterrupt:
                print('Keyboard interrupt detected ... Exiting!')

                # Say to the daemon threads that the work has been finished,
                splitter.alive = False

                # Wake up the "moderate_the_team" daemon, which is waiting
                # in a cluster_sock.recvfrom(...).
                if not args.mcast:
                    splitter.say_goodbye(("localhost", splitter.PORT), splitter.team_socket)

                # Wake up the "handle_arrivals" daemon, which is waiting
                # in a peer_connection_sock.accept().
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.connect(("localhost", splitter.PORT))
                sock.recv(splitter.CHUNK_SIZE*splitter.HEADER_SIZE) # Header
                sock.recv(struct.calcsize("H")) # Buffer size
                sock.recv(struct.calcsize("H")) # Chunk size
                if args.mcast:
                    number_of_peers = 0
                else:
                    number_of_peers = socket.ntohs(struct.unpack("H", sock.recv(struct.calcsize("H")))[0])

                # Receive the list
                while number_of_peers > 0:
                    sock.recv(struct.calcsize("4sH"))
                    number_of_peers -= 1

                # Breaks this thread and returns to the parent process
                # (usually, the shell).
                break

            # }}}

        # }}}

x = Splitter()

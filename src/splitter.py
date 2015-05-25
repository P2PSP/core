#!/usr/bin/python -O
# -*- coding: iso-8859-15 -*-

# This code is distributed under the GNU General Public License (see
# THE_GENERAL_GNU_PUBLIC_LICENSE.txt for extending this information).
# Copyright (C) 2014, the P2PSP team.
# http://www.p2psp.org

# PYTHON_ARGCOMPLETE_OK

# {{{ Imports

from __future__ import print_function
import time
import sys
import socket
import threading
import struct
import argparse
from color import Color
from splitter_ims import Splitter_IMS
from splitter_dbs import Splitter_DBS
from splitter_fns import Splitter_FNS
from splitter_acs import Splitter_ACS
from splitter_lrs import Splitter_LRS
import common
from _print_ import _print_
try:
    import colorama
except ImportError:
    pass
try:
    import argcomplete
except ImportError:
    pass
# }}}

class Splitter():

    def __init__(self):

        try:
            colorama.init()
        except Exception:
            pass

        _print_("Running in", end=' ')
        if __debug__:
            print("debug mode")
        else:
            print("release mode")

        # {{{ Args parsing and instantiation

        parser = argparse.ArgumentParser(description='This is the splitter node of a P2PSP team.')

        #parser.add_argument('--splitter_addr', help='IP address to serve (TCP) the peers. (Default = "{}")'.format(Splitter_IMS.SPLITTER_ADDR)) <- no ahora

        parser.add_argument('--buffer_size', help='size of the video buffer in blocks. Default = {}.'.format(Splitter_IMS.BUFFER_SIZE))

        parser.add_argument('--channel', help='Name of the channel served by the streaming source. Default = "{}".'.format(Splitter_IMS.CHANNEL))

        parser.add_argument('--chunk_size', help='Chunk size in bytes. Default = {}.'.format(Splitter_IMS.CHUNK_SIZE))

        parser.add_argument('--header_size', help='Size of the header of the stream in chunks. Default = {}.'.format(Splitter_IMS.HEADER_SIZE))

        parser.add_argument('--max_chunk_loss', help='Maximum number of lost chunks for an unsupportive peer. Makes sense only in unicast mode. Default = {}.'.format(Splitter_DBS.MAX_CHUNK_LOSS))

        parser.add_argument("--mcast", action="store_true", help="Uses the IP multicast infrastructure, if available.")

        parser.add_argument('--mcast_addr', help='IP multicast address used to serve the chunks. Makes sense only in multicast mode. Default = "{}".'.format(Splitter_IMS.MCAST_ADDR))

        parser.add_argument('--port', help='Port to serve the peers. Default = "{}".'.format(Splitter_IMS.PORT))

        parser.add_argument('--source_addr', help='IP address or hostname of the streaming server. Default = "{}".'.format(Splitter_IMS.SOURCE_ADDR))

        parser.add_argument('--source_port', help='Port where the streaming server is listening. Default = {}.'.format(Splitter_IMS.SOURCE_PORT))

        try:
            argcomplete.autocomplete(parser)
        except Exception:
            pass
        args = parser.parse_args()
        #args = parser.parse_known_args()[0]

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
            Splitter_IMS.SOURCE_ADDR = socket.gethostbyname(args.source_addr)

        if args.source_port:
            Splitter_IMS.SOURCE_PORT = int(args.source_port)

        if args.mcast:
            print("IP multicast mode selected")

            if args.mcast_addr:
                Splitter_IMS.MCAST_ADDR = args.mcast_addr

            splitter = Splitter_IMS()
            splitter.peer_list = []

        else:

            if args.max_chunk_loss:
                Splitter_DBS.MAX_CHUNK_LOSS = int(args.max_chunk_loss)

            #splitter = Splitter_DBS()
            #splitter = Splitter_FNS()
            #splitter = Splitter_ACS()
            splitter = Splitter_LRS()

        # }}}

        # {{{ Run!

        splitter.start()

        # {{{ Prints information until keyboard interruption

        print("         | Received  | Sent      | Number       losses/ losses")
        print("    Time | (kbps)    | (kbps)    | peers (peer) sents   threshold period kbps")
        print("---------+-----------+-----------+-----------------------------------...")

        last_sendto_counter = splitter.sendto_counter
        last_recvfrom_counter = splitter.recvfrom_counter

        while splitter.alive:
            try:
                time.sleep(1)
                chunks_sendto = splitter.sendto_counter - last_sendto_counter
                kbps_sendto = (chunks_sendto * splitter.CHUNK_SIZE * 8) / 1000
                chunks_recvfrom = splitter.recvfrom_counter - last_recvfrom_counter
                kbps_recvfrom = ( chunks_recvfrom * splitter.CHUNK_SIZE * 8) / 1000
                last_sendto_counter = splitter.sendto_counter
                last_recvfrom_counter = splitter.recvfrom_counter
                sys.stdout.write(Color.none)
                _print_("|" + repr(kbps_recvfrom).rjust(10) + " |" + repr(kbps_sendto).rjust(10), end=" | ")
                #print('%5d' % splitter.chunk_number, end=' ')
                sys.stdout.write(Color.cyan)
                print(len(splitter.peer_list), end=' ')
                if not __debug__:
                    counter = 0
                for p in splitter.peer_list:
                    if not __debug__:
                        if counter > 10:
                            break
                        counter += 1
                    sys.stdout.write(Color.blue)
                    print(p, end= ' ')
                    sys.stdout.write(Color.red)
                    print(str('%3d' % splitter.losses[p]) + '/' + str('%3d' % chunks_sendto), splitter.MAX_CHUNK_LOSS, end=' ')
                    try:
                        sys.stdout.write(Color.yellow)
                        print('%3d' % splitter.period[p], end= ' ')
                        sys.stdout.write(Color.purple)
                        print(repr((splitter.number_of_sent_chunks_per_peer[p] * splitter.CHUNK_SIZE * 8) / 1000).rjust(10), end = ' ')
                        splitter.number_of_sent_chunks_per_peer[p] = 0
                    except KeyError as e:
                        print("!", e, "--")
                        print(splitter.period[p])
                        pass
                    sys.stdout.write(Color.none)
                    print('', end=' ')
                print()

            except KeyboardInterrupt:
                print('Keyboard interrupt detected ... Exiting!')

                # Say to the daemon threads that the work has been finished,
                splitter.alive = False

                # Wake up the "moderate_the_team" daemon, which is waiting
                # in a cluster_sock.recvfrom(...).
                if not args.mcast:
                    splitter.say_goodbye(("127.0.0.1", splitter.PORT), splitter.team_socket)

                # Wake up the "handle_arrivals" daemon, which is waiting
                # in a peer_connection_sock.accept().
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.connect(("127.0.0.1", splitter.PORT))
                sock.recv(struct.calcsize("4sH")) # Multicast channel
                sock.recv(struct.calcsize("H")) # Header size
                sock.recv(struct.calcsize("H")) # Chunk size
                sock.recv(splitter.CHUNK_SIZE*splitter.HEADER_SIZE) # Header
                sock.recv(struct.calcsize("H")) # Buffer size
                if args.mcast:
                    number_of_peers = 0
                else:
                    number_of_peers = socket.ntohs(struct.unpack("H", sock.recv(struct.calcsize("H")))[0])
                    print("Number of peers =", number_of_peers)
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

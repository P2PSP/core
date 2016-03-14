##!/opt/local/bin/python3.4
##!/usr/bin/python -O

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

from core.common import Common
from core._print_ import _print_
from core.color import Color
import libp2psp

try:
    import colorama                       # Enable console color using ANSI codes in Windows
except ImportError:
    pass

import argparse
try:
    import argcomplete                    # Bash tab completion for argparse in Unixes
except ImportError:
    pass

# }}}

class Splitter():

    def __init__(self):

        # {{{ colorama.init()

        try:
            colorama.init()
        except Exception:
            pass

        # }}}

        # {{{ Running in debug/release mode

        _print_("Running in", end=' ')
        if __debug__:
            print("debug mode")
        else:
            print("release mode")

        # }}}

        splitter = libp2psp.SplitterDBS()

        # {{{ Arguments handling

        parser = argparse.ArgumentParser(description='This is the splitter node of a P2PSP team.  The splitter is in charge of defining the Set or Rules (SoR) that will control the team. By default, DBS (unicast transmissions) will be used.')
        #parser.add_argument('--splitter_addr', help='IP address to serve (TCP) the peers. (Default = "{}")'.format(Splitter_IMS.SPLITTER_ADDR)) <- no ahora
        parser.add_argument('--buffer_size', help='size of the video buffer in blocks. Default = {}.')#.format(Splitter_IMS.BUFFER_SIZE))
        parser.add_argument('--channel', help='Name of the channel served by the streaming source. Default = "{}".')#.format(Splitter_IMS.CHANNEL))
        parser.add_argument('--chunk_size', help='Chunk size in bytes. Default = {}.')#.format(Splitter_IMS.CHUNK_SIZE))
        parser.add_argument('--header_size', help='Size of the header of the stream in chunks. Default = {}.')#.format(Splitter_IMS.HEADER_SIZE))
        parser.add_argument('--max_chunk_loss', help='Maximum number of lost chunks for an unsupportive peer. Makes sense only in unicast mode. Default = {}.')#.format(Splitter_DBS.MAX_CHUNK_LOSS))
        parser.add_argument('--max_number_of_monitor_peers', help='Maxium number of monitors in the team. The first connecting peers will automatically become monitors. Default = "{}".')#.format(Splitter_DBS.MONITOR_NUMBER))
        parser.add_argument('--mcast_addr', help='IP multicast address used to serve the chunks. Makes sense only in multicast mode. Default = "{}".')#.format(Splitter_IMS.MCAST_ADDR))
        parser.add_argument('--port', help='Port to serve the peers. Default = "{}".')#.format(Splitter_IMS.PORT))
        parser.add_argument('--source_addr', help='IP address or hostname of the streaming server. Default = "{}".')#.format(Splitter_IMS.SOURCE_ADDR))
        parser.add_argument('--source_port', help='Port where the streaming server is listening. Default = {}.')#.format(Splitter_IMS.SOURCE_PORT))
        #parser.add_argument("--IMS", action="store_true", help="Uses the IP multicast infrastructure, if available. IMS mode is incompatible with ACS, LRS, DIS and NTS modes.")
        #parser.add_argument("--NTS", action="store_true", help="Enables NAT traversal.")
        #parser.add_argument("--ACS", action="store_true", help="Enables Adaptive Chunk-rate.")
        #parser.add_argument("--LRS", action="store_true", help="Enables Lost chunk Recovery.")
        #parser.add_argument("--DIS", action="store_true", help="Enables Data Integrity check.")
        #parser.add_argument('--strpe', nargs='+', type=str, help='Selects STrPe model for DIS')
        #parser.add_argument('--strpeds', nargs='+', type=str, help='Selects STrPe-DS model for DIS')
        #parser.add_argument('--strpeds_majority_decision', help='Sets majority decision ratio for STrPe-DS model.')
        #parser.add_argument('--strpe_log', help='Logging STrPe & STrPe-DS specific data to file.')
        #parser.add_argument('--TTL', help='Time To Live of the multicast messages. Default = {}.')#.format(Splitter_IMS.TTL))
        
        try:
            argcomplete.autocomplete(parser)
        except Exception:
            pass
        args = parser.parse_args()
        #args = parser.parse_known_args()[0]

        _print_("My IP address is =", socket.gethostbyname(socket.gethostname()))
        

        if args.buffer_size:
            splitter.SetBufferSize(int(args.buffer_size))
        _print_("Buffer size =", str(splitter.GetBufferSize()))

        if args.channel:
            splitter.SetChannel(args.channel)
        _print_("Channel = \"" + str(splitter.GetChannel()) + "\"")

        if args.chunk_size:
            splitter.SetChunkSize(int(args.chunk_size))
        _print_("Chunk size =", str(splitter.GetChunkSize()))

        if args.header_size:
            splitter.SetHeaderSize(int(args.header_size))
        _print_("Header size =", str(splitter.GetHeaderSize()))

        if args.port:
            splitter.SetPort(int(args.port))
        _print_("Listening port =", str(splitter.GetPort()))

        if args.source_addr:
            splitter.SetSourceAddr(socket.gethostbyname(args.source_addr))
        _print_("Source address = ", str(splitter.GetSourceAddr()))

        if args.source_port:
            splitter.SetSourcePort(int(args.source_port))
        _print_("Source port =", str(splitter.GetSourcePort()))

        
        _print_("IP unicast mode selected")

        if args.max_chunk_loss:
            splitter.SetMaxChunkLoss( int(args.max_chunk_loss))
            _print_("Maximun chunk loss =", str(splitter.GetMaxChunkLoss()))

        if args.max_number_of_monitor_peers:
           splitter.SetMonitorNumber(int(args.max_number_of_monitor_peers))
           _print_("Maximun number of monitor peers =", str(splitter.GetMonitorNumber()))


        # {{{ Run!

        splitter.Start()

        # {{{ Prints information until keyboard interruption

        print("         | Received  | Sent      | Number       losses/ losses")
        print("    Time | (kbps)    | (kbps)    | peers (peer) sents   threshold period kbps")
        print("---------+-----------+-----------+-----------------------------------...")

        last_sendto_counter = splitter.GetSendToCounter()
        last_recvfrom_counter = splitter.GetRecvFromCounter()

        while splitter.isAlive():
            try:
                time.sleep(1)
                chunks_sendto = splitter.GetSendToCounter() - last_sendto_counter
                kbps_sendto = (chunks_sendto * splitter.GetChunkSize() * 8) / 1000
                chunks_recvfrom = splitter.GetRecvFromCounter() - last_recvfrom_counter
                kbps_recvfrom = ( chunks_recvfrom * splitter.GetChunkSize() * 8) / 1000
                last_sendto_counter = splitter.GetSendToCounter()
                last_recvfrom_counter = splitter.GetRecvFromCounter()
                sys.stdout.write(Color.none)
                _print_("|" + repr(int(kbps_recvfrom)).rjust(10) + " |" + repr(int(kbps_sendto)).rjust(10), end=" | ")
                #print('%5d' % splitter.chunk_number, end=' ')
                sys.stdout.write(Color.cyan)
                print(len(splitter.GetPeerList()), end=' ')
                if not __debug__:
                    counter = 0
                for p in splitter.GetPeerList():
                    if not __debug__:
                        if counter > 10:
                            break
                        counter += 1
                    sys.stdout.write(Color.blue)
                    print(p, end= ' ')
                    sys.stdout.write(Color.red)
                    #print(str('%3d' % splitter.GetLoss(p)) + '/' + str('%3d' % chunks_sendto), splitter.GetMaxChunkLoss(), end=' ')
                   
                print()

            except KeyboardInterrupt:
                print('Keyboard interrupt detected ... Exiting!')

                # Say to daemon threads that the work has been finished,
                splitter.SetAlive(False)

                # Wake up the "moderate_the_team" daemon, which is
                # waiting in a recvfrom().
                splitter.SayGoodbye()
                '''                
				if not args.IMS:
                    #splitter.say_goodbye(("127.0.0.1", splitter.PORT), splitter.team_socket)
                    splitter.team_socket.sendto(b'', ("127.0.0.1", splitter.PORT))
				'''
                # Wake up the "handle_arrivals" daemon, which is waiting
                # in an accept().
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.connect(("127.0.0.1", splitter.GetPort()))
                sock.recv(struct.calcsize("4sH")) # Multicast channel
                sock.recv(struct.calcsize("H")) # Header size
                sock.recv(struct.calcsize("H")) # Chunk size
                sock.recv(splitter.CHUNK_SIZE*splitter.HEADER_SIZE) # Header
                sock.recv(struct.calcsize("H")) # Buffer size
                sock.recv(struct.calcsize("4sH")) # Endpoint
                sock.recv(struct.calcsize("B")) # Magic flags
                if args.IMS:
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

    # {{{# -COM-
    '''
    def init_strpe_splitter(self, type, trusted_peers, log_file = None):
        if type == 'strpe':
            re = StrpeSplitter()
        if type == 'strpeds':
            re = StrpeDsSplitter()
        for peer in trusted_peers:
            re.add_trusted_peer(peer)
        if log_file != None:
            re.LOGGING = True
            re.LOG_FILE = open(log_file, 'w', 0)
        return re

    # }}}
    '''

x = Splitter()

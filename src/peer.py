#!/usr/bin/python -O
# -*- coding: iso-8859-15 -*-

# This code is distributed under the GNU General Public License (see
# THE_GENERAL_GNU_PUBLIC_LICENSE.txt for extending this information).
# Copyright (C) 2014, the P2PSP team.
# http://www.p2psp.org

# PYTHON_ARGCOMPLETE_OK

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

from peer_ims import Peer_IMS
from peer_dbs import Peer_DBS
from peer_fns import Peer_FNS
from monitor_dbs import Monitor_DBS
from monitor_fns import Monitor_FNS
#from peer_lossy import Peer_Lossy
from monitor_lrs import Monitor_LRS
from lossy_peer import Lossy_Peer

# }}}

# Some useful definitions.
ADDR = 0
PORT = 1

class Peer():

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

        # {{{ Args handling and object instantiation
        parser = argparse.ArgumentParser(description='This is the peer node of a P2PSP team.')

        parser.add_argument('--chunk_loss_period', help='0 -> no chunk loss, 1 -> lost all chunks, 2, lost half of the chunks ... Default = {}'.format(Lossy_Peer.CHUNK_LOSS_PERIOD))

        parser.add_argument('--max_chunk_debt', help='The maximun number of times that other peer can not send a chunk to this peer. Defaut = {}'.format(Peer_DBS.MAX_CHUNK_DEBT))

        parser.add_argument('--player_port', help='Port to communicate with the player. Default = {}'.format(Peer_IMS.PLAYER_PORT))

        parser.add_argument('--splitter_addr', help='IP address or hostname of the splitter. Default = {}.'.format(Peer_IMS.SPLITTER_ADDR))

        parser.add_argument('--splitter_port', help='Listening port of the splitter. Default = {}.'.format(Peer_IMS.SPLITTER_PORT))

        parser.add_argument('--port', help='Port to communicate with the peers. Default {} (the OS will chose it).'.format(Peer_IMS.PORT))

        parser.add_argument('--use_localhost', action="store_true", help='Forces the peer to use localhost instead of the IP of the adapter to connect to the splitter.')

        try:
            argcomplete.autocomplete(parser)
        except Exception:
            pass

        #args = parser.parse_known_args()[0]
        args = parser.parse_args()

        if args.splitter_addr:
            Peer_IMS.SPLITTER_ADDR = socket.gethostbyname(args.splitter_addr)
            print ('SPLITTER_ADDR =', Peer_IMS.SPLITTER_ADDR)

        if args.splitter_port:
            Peer_IMS.SPLITTER_PORT = int(args.splitter_port)
            print ('SPLITTER_PORT =', Peer_IMS.SPLITTER_PORT)

        if args.port:
            Peer_IMS.PORT = int(args.port)
            print ('(Peer) PORT =', Peer_IMS.PORT)

        if args.player_port:
            Peer_IMS.PLAYER_PORT = int(args.player_port)
            print ('PLAYER_PORT =', Peer_IMS.PLAYER_PORT)

        if args.max_chunk_debt:
            Peer_DBS.MAX_CHUNK_DEBT = int(args.max_chunk_debt)
            print ('MAX_CHUNK_DEBT =', Peer_DBS.MAX_CHUNK_DEBT)

        if args.use_localhost:
            Peer_IMS.USE_LOCALHOST = True
            print('Using localhost!')

        peer = Peer_IMS()
        peer.wait_for_the_player()
        peer.connect_to_the_splitter()
        peer.receive_the_mcast_endpoint()
        peer.receive_the_header_size()
        peer.receive_the_chunk_size()
        peer.receive_the_header()
        peer.receive_the_buffer_size()
        #peer.receive_configuration()
        _print_("IP Multicast address =", peer.mcast_addr)
        
        # A multicast address is always received, even for DBS peers.
        if peer.mcast_addr == "0.0.0.0":
            # {{{ This is an "unicast" peer.

            peer = Peer_DBS(peer)
            peer.receive_my_endpoint()
            peer.receive_the_number_of_peers()
            print("===============> number_of_peers =", peer.number_of_peers)
            print("===============> is_a_monitor =",peer.am_i_a_monitor())
            peer.listen_to_the_team()
            peer.receive_the_list_of_peers()

            if peer.am_i_a_monitor():
                #peer = Monitor_DBS(peer)
                #peer = Monitor_FNS(peer)
                peer = Monitor_LRS(peer)
            else:
                peer = Peer_FNS(peer)
                if args.chunk_loss_period:
                    Lossy_Peer.CHUNK_LOSS_PERIOD = int(args.chunk_loss_period)
                    print('CHUNK_LOSS_PERIOD =', Lossy_Peer.CHUNK_LOSS_PERIOD)
                    if int(args.chunk_loss_period) != 0:
                        peer = Lossy_Peer(peer)
                    
            #peer.receive_my_endpoint()
            
            # }}}
        else:
            peer.listen_to_the_team()

        # }}}

        # {{{ Run!
        peer.disconnect_from_the_splitter()
        peer.buffer_data()
        peer.start()

        print("+-----------------------------------------------------+")
        print("| Received = Received kbps, including retransmissions |")
        print("|     Sent = Sent kbps                                |")
        print("|       (Expected values are between parenthesis)     |")
        print("------------------------------------------------------+")
        print()
        print("    Time |     Received (Expected) |          Sent (Expected) | Team description")
        print("---------+-------------------------+--------------------------+-----------------...")

        last_chunk_number = peer.played_chunk
        if hasattr(peer, 'sendto_counter'):
            last_sendto_counter = 0
        else:
            peer.sendto_counter = 0
            last_sendto_counter = 0
        if not hasattr(peer, 'peer_list'):
            peer.peer_list = []
        last_recvfrom_counter = peer.recvfrom_counter
        while peer.player_alive:
            time.sleep(1)
            kbps_expected_recv = ((peer.played_chunk - last_chunk_number) * peer.chunk_size * 8) / 1000
            last_chunk_number = peer.played_chunk
            kbps_recvfrom = ((peer.recvfrom_counter - last_recvfrom_counter) * peer.chunk_size * 8) / 1000
            last_recvfrom_counter = peer.recvfrom_counter
            team_ratio = len(peer.peer_list) /(len(peer.peer_list) + 1.0)
            kbps_expected_sent = int(kbps_expected_recv*team_ratio)
            kbps_sendto = ((peer.sendto_counter - last_sendto_counter) * peer.chunk_size * 8) / 1000
            last_sendto_counter = peer.sendto_counter
            if kbps_recvfrom > 0 and kbps_expected_recv > 0:
                nice = 100.0/float((float(kbps_expected_recv)/kbps_recvfrom)*(len(peer.peer_list)+1))
            else:
                nice = 0.0
            _print_('|', end=Color.none)
            if kbps_expected_recv < kbps_recvfrom:
                sys.stdout.write(Color.red)
            elif kbps_expected_recv > kbps_recvfrom:
                sys.stdout.write(Color.green)
            print(repr(kbps_expected_recv).rjust(12), end=Color.none)
            print(('(' + repr(kbps_recvfrom) + ')').rjust(12), end=' | ')
            #print(("{:.1f}".format(nice)).rjust(6), end=' | ')
            #sys.stdout.write(Color.none)
            if kbps_expected_sent > kbps_sendto:
                sys.stdout.write(Color.red)
            elif kbps_expected_sent < kbps_sendto:
                sys.stdout.write(Color.green)
            print(repr(kbps_sendto).rjust(12), end=Color.none)
            print(('(' + repr(kbps_expected_sent) + ')').rjust(12), end=' | ')
            #sys.stdout.write(Color.none)
            #print(repr(nice).ljust(1)[:6], end=' ')
            print(len(peer.peer_list), end=' ')
            counter = 0
            for p in peer.peer_list:
                if (counter < 5):
                    print(p, end=' ')
                    counter += 1
                else:
                    break
            print()

            # }}}
if __name__ == "__main__":
    x = Peer()

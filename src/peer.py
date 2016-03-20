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
import sys
import socket
import struct
import time
import threading

import argparse
try:
    import argcomplete                    # Bash tab completion for argparse in Unixes
except ImportError:
    pass

try:
    import colorama # Enable console color using ANSI codes in Windows
except ImportError:
    pass

from core.common import Common
from core.color import Color
from core._print_ import _print_
from core.peer_ims import Peer_IMS
from core.peer_dbs import Peer_DBS
from core.lossy_socket import lossy_socket
from core.symsp_peer import Symsp_Peer
from core.monitor_dbs import Monitor_DBS
from core.monitor_lrs import Monitor_LRS
from core.monitor_nts import Monitor_NTS
from core.peer_nts import Peer_NTS
from core.lossy_peer import Lossy_Peer
from core.peer_strpeds import Peer_StrpeDs
from core.malicious_peer import MaliciousPeer # Other dir, maybe "DIS" ??
from core.peer_strpeds_malicious import Peer_StrpeDsMalicious
from core.trusted_peer import TrustedPeer

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

        parser.add_argument('--enable_chunk_loss', help='Forces a lost of chunks')
        parser.add_argument('--max_chunk_debt', help='The maximun number of times that other peer can not send a chunk to this peer. Defaut = {}'.format(Peer_DBS.MAX_CHUNK_DEBT))
        parser.add_argument('--player_port', help='Port to communicate with the player. Default = {}'.format(Peer_IMS.PLAYER_PORT))
        parser.add_argument('--port_step', help='Source port step forced when behind a sequentially port allocating NAT (conflicts with --chunk_loss_period). Default = {}'.format(Symsp_Peer.PORT_STEP))
        parser.add_argument('--splitter_addr', help='IP address or hostname of the splitter. Default = {}.'.format(Peer_IMS.SPLITTER_ADDR))
        parser.add_argument('--splitter_port', help='Listening port of the splitter. Default = {}.'.format(Peer_IMS.SPLITTER_PORT))
        parser.add_argument('--port', help='Port to communicate with the peers. Default {} (the OS will chose it).'.format(Peer_IMS.PORT))
        parser.add_argument('--use_localhost', action="store_true", help='Forces the peer to use localhost instead of the IP of the adapter to connect to the splitter. Notice that in this case, peers that run outside of the host will not be able to communicate with this peer.')
        parser.add_argument('--malicious', action="store_true", help='Enables the malicious activity for peer.')
        parser.add_argument('--persistent', action="store_true", help='Forces the peer to send poisoned chunks to other peers.')
        parser.add_argument('--on_off_ratio', help='Enables on-off attack and sets ratio for on off (from 1 to 100)')
        parser.add_argument('--selective', nargs='+', type=str, help='Enables selective attack for given set of peers.')
        parser.add_argument('--bad_mouth', nargs='+', type=str, help='Enables Bad Mouth attack for given set of peers.')
        parser.add_argument('--trusted', action="store_true", help='Forces the peer to send hashes of chunks to splitter')
        parser.add_argument('--checkall', action="store_true", help='Forces the peer to send hashes of every chunks to splitter (works only with trusted option)')
        parser.add_argument('--strpeds', action="store_true", help='Enables STrPe-DS')
        parser.add_argument('--strpe_log', help='Logging STrPe & STrPe-DS specific data to file.')
        parser.add_argument('--show_buffer', action="store_true", help='Shows the status of the buffer of chunks.')

        try:
            argcomplete.autocomplete(parser)
        except Exception:
            pass

        #args = parser.parse_known_args()[0]
        args = parser.parse_args()

        if args.splitter_addr:
            Peer_IMS.SPLITTER_ADDR = socket.gethostbyname(args.splitter_addr)
        _print_('Splitter address =', Peer_IMS.SPLITTER_ADDR)

        if args.splitter_port:
            Peer_IMS.SPLITTER_PORT = int(args.splitter_port)
        _print_('Splitter port =', Peer_IMS.SPLITTER_PORT)

        if args.port:
            Peer_IMS.PORT = int(args.port)
        _print_('(Peer) PORT =', Peer_IMS.PORT)

        if args.player_port:
            Peer_IMS.PLAYER_PORT = int(args.player_port)
        _print_('Listening port (player) =', Peer_IMS.PLAYER_PORT)

        if args.max_chunk_debt:
            Peer_DBS.MAX_CHUNK_DEBT = int(args.max_chunk_debt)
        _print_('Maximun chunk debt =', Peer_DBS.MAX_CHUNK_DEBT)

        if args.use_localhost:
            Peer_IMS.USE_LOCALHOST = True
            _print_('Using localhost address')

        peer = Peer_IMS()
        peer.wait_for_the_player()
        peer.connect_to_the_splitter()
        peer.receive_the_mcast_endpoint()
        peer.receive_the_header_size()
        peer.receive_the_chunk_size()
        peer.receive_the_header()
        peer.receive_the_buffer_size()
        _print_("Using IP Multicast address =", peer.mcast_addr)

        if args.show_buffer:
            Peer_IMS.SHOW_BUFFER = True

        # A multicast address is always received, even for DBS peers.
        if peer.mcast_addr == "0.0.0.0":
            # {{{ IP unicast mode.

            peer = Peer_DBS(peer)
            _print_("Peer DBS enabled")
            peer.receive_my_endpoint()
            peer.receive_magic_flags()
            _print_("Magic flags =", bin(peer.magic_flags))
            peer.receive_the_number_of_peers()
            _print_("Number of peers in the team (excluding me) =", peer.number_of_peers)
            _print_("Am I a monitor peer? =", peer.am_i_a_monitor())

            if args.port_step:
                Symsp_Peer.PORT_STEP = int(args.port_step)
                print('PORT_STEP =', Symsp_Peer.PORT_STEP)
                if int(args.port_step) != 0:
                    peer = Symsp_Peer(peer)

            peer.listen_to_the_team()
            peer.receive_the_list_of_peers()
            _print_("List of peers received")

            # After receiving the list of peers, the peer can check
            # whether is a monitor peer or not (only the first
            # arriving peers are monitors)
            if peer.am_i_a_monitor():
                peer = Monitor_DBS(peer)
                _print_("Monitor DBS enabled")

                # The peer is a monitor. Now it's time to know the sets of rules that control this team.

                if (peer.magic_flags & Common.LRS):
                    peer = Peer_LRS(peer)
                    _print_("Peer LRS enabled")
                    peer = Monitor_LRS(peer)
                    _print_("Monitor LRS enabled")
                if (peer.magic_flags & Common.NTS):
                    peer = Peer_NTS(peer)
                    _print_("Peer NTS enabled")
                    peer = Monitor_NTS(peer)
                    _print_("Monitor NTS enabled")
            else:
                # The peer is a normal peer. Let's know the sets of rules that control this team.

                if (peer.magic_flags & Common.NTS):
                    peer = Peer_NTS(peer)
                    _print_("Peer NTS enabled")

                if args.enable_chunk_loss:

                    if args.chunk_loss_period:
                        Lossy_Peer.CHUNK_LOSS_PERIOD = int(args.chunk_loss_period)
                        print('CHUNK_LOSS_PERIOD =', Lossy_Peer.CHUNK_LOSS_PERIOD)
                        if int(args.chunk_loss_period) != 0:
                            peer = Lossy_Peer(peer)
                            _print_("Lost of chunks enabled")

            if args.strpeds:
                peer = Peer_StrpeDs(peer)
                peer.receive_dsa_key()

            if args.malicious and not args.strpeds: # workaround for malicous strpeds peer
                peer = MaliciousPeer(peer)
                if args.persistent:
                    peer.setPersistentAttack(True)
                if args.on_off_ratio:
                    peer.setOnOffAttack(True, int(args.on_off_ratio))
                if args.selective:
                    peer.setSelectiveAttack(True, args.selective)

            if args.malicious and args.strpeds:
                peer = Peer_StrpeDsMalicious(peer)
                if args.persistent:
                    peer.setPersistentAttack(True)
                if args.on_off_ratio:
                    peer.setOnOffAttack(True, int(args.on_off_ratio))
                if args.selective:
                    peer.setSelectiveAttack(True, args.selective)
                if args.bad_mouth:
                    peer.setBadMouthAttack(True, args.bad_mouth)

            if args.trusted:
                peer = TrustedPeer(peer)
                if args.checkall:
                    peer.setCheckAll(True)

            if args.strpe_log != None:
                peer.LOGGING = True
                peer.LOG_FILE = open(args.strpe_log, 'w', 0)

            # }}}
        else:
            # {{{ IP multicast mode

            peer.listen_to_the_team()

            # }}}

        # }}}

        print("Created new peer of type %s\n" % peer.__class__.__name__)

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
        print("         |     Received (kbps) |          Sent (kbps) |")
        print("    Time |      Real  Expected |       Real  Expected | Team description")
        print("---------+---------------------+----------------------+-----------------------------------...")

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
            try:
                if Common.CONSOLE_MODE == False :
                    from gi.repository import GObject
                    try:
                        from adapter import speed_adapter
                    except ImportError as msg:
                        pass
                    GObject.idle_add(speed_adapter.update_widget,str(kbps_recvfrom) + ' kbps'
                                            ,str(kbps_sendto) + ' kbps'
                                            ,str(len(peer.peer_list)+1))
            except Exception as msg:
                pass
            if kbps_recvfrom > 0 and kbps_expected_recv > 0:
                nice = 100.0/float((float(kbps_expected_recv)/kbps_recvfrom)*(len(peer.peer_list)+1))
            else:
                nice = 0.0
            _print_('|', end=Color.none)
            if kbps_expected_recv < kbps_recvfrom:
                sys.stdout.write(Color.red)
            elif kbps_expected_recv > kbps_recvfrom:
                sys.stdout.write(Color.green)
            print(repr(int(kbps_expected_recv)).rjust(10), end=Color.none)
            print(repr(int(kbps_recvfrom)).rjust(10), end=' | ')
            #print(("{:.1f}".format(nice)).rjust(6), end=' | ')
            #sys.stdout.write(Color.none)
            if kbps_expected_sent > kbps_sendto:
                sys.stdout.write(Color.red)
            elif kbps_expected_sent < kbps_sendto:
                sys.stdout.write(Color.green)
            print(repr(int(kbps_sendto)).rjust(10), end=Color.none)
            print(repr(int(kbps_expected_sent)).rjust(10), end=' | ')
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
        try:
            if Common.CONSOLE_MODE == False :
                GObject.idle_add(speed_adapter.update_widget,str(0)+' kbps',str(0)+' kbps',str(0))
        except  Exception as msg:
            pass
            # }}}

if __name__ == "__main__":
    x = Peer()

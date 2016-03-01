#!/usr/bin/python -O
# -*- coding: iso-8859-15 -*-

# This code is distributed under the GNU General Public License (see
# THE_GENERAL_GNU_PUBLIC_LICENSE.txt for extending this information).
# Copyright (C) 2015, the P2PSP team.
# http://www.p2psp.org

import struct
import socket
import sys
import threading
import random

from color import Color
from _print_ import _print_
from peer_dbs import Peer_DBS
from peer_strpeds import Peer_StrpeDs

class Peer_StrpeDsMalicious(Peer_StrpeDs):

    persistentAttack = False
    onOffAttack = False
    onOffRatio = 1.0
    selectiveAttack = False
    selectedPeersForSelectiveAttack = []
    badMouthAttack = False
    mainTarget = None
    numberChunksSendToMainTarget = 0
    allAttackC = False
    regularPeers = []
    MPTR = 2

    def __init__(self, peer):
        sys.stdout.write(Color.yellow)
        _print_("STrPe-DS Malicious Peer")
        sys.stdout.write(Color.none)

        threading.Thread.__init__(self)

        self.splitter_socket = peer.splitter_socket
        self.player_socket = peer.player_socket
        self.buffer_size = peer.buffer_size
        self.splitter = peer.splitter
        self.chunk_size = peer.chunk_size
        self.peer_list = peer.peer_list
        self.debt = peer.debt
        self.message_format = peer.message_format
        self.team_socket = peer.team_socket
        self.bad_peers = peer.bad_peers
        self.dsa_key = peer.dsa_key
        self.mainTarget = self.chooseMainTarget()
        _print_("mainTarget = {0}".format(self.mainTarget))

    def chooseMainTarget(self):
        attackedPeers = []
        with open('../src/attacked.txt', 'r') as fh:
            for line in fh:
                attackedPeers.append(line)
            fh.close()

        maliciousPeers = []
        with open('../src/malicious.txt', 'r') as fh:
            for line in fh:
                maliciousPeers.append(line)
            fh.close()

        re = None
        while re == None:
            r = random.randint(0, len(self.peer_list) - 1)
            peerEndpoint = '{0}:{1}'.format(self.peer_list[r][0], self.peer_list[r][1])
            if not ((peerEndpoint+'\n') in attackedPeers) and not ((peerEndpoint+'\n') in maliciousPeers):
                re = self.peer_list[r]
		print "====>",peerEndpoint,attackedPeers,maliciousPeers

        with open('../src/attacked.txt', 'a') as fh:
	    if not (peerEndpoint in attackedPeers):
            	fh.write('{0}:{1}\n'.format(re[0], re[1]))
            fh.close()

        return re

    def process_message(self, message, sender):
        if sender in self.bad_peers:
            return -1

        if self.is_current_message_from_splitter() or self.check_message(message, sender):
            if self.is_control_message(message) and message == 'B':
                return self.handle_bad_peers_request()
            else:
                return self.dbs_process_message(message, sender)
        else:
            self.process_bad_message(message, sender)
            return -1

    def dbs_process_message(self, message, sender):
        # {{{ Now, receive and send.

        if len(message) == struct.calcsize(self.message_format):
            # {{{ A video chunk has been received

            chunk_number, chunk = self.unpack_message(message)
            self.chunks[chunk_number % self.buffer_size] = chunk
            self.received_flag[chunk_number % self.buffer_size] = True
            self.received_counter += 1

            if sender == self.splitter:
                # {{{ Send the previous chunk in burst sending
                # mode if the chunk has not been sent to all
                # the peers of the list of peers.

                # {{{ debug

                if __debug__:
                    _print_("DBS:", self.team_socket.getsockname(), \
                        Color.red, "<-", Color.none, chunk_number, "-", sender)

                # }}}

                while( (self.receive_and_feed_counter < len(self.peer_list)) and (self.receive_and_feed_counter > 0) ):
                    peer = self.peer_list[self.receive_and_feed_counter]
                    self.send_chunk(peer)

                    # {{{ debug

                    if __debug__:
                        print ("DBS:", self.team_socket.getsockname(), "-",\
                            socket.ntohs(struct.unpack(self.message_format, \
                                                           self.receive_and_feed_previous)[0]),\
                            Color.green, "->", Color.none, peer)

                    # }}}

                    self.debt[peer] += 1
                    if self.debt[peer] > self.MAX_CHUNK_DEBT:
                        print (Color.red, "DBS:", peer, 'removed by unsupportive (' + str(self.debt[peer]) + ' lossess)', Color.none)
                        del self.debt[peer]
                        self.peer_list.remove(peer)

                    self.receive_and_feed_counter += 1

                self.receive_and_feed_counter = 0
                self.receive_and_feed_previous = message

               # }}}
            else:
                # {{{ The sender is a peer

                # {{{ debug

                if __debug__:
                    print ("DBS:", self.team_socket.getsockname(), \
                        Color.green, "<-", Color.none, chunk_number, "-", sender)

                # }}}

                if sender not in self.peer_list:
                    # The peer is new
                    self.peer_list.append(sender)
                    self.debt[sender] = 0
                    print (Color.green, "DBS:", sender, 'added by chunk', \
                        chunk_number, Color.none)
                else:
                    self.debt[sender] -= 1

                # }}}

            # {{{ A new chunk has arrived and the
            # previous must be forwarded to next peer of the
            # list of peers.
            if ( self.receive_and_feed_counter < len(self.peer_list) and ( self.receive_and_feed_previous != '') ):
                # {{{ Send the previous chunk in congestion avoiding mode.

                peer = self.peer_list[self.receive_and_feed_counter]
                self.send_chunk(peer)

                self.debt[peer] += 1
                if self.debt[peer] > self.MAX_CHUNK_DEBT:
                    print (Color.red, "DBS:", peer, 'removed by unsupportive (' + str(self.debt[peer]) + ' lossess)', Color.none)
                    del self.debt[peer]
                    self.peer_list.remove(peer)

                # {{{ debug

                if __debug__:
                    print ("DBS:", self.team_socket.getsockname(), "-", \
                        socket.ntohs(struct.unpack(self.message_format, self.receive_and_feed_previous)[0]),\
                        Color.green, "->", Color.none, peer)

                # }}}

                self.receive_and_feed_counter += 1

                # }}}
            # }}}

            return chunk_number

            # }}}
        else:
            # {{{ A control chunk has been received
            print("DBS: Control received")
            if message == 'H':
                if sender not in self.peer_list:
                    # The peer is new
                    self.peer_list.append(sender)
                    self.debt[sender] = 0
                    print (Color.green, "DBS:", sender, 'added by [hello]', Color.none)
            else:
                if sender in self.peer_list:
                    sys.stdout.write(Color.red)
                    print ("DBS:", self.team_socket.getsockname(), '\b: received "goodbye" from', sender)
                    sys.stdout.write(Color.none)
                    self.peer_list.remove(sender)
                    del self.debt[sender]
            return -1

            # }}}

        # }}}
    def allAttack(self):
        _print_("ALL_ATTACK MODE")
        self.allAttackC = True
        del self.regularPeers[:]
        with open('../src/regular.txt', 'a') as fh:
            fh.write('{0}:{1}\n'.format(self.mainTarget[0], self.mainTarget[1]))
            fh.close()
        with open('../src/regular.txt', 'r') as fh:
            for line in fh:
                t = (line.split(':')[0], int(line.split(':')[1]))
                if t in self.peer_list:
                    self.regularPeers.append(t)
                if len(self.regularPeers) * 2 > len(self.peer_list):
                    break

            fh.close()

    def send_chunk(self, peer):
        # im sorry for this part of code =(
        if self.persistentAttack:
            if peer == self.mainTarget and self.numberChunksSendToMainTarget < self.MPTR:
		if self.numberChunksSendToMainTarget<1:
                    self.team_socket.sendto(self.get_poisoned_chunk(self.receive_and_feed_previous), peer)
                    print "Searching mainTarget:", peer
                self.numberChunksSendToMainTarget += 1
                _print_("mainTarget+=1 ({0})".format(self.numberChunksSendToMainTarget))
            elif self.allAttackC:
                if peer in self.regularPeers or peer == self.mainTarget:
                    self.team_socket.sendto(self.get_poisoned_chunk(self.receive_and_feed_previous), peer)
                    print "allAttackC mode:", peer
                else:
                    self.team_socket.sendto(self.receive_and_feed_previous, peer)
            elif peer == self.mainTarget and self.numberChunksSendToMainTarget >= self.MPTR:
                self.allAttack()
                self.team_socket.sendto(self.get_poisoned_chunk(self.receive_and_feed_previous), peer)
		self.mainTarget = self.chooseMainTarget() # To select
                                                          # a new
                                                          # mainTarget
                                                          # after
                                                          # incorporating
                                                          # a new peer
                                                          # to the
                                                          # regular
                                                          # list
            else:
                self.team_socket.sendto(self.receive_and_feed_previous, peer)

            return

            # self.team_socket.sendto(self.get_poisoned_chunk(self.receive_and_feed_previous), peer)
            # self.sendto_counter += 1
            # return

        if self.onOffAttack:
            x = random.randint(1, 100)
            if (x <= self.onOffRatio):
                self.team_socket.sendto(self.get_poisoned_chunk(self.receive_and_feed_previous), peer)
            else:
                self.team_socket.sendto(self.receive_and_feed_previous, peer)

            self.sendto_counter += 1
            return

        if self.selectiveAttack:
            if peer in self.selectedPeersForSelectiveAttack:
                self.team_socket.sendto(self.get_poisoned_chunk(self.receive_and_feed_previous), peer)
            else:
                self.team_socket.sendto(self.receive_and_feed_previous, peer)

            self.sendto_counter += 1
            return

        self.team_socket.sendto(self.receive_and_feed_previous, peer)
        self.sendto_counter += 1

    def get_poisoned_chunk(self, message):
        if len(message) == struct.calcsize(self.message_format):
            n, m, k1, k2 = struct.unpack(self.message_format, message)
            return struct.pack(self.message_format, n, "0", k1, k2)
        return message

    def setPersistentAttack(self, value):
        self.persistentAttack = value

    def setOnOffAttack(self, value, ratio):
        self.onOffAttack = value
        self.onOffRatio = ratio

    def setSelectiveAttack(self, value, selected):
        self.selectiveAttack = True
        for peer in selected:
            l = peer.split(':')
            peer_obj = (l[0], int(l[1]))
            self.selectedPeersForAttack.append(peer_obj)

    def setBadMouthAttack(self, value, selected):
        self.badMouthAttack = value
        if value:
            for peer in selected:
                l = peer.split(':')
                peer_obj = (l[0], int(l[1]))
                self.bad_peers.append(peer_obj)
        else:
            self.bad_peers = []

    def handle_bad_peers_request(self):
        msg = struct.pack("3sH", "bad", len(self.regularPeers))
        self.team_socket.sendto(msg, self.splitter)
        for peer in self.regularPeers:
            ip = struct.unpack("!L", socket.inet_aton(peer[0]))[0]
            msg = struct.pack('ii', ip, peer[1])
            self.team_socket.sendto(msg, self.splitter)
        return -1

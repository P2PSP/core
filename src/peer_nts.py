# This code is distributed under the GNU General Public License (see
# THE_GENERAL_GNU_PUBLIC_LICENSE.txt for extending this information).
# Copyright (C) 2015, the P2PSP team.
# http://www.p2psp.org

# The P2PSP.org project has been supported by the Junta de Andalucia
# through the Proyecto Motriz "Codificacion de Video Escalable y su
# Streaming sobre Internet" (P10-TIC-6548).

# {{{

import threading
import sys
from color import Color
from _print_ import _print_
from peer_dbs import Peer_DBS

# }}}

# NTS: NAT Traversal Set of rules
class Peer_NTS(Peer_DBS):
    # {{{

    def __init__(self, peer):
        # {{{

        sys.stdout.write(Color.yellow)
        _print_("Peer NTS")
        sys.stdout.write(Color.none)

        threading.Thread.__init__(self)

        self.splitter_socket = peer.splitter_socket
        self.player_socket = peer.player_socket
        self.buffer_size = peer.buffer_size
        self.splitter = peer.splitter
        self.chunk_size = peer.chunk_size
        self.message_format = peer.message_format

        # }}}

    def say_hello(self, node):
        # {{{

        self.team_socket.sendto(b'H', node)

        # }}}

    def say_goodbye(self, node):
        # {{{

        self.team_socket.sendto(b'G', node)

        # }}}

    def disconnect_from_the_splitter(self):
        # {{{

        # Close the TCP socket
        Peer_DBS.disconnect_from_the_splitter(self)

        # Use UDP to create a working NAT entry
        self.say_hello(self.splitter)
        self.say_hello(self.splitter)
        self.say_hello(self.splitter)

        # }}}

    def process_next_message(self):
        # {{{ Now, receive and send.

        try:
            # {{{ Receive and send

            message, sender = self.receive_the_next_message()

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
                        _print_("NTS:", self.team_socket.getsockname(), \
                            Color.red, "<-", Color.none, chunk_number, "-", sender)

                    # }}}

                    while( (self.receive_and_feed_counter < len(self.peer_list)) and (self.receive_and_feed_counter > 0) ):
                        peer = self.peer_list[self.receive_and_feed_counter]
                        self.team_socket.sendto(self.receive_and_feed_previous, peer)
                        self.sendto_counter += 1

                        # {{{ debug

                        if __debug__:
                            print ("NTS:", self.team_socket.getsockname(), "-",\
                                socket.ntohs(struct.unpack(self.message_format, \
                                                               self.receive_and_feed_previous)[0]),\
                                Color.green, "->", Color.none, peer)

                        # }}}

                        self.debt[peer] += 1
                        if self.debt[peer] > self.MAX_CHUNK_DEBT:
                            print (Color.red, "NTS:", peer, 'removed by unsupportive (' + str(self.debt[peer]) + ' lossess)', Color.none)
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
                        print ("NTS:", self.team_socket.getsockname(), \
                            Color.green, "<-", Color.none, chunk_number, "-", sender)

                    # }}}

                    if sender not in self.peer_list:
                        # The peer is new
                        self.peer_list.append(sender)
                        self.debt[sender] = 0
                        print (Color.green, "NTS:", sender, 'added by chunk', \
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
                    self.team_socket.sendto(self.receive_and_feed_previous, peer)
                    self.sendto_counter += 1

                    self.debt[peer] += 1
                    if self.debt[peer] > self.MAX_CHUNK_DEBT:
                        print (Color.red, "NTS:", peer, 'removed by unsupportive (' + str(self.debt[peer]) + ' lossess)', Color.none)
                        del self.debt[peer]
                        self.peer_list.remove(peer)

                    # {{{ debug

                    if __debug__:
                        print ("NTS:", self.team_socket.getsockname(), "-", \
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
                print("NTS: Control received")
                if message == 'H':
                    if sender not in self.peer_list:
                        # The peer is new
                        self.peer_list.append(sender)
                        self.debt[sender] = 0
                        print (Color.green, "NTS:", sender, 'added by [hello]', Color.none)
                else:
                    if sender in self.peer_list:
                        sys.stdout.write(Color.red)
                        print ("NTS:", self.team_socket.getsockname(), '\b: received "goodbye" from', sender)
                        sys.stdout.write(Color.none)
                        self.peer_list.remove(sender)
                        del self.debt[sender]
                return -1

                # }}}

            # }}}
        except socket.timeout:
            return -2
        #except socket.error:
        #    return -3

        # }}}

    # }}}

    # }}}

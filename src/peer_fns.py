# This code is distributed under the GNU General Public License (see
# THE_GENERAL_GNU_PUBLIC_LICENSE.txt for extending this information).
# Copyright (C) 2014, the P2PSP team.

# {{{ Imports
import threading
import sys
from peer_ims import Peer_IMS
from peer_dbs import Peer_DBS
from _print_ import _print_
from color import Color
# }}}

# Full-cone Nat Set of rules
class Peer_FNS(Peer_DBS):
    # {{{

    def __init__(self, peer):
        # {{{

        sys.stdout.write(Color.yellow)
        _print_("Peer FNS")
        sys.stdout.write(Color.none)

        #Peer_DBS.__init__(self, peer)
        #self = peer

        threading.Thread.__init__(self)

        self.splitter_socket = peer.splitter_socket
        self.player_socket = peer.player_socket
        self.buffer_size = peer.buffer_size
        self.chunk_format_string = peer.chunk_format_string
        self.splitter = peer.splitter
        self.chunk_size = peer.chunk_size
        self.peer_list = peer.peer_list
        self.debt = peer.debt

        # }}}

    def print_the_module_name(self):
        # {{{

        sys.stdout.write(Color.yellow)
        _print_("Peer FNS")
        sys.stdout.write(Color.none)

        # }}}

    def say_hello(self, node):
        # {{{

        self.team_socket.sendto('H', node)

        # }}}

    def say_goodbye(self, node):
        # {{{

        self.team_socket.sendto('G', node)

        # }}}

    def disconnect_from_the_splitter(self):
        # {{{

        Peer_IMS.disconnect_from_the_splitter(self)
        self.say_hello(self.splitter)
        self.say_hello(self.splitter)
        self.say_hello(self.splitter)

        # }}}
        
    ## def run(self):
    ##     # {{{

    ##     self.wait_for_the_player()
    ##     self.connect_to_the_splitter()
    ##     self.receive_the_header()
    ##     self.receive_the_buffersize()
    ##     self.receive_the_chunksize()
    ##     self.setup_team_socket()
    ##     self.retrieve_the_list_of_peers()
    ##     self.splitter_socket.close()
    ##     # BEGIN NEW
    ##     self.say_hello(self.splitter)
    ##     self.say_hello(self.splitter)
    ##     self.say_hello(self.splitter)
    ##     # END NEW
    ##     self.create_buffer()
    ##     self.buffer_data()
    ##     self.buffering.set()
    ##     self.peers_life()
    ##     self.polite_farewell()

    ##     # }}}

    # }}}

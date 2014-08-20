# This code is distributed under the GNU General Public License (see
# THE_GENERAL_GNU_PUBLIC_LICENSE.txt for extending this information).
# Copyright (C) 2014, the P2PSP team.

import threading
from peer_dbs import Peer_DBS
from monitor_dbs import Monitor_DBS
from peer_fns import Peer_FNS
from _print_ import _print_

class Monitor_FNS(Monitor_DBS, Peer_FNS):
    # {{{

    def __init__(self, peer):
        # {{{

        #Monitor_DBS.__init__(self)
        #Peer_DBS.__init__(self)

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
        _print_("Monitor FNS")
        sys.stdout.write(Color.none)

        # }}}

    def say_hello(self, node):
        # {{{

        Peer_FNS.say_hello(self, node)

        # }}}

    def say_goodbye(self, node):
        # {{{

        Peer_FNS.say_goodbye(self, node)

        # }}}

    def disconnect_from_the_splitter(self):
        # {{{

        Peer_FNS.disconnect_from_the_splitter(self)

        # }}}

    ## def run(self):
    ##     # {{{

    ##     Peer_FNS.run(self)

    ##     # }}}

    # }}}

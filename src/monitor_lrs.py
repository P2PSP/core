# This code is distributed under the GNU General Public License (see
# THE_GENERAL_GNU_PUBLIC_LICENSE.txt for extending this information).
# Copyright (C) 2014, the P2PSP team.

import threading
from _print_ import _print_
from monitor_fns import Monitor_FNS

# Lost chunks Recovery Set of rules
class Monitor_LRS(Monitor_FNS):
    # {{{

    def __init__(self, peer):
        # {{{

        Monitor_FNS.__init__(self, peer)

        # }}}

    def print_the_module_name(self):
        # {{{

        sys.stdout.write(Color.yellow)
        _print_("Monitor LRS")
        sys.stdout.write(Color.none)

        # }}}

    def receive_the_buffer_size(self):
        # {{{

        message = self.splitter_socket.recv(struct.calcsize("H"))
        buffer_size = struct.unpack("H", message)[0]
        self.buffer_size = socket.ntohs(buffer_size)
        # Monitor peers that implements the LRS use a smaller buffer
        # in order to complains before the rest of peers reach them in
        # their buffers.
        self.buffer_size /= 2
        print ("buffer_size =", self.buffer_size)

        # }}}

    # }}}

from peer_dbs import Peer_DBS
from monitor_dbs import Monitor_DBS
from peer_fns import Peer_FNS

class Monitor_FNS(Monitor_DBS, Peer_FNS):
    # {{{

    def __init__(self):
        # {{{

        Monitor_DBS.__init__(self)
        Peer_DBS.__init__(self)

        sys.stdout.write(Color.yellow)
        print ("Monitor FNS")
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

    def run(self):
        # {{{

        Peer_FNS.run(self)

        # }}}

    # }}}

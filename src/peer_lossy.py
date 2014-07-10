from peer_fns import Peer_FNS

class Peer_Lossy(Peer_FNS):
    # {{{

    CHUNK_LOSS_PERIOD = 0

    def __init__(self):
        # {{{

        Peer_FNS.__init__(self)

        sys.stdout.write(Color.yellow)
        print ("Peer Lossy")
        sys.stdout.write(Color.none)

        # }}}

    def setup_team_socket(self):
        # {{{ Create "team_socket" (UDP) as a copy of "splitter_socket" (TCP)

        self.team_socket = lossy_socket(self.CHUNK_LOSS_PERIOD, socket.AF_INET, socket.SOCK_DGRAM)
        try:
            # In Windows systems this call doesn't work!
            self.team_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        except Exception, e:
            print (e)
            pass
        self.team_socket.bind(('', self.splitter_socket.getsockname()[PORT]))

        # This is the maximum time the peer will wait for a chunk
        # (from the splitter or from another peer).
        self.team_socket.settimeout(1)

        # }}}

    # }}}

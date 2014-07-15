# This is a peer that does not know if is IMS or DBS until receiving
# this information from the splitter.

from __future__ import print_function

class Peer_mother():
    # {{{

    # {{{ Class "constants"

    SPLITTER_ADDR = "localhost" # Address of the splitter.
    SPLITTER_PORT = 4552        # Port of the splitter.
    TEAM_PORT = 0               # TCP port used to communicate the splitter.

    # }}}

    def __init__(self):
        # {{{

        print("Running in", end=' ')
        if __debug__:
            print("debug mode")
        else:
            print("release mode")

        self.print_modulename()

        print("Splitter address =", self.SPLITTER_ADDR)
        print("Splitter port =", self.SPLITTER_PORT)
        print("Team port =", self.TEAM_PORT)

        # }}}

    def print_modulename(self):
        # {{{

        sys.stdout.write(Color.yellow)
        print("Peer mother")
        sys.stdout.write(Color.none)

        # }}}

    def connect_to_the_splitter(self):
        # {{{ 
        
        splitter_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print ("Connecting to the splitter at", self.splitter)
        if self.TEAM_PORT != 0:
            try:
                splitter_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            except Exception, e:
                print (e)
                pass
            sys.stdout.write(Color.purple)
            print ("I'm using port the port", self.TEAM_PORT)
            sys.stdout.write(Color.none)
            splitter_socket.bind(("", self.TEAM_PORT))
        try:
            splitter_socket.connect(self.splitter)
        except Exception, e:
            print(e)
            sys.exit("Sorry. Can't connect to the splitter at " + str(self.splitter))
        print("Connected to the splitter at", self.splitter)

        return splitter_socket

        # }}}

    def receive_the_mcast_channel(self):
        # {{{

        message = self.splitter_socket.recv(struct.calcsize("4sH"))
        mcast_addr, mcast_port = struct.unpack("4sH", message)
        mcast_addr = socket.inet_ntoa(mcast_addr)
        mcast_port = socket.ntohs(mcast_port)
        mcast_channel = (mcast_addr, mcast_port)
        if __debug__:
            print ("mcast_channel =", mcast_channel)

        return mcast_channel

        # }}}

    def run(self):
        # {{{

        self.splitter = (self.SPLITTER_ADDR, self.SPLITTER_PORT)
        self.splitter_socket = self.connect_to_the_splitter()
        self.mcast_channel = self.receive_the_mcast_channel()
        self.splitter_socket.close()

        # }}}

    def start(self):
        run(self)

    # }}}


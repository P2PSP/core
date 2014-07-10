# Full-cone Nat Set of Rules

from peer_dbs import Peer_DBS

class Peer_FNS(Peer_DBS):
    # {{{

    def __init__(self):
        # {{{

        Peer_DBS.__init__(self)

        sys.stdout.write(Color.yellow)
        print ("Peer FNS")
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

    def run(self):
        # {{{

        self.wait_for_the_player()
        self.connect_to_the_splitter()
        self.receive_the_header()
        self.receive_the_buffersize()
        self.receive_the_chunksize()
        self.setup_team_socket()
        self.retrieve_the_list_of_peers()
        self.splitter_socket.close()
        # BEGIN NEW
        self.say_hello(self.splitter)
        self.say_hello(self.splitter)
        self.say_hello(self.splitter)
        # END NEW
        self.create_buffer()
        self.buffer_data()
        self.buffering.set()
        self.peers_life()
        self.polite_farewell()

        # }}}

    # }}}

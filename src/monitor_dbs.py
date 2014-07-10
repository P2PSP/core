class Monitor_DBS(Peer_DBS):
    # {{{

    def __init__(self):
        # {{{

        Peer_DBS.__init__(self)

        sys.stdout.write(Color.yellow)
        print("Monitor DBS")
        sys.stdout.write(Color.none)

        # }}}

    def complain(self, chunk_number):
        # {{{

        #message = struct.pack("!H", (chunk_number % self.buffer_size))
        message = struct.pack("!H", chunk_number)
        self.team_socket.sendto(message, self.splitter)

        if __debug__:
            sys.stdout.write(Color.blue)
            print ("lost chunk:", self.numbers[chunk_number % self.buffer_size], chunk_number, self.received[chunk_number % self.buffer_size])
            sys.stdout.write(Color.none)

        # }}}

    def find_next_chunk(self):
        # {{{

        chunk_number = (self.played_chunk + 1) % common.MAX_CHUNK_NUMBER
        while not self.received[chunk_number % self.buffer_size]:
            self.complain(chunk_number)
            chunk_number = (chunk_number + 1) % common.MAX_CHUNK_NUMBER
        return chunk_number

        # }}}

    # }}}

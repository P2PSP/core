# Adaptive Chunk-rate Set of rules
class Splitter_ACS(Splitter_FNS):
    # {{{

    def __init__(self):
        # {{{

        Splitter_FNS.__init__(self)

        self.period = {}                         # Indexed by a peer (IP address, port)
        self.period_counter = {}                 # Indexed by a peer (IP address, port)
        self.number_of_sent_chunks_per_peer = {} # Indexed by a peer (IP address, port)

        # }}}

    def print_modulename(self):
        # {{{

        sys.stdout.write(Color.yellow)
        print("Using ACS")
        sys.stdout.write(Color.none)

        # }}}

    def append_peer(self, peer):
        # {{{

        Splitter_DBS.append_peer(self, peer)
        self.period[peer] = self.period_counter[peer] = 1
        self.number_of_sent_chunks_per_peer[peer] = 0

        # }}}

    def increment_unsupportivity_of_peer(self, peer):
        # {{{

        Splitter_DBS.increment_unsupportivity_of_peer(self, peer)
        try:
            if peer != self.peer_list[0]:
                self.period[peer] += 1
                self.period_counter[peer] = self.period[peer]
        except KeyError:
            pass

        # }}}

    def remove_peer(self, peer):
        # {{{

        Splitter_DBS.remove_peer(self, peer)
        try:
            del self.period[peer]
        except KeyError:
            pass

        try:
            del self.period_counter[peer]
        except KeyError:
            pass

        try:
            del self.number_of_sent_chunks_per_peer[peer]
        except KeyError:
            pass

        # }}}

    def reset_counters(self):
        Splitter_DBS.reset_counters(self)
        for i in self.period:
            #self.period[i] = ( self.period[i] + 1 ) / 2
            self.period[i] -= 1
            if self.period[i] < 1:
                self.period[i] = 1
            #self.period_counter[i] = self.period[i]

    def run(self):
        # {{{

        try:
            self.setup_peer_connection_socket()
        except:
            print(self.peer_connection_socket.getsockname(), "\b: unable to bind", (self.TEAM_ADDR, self.TEAM_PORT))
            sys.exit('')

        try:
            self.setup_team_socket()
        except:
            print(self.team_socket.getsockname(), "\b: unable to bind", (self.TEAM_ADDR, self.TEAM_PORT))
            sys.exit('')

        source_socket = self.request_video()

        for i in xrange(self.HEADER_CHUNKS):
            self.header += self.receive_next_chunk(source_socket, 0)[0]

        print(self.peer_connection_socket.getsockname(), "\b: waiting for the monitor peer ...")
        self.handle_peer_arrival(self.peer_connection_socket.accept())
        threading.Thread(target=self.handle_arrivals).start()
        threading.Thread(target=self.moderate_the_team).start()
        threading.Thread(target=self.reset_counters_thread).start()

        header_length = 0

        while self.alive:
            # Receive data from the source
            chunk, source_socket, header_length = self.receive_next_chunk(source_socket, header_length)

            if header_length > 0:
                print("Header length =", header_length)
                self.header += chunk
                header_length -= 1

            try:
                peer = self.peer_list[self.peer_number]
            except:
                pass

            message = struct.pack(self.chunk_format_string, socket.htons(self.chunk_number), chunk)
            self.team_socket.sendto(message, peer)
            try:
                self.number_of_sent_chunks_per_peer[peer] += 1
            except KeyError:
                pass
            ## try:
            ##     self.period[peer] -= 1
            ##     if self.period[peer] < 1:
            ##          self.period[peer] = 1
            ##     #self.period_counter[peer] = self.period[peer]
            ## except KeyError:
            ##     pass
            ## #self.period[peer] = ( self.period[peer] + 1 ) / 2
            ## #self.period_counter[peer] = self.period[peer]

            if __debug__:
                print('%5d' % self.chunk_number, Color.red, '->', Color.none, peer)
                sys.stdout.flush()

            self.destination_of_chunk[self.chunk_number % self.BUFFER_SIZE] = peer
            self.chunk_number = (self.chunk_number + 1) % MAX_CHUNK_NUMBER

            try:
                while self.period_counter[peer] != 0:
                    self.period_counter[peer] -= 1
                    self.peer_number = (self.peer_number + 1) % len(self.peer_list)
                    peer = self.peer_list[self.peer_number]
                self.period_counter[peer] = self.period[peer] # ojo, inservible?
            except KeyError:
                pass

        # }}}

    # }}}

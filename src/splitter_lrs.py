# Lost chunk Recovery Set of rules
class Splitter_LRS(Splitter_ACS):
    # {{{

    def __init__(self):
        # {{{

        Splitter_ACS.__init__(self)

        sys.stdout.write(Color.yellow)
        print("Using LRS")
        sys.stdout.write(Color.none)

        # A circular array of messages (chunk_number, chunk) in network endian
        self.buffer = [""]*self.BUFFER_SIZE

        # }}}

    def process_lost_chunk(self, lost_chunk_number, sender):
        # {{{

        Splitter_ACS.process_lost_chunk(self, lost_chunk_number, sender)
        message = self.buffer[lost_chunk_number % self.BUFFER_SIZE]
        peer = self.peer_list[0]
        self.team_socket.sendto(message, peer)
        #self.number_of_sent_chunks_per_peer[peer] += 1
        #self.destination_of_chunk[self.chunk_number % self.BUFFER_SIZE] = peer
        #number, chunk = struct.unpack(self.chunk_format_string, message)
        #chunk_number = socket.ntohs(number)
        if __debug__:
            sys.stdout.write(Color.cyan)
            print ("Re-sending", lost_chunk_number, "to", peer)
            sys.stdout.write(Color.none)

        # }}}

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

        #chunk_format_string = "H" + str(self.CHUNK_SIZE) + "s" +"F" # "H1024sF
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

            #message = struct.pack(chunk_format_string, socket.htons(self.chunk_number), chunk, time.time())
            message = struct.pack(self.chunk_format_string, socket.htons(self.chunk_number), chunk)

            self.team_socket.sendto(message, peer)
            try:
                self.number_of_sent_chunks_per_peer[peer] += 1
            except KeyError:
                pass
            # B E G I N   N E W
            self.buffer[self.chunk_number % self.BUFFER_SIZE] = message
            # E N D   N E W

            if __debug__:
                print('%5d' % self.chunk_number, Color.red, '->', Color.none, peer)
                sys.stdout.flush()

            self.destination_of_chunk[self.chunk_number % self.BUFFER_SIZE] = peer
            if __debug__:
                for i in xrange(self.BUFFER_SIZE):
                    print (i, self.destination_of_chunk[i])
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

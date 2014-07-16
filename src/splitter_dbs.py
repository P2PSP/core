# Data Broadcasting Set of rules

from __future__ import print_function
import threading

# Some useful definitions.
ADDR = 0
PORT = 1

class Splitter_DBS(threading.Thread):
    # {{{

    # {{{ Class "constants"

    # {{{

    # The buffer_size depends on the stream bit-rate and the maximun
    # latency experimented by the users, and must be transmitted to
    # the peers. The buffer_size is proportional to the bit-rate and
    # the latency is proportional to the buffer_size.

    # }}}
    BUFFER_SIZE = 256

    # {{{

    # The chunk_size depends mainly on the network technology and
    # should be selected as big as possible, depending on the MTU and
    # the bit-error rate.

    # }}}
    CHUNK_SIZE = 1024

    # {{{

    # Channel served by the streaming source.

    # }}}
    CHANNEL = "/root/Videos/Big_Buck_Bunny_small.ogv"

    # {{{

    # The streaming server.

    # }}}
    SOURCE_ADDR = "150.214.150.68"

    # {{{

    # Port where the streaming server is listening.
    # }}}
    SOURCE_PORT = 4551

    # {{{ IP address to talk with the peers (a host can use several
    # network adapters).
    # }}}

    TEAM_ADDR = "150.214.150.68"

    # {{{ Port to talk with the peers.
    # }}}
    TEAM_PORT = 4552

    # {{{ Maximum number of lost chunks for an unsupportive peer.
    # }}}
    HEADER_CHUNKS = 10 # In chunks

    # {{{ Threshold to reject a peer from the team.
    # }}}
    LOSSES_THRESHOLD = 128

    # {{{ Number of chunks that must be sent to divide by 2 the number
    # of lost chunks.
    # }}}
    LOSSES_MEMORY = 1024

    MAX_NUMBER_OF_MONITORS = 1

    # }}}

    def __init__(self):
        # {{{

        threading.Thread.__init__(self)

        print("Running in", end=' ')
        if __debug__:
            print("debug mode")
        else:
            print("release mode")

        self.print_modulename()
        print("Buffer size =", self.BUFFER_SIZE)
        print("Chunk size =", self.CHUNK_SIZE)
        print("Channel =", self.CHANNEL)
        print("Source IP address =", self.SOURCE_ADDR)
        print("Source port =", self.SOURCE_PORT)
        print("(Team) IP address =", self.TEAM_ADDR)
        print("(Team) Port =", self.TEAM_PORT)

        # {{{

        # A splitter runs 3 threads. The first one controls the peer
        # arrivals. The second one listens to the team, for example,
        # to re-sends lost blocks. The third one shows some
        # information about the transmission. This variable is used to
        # stop the child threads. They will be alive only while the
        # main thread is alive.

        # }}}
        self.alive = True

        # {{{

        # The list of peers in the team.

        # }}}
        self.peer_list = []

        # {{{

        # Destination peers of the chunk, indexed by a chunk
        # number. Used to find the peer to which a chunk has been
        # sent.

        # }}}
        self.destination_of_chunk = [('0.0.0.0',0)] * self.BUFFER_SIZE
        #for i in xrange(self.BUFFER_SIZE):
        #    self.destination_of_chunk.append(('0.0.0.0',0))
        self.losses = {}

        # {{{

        # Counts the number of times a peer has been removed from the team.

        # }}}
        #self.deletions = {}

        self.chunk_number = 0

        # {{{

        # Used to listen to the incomming peers.

        # }}}
        self.peer_connection_socket = ""

        # {{{

        # Used to listen the team messages.

        # }}}
        self.team_socket = ""

        self.peer_number = 0

        self.header = ""

        self.source = (self.SOURCE_ADDR, self.SOURCE_PORT)
        self.GET_message = 'GET ' + self.CHANNEL + ' HTTP/1.1\r\n'
        self.GET_message += '\r\n'

        self.number_of_monitors = 0

        self.chunk_format_string = "H" + str(self.CHUNK_SIZE) + "s" # "H1024s

        # }}}

    def print_modulename(self):
        # {{{

        sys.stdout.write(Color.yellow)
        print("Splitter DBS")
        sys.stdout.write(Color.none)

        # }}}

    def say_goodbye(self, node, sock):
        # {{{

        sock.sendto('', node)

        # }}}

    def send_the_header(self, peer_serve_socket):
        # {{{

        if __debug__:
            print("Sending a header of", len(self.header), "bytes")
        peer_serve_socket.sendall(self.header)

        # }}}

    def send_the_buffersize(self, peer_serve_socket):
        # {{{

        if __debug__:
            print("Sending a buffer_size of", self.BUFFER_SIZE, "bytes")
        message = struct.pack("H", socket.htons(self.BUFFER_SIZE))
        peer_serve_socket.sendall(message)

        # }}}

    def send_the_chunksize(self, peer_serve_socket):
        # {{{

        if __debug__:
            print("Sending a chunk_size of", self.CHUNK_SIZE, "bytes")
        message = struct.pack("H", socket.htons(self.CHUNK_SIZE))
        peer_serve_socket.sendall(message)

        # }}}

    def send_the_debt_memory(self, peer_serve_socket):
        # {{{

        if __debug__:
            print("Sending a debt_memory of", self.CHUNK_DEBT_MEMORY)
        message = struct.pack("H", socket.htons(self.CHUNK_MEMORY))
        peer_serve_socket.sendall(message)

        # }}}

    def send_the_debt_threshold(self, peer_serve_socket):
        # {{{

        if __debug__:
            print("Sending a debt_threshold of", self.CHUNK_DEBT_THRESHOLD)
        message = struct.pack("H", socket.htons(self.CHUNK_THRESHOLD))
        peer_serve_socket.sendall(message)

        # }}}

    def send_the_listsize(self, peer_serve_socket):
        # {{{

        if __debug__:
            print("Sending a list of peers of size", len(self.peer_list))
        message = struct.pack("H", socket.htons(len(self.peer_list)))
        peer_serve_socket.sendall(message)

        # }}}

    def send_you_are_a_monitor(self, peer_serve_socket, yes_or_not):
        # {{{

        if __debug__:
            print("Sending that your are a monitor peer")
        if yes_or_not == True:
            message = struct.pack("c", 255)
        else:
            message = struct.pack("c", 0)
        peer_serve_socket.sendall(message)

        # }}}

    def send_list(self, peer_serve_socket):
        # {{{

        if __debug__:
            counter = 0
        for p in self.peer_list:
            message = struct.pack("4sH", socket.inet_aton(p[ADDR]), socket.htons(p[PORT]))
            peer_serve_socket.sendall(message)
            if __debug__:
                print("[%5d]" % counter, p)
                counter += 1

        # }}}

    def append_peer(self, peer):
        # {{{

        if peer not in self.peer_list:
            self.peer_list.append(peer)
        #self.deletions[peer] = 0
        self.losses[peer] = 0

        # }}}

    def are_you_a_monitor(self):
        # {{{

        self.number_of_monitors += 1
        if self.counter_monitors < self.MAX_NUMBER_OF_MONITORS:
            return True
        else:
            self.number_of_monitors = self.MAX_NUMBER_OF_MONITORS
            return False

        # }}}

    def send_you_are_a_monitor(self, sock):
        pass

    # Pensar en reutilizar Splitter_IMS.handle_peer_arrival()
    # concatenando las llamadas a las funciones.
    
    def handle_peer_arrival(self, connection):
        # {{{

        # {{{ Handle the arrival of a peer. When a peer want to join a
        # team, first it must establish a TCP connection with the
        # splitter. In that connection, the splitter sends to the
        # incomming peer the list of peers. Notice that the
        # transmission of the list of peers (something that could need
        # some time if the team is big or the peer is slow) is done in
        # a separate thread. This helps to avoid a DoS
        # (Denial of Service) attack.
        # }}}

        sys.stdout.write(Color.green)
        sock = connection[0]
        peer = connection[1]
        print(sock.getsockname(), '\b: accepted connection from peer', peer)
        self.send_mcast_channel(sock)
        if self.are_you_a_monitor():
            self.send_you_are_a_monitor(sock)
        self.send_the_header(sock)
        self.send_the_buffersize(sock)
        self.send_the_chunksize(sock)
        self.send_the_debt_memory(sock)
        self.send_the_debt_threshold(sock)
        self.send_the_listsize(sock)
        self.send_the_list(sock)
        sock.close()
        self.append_peer(peer)
        sys.stdout.write(Color.none)

        # }}}

    def handle_arrivals(self):
        # {{{

        while self.alive:
            connection = self.peer_connection_socket.accept()
            threading.Thread(target=self.handle_peer_arrival, args=(connection, False, )).start()

        # }}}

    def receive_message(self):
        # {{{

        return self.team_socket.recvfrom(struct.calcsize("H"))

        # }}}

    def get_lost_chunk_number(self, message):
        # {{{

        return struct.unpack("!H",message)[0]

        # }}}

    def get_losser(self, lost_chunk_number):
        # {{{
        
        return self.destination_of_chunk[lost_chunk_number % self.BUFFER_SIZE]

        # }}}

    def remove_peer(self, peer):
        # {{{

        try:
            self.peer_list.remove(peer)
        except ValueError:
            pass
        else:
            self.peer_number -= 1

        try:
            del self.losses[peer]
        except KeyError:
            pass

          #try:
          #     del self.deletions[peer]
          #except KeyError:
          #     pass

        # }}}

    def increment_unsupportivity_of_peer(self, peer):
        # {{{

        try:
            self.losses[peer] += 1
        except KeyError:
            print("the unsupportive peer", peer, "does not exist!")
        else:
            if __debug__:
                sys.stdout.write(Color.blue)
                print(peer, "has loss", self.losses[peer], "chunks")
                sys.stdout.write(Color.none)
            if self.losses[peer] > self.LOSSES_THRESHOLD:
                sys.stdout.write(Color.red)
                print(peer, 'removed')
                self.remove_peer(peer)
                sys.stdout.write(Color.none)
        finally:
           pass

        # }}}

    def process_lost_chunk(self, lost_chunk_number, sender):
        # {{{

        destination = self.get_losser(lost_chunk_number)

        if __debug__:
            
            sys.stdout.write(Color.cyan)
            print(sender, "complains about lost chunk", lost_chunk_number, "sent to", destination)
            sys.stdout.write(Color.none)

            if destination == self.peer_list[0]:
                print ("=============================")
                print ("Lost chunk index =", lost_chunk_number)
                print ("=============================")

        self.increment_unsupportivity_of_peer(destination)

        # }}}

    def process_goodbye(self, peer):
        # {{{

        sys.stdout.write(Color.green)
        print('Received "goodbye" from', peer)
        sys.stdout.write(Color.none)
        sys.stdout.flush()

        #if peer != self.peer_list[0]:
        self.remove_peer(peer)

        # }}}

    def moderate_the_team(self):
        # {{{

        while self.alive:
            # {{{

            message, sender = self.receive_message()

            if len(message) == 2:

                # {{{ The peer complains about a lost chunk.

                # In this situation, the splitter counts the number of
                # complains. If this number exceeds a threshold, the
                # unsupportive peer is expelled from the
                # team.

                lost_chunk_number = self.get_lost_chunk_number(message)
                self.process_lost_chunk(lost_chunk_number, sender)

                # }}}

            else:
                
                # {{{ The peer wants to leave the team.

                # A !2-length payload means that the peer wants to go
                # away.

                self.process_goodbye(sender)

                # }}}

            # }}}

        # }}}

    def setup_peer_connection_socket(self):
        # {{{

        # peer_connection_socket is used to listen to the incomming peers.
        self.peer_connection_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            # This does not work in Windows systems.
            self.peer_connection_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        except: # Falta averiguar excepcion
            pass

        try:
            self.peer_connection_socket.bind((self.TEAM_ADDR, self.TEAM_PORT))
        except: # Falta averiguar excepcion
            raise

        self.peer_connection_socket.listen(socket.SOMAXCONN) # Set the connection queue to the max!

        # }}}

    def setup_team_socket(self):
        # {{{

        # "team_socket" is used to talk to the peers of the team.
        self.team_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        try:
            # This does not work in Windows systems !!
            self.team_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        except:
            pass
        try:
            self.team_socket.bind((self.TEAM_ADDR, self.TEAM_PORT))
        except: # Falta averiguar excepcion
            raise

        # }}}

    def request_video(self):
        # {{{

        source_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        if __debug__:
            print(source_socket.getsockname(), 'connecting to the source', self.source, '...')
        source_socket.connect(self.source)
        if __debug__:
            print(source_socket.getsockname(), 'connected to', self.source)
        source_socket.sendall(self.GET_message)
        return source_socket

        # }}}

    def receive_next_chunk(self, sock, header_length):
        # {{{

        data = sock.recv(self.CHUNK_SIZE)
        prev_size = 0
        while len(data) < self.CHUNK_SIZE:
            if len(data) == prev_size:
                # This section of code is reached when the streaming
                # server (Icecast) finishes a stream and starts with
                # the following one.
                print('?', end='')
                sys.stdout.flush()
                #time.sleep(1)
                sock.close()
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.connect(self.source)
                sock.sendall(self.GET_message)
                self.header = ""
                header_length = self.HEADER_CHUNKS
                data = ""
            prev_size = len(data)
            data += sock.recv(self.CHUNK_SIZE - len(data))
        return data, sock, header_length

        # }}}

    def reset_counters(self):
        # {{{

        for i in self.losses:
            self.losses[i] /= 2

        # }}}

    def reset_counters_thread(self):
        # {{{

        while True:
            self.reset_counters()
            time.sleep(COUNTERS_TIMING)

        # }}}

    def run(self):
        # {{{

        try:
            self.setup_peer_connection_socket()
        except Exception, e:
            print(e)
            print(self.peer_connection_socket.getsockname(), "\b: unable to bind", (self.TEAM_ADDR, self.TEAM_PORT))
            sys.exit('')

        try:
            self.setup_team_socket()
        except Exception, e:
            print(e)
            print(self.team_socket.getsockname(), "\b: unable to bind", (self.TEAM_ADDR, self.TEAM_PORT))
            sys.exit('')

        source_socket = self.request_video()

        for i in xrange(self.HEADER_CHUNKS):
            self.header += self.receive_next_chunk(source_socket, 0)[0]

        print(self.peer_connection_socket.getsockname(), "\b: waiting for the monitor peer ...")
        def _():
            connection  = self.peer_connection_socket.accept()
            self.handle_peer_arrival(connection, True)
        _()
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
                peer = self.peer_list[self.peer_number] # Ojo, esto nunca deberia provocar una excepcion
            except KeyError:
                pass

            message = struct.pack(self.chunk_format_string, socket.htons(self.chunk_number), chunk)
            self.team_socket.sendto(message, peer)

            if __debug__:
                print('%5d' % self.chunk_number, Color.red, '->', Color.none, peer)
                sys.stdout.flush()

            self.destination_of_chunk[self.chunk_number % self.BUFFER_SIZE] = peer
            self.chunk_number = (self.chunk_number + 1) % MAX_CHUNK_NUMBER
            self.peer_number = (self.peer_number + 1) % len(self.peer_list)

        # }}}

    # }}}


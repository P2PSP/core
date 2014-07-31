# Data Broadcasting Set of rules

from __future__ import print_function
import threading
import sys
import socket
import struct
from color import Color
import common
from splitter_ims import Splitter_IMS

# Some useful definitions.
ADDR = 0
PORT = 1

class Splitter_DBS(Splitter_IMS):
    # {{{

    # {{{ Class "constants"

    # {{{ Threshold of chunk losses to reject a peer from the team.
    # }}}
    MAX_CHUNK_LOSS = 128

    MAX_NUMBER_OF_MONITORS = 1

    # }}}

    def __init__(self):
        # {{{

        supper(Splitter_DBS, self).__init__()

        self.number_of_monitors = 0
        self.peer_number = 0

        # {{{ The list of peers in the team.
        # }}}
        self.peer_list = []

        # }}}
        
        # {{{ Destination peers of the chunk, indexed by a chunk
        # number. Used to find the peer to which a chunk has been
        # sent.
        # }}}
        self.destination_of_chunk = [('0.0.0.0',0)] * self.BUFFER_SIZE
        #for i in xrange(self.BUFFER_SIZE):
        #    self.destination_of_chunk.append(('0.0.0.0',0))

        self.losses = {}

        # {{{ A splitter runs 3 threads. The first one controls the
        # peer arrivals. The second one listens to the team, for
        # example, to re-sends lost blocks. The third one shows some
        # information about the transmission. This variable is used to
        # stop the child threads. They will be alive only while the
        # main thread is alive.
        # }}}

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

    def send_the_list_size(self, peer_serve_socket):
        # {{{

        if __debug__:
            print("Sending a list of peers of size", len(self.peer_list))
        message = struct.pack("H", socket.htons(len(self.peer_list)))
        peer_serve_socket.sendall(message)

        # }}}

    def are_you_a_monitor(self):
        # {{{

        self.number_of_monitors += 1
        if self.number_of_monitors < self.MAX_NUMBER_OF_MONITORS:
            return True
        else:
            self.number_of_monitors = self.MAX_NUMBER_OF_MONITORS
            return False

        # }}}

    def send_you_are_a_monitor(self, peer_serve_socket):
        # {{{
        
        if __debug__:
            print("Sending that your are the monitor peer", peer_serve_socket.getpeername())
        if self.you_are_a_monitor():
            message = struct.pack("c", 255)
        else:
            message = struct.pack("c", 0)
        peer_serve_socket.sendall(message)

        # }}}

    def send_the_list(self, peer_serve_socket):
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

    # Pensar en reutilizar Splitter_IMS.handle_peer_arrival()
    # concatenando las llamadas a las funciones.
    
    def handle_a_peer_arrival(self, connection):
        # {{{

        # {{{ In the DBS, the splitter sends to the incomming peer the
        # list of peers. Notice that the transmission of the list of
        # peers (something that could need some time if the team is
        # big or if the peer is slow) is done in a separate thread. This
        # helps to avoid DoS (Denial of Service) attacks.
        # }}}

        sock = connection[0]
        self.send_you_are_a_monitor(sock)
        #self.send_the_debt_memory(sock)
        #self.send_the_debt_threshold(sock)
        self.send_the_list_size(sock)
        self.send_the_list(sock)
        #sock.close()
        self.append_peer(peer)

        supper(Splitter_DBS, self).handle_a_peer_arrival(connection)
                
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
            if self.losses[peer] > self.MAX_CHUNK_LOSS:
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
            self.team_socket.bind(('', self.PORT))
        except:
            raise

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

        self.receive_the_header()

        print(self.peer_connection_socket.getsockname(), "\b: waiting for the monitor peer ...")
        def _():
            connection  = self.peer_connection_socket.accept()
            self.handle_peer_arrival(connection, True)
        _()
        threading.Thread(target=self.handle_arrivals).start()
        threading.Thread(target=self.moderate_the_team).start()
        threading.Thread(target=self.reset_counters_thread).start()

        header_load_counter = 0
        while self.alive:

            chunk = self.receive_chunk(header_load_counter)

            try:
                peer = self.peer_list[self.peer_number] # Ojo, esto nunca deberia provocar una excepcion
            except KeyError:
                pass

            self.send_chunk(chunk, peer)
            
            self.destination_of_chunk[self.chunk_number % self.BUFFER_SIZE] = peer
            self.chunk_number = (self.chunk_number + 1) % MAX_CHUNK_NUMBER
            self.peer_number = (self.peer_number + 1) % len(self.peer_list)

        # }}}

    # }}}


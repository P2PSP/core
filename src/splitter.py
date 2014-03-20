#!/usr/bin/python -O
# -*- coding: iso-8859-15 -*-

# {{{ GNU GENERAL PUBLIC LICENSE

# This is the splitter node of the P2PSP (Peer-to-Peer Simple Protocol)
# <https://launchpad.net/p2psp>.
#
# Copyright (C) 2014 Vicente González Ruiz,
#                    Cristóbal Medina López,
#                    Juan Alvaro Muñoz Naranjo.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

# }}}

# This code implements the DBS splitter side of the P2PSP.

# {{{ Imports

import time
import sys
import socket
import threading
import struct
import argparse
from color import Color

# }}}

# Some useful definitions.
IP_ADDR = 0
PORT = 1

# Data Broadcasting Set of rules
class Splitter_DBS(threading.Thread):
     # {{{ 

     # {{{

     # The buffer_size depends on the stream bit-rate and
     # the maximun latency experimented by the users, and
     # must be transmitted to the peers. The buffer_size
     # is proportional to the bit-rate and the latency is
     # proportional to the buffer_size.

     # }}}
     BUFFER_SIZE = 256
     
     # {{{

     # The chunk_size depends mainly on the network
     # technology and should be selected as big as
     # possible, depending on the MTU and the bit-error
     # rate.

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

     # {{{

     # IP address to talk with the peers (a host can use
     # several network adapters).

     # }}}
     ADDR = "150.214.150.68"

     # {{{

     # Port to talk with the peers.

     # }}}
     PORT = 4552

     # {{{

     # Maximum number of lost chunks for an unsupportive peer.

     # }}}
     LOSSES_THRESHOLD = 128
     LOSSES_MEMORY = 1024

     HEADER_LENGTH = 10 # In chunks

     def __init__(self):
          # {{{

          threading.Thread.__init__(self)

          print "Splitter running in",
          if __debug__:
               print "debug mode"
          else:
               print "release mode"
               
          self.print_modulename()
          print "Buffer size =", self.BUFFER_SIZE
          print "Chunk size =", self.CHUNK_SIZE
          print "Channel =", self.CHANNEL
          print "Source IP address =", self.SOURCE_ADDR
          print "Source port =", self.SOURCE_PORT
          print "(Team) IP address =", self.ADDR
          print "(Team) Port =", self.PORT

          # {{{

          # A splitter runs 3 threads. The first one controls the peer
          # arrivals. The second one listens to the team, for example, to
          # re-sends lost blocks. The third one shows some information about
          # the transmission. This variable is used to stop the child
          # threads. They will be alive only while the main thread is alive.

          # }}}
          self.alive = True
         
          # {{{

          # The list of peers in the team.

          # }}}
          self.peer_list = []

          # {{{

          # Destination peers of the chunk, indexed by a chunk number. Used to
          # find the peer to which a chunk has been sent.

          # }}}
          self.destination_of_chunk = []
          for i in xrange(self.BUFFER_SIZE):
               self.destination_of_chunk.append(('0.0.0.0',0))
          self.losses = {}

          # {{{

          # Counts the number of times a peer has ben removed from the team.

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

          self.peer_index = 0

          self.header = ""

          # }}}

     def print_modulename(self):
          # {{{

          sys.stdout.write(Color.yellow)
          print "Using DBS"
          sys.stdout.write(Color.none)

          # }}}

     def say_goodbye(self, node, sock):
          sock.sendto('', node)

     def send_header(self, peer_serve_socket):
          # {{{

          print "Sending a header of", len(self.header), "bytes"
          peer_serve_socket.sendall(self.header)

          # }}}

     def send_buffersize(self, peer_serve_socket):
          # {{{

          print "Sending a buffer_size of", self.BUFFER_SIZE, "bytes"
          message = struct.pack("H", socket.htons(self.BUFFER_SIZE))
          peer_serve_socket.sendall(message)

          # }}}
          
     def send_chunksize(self, peer_serve_socket):
          # {{{

          print "Sending a chunk_size of", self.CHUNK_SIZE, "bytes"
          message = struct.pack("H", socket.htons(self.CHUNK_SIZE))
          peer_serve_socket.sendall(message)

          # }}}

     def send_listsize(self, peer_serve_socket):
          # {{{

          print "Sending a list of peers whose size is", len(self.peer_list)
          message = struct.pack("H", socket.htons(len(self.peer_list)))
          peer_serve_socket.sendall(message)

          # }}}

     def send_list(self, peer_serve_socket):
          # {{{

          counter = 0
          for p in self.peer_list:
                message = struct.pack("4sH", socket.inet_aton(p[IP_ADDR]), socket.htons(p[PORT]))
                peer_serve_socket.sendall(message)
                print "[%5d]" % counter, p
                counter += 1

          # }}}

     def append_peer(self, peer):
          # {{{

          if peer not in self.peer_list:
               self.peer_list.append(peer)                 
          #self.deletions[peer] = 0
          self.losses[peer] = 0

          # }}}

     def handle_peer_arrival(self, (peer_serve_socket, peer)):
          # {{{

          # {{{

          # Handle the arrival of a peer. When a peer want to join a
          # team, first it must establish a TCP connection with the
          # splitter. In that connection, the splitter sends to the
          # incomming peer the list of peers. Notice that the
          # transmission of the list of peers (something that could
          # need some time if the team is big or the peer is slow) is
          # done in a separate thread. This helps to avoid a DoS
          # (Denial-of-Service) attack.

          # }}}          

          sys.stdout.write(Color.green)
          print peer_serve_socket.getsockname(), '\b: accepted connection from peer', peer
          self.send_header(peer_serve_socket)
          self.send_buffersize(peer_serve_socket)
          self.send_chunksize(peer_serve_socket)
          self.send_listsize(peer_serve_socket)
          self.send_list(peer_serve_socket)
          peer_serve_socket.close()
          self.append_peer(peer)
          sys.stdout.write(Color.none)

          # }}}

     def handle_arrivals(self):
          # {{{

          while self.alive:
               peer_serve_socket, peer = self.peer_connection_socket.accept()
               threading.Thread(target=self.handle_peer_arrival, args=((peer_serve_socket, peer), )).start()

          # }}}

     def receive_message(self):
          # {{{

          return self.team_socket.recvfrom(struct.calcsize("H"))

          # }}}

     def get_lost_chunk_index(self, message):
          # {{{

          return struct.unpack("!H",message)[0]

          # }}}

     def get_losser(self, lost_chunk):
          # {{{

          return self.destination_of_chunk[lost_chunk]

          # }}}

     def remove_peer(self, peer):
          # {{{

          try:
               self.peer_list.remove(peer)
          except ValueError:
               pass
          else:
               self.peer_index -= 1
               
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
               print "the unsupportive peer ", peer, "does not exist!"
               for p in self.peer_list:
                    print p,
               print
          else:
               if __debug__:
                    sys.stdout.write(Color.blue)
                    print peer, "has loss", self.losses[peer], "chunks"
                    sys.stdout.write(Color.none)
               if peer != self.peer_list[0]: # Check it!!!!!
                    if self.losses[peer] > self.LOSSES_THRESHOLD:

                         sys.stdout.write(Color.red)
                         print "Too much complains about the unsupportive peer", \
                             peer, "\b. Removing it!"

                         self.remove_peer(peer)

                         sys.stdout.write(Color.none)
          finally:
               pass

          # }}}

     def process_lost_chunk(self, message, sender):
          # {{{

          lost_chunk = self.get_lost_chunk_index(message)
          destination = self.get_losser(lost_chunk)

          if __debug__:
               sys.stdout.write(Color.blue)
               print sender, "complains about lost chunk", lost_chunk, "sent to", destination
               sys.stdout.write(Color.none)

          if (destination != self.peer_list[0]):
               self.increment_unsupportivity_of_peer(destination)

          # }}}

     def process_goodbye(self, peer):
          # {{{

          sys.stdout.write(Color.red)
          print 'Received "goodbye" from', peer
          sys.stdout.write(Color.none)
          sys.stdout.flush()

          if peer != self.peer_list[0]:
               self.remove_peer(peer)

          # }}}

     def moderate_the_team(self):
          # {{{

          while self.alive:
               # {{{

               message, sender = self.receive_message()

               if len(message) == 2:

                    # {{{ The peer complains about a lost chunk.

                    # In this situation, the splitter counts the
                    # number of times a peer has not achieved to send
                    # a chunk to other peers. If this number exceeds a
                    # threshold, the unsupportive peer is expelled
                    # from the team. Moreover, if we receive too much
                    # complains from the same peer, the problem could
                    # be in that peer and it will be expelled from the
                    # team.

                    self.process_lost_chunk(message, sender)

                    # }}}

               else:
                    # {{{ The peer wants to leave the team.

                    # A !2-length payload means that the peer wants to
                    # go away.

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
               self.peer_connection_socket.bind((self.ADDR, self.PORT))
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
               self.team_socket.bind((self.ADDR, self.PORT))
          except: # Falta averiguar excepcion
               raise

          # }}}

     def request_video(self, source, GET_message):
          # {{{

          source_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
          print source_socket.getsockname(), 'connecting to the source', source, '...'
          source_socket.connect(source)
          print source_socket.getsockname(), 'connected to', source
          source_socket.sendall(GET_message)
          return source_socket

          # }}}

     def receive_next_chunk(self, GET, source, sock, size, header_length):
          # {{{

          data = sock.recv(size)
          prev_size = 0
          while len(data) < size:
               if len(data) == prev_size:
                    # This section of code is reached when
                    # the streaming server (Icecast)
                    # finishes a stream and starts with the
                    # following one.
                    print '\b!',
                    sys.stdout.flush()
                    #time.sleep(1)
                    sock.close()
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.connect(source)
                    sock.sendall(GET)
                    self.header = ""
                    header_length = self.HEADER_LENGTH
                    data = ""
               prev_size = len(data)
               data += sock.recv(size - len(data))
          return data, sock, header_length

          # }}}

     def run(self):
          # {{{

          try:
               self.setup_peer_connection_socket()
          except: # Falta averiguar excepcion
               print self.peer_connection_socket.getsockname(), "\b: unable to bind", (self.ADDR, self.PORT)
               sys.exit('')

          try:
               self.setup_team_socket()
          except: # Falta averiguar excepcion
               print self.team_socket.getsockname(), "\b: unable to bind", (self.ADDR, self.PORT)
               sys.exit('')

          source = (self.SOURCE_ADDR, self.SOURCE_PORT)
          GET_message = 'GET ' + self.CHANNEL + ' HTTP/1.1\r\n'
          GET_message += '\r\n'
          source_socket = self.request_video(source, GET_message)

          for i in xrange(self.HEADER_LENGTH):
               self.header += self.receive_next_chunk(GET_message, source, source_socket, 1024, 0)[0]

          print self.peer_connection_socket.getsockname(), "\b: waiting for the monitor peer ..."
          self.handle_peer_arrival(self.peer_connection_socket.accept())
          threading.Thread(target=self.handle_arrivals).start()
          threading.Thread(target=self.moderate_the_team).start()

          chunk_format_string = "H" + str(self.CHUNK_SIZE) + "s" # "H1024s

          header_length = 0

          while self.alive:
               # Receive data from the source
               chunk, source_socket, header_length = \
                   self.receive_next_chunk(GET_message, source, source_socket, self.CHUNK_SIZE, \
                                                    header_length)

               if header_length > 0:
                    print "Header length =", header_length
                    self.header += chunk
                    header_length -= 1

               try:
                    peer = self.peer_list[self.peer_index]
               except KeyError:
                    pass

               message = struct.pack(chunk_format_string, socket.htons(self.chunk_number), chunk)
               self.team_socket.sendto(message, peer)

               if __debug__:
                    print '%5d' % self.chunk_number, Color.red, '->', Color.none, peer
                    sys.stdout.flush()

               self.destination_of_chunk[self.chunk_number % self.BUFFER_SIZE] = peer
               self.chunk_number = (self.chunk_number + 1) % 65536
               self.peer_index = (self.peer_index + 1) % len(self.peer_list)

               # Decrement (dividing by 2) the number of losses after
               # every 256 sent chunks.
               if (self.chunk_number % Splitter_DBS.LOSSES_MEMORY) == 0:
                    for i in self.losses:
                         self.losses[i] /= 2
                    '''
                    for i in self.complains:
                         self.complains[i] /= 2
                    '''

          # }}}

     # }}}

# Full-cone Nat Set of rules
class Splitter_FNS(Splitter_DBS):
     # {{{

     def print_modulename(self):
          # {{{

          sys.stdout.write(Color.yellow)
          print "Using FNS"
          sys.stdout.write(Color.none)

          # }}}

     def say_goodbye(self, node, sock):
          sock.sendto('G', node)

     def moderate_the_team(self):
          # {{{

          while self.alive:
               # {{{

               message, sender = self.receive_message()

               if len(message) == 2:

                    # {{{ The peer complains about a lost chunk.

                    # In this situation, the splitter counts the
                    # number of times a peer has not achieved to send
                    # a chunk to other peers. If this number exceeds a
                    # threshold, the unsupportive peer is expelled
                    # from the team. Moreover, if we receive too much
                    # complains from the same peer, the problem could
                    # be in that peer and it will be expelled from the
                    # team.

                    self.process_lost_chunk(message, sender)

                    # }}}

               else:
                    # {{{ The peer wants to leave the team.

                    if struct.unpack("s", message)[0] == 'G': # <G>oodbye
                         self.process_goodbye(sender)

                    # }}}

               # }}}

          # }}}

     # }}}

# Super-Monitor Set of rules
class Splitter_SMS(Splitter_FNS):

     def __init__(self):
          Splitter_FNS.__init__(self)

          self.period = {}
          self.period_counter = {}
          self.number_of_sent_chunks_per_peer = {}

     def print_modulename(self):
          # {{{

          sys.stdout.write(Color.yellow)
          print "Using SMS"
          sys.stdout.write(Color.none)

          # }}}

     def append_peer(self, peer):
          # {{{

          Splitter_DBS.append_peer(self, peer)
          self.period[peer] = self.period_counter[peer] = 1
          self.number_of_sent_chunks_per_peer[peer] = 0

          # }}}

     def increment_unsupportivity_of_peer(self, peer):
          Splitter_DBS.increment_unsupportivity_of_peer(self, peer)
          try:
               self.period[peer] += 1
               self.period_counter[peer] = self.period[peer]
          except KeyError:
               pass

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

     def run(self):
          # {{{

          try:
               self.setup_peer_connection_socket()
          except: # Falta averiguar excepcion
               print self.peer_connection_socket.getsockname(), "\b: unable to bind", (self.ADDR, self.PORT)
               sys.exit('')

          try:
               self.setup_team_socket()
          except: # Falta averiguar excepcion
               print self.team_socket.getsockname(), "\b: unable to bind", (self.ADDR, self.PORT)
               sys.exit('')

          source = (self.SOURCE_ADDR, self.SOURCE_PORT)
          GET_message = 'GET ' + self.CHANNEL + ' HTTP/1.1\r\n'
          GET_message += '\r\n'
          source_socket = self.request_video(source, GET_message)

          for i in xrange(self.HEADER_LENGTH):
               self.header += self.receive_next_chunk(GET_message, source, source_socket, 1024, 0)[0]

          print self.peer_connection_socket.getsockname(), "\b: waiting for the monitor peer ..."
          self.handle_peer_arrival(self.peer_connection_socket.accept())
          threading.Thread(target=self.handle_arrivals).start()
          threading.Thread(target=self.moderate_the_team).start()

          chunk_format_string = "H" + str(self.CHUNK_SIZE) + "s" # "H1024s

          header_length = 0

          while self.alive:
               # Receive data from the source
               chunk, source_socket, header_length = \
                   self.receive_next_chunk(GET_message, source, source_socket, self.CHUNK_SIZE, \
                                                    header_length)

               if header_length > 0:
                    print "Header length =", header_length
                    self.header += chunk
                    header_length -= 1

               try:
                    peer = self.peer_list[self.peer_index]
               except KeyError:
                    pass

               message = struct.pack(chunk_format_string, socket.htons(self.chunk_number), chunk)
               self.team_socket.sendto(message, peer)
               self.number_of_sent_chunks_per_peer[peer] += 1

               if __debug__:
                    print '%5d' % self.chunk_number, Color.red, '->', Color.none, peer
                    sys.stdout.flush()

               self.destination_of_chunk[self.chunk_number % self.BUFFER_SIZE] = peer
               self.chunk_number = (self.chunk_number + 1) % 65536

               while self.period_counter[peer] != 0:
                    self.period_counter[peer] -= 1
                    self.peer_index = (self.peer_index + 1) % len(self.peer_list)
                    try:
                         peer = self.peer_list[self.peer_index]
                    except KeyError:
                         pass  
               self.period_counter[peer] = self.period[peer]

               # Decrement (dividing by 2) the number of losses after
               # every 256 sent chunks.
               if (self.chunk_number % Splitter_DBS.LOSSES_MEMORY) == 0:
                    for i in self.losses:
                         self.losses[i] /= 2
                    '''
                    for i in self.complains:
                         self.complains[i] /= 2
                    '''

               if (self.chunk_number % 1024) == 0:
                    for i in self.period:
                         self.period[i] = ( self.period[i] + 1 ) / 2
                         self.period_counter[i] = self.period[i]

          # }}}

def main():

     # {{{ Args parsing
     
     parser = argparse.ArgumentParser(description='This is the splitter node of a P2PSP network.')
     parser.add_argument('--addr', help='IP address to talk with the peers. (Default = "{}")'.format(Splitter_DBS.ADDR))
     parser.add_argument('--buffer_size', help='size of the video buffer in blocks. (Default = {})'.format(Splitter_DBS.BUFFER_SIZE))
     parser.add_argument('--channel', help='Name of the channel served by the streaming source. (Default = "{}")'.format(Splitter_DBS.CHANNEL))
     parser.add_argument('--chunk_size', help='Chunk size in bytes. (Default = {})'.format(Splitter_DBS.CHUNK_SIZE))
     parser.add_argument('--port', help='Port to talk with the peers. (Default = {})'.format(Splitter_DBS.PORT))
     parser.add_argument('--losses_memory', help='Number of chunks to divide by two the losses counters. (Default = {})'.format(Splitter_DBS.LOSSES_MEMORY))
     parser.add_argument('--losses_threshold', help='Maximum number of lost chunks for an unsupportive peer. (Default = {})'.format(Splitter_DBS.LOSSES_THRESHOLD))
     parser.add_argument('--source_addr', help='IP address of the streaming server. (Default = "{}")'.format(Splitter_DBS.SOURCE_ADDR))
     parser.add_argument('--source_port', help='Port where the streaming server is listening. (Default = {})'.format(Splitter_DBS.SOURCE_PORT))

     args = parser.parse_known_args()[0]
     if args.source_addr:
          Splitter_DBS.SOURCE_ADDR = socket.gethostbyname(args.source_addr)
     if args.source_port:
          Splitter_DBS.SOURCE_PORT = int(args.source_port)
     if args.channel:
          Splitter_DBS.CHANNEL = args.channel
     if args.addr:
          Splitter_DBS.ADDR = socket.gethostbyname(args.addr)
     if args.port:
          Splitter_DBS.PORT = int(args.port)
     if args.buffer_size:
          Splitter_DBS.BUFFER_SIZE = int(args.buffer_size)
     if args.chunk_size:
          Splitter_DBS.CHUNK_SIZE = int(args.chunk_size)
     if args.losses_threshold:
          Splitter_DBS.LOSSES_THRESHOLD = int(args.losses_threshold)
     if args.losses_memory:
          Splitter_DBS.LOSSES_MEMORY = int(args.losses_memory)
     
     # }}}

#     splitter = Splitter_DBS()
#     splitter = Splitter_FNS()
     splitter = Splitter_SMS()
     splitter.start()

     # {{{ Prints information until keyboard interrupt

     #last_chunk_number = 0
     while splitter.alive:
          try:
               print '%5d'% splitter.chunk_number, len(splitter.peer_list),
               for p in splitter.peer_list:
                    print p, splitter.losses[p],
                    try:
                         print splitter.period[p], splitter.number_of_sent_chunks_per_peer[p],
                    except AttributeError:
                         pass
               print
               '''
               print "[%3d] " % len(splitter.peer_list),
               kbps = (splitter.chunk_number - last_chunk_number) * \
                   splitter.CHUNK_SIZE * 8/1000
               last_chunk_number = splitter.chunk_number

               for x in xrange(0,kbps/10):
                    print "\b#",
               print kbps, "kbps"
               '''
               time.sleep(1)

          except KeyboardInterrupt:
               print 'Keyboard interrupt detected ... Exiting!'

               # Say to the daemon threads that the work has been finished,
               splitter.alive = False

               print splitter.peer_list[0]

               # Wake up the "moderate_the_team" daemon, which is waiting
               # in a cluster_sock.recvfrom(...).
               splitter.say_goodbye((splitter.ADDR, splitter.PORT), splitter.team_socket)

               # Wake up the "handle_arrivals" daemon, which is waiting in a
               # peer_connection_sock.accept().
               sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
               print splitter.ADDR, splitter.PORT
               sock.connect((splitter.ADDR, splitter.PORT))
               sock.recv(1024*10) # Header
               sock.recv(struct.calcsize("H")) # Buffer size
               sock.recv(struct.calcsize("H")) # Chunk size
               number_of_peers = socket.ntohs(struct.unpack("H", sock.recv(struct.calcsize("H")))[0])
               # Receive the list
               while number_of_peers > 0:
                    sock.recv(struct.calcsize("4sH"))
                    number_of_peers -= 1

               # Breaks this thread and returns to the parent process (usually,
               # the shell).
               break

     # }}}

if __name__ == "__main__":
     main()


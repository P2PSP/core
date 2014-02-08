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

class Splitter_DBS(threading.Thread):

     # The buffer_size depends on the stream bit-rate and
     # the maximun latency experimented by the users, and
     # must be transmitted to the peers. The buffer_size
     # is proportional to the bit-rate and the latency is
     # proportional to the buffer_size.
     buffer_size = 256
     
     # The chunk_size depends mainly on the network
     # technology and should be selected as big as
     # possible, depending on the MTU and the bit-error
     # rate.
     chunk_size = 1024
     
     # Channel served by the streaming source.
     channel = "/root/Videos/Big_Buck_Bunny_small.ogv"

     # The streaming server.
     source_host = "150.214.150.68"

     # Port where the streaming server is listening.
     source_port = 4551

     # IP address to talk with the peers (a host can use
     # several network adapters).
     team_host = "150.214.150.68"

     # Port to talk with the peers.
     team_port = 4552

     # Maximum number of lost chunks for an unsupportive peer.
     losses_threshold = 8

     # Maximum number of complains for a peevish peer.
     #complaining_threshold = 8

     def __init__(self):
          # {{{

          threading.Thread.__init__(self)
 
          # A splitter runs 3 threads. The first one controls the peer
          # arrivals. The second one listens to the team, for example, to
          # re-sends lost blocks. The third one shows some information about
          # the transmission. This variable is used to stop the child
          # threads. They will be alive only while the main thread is alive.
          self.alive = True
         
          print "Splitter running in",
          if __debug__:
               print "debug mode"
          else:
               print "release mode"
               
          # The list of peers in the team.
          self.peer_list = []
          #peer_list = [('127.0.0.1',team_port+1)]

          # Destination peers of the chunk, indexed by a chunk number. Used to
          # find the peer to which a chunk has been sent.
          self.destination_of_chunk = [('0.0.0.0',0) for i in xrange(self.buffer_size)]
          self.losses = {}

          # Counts the number of times a peer has ben removed from the team.
          self.deletions = {}

          # Complaining rate of a peer. Sometimes the complaining peer has not
          # enough bandwidth in his download link. In this case, the peevish
          # peers should be rejected from the team.
          #self.complains = {}
          #complains[('127.0.0.1',team_port+1)] = 0

          self.chunk_number = 0

          # Used to listen to the incomming peers.
          self.peer_connection_socket = ""

          # Used to listen the team messages.
          self.team_socket = ""

          self.peer_index = 0

          # }}}

     # Handle the arrival of a peer. When a peer
     # want to join a team, first it must establish a TCP connection
     # with the splitter. In that connection, the splitter sends to
     # the incomming peer the list of peers. Notice that the
     # transmission of the list of peers (something that could need
     # some time if the team is big or the peer is slow) is done in a
     # separate thread. This helps to avoid a DoS (Denial-of-Service)
     # attack.
     def handle_peer_arrival(self, (peer_serve_socket, peer)):
          # {{{
          

          sys.stdout.write(Color.green)
          print peer_serve_socket.getsockname(), '\b: accepted connection from peer', peer

          # Send the source node IP address.
          message = struct.pack("4s", socket.inet_aton(self.source_host))
          peer_serve_socket.sendall(message)

          # Send the source node listening port.
          message = struct.pack("H", socket.htons(self.source_port))
          peer_serve_socket.sendall(message)

          # Send the name of the channel.
          message = struct.pack("H", socket.htons(len(self.channel)))    
          peer_serve_socket.sendall(message)
          peer_serve_socket.sendall(self.channel)

          # Send the buffer size.
          message = struct.pack("H", socket.htons(self.buffer_size))
          peer_serve_socket.sendall(message)

          # Send the chunk size.
          message = struct.pack("H", socket.htons(self.chunk_size))
          peer_serve_socket.sendall(message)

          print peer_serve_socket.getsockname(), '\b: sending the list of peers ...'

          # Sends the size of the list of peers.
          message = struct.pack("H", socket.htons(len(self.peer_list)))
          peer_serve_socket.sendall(message)

          # Send the list of peers.
          counter = 0
          for p in self.peer_list:
                message = struct.pack("4sH", socket.inet_aton(p[IP_ADDR]), socket.htons(p[PORT]))
                peer_serve_socket.sendall(message)
                print "[%5d]" % counter, p
                counter += 1

          print 'done'
          sys.stdout.write(Color.none)

          peer_serve_socket.close()

          if peer not in self.peer_list:
               self.peer_list.append(peer)                 
               self.deletions[peer] = 0
               self.losses[peer] = 0
               #self.complains[peer] = 0

          # }}}

     def handle_arrivals(self):
          # {{{

          while self.alive:
               peer_serve_socket, peer = self.peer_connection_socket.accept()
               threading.Thread(target=self.handle_peer_arrival, args=((peer_serve_socket, peer), )).start()

          # }}}

     def moderate_the_team(self):
          # {{{

          while self.alive:
               # {{{

               message, sender = self.team_socket.recvfrom(struct.calcsize("4sH"))
               print "---------------", len(message)
               if len(message) == 0:
                    # {{{ The peer wants to leave the team

                    # A zero-length payload means that the peer wants to go away
                    sys.stdout.write(Color.red)
                    print self.team_socket.getsockname(), '\b: received "goodbye" from', sender
                    sys.stdout.write(Color.none)
                    sys.stdout.flush()
                    if sender != self.peer_list[0]:
                         try:
                              self.peer_index -= 1
                              self.peer_list.remove(sender)
                              #print Color.red, "\b", sender, 'removed by "goodbye" message', Color.none
                         except:
                              # Received a googbye message from a peer which is
                              # not in the list of peers.
                              pass

                    # }}}

               elif len(message) == 4:

                    # {{{ The peer complains about a lost chunk

                    # The sender of the packet complains, and the
                    # packet comes with the index of a lost
                    # (non-received) chunk. In this situation, the
                    # splitter counts the number of times a peer has
                    # not achieved to send a chunk to other peers. If
                    # this number exceeds a threshold, the
                    # unsupportive peer is expelled from the
                    # team. Moreover, if we receive too much complains
                    # from the same peer, the problem could be in that
                    # peer and it will be expelled from the team.

                    lost_chunk = struct.unpack("!H",message)[0]
                    destination = self.destination_of_chunk[lost_chunk]
                    sys.stdout.write(Color.blue)
                    print self.team_socket.getsockname(), "\b:", sender, "complains about lost chunk", lost_chunk, "sent to", destination, Color.none
                    sys.stdout.write(Color.none)
                    try:
                         self.losses[destination]
                    except:
                         print "the unsupportive peer does not exist ???"
                         pass
                    else:
                         self.losses[destination] += 1
                         #print Color.blue, "complains about", destination, \
                         #    "=", losses[destination], Color.none
                         if self.losses[destination] > self.losses_threshold:
                              sys.stdout.write(Color.red)
                              print self.team_socket.getsockname(), "\b: too much complains about unsupportive peer", destination, "\b. Removing it!"
                              self.peer_index -= 1
                              self.peer_list.remove(destination)
                              del self.losses[destination]
                              del self.complains[destination]
                              sys.stdout.write(Color.none)
                    finally:
                         pass


               else:
                    # {{{ The peer sends an "erased" peer

                    erased_addr, erased_port = struct.unpack("4sH", message)
                    erased_addr = socket.inet_ntoa(erased_addr)
                    erased_port = socket.ntohs(erased_port)
                    erased = (erased_addr, erased_port)
                    sys.stdout.write(Color.blue)
                    print self.team_socket.getsockname(), "\b:", sender, "says that", erased, "was removed from the team"
                    sys.stdout.write(Color.none)
                    try:
                         self.deletions[erased]
                    except:
                         print "the erased peer does not exist ???"
                         pass
                    else:
                         self.deletions[erased] += 1
                         #print Color.blue, "complains about", destination, \
                         #    "=", deletions[destination], Color.none
                         if self.deletions[erased] >= len(self.peer_list)/2:
                              sys.stdout.write(Color.red)
                              print self.team_socket.getsockname(), "\b: removing", erased
                              self.peer_index -= 1
                              try:
                                   self.peer_list.remove(erased)
                                   del self.deletions[erased]
                                   #del self.complains[erased]
                              except:
                                   pass
                              sys.stdout.write(Color.none)
                    finally:
                         pass

                    '''
                    if sender != self.peer_list[0]:
                         try:
                              self.complains[sender]
                         except:
                              print "the complaining peer does not exit ???"
                              pass
                         else:
                              #print "------------__", self.peer_list[0]
                              self.complains[sender] += 1
                              if self.complains[sender] > self.complaining_threshold:
                                   sys.stdout.write(Color.red)
                                   print self.team_socket.getsockname(), "\b: too much complains of a peevish peer", sender, "\b. Removing it!"
                                   sys.stdout.write(Color.none)
                                   self.peer_index -= 1
                                   self.peer_list.remove(sender)
                                   del self.complains[sender]
                                   del self.deletions[sender]
                         finally:
                              pass
                    '''
                    # }}}
               # }}}

          # }}}

     def run(self):
          # {{{ Setup "peer_connection_socket"

          # peer_connection_socket is used to listen to the incomming peers.
          self.peer_connection_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
          try:
               # This does not work in Windows systems.
               self.peer_connection_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
          except:
               pass
          self.peer_connection_socket.bind((self.team_host, self.team_port))
          self.peer_connection_socket.listen(socket.SOMAXCONN) # Set the connection queue to the max!

          # }}}
          # {{{ Setup "team_socket"

          # "team_socket" is used to talk to the peers of the team.
          self.team_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
          try:
               # This does not work in Windows systems !!
               self.team_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
          except:
               pass
          self.team_socket.bind((self.team_host, self.team_port))

          # }}}

          # {{{ Wait for the monitor peer

          # The fist peer that contacts the splitter is a "monitor"
          # peer that the team administrator can use to monitorize the
          # performance of the streaming. This peer MUST run on the
          # same host than the splitter to avoid bandwidth consumption
          # and usually listen to the port team_port+1 (although this
          # is configurable by the administrator selecting a different
          # peer_port). This peer MUST also use the same public IP
          # address that the splitter in order the rest of peers of
          # the team communicate with it. The splitter will use its
          # public IP address as the IP address of the monitor peer.

          #handle_peer_arrival(peer_connection_socket, peer_list, deletions)

          # }}}
          print self.peer_connection_socket.getsockname(), "\b: waiting for the monitor peer ..."
          self.handle_peer_arrival(self.peer_connection_socket.accept())
          threading.Thread(target=self.handle_arrivals).start()
          threading.Thread(target=self.moderate_the_team).start()
          
          source_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
          GET_message = 'GET ' + self.channel + ' HTTP/1.1\r\n'
          GET_message += '\r\n'
          def _():
               source = (self.source_host, self.source_port)
               print source_socket.getsockname(), 'connecting to the source', source, '...'
               source_socket.connect(source)
               print source_socket.getsockname(), 'connected to', source

               source_socket.sendall(GET_message)
          _()

          chunk_format_string = "H" + str(self.chunk_size) + "s" # "H1024s

          while self.alive:
               # Receive data from the source
               def receive_next_chunk(source_socket):
                    chunk = source_socket.recv(self.chunk_size)
                    prev_chunk_size = 0
                    while len(chunk) < self.chunk_size:
                         if len(chunk) == prev_chunk_size:
                              # This section of code is reached when
                              # the streaming server (Icecast)
                              # finishes a stream and starts with the
                              # following one.
                              print '\b!',
                              sys.stdout.flush()
                              time.sleep(1)
                              source_socket.close()
                              source_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                              source_socket.connect((self.source_host, self.source_port))
                              source_socket.sendall(GET_message)
                         prev_chunk_size = len(chunk)
                         chunk += source_socket.recv(self.chunk_size - len(chunk))
                    return chunk, source_socket

               chunk, source_socket = receive_next_chunk(source_socket)

               peer = self.peer_list[self.peer_index]
               message = struct.pack(chunk_format_string, socket.htons(self.chunk_number), chunk)
               self.team_socket.sendto(message, peer)
               self.destination_of_chunk[self.chunk_number % self.buffer_size] = peer
               self.chunk_number = (self.chunk_number + 1) % 65536

               self.peer_index = (self.peer_index + 1) % len(self.peer_list)

               # Decrement (dividing by 2) complains after
               # every 256 sent chunks.
               if (self.chunk_number % 256) == 0:
                    for i in self.losses:
                         self.losses[i] /= 2
                    '''
                    for i in self.complains:
                         self.complains[i] /= 2
                    '''
               if __debug__:
                    print '%5d' % self.chunk_number, Color.red, '->', Color.none, peer
                    sys.stdout.flush()

def main():

     # {{{ Args parsing
     
     parser = argparse.ArgumentParser(description='This is the splitter node of a P2PSP network.')
     parser.add_argument('--source_host', help='The streaming server. (Default = "{}")'.format(Splitter_DBS.source_host))
     parser.add_argument('--source_port', help='Port where the streaming server is listening. (Default = {})'.format(Splitter_DBS.source_port))
     parser.add_argument('--channel', help='Name of the channel served by the streaming source. (Default = "{}")'.format(Splitter_DBS.channel))
     parser.add_argument('--team_host', help='IP address to talk with the peers. (Default = "{}")'.format(Splitter_DBS.team_host))
     parser.add_argument('--team_port', help='Port to talk with the peers. (Default = {})'.format(Splitter_DBS.team_port))
     parser.add_argument('--buffer_size', help='size of the video buffer in blocks. (Default = {})'.format(Splitter_DBS.buffer_size))
     parser.add_argument('--chunk_size', help='Chunk size in bytes. (Default = {})'.format(Splitter_DBS.chunk_size))
     parser.add_argument('--losses_threshold', help='Maximum number of lost chunks for an unsupportive peer. (Default = {})'.format(Splitter_DBS.losses_threshold))
     #parser.add_argument('--complaining_threshold', help='Maximum number of complains for a peevish peer. (Default = {})'.format(Splitter_DBS.complaining_threshold))

     splitter = Splitter_DBS()

     args = parser.parse_known_args()[0]
     if args.source_host:
          splitter.source_host = socket.gethostbyname(args.source_host)
     if args.source_port:
          splitter.source_port = int(args.source_port)
     if args.channel:
          splitter.channel = args.channel
     if args.team_host:
          splitter.team_host = socket.gethostbyname(args.team_host)
     if args.team_port:
          splitter.team_port = int(args.team_port)
     if args.buffer_size:
          splitter.buffer_size = int(args.buffer_size)
     if args.chunk_size:
          splitter.chunk_size = int(args.chunk_size)
     if args.losses_threshold:
          splitter.losses_threshold = int(losses_threshold)
     #if args.complaining_threshold:
     #     splitter.complaining_threshold = int(complaining_threshold)
     
     # }}}

     splitter.start()
     last_chunk_number = 0
     while splitter.alive:
          try:
               print "[%3d] " % len(splitter.peer_list),
               kbps = (splitter.chunk_number - last_chunk_number) * \
                   splitter.chunk_size * 8/1000
               last_chunk_number = splitter.chunk_number

               for x in xrange(0,kbps/10):
                    print "\b#",
               print kbps, "kbps"

               time.sleep(1)

          except KeyboardInterrupt:
               print 'Keyboard interrupt detected ... Exiting!'

               # Say to the daemon threads that the work has been finished,
               splitter.alive = False

               print splitter.peer_list[0]

               # Wake up the "listen_to_the_cluster" daemon, which is waiting
               # in a cluster_sock.recvfrom(...).
               splitter.team_socket.sendto('',('127.0.0.1',splitter.team_port))

               # Wake up the "handle_arrivals" daemon, which is waiting in a
               # peer_connection_sock.accept().
               sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
               sock.connect(('127.0.0.1',splitter.team_port))
               sock.recv(struct.calcsize("4s")) # IP address of the source node
               sock.recv(struct.calcsize("H")) # Port of the source node
               message = sock.recv(struct.calcsize("H"))
               channel_size = struct.unpack("H", message)[0]
               channel_size = socket.ntohs(channel_size)
               channel = sock.recv(channel_size) # Channel name
               sock.recv(struct.calcsize("H")) # Buffer size
               sock.recv(struct.calcsize("H")) # Chunk size
               number_of_peers = socket.ntohs(struct.unpack("H",sock.recv(struct.calcsize("H")))[0])
               # Receive the list
               while number_of_peers > 0:
                    sock.recv(struct.calcsize("4sH"))
                    number_of_peers -= 1

               # Breaks this thread and returns to the parent process (usually,
               # the shell).
               break

if __name__ == "__main__":
     main()


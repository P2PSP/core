#!/usr/bin/python -O
# -*- coding: iso-8859-15 -*-

# Note: if you run the python interpreter in the optimzed mode (-O),
# debug messages will be disabled.

# {{{ GNU GENERAL PUBLIC LICENSE

# This is the splitter node of the P2PSP (Peer-to-Peer Simple Protocol)
# <https://launchpad.net/p2psp>.
#
# Copyright (C) 2013 Vicente González Ruiz,
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

# Try running me as (you will need Internet access):
#
# ./splitter.py &
#
# For getting help on the console parameters:
#
# ./splitter -h
#
# More info about the P2PSP protocol at:
#
# www.p2psp.org

# {{{ imports

if __debug__:
    import logging
from colors import Color
from config import Config
import socket
from blocking_TCP_socket import blocking_TCP_socket
import sys
import struct
import time
#import thread
from threading import Thread
from threading import Lock
from threading import RLock
from time import gmtime, strftime
import os
import argparse

# }}}

total_blocks = long(1)     #  Starts in 1 to avoid div-by-zero issues when calculating the percentage 
loss_percentage = float(0) # the same with the percentage of loss 

# Two constants
IP_ADDR = 0
PORT = 1

buffer_size = Config.buffer_size
block_size = Config.block_size
channel = Config.channel
source_hostname = Config.source_hostname
source_port = Config.source_port
listening_port = Config.splitter_port

if __debug__:
    logging_levelname = 'INFO' # 'DEBUG' (default), 'INFO' (cyan),
                               # 'WARNING' (blue), 'ERROR' (red),
                               # 'CRITICAL' (yellow)
    logging_level = logging.INFO

# {{{ Args handing

print 'Argument List:', str(sys.argv)

parser = argparse.ArgumentParser(
    description='This is the splitter node of a P2PSP network.')

parser.add_argument('--buffer_size',
                    help='size of the video buffer in blocks'.format(buffer_size))

parser.add_argument('--block_size',
                    help='Block size in bytes. (Default = {})'.format(block_size))

parser.add_argument('--channel',
                    help='Name of the channel served by the streaming source. (Default = "{}")'.format(channel))

if __debug__:
    parser.add_argument('--logging_levelname',
                        help='Name of the channel served by the streaming source. (Default = "{}")'.format(logging_levelname))

parser.add_argument('--source_hostname',
                    help='Hostname of the streaming server. (Default = "{}")'.format(source_hostname))

parser.add_argument('--source_port',
                    help='Listening port of the streaming server. (Default = {})'.format(source_port))

parser.add_argument('--listening_port',
                    help='Port to talk with the peers. (Default = {})'.format(listening_port))

args = parser.parse_known_args()[0]
if args.buffer_size:
    buffer_size = int(args.buffer_size)
if args.block_size:
    block_size = int(args.block_size)
if args.channel:
    channel = args.channel
if __debug__:
    if args.logging_levelname == 'DEBUG':
        logging_level = logging.DEBUG
    if args.logging_levelname == 'INFO':
        logging_level = logging.INFO
    if args.logging_levelname == 'WARNING':
        logging_level = logging.WARNING
    if args.logging_levelname == 'ERROR':
        logging_level = logging.ERROR
    if args.logging_levelname == 'CRITICAL':
        logging_level = logging.CRITICAL
if args.source_hostname:
    source_hostname = str(args.source_hostname)
if args.source_port:
    source_port = int(args.source_port)
if args.listening_port:
    listening_port = int(args.listening_port)

# }}}

print 'This is a P2PSP splitter node ...',
if __debug__:
    print 'running in debug mode'
else:
    print 'running in release mode'

# {{{ Logging initialization

# Echar un vistazo a logging.config.

if __debug__:
    # create logger
    logger = logging.getLogger('splitter (' + str(os.getpid()) + ')')
    logger.setLevel(logging_level)

    # create console handler and set the level
    ch = logging.StreamHandler()
    ch.setLevel(logging_level)

    # create formatter
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    #formatter = logging.Formatter("%(asctime)s [%(funcName)s: %(filename)s,%(lineno)d] %(message)s")

    # add formatter to ch
    ch.setFormatter(formatter)

    # add ch to logger
    logger.addHandler(ch)

    #logging.basicConfig(format='%(asctime)s.%(msecs)d %(message)s',
    #                    datefmt='%H:%M:%S',
    #                    level=logging.DEBUG)
    #    logging.basicConfig(format='%(asctime)s.%(msecs)d %(message)s',
    #                        datefmt='%H:%M:%S')
    #  else:
    #    print 'Running in release mode'
    #    logging.basicConfig(format='%(asctime)s.%(msecs)d %(message)s',
    #                        datefmt='%H:%M:%S',
    #                        level=logging.CRITICAL)

# }}}

source = (source_hostname, source_port)

# }}} 
               
# The list of peers.
peer_list = [] 

# The number of the last received block from the streaming server.
block_number = 0 # Ojo (long(0))

# Used to find the peer to which a block has been sent.
destination_of_block = [('0.0.0.0',0) for i in xrange(buffer_size)]

# Unreliability rate of a peer.
unreliability = {}

# Complaining rate of a peer.
complains = {}

# The peer_list iterator.
peer_index = 0

# A lock to perform mutual exclusion for accesing to the list of
# peers.
peer_list_lock = Lock()

block_format_string = "H"+str(block_size)+"s" # "H1024s

if __debug__:
    logger.info("Buffer size: " + str(buffer_size) + " blocks")
    logger.info("Block size: " + str(block_size) + " bytes")

# {{{ Handle a telnet session.

class get_the_state(Thread):
    # {{{

    global peer_list

    def __init__(self):
        Thread.__init__(self)

    def run(self): 
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            # This does not work in Windows systems.
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        except:
            pass
        sock.bind(('', listening_port+1))

        if __debug__:
            logger.info(Color.cyan +
                        '{}'.format(sock.getsockname()) +
                        ' listening (telnet) on port ' +
                        str(listening_port+1) +
                        Color.none)

        print sock.getsockname(), 'listening (telnet) on port', listening_port+1

        sock.listen(0)
        try:
            while True:
                connection = sock.accept()[0]
                message = 'a'
                while message[0] != 'q':
                    connection.sendall('Number of peers = ' + str(len(peer_list)) + '\n')
                    counter = 0
                    for p in peer_list:
                        loss_percentage = float(unreliability[p]*100)/float(total_blocks)
                        connection.sendall(str(counter) +
                                           '\t' + str(p) +
                                           '\t' + 'unreliability=' +
                                           str(unreliability[p]) +
                                           ' ({:.2}%)'.format(loss_percentage)+
                                           '\t' + 'complains=' + str(complains[p]) +
                                           '\n')
                        counter += 1
                    connection.sendall('\n Total blocks sent = '+str(total_blocks))
                    connection.sendall(Color.cyan + '\nEnter a line that beggings with "q" to exit or any other key to continue\n' + Color.none)
                    message = connection.recv(2)

                connection.close()

        except:
            pass

get_the_state().setDaemon(True)
get_the_state().daemon=True
get_the_state().start()

# }}}

# Return the connection socket used to establish the connections of
# the peers.

def get_peer_connection_socket():
    #sock = blocking_TCP_socket(socket.AF_INET, socket.SOCK_STREAM)
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        # This does not work in Windows systems.
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    except:
        pass

    sock.bind( ('', listening_port) )
    #sock.listen(5)
    sock.listen(socket.SOMAXCONN)   # Set the connection queue to the max!

    return sock

peer_connection_sock = get_peer_connection_socket()

# {{{ Handle the arrival of a peer.
class handle_one_arrival(Thread):
    peer_serve_socket = ""
    peer = ""
    
    def __init__(self, peer_serve_socket, peer):
        Thread.__init__(self)
        self.peer_serve_socket = peer_serve_socket
        self.peer = peer
        
    def run(self):
        
        global peer_list
        global unreliability
        global complains
        global logger
        
        # {{{ debug
        if __debug__:
            logger.debug('{}'.format(self.peer_serve_socket.getsockname()) +
                         ' Accepted connection from peer ' +
                         str(self.peer))
        # }}}

        print self.peer_serve_socket.getsockname(), 'Accepted connection from peer', self.peer

        # {{{ Send the list of peers to the peer.
        # {{{ debug

        if __debug__:
            logger.debug('{}'.format(self.peer_serve_socket.getsockname()) +
                         ' Sending the list of peers')
        # }}}

        print self.peer_serve_socket.getsockname(), 'Sending the list of peers ...',

        message = struct.pack("H", socket.htons(len(peer_list)))
        self.peer_serve_socket.sendall(message)
       
        for p in peer_list:
            message = struct.pack(
                "4sH", socket.inet_aton(p[IP_ADDR]),
                socket.htons(p[PORT]))
            self.peer_serve_socket.sendall(message)
            print p

        # {{{ debug

        if __debug__:
            logger.debug(str(len(peer_list)) + ' peers sent')

        # }}}

        print 'done'

        # }}}

        # {{{ Close the TCP socket with the peer.

        self.peer_serve_socket.close()

        # }}}

        peer_list.append(self.peer)
        unreliability[self.peer] = 0
        complains[self.peer] = 0

        if __debug__:
            logger.info(Color.cyan +
                        str(self.peer) +
                        ' has joined the cluster' +
                        Color.none)
    # }}}
            
# {{{ Main handler peer arrivals.
class handle_arrivals(Thread):
    # {{{

    def __init__(self):
        Thread.__init__(self)

    def run(self):
        while True:
            peer_serve_socket, peer = peer_connection_sock.accept()
            handle_one_arrival(peer_serve_socket, peer).start()
           
    # }}}

#print("Peer list length: "+str(len(peer_list)))

handle_arrivals().setDaemon(True) # Setting the thread as daemon makes
                                  # it die when the main process
                                  # ends. Otherwise, it'd never stop
                                  # since it runs a while(true).
handle_arrivals().daemon = True
handle_arrivals().start()

# }}}

# {{{ Create the socket to send the blocks of stream to the peers.

def create_cluster_sock(listening_port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # This does not work in Windows systems !!
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    except:
        pass
    sock.bind(('', listening_port))
    #peer_socket.bind(('',peer_connection_sock.getsockname()[PORT]))

    return sock

cluster_sock = create_cluster_sock(listening_port)

# }}}

# {{{ Handle peer complains and goodbye messages.

class listen_to_the_cluster(Thread):
    # {{{

    def __init__(self):
        Thread.__init__(self)

    def run(self):

        global peer_index

        while True:
            # {{{ debug
            if __debug__:
                logger.debug('waiting for messages from the cluster')
            # }}}
            message, sender = cluster_sock.recvfrom(struct.calcsize("H"))

            if len(message) == 0:
            #if message == 'bye':
                try:
                    peer_list.remove(sender)
                    if __debug__:
                        logger.info(Color.cyan +
                                    str(sender) +
                                    ' has left the cluster' +
                                    Color.none)

                    print sender, 'has left the cluster'

                except:
                    if __debug__:
                        logger.warning(Color.blue +
                                       'Received a googbye message from ' +
                                       str(sender) +
                                       ' which is not in the list of peers' +
                                       Color.none)
                    pass
            else:
                # The sender of the packet complains and the packet
                # comes with the index of a lost block.
                lost_block = struct.unpack("!H",message)[0]
                try:
                    destination = destination_of_block[lost_block]
                    if __debug__:
                        logger.info(Color.cyan +
                                    str(sender) +
                                    ' complains about lost block ' +
                                    str(lost_block) +
                                    ' sent to ' +
                                    str(destination) +
                                    Color.none)
                    unreliability[destination] += 1
                    if unreliability[destination] > len(peer_list):
                        # Too much complains about an unsupportive peer
                        peer_list.remove(destination)
                        del unreliability[destination]
                        del complains[destination]

                        print 'Too much complains about unsupportive peer', destination

                        if __debug__:
                            logger.info(Color.cyan +
                                        str(destination) +
                                        ' has been removed' +
                                        Color.none)
                except:
                    # The destination does not exit
                    pass


'''jalvaro: i'm commenting this so peers are not expeled
#if the sender of the complaint is the gatherer then the splitter removes the infractor inmediately
                if sender == gatherer:
                    try:
                        peer_list.remove(destination)
                        del unreliability[destination]
                        del complains[destination]
                        
                        logger.info(Color.cyan +
                                    str(destination) +
                                    ' has been removed' +
                                    Color.none)
                    except:
                        pass

                else:
                    try:
                        unreliability[destination] += 1
                        if unreliability[destination] > len(peer_list):
                            # Too many complains about an unsuportive peer
                            peer_list.remove(destination)
                            del unreliability[destination]
                            del complains[destination]

                            logger.info(Color.cyan +
                                        str(destination) +
                                        ' has been removed' +
                                        Color.none)

                    except:
                        pass
'''
                
    # }}}

listen_to_the_cluster().setDaemon(True)
listen_to_the_cluster().daemon=True
listen_to_the_cluster().start()

# }}}

# {{{ Connect to the streaming server and request the channel

source_sock = blocking_TCP_socket(socket.AF_INET, socket.SOCK_STREAM)
print source_sock.getsockname(), 'Connecting to the source ', source, '...',
source_sock.connect(source)
print 'connected!'

# {{{ debug

if __debug__:
    logger.debug('{}'.format(source_sock.getsockname()) +
                 ' connected to the source ' +
                 '{}'.format(source_sock.getpeername()))

# }}}

# {{{ Request the video to the source

GET_message = 'GET /' + channel + ' HTTP/1.1\r\n'
#GET_message += 'User-Agent: P2PSP-splitter\r\n'
#GET_message += 'Accept: */*\r\n'
#GET_message += 'Host: localhost:10000\r\n'
#GET_message += 'Connection: Keep-Alive\r\n'
#GET_message += '\r\n'
GET_message += '\r\n'
source_sock.sendall(GET_message)
#print GET_message
print source_sock.getsockname(), 'Requesting http://'+str(source_sock.getpeername()[0])+':'+str(source_sock.getpeername()[1])+'/'+str(channel)

# }}}

# {{{ debug

if __debug__:
    logger.debug('{}'.format(cluster_sock.getsockname()) +
                 ' sending the rest of the stream ...')

# }}}

# {{{ Feed the peers

while True:

    def receive_next_block():
        # {{{

        global source_sock

        block = source_sock.recv(block_size)
        tries = 0
        while len(block) < block_size:
            tries += 1
            if tries > 3:
                tries = 0
                # {{{ debug
                if __debug__:
                    logger.debug('GET')
                # }}}

                sys.stdout.flush()

                time.sleep(1)
                source_sock.close()
                source_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                source_sock.connect(source)
                source_sock.sendall(GET_message)
            block += source_sock.recv(block_size - len(block))
        return block

        # }}}

    #print "Retrieving block:", block_number,
    block = receive_next_block()
    #system.out.write('.')
    #block = source_sock.brecv(block_size)

    # {{{ debug
    if __debug__:
        logger.debug('{}'.format(source_sock.getsockname()) +
                     Color.green + ' <- ' + Color.none +
                     '{}'.format(source_sock.getpeername()) +
                     ' ' +
                     '{}'.format(block_number))
    # }}}
    #print("Block "+str(block_number)+" received")

    #with peer_list_lock:
    #peer_list_lock.acquire()
    len_peer_list = len(peer_list)
    #print("Length of peer_list: "+str(len_peer_list))
    #if peer_index < len_peer_list:
    try:
        peer = peer_list[peer_index]
	#print("Destinatario peer: "+str(peer))
        #print 'and sent to', peer
        print 'Block', block_number, 'sent to', peer, '\r',
    except:
        try:
            peer = peer_list[0]
            print 'Block', block_number, 'sent to', peer, '\r',
            #print("Destinatario peer2: "+str(peer))
        except:
            peer = None
            print 'Block', block_number, 'not sent (empty cluster)', '\r',
            len_peer_list = 1	# Should be zero but that would raise
                                # a modulo by zero exception
    
    #peer_list_lock.release()

    # {{{ debug
	if __debug__:
        	logger.debug('{}'.format(cluster_sock.getsockname()) +
                     Color.green + ' -> ' + Color.none +
                     '{}'.format(peer) +
                     ' ' +
                     '{}'.format(block_number))
    # }}}

    #print("peer != None: "+str(peer!=None))
    if peer != None:
    	#print("Sending block "+str(block_number))
	#message = struct.pack("H1024s", socket.htons(block_number), block)
	message = struct.pack(block_format_string, socket.htons(block_number), block)
	#if not (block_number%2)==0:
	cluster_sock.sendto(message, peer)
	#print("Block "+str(block_number)+"sent to "+str(peer))

    # Ojo, a veces peta diciendo: "IndexError: list index out of range"
    destination_of_block[block_number % buffer_size] = peer

    peer_index = (peer_index + 1) % len_peer_list

    block_number = (block_number + 1) % 65536

    total_blocks += 1

    # Decrement unreliability and complaints after every 256 packets
    if (block_number % 256) == 0:
        for i in unreliability:
            unreliability[i] /= 2
        for i in complains:
            complains[i] /= 2

# }}}

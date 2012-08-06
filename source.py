#!/usr/bin/python
# -*- coding: iso-8859-15 -*-

'''
Utilization example:

oggfwd localhost 4551 1qaz /480.ogg < big_buck_bunny_480p_stereo.ogg
python source.py 4552 localhost 4551 480.ogg
'''

# Esta versión del nodo fuente no tiene buffer porque no reenvía
# bloques perdidos. Para saber qué peers hay en el cluster confía en
# los mensajes que le envían los peers indicándo que un determinado
# peer ya no está entre su lista de peers. Cuando más de la mitad de
# los peers descarta a otro, el nodo fuente hace lo mismo.

import socket
from blocking_socket import blocking_socket
import sys
import struct
import time
from threading import Thread
from threading import Lock
from colors import Color
import signal
from time import gmtime, strftime

IP_ADDR = 0
PORT = 1
VIDEO_HEADER_SIZE = 20 # In blocks

listen_port = int(sys.argv[1])
video_server_host = sys.argv[2]
video_server_port = int(sys.argv[3])
channel = sys.argv[4]

print "(source) -> (peer) : Sends a block or other kind of data"
print "(source) <~ (peer) : Receives a lost block retransmission request"
print "(source) ~> (peer) : Sends a retransmitted block"

peer_connection_socket = blocking_socket(socket.AF_INET, socket.SOCK_STREAM)
peer_connection_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
peer_connection_socket.bind(("", listen_port)) # We listen to any interface
peer_connection_socket.listen(5)
print peer_connection_socket.getsockname(), "Waiting for peers ..."

number_of_peers = 0
peer_list = []
private_list = []
block_number = 0
removing_ratio = {}

video_server_socket = blocking_socket(socket.AF_INET, socket.SOCK_STREAM)
video_server_socket.connect((video_server_host, video_server_port))
print video_server_socket.getsockname(), "Connected to Video Server at", video_server_socket.getpeername()
video_server_socket.sendall("GET /" + channel + " HTTP/1.1\r\n\r\n")
print video_server_socket.getsockname(), "<- [Video header",
video_header = [None]*VIDEO_HEADER_SIZE
for i in xrange(VIDEO_HEADER_SIZE):
    block = video_server_socket.brecv(1024)
    video_header[i] = block
    print "\b.",
print "] done"

class Peer_Connection_Thread(Thread):

    def __init__(self):
        Thread.__init__(self)
    
    def run(self):
        
        while True:
            peer_serve_socket, peer = peer_connection_socket.baccept()
            print peer_serve_socket.getsockname(), \
                "Accepted connection from:", peer

            payload = peer_serve_socket.recv(struct.calcsize("4sH"))
            private_IP, private_port = struct.unpack("4sH", payload)
            private_IP = socket.inet_ntoa(private_IP)
            private_port = socket.ntohs(private_port)
            private_endpoint = (private_IP, private_port)
            print peer_serve_socket.getsockname(), \
                "Private endpoint =", private_endpoint

            print peer_serve_socket.getsockname(), "Sending the list of peers"
            payload = struct.pack("H", socket.htons(len(peer_list)))
            peer_serve_socket.sendall(payload)
            print "Len Peer List = ",len(peer_list)
            print "Peer List"
            for (pub,pri) in zip(peer_list,private_list):
                print "Public =", pub, "Private =", pri
                if peer[0] == pub[0]:
                    payload = struct.pack("4sH",
                                          socket.inet_aton(pri[IP_ADDR]),
                                          socket.htons(pri[PORT]))
                    print pri[IP_ADDR], ":", pri[PORT], "->", peer, "(private)"
                else:                  
                    payload = struct.pack("4sH",
                                          socket.inet_aton(pub[IP_ADDR]),
                                          socket.htons(pub[PORT]))
                    print pub[IP_ADDR], ":", pub[PORT], "->", peer, "(public)"
                peer_serve_socket.sendall(payload)
            print "done"
                
            print peer_serve_socket.getsockname(), "Video header ->", peer
            payload = struct.pack("H", socket.htons(VIDEO_HEADER_SIZE))
            peer_serve_socket.sendall(payload)
            for i in xrange(VIDEO_HEADER_SIZE):
                peer_serve_socket.sendall(video_header[i])
                print "\b.",
            print "done"

            peer_serve_socket.close()
  
            peer_list.append(peer)                
            private_list.append(private_endpoint)
                
            removing_ratio[peer] = 0
            
Peer_Connection_Thread().start()

peer_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
peer_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
peer_socket.bind(('',peer_connection_socket.getsockname()[PORT]))

peer_index = 0

peer_index_lock = Lock()
printing_lock = Lock()

class Prune_The_Cluster_Thread(Thread):

    def __init__(self):
        Thread.__init__(self)

    def run(self):
        global peer_index
        global peer_index_lock
        global printing_lock
        while True:
            try:
                payload, complaining_peer = peer_socket.recvfrom(struct.calcsize("4sH"))
            except socket.error:
                print("Received from a peer offline now - continue")
                break
            peer_to_remove_IP, peer_to_remove_port = struct.unpack("4sH", payload)
            peer_to_remove_IP = socket.inet_ntoa(peer_to_remove_IP)
            peer_to_remove_port = socket.ntohs(peer_to_remove_port)
            peer_to_remove = (peer_to_remove_IP, peer_to_remove_port)

            printing_lock.acquire()
            print Color.blue + \
                "% " + strftime("%Y-%m-%d %H:%M:%S", gmtime()) + \
                ": ('" + peer_to_remove_IP + "', " + str(peer_to_remove_port) + \
                ") removed in peer ('" + complaining_peer[0] + "'," + \
                str(complaining_peer[1]) + ")" + Color.none
            printing_lock.release()

            # El problema está en que cuando un peer echa a otro en su
            # misma red privada, debe indicar a S la dir IP pública de
            # dicho peer, no la dir IP privada que está usando para
            # comunicarse con él. S sólo eliminar peers a partir de su
            # dirección IP pública. La otra opción, que permite que
            # los peers no tengan que almacenar las dirs IP públicas
            # de sus interlocutores privados es que se elimine a aquel
            # peer que tiene la misma IP pública del peer que se queja
            # y tenga asociada dicha entrada la dir IP privada que ha
            # indicado el peer que se queja.
            
            counter = 0
            for x in peer_list:
                if x == peer_to_remove:
                    printing_lock.acquire()
                    print Color.blue + "% " + strftime("%Y-%m-%d %H:%M:%S", gmtime()) + \
                        ": removed " +  str(peer_list[counter]) + \
                        " " +  str(private_list[counter]) + \
                        Color.none
                    printing_lock.release()
                    peer_index_lock.acquire()
                    del peer_list[counter]
                    del private_list[counter]
                    if peer_index > 0:
                       peer_index -= 1
                    peer_index_lock.release()
                counter += 1

Prune_The_Cluster_Thread().start()

def SIGHUP_handler(signum, frame):
    global printing_lock
    printing_lock.acquire()
    print
    print Color.red + "############### " + \
        strftime("%Y-%m-%d %H:%M:%S", gmtime()) + \
        " ###############"
    print "# List of peers:"
    counter = 1
    for p in zip(peer_list, private_list):
        print '# ', counter, p
        counter += 1
    print Color.none
    printing_lock.release()

signal.signal(signal.SIGHUP, SIGHUP_handler)
signal.siginterrupt(signal.SIGHUP, False)

print peer_socket.getsockname(), "Sending the rest of the stream ..."
while True:

    block = video_server_socket.recv(1024)
    tries = 0
    
    while len(block) < 1024:
        tries += 1
        if tries > 3:
            sys.stdout.write(".")
            sys.stdout.flush()
            time.sleep(1)
            video_server_socket.close()
            video_server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            video_server_socket.connect((video_server_host, video_server_port))
            video_server_socket.sendall("GET /" + channel + " HTTP/1.1\r\n\r\n")
        block += video_server_socket.recv(1024-len(block))
    
 #   print video_server_socket.getsockname(), \
        Color.green + "<-" + Color.none, \
        video_server_socket.getpeername(), \
        block_number
    
    
    time.sleep(0.01) #give time to helping the peer send block to player (prevents missing in peer)
   
    peer_index_lock.acquire()
    if len(peer_list) > 0:
#        print peer_socket.getsockname(), \
#            block_number, \
#            Color.green + "->" + Color.none, \
#            peer_list[peer_index], "(", peer_index+1, "/", len(peer_list), ")"
        
        payload = struct.pack("H1024s", socket.htons(block_number), block)
        peer_socket.sendto(payload, peer_list[peer_index])

        peer_index = (peer_index + 1) % len(peer_list)
        
    peer_index_lock.release()
    
    block_number = (block_number + 1) % 65536
    


#!/usr/bin/python
# -*- coding: iso-8859-15 -*-
#
# source.py
#

# Esta versión del nodo fuente no tiene buffer porque no reenvía
# bloques perdidos. Para saber qué peers hay en el cluster confía en
# los mensajes que le envían los peers indicándo que un determinado
# peer ya no está entre su lista de peers. Cuando al menos la mitad de
# los peers descarta a otro, el nodo fuente hace lo mismo, siempre que
# no se trate de un superpeer, que no puede expulsarse de la red.

# El coste del hosting de un nodo S(source) es del mismo orden que el
# hosting de un nodo P(peer). Atendiendo a requerimientos de la red
# (por ejemplo, que un determinado conjunto de peers están detrás de
# un NAT simétrico), se puede realizar un cluster P2PSP detrás de
# dicho NAT si al menos un peer cambia su comportamiento y reenvía
# todo lo que recibe a un nodo S que esté tras el cortefuegos. Dicho
# cambio de comportamiento en un nodo P_x se produce simplemente si
# dicho peer posee una lista de peers con un único nodo, el que está
# tras el NAT. Para evitar que el resto de P's que están fuera del NAT
# alimentando a P_x estén quejándose a su correspondiente nodo fuente
# de la insolidaridad de P_x, lo más simple es desechar este
# comportamiento y usar un heart-beat o considerar a estos peers
# "especiales" como super-peers. A un super-peer, se le envía si
# esperar nada a cambio. Los super-peers pueden ser reconocidos porque
# alimentan a un S que está tras un NAT simétrico. Por otra parte, la
# política del hear-beat es la más simple porque, suponiendo que no
# hay "mutaciones" del código de los peers que envien el heart-beat y
# luego no sean solidarios, implica que S no va a recibir quejas de un
# super-peer.

# Estudiar también la posibilidad de pedir bloques de vídeo bajo demanda, es decir, que si un peer no pide entonces no se le entrega

# {{{ imports

import socket
from blocking_socket import blocking_socket
import sys
import getopt
import struct
import time
from threading import Thread
from threading import Lock
from colors import Color
import signal
from time import gmtime, strftime

# }}}

IP_ADDR = 0
PORT = 1

header_size = 20
listening_port = 4552
server_host = "150.214.150.68"
server_port = 4551
channel = "134.ogg"

def usage():
    # {{{

    print "This is " + sys.argv[0] + ", the source node of a P2PSP network"
    print
    print "Parameters (and default values):"
    print
    print " -[-c]hannel=name of the video/audio sequence served by (" + channel + ")"
    print " -[-h]eader_size=number of blocks of the header of the stream (" + str(header_size) + ")"
    print " -[-l]istening_port=the port that the source uses to communicate the peers (" + str(listening_port) + ")"
    print " -[-s]erver=host name and port of the video/audio server ((" + server_host + ":" + str(server_port) + "))"
    print

    # }}}

# {{{ Args handing

opts = ""

try:
    opts, extraparams = getopt.getopt(sys.argv[1:],"c:h:l:s:?",
                                      ["channel=",
                                       "header_size=",
                                       "listening_port=",
                                       "server=",
                                       "help"
                                       ])

except getopt.GetoptError, exc:
    sys.stderr.write(sys.argv[0] + ": " + exc.msg + "\n")
    sys.exit(2)

print sys.argv[0] + ": Parsing:" + str(opts)

for o, a in opts:
    if o in ("-c", "--channel"):
        channel = a
        print sys.argv[0] + ": channel=" + channel
    elif o in ("-h", "--header_size"):
        header_size = int(a)
        print sys.argv[0] + ": header_size=" + str(header_size)
    elif o in ("-l", "--listening_port"):
        listening_port = int(a)
        print sys.argv[0] + ": listening_port=" + str(listening_port)
    elif o in ("-s", "--server"):
        server_host = a.split(":")[0]
        server_port = int(a.split(":")[1])
    elif o in ("-?", "--help"):
	usage()
	sys.exit()
    else:
        assert False, "Undandled option!"

# }}}

# {{{ obsolete

#print "(source) -> (peer) : Sends a block or other kind of data"
#print "(source) <~ (peer) : Receives a lost block retransmission request"
#print "(source) ~> (peer) : Sends a retransmitted block"

# }}}


# {{{ Waiting for peers

peer_connection_socket = blocking_socket(socket.AF_INET, socket.SOCK_STREAM)
peer_connection_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
try:
    peer_connection_socket.bind(("", listening_port)) # We listen to any interface
except socket.error, msg:
    print strftime("[%Y-%m-%d %H:%M:%S]", gmtime()), \
        "Can't bind", listening_port, \
        "(already used?)"
peer_connection_socket.listen(5)
print strftime("[%Y-%m-%d %H:%M:%S]", gmtime()), peer_connection_socket.getsockname(), "Waiting for peers ..."

# }}}

number_of_peers = 0
peer_list = []
private_list = []
block_number = 0
removing_ratio = {}

# {{{ Connect to the server

icecast_socket = blocking_socket(socket.AF_INET, socket.SOCK_STREAM)
icecast_socket.connect((server_host, server_port))
print strftime("[%Y-%m-%d %H:%M:%S]", gmtime()), \
    icecast_socket.getsockname(), "Connected to the video server", icecast_socket.getpeername()

# }}}

# {{{ Header retrieving

icecast_socket.sendall("GET /" + channel + " HTTP/1.1\r\n\r\n")
print strftime("[%Y-%m-%d %H:%M:%S]", gmtime()),\
    icecast_socket.getsockname(), "<- [Video header",
video_header = [None]*header_size
for i in xrange(header_size):
    block = icecast_socket.brecv(1024)
    video_header[i] = block
    print "\b.",
print "] done"

# }}}

peer_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
peer_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
peer_socket.bind(('',peer_connection_socket.getsockname()[PORT]))


class Peer_Connection(Thread):
    # {{{

    def __init__(self):
        Thread.__init__(self)

    def run(self):
        
        while True:
            peer_serve_socket, peer = peer_connection_socket.baccept()
            print Color.red
            print strftime("[%Y-%m-%d %H:%M:%S]", gmtime()), \
                peer_serve_socket.getsockname(), \
                "Accepted connection from:", peer

            payload = peer_serve_socket.recv(struct.calcsize("4sH"))
            private_IP, private_port = struct.unpack("4sH", payload)
            private_IP = socket.inet_ntoa(private_IP)
            private_port = socket.ntohs(private_port)
            private_endpoint = (private_IP, private_port)
            print strftime("[%Y-%m-%d %H:%M:%S]", gmtime()), \
                peer_serve_socket.getsockname(), \
                "Private endpoint =", private_endpoint

            print strftime("[%Y-%m-%d %H:%M:%S]", gmtime()), \
                peer_serve_socket.getsockname(), "Sending the list of peers"
            payload = struct.pack("H", socket.htons(len(peer_list)))
            peer_serve_socket.sendall(payload)
            print strftime("[%Y-%m-%d %H:%M:%S]", gmtime()), \
                "Len Peer List = ",len(peer_list)
            print strftime("[%Y-%m-%d %H:%M:%S]", gmtime()), \
                "Peer List"
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
                
            print strftime("[%Y-%m-%d %H:%M:%S]", gmtime()), \
                peer_serve_socket.getsockname(), "Video header ->", peer
            payload = struct.pack("H", socket.htons(header_size))
            peer_serve_socket.sendall(payload)
            for i in xrange(header_size):
                peer_serve_socket.sendall(video_header[i])
                print "\b.",
            print "done"

            peer_serve_socket.close()
            
            #Introducing the new peer to all cluster
            payload = struct.pack("4sH",socket.inet_aton(peer[IP_ADDR]),socket.htons(peer[PORT]))
            
            for p in peer_list:                   
                peer_socket.sendto(payload, p)
                print "Introducing ", peer[IP_ADDR], ":", peer[PORT], " to ->", p
            
            peer_list.append(peer)
            private_list.append(private_endpoint)
            
            removing_ratio[peer] = 0

            print Color.none         
                

    # }}}
            
Peer_Connection().start()

peer_index = 0
peer_index_lock = Lock()
printing_lock = Lock()

class Prune_The_Cluster(Thread):
    # {{{

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
                print strftime("[%Y-%m-%d %H:%M:%S]", gmtime()), \
                    "Received from a peer offline now - continue"
                break
            peer_to_remove_IP, peer_to_remove_port = struct.unpack("4sH", payload)
            peer_to_remove_IP = socket.inet_ntoa(peer_to_remove_IP)
            peer_to_remove_port = socket.ntohs(peer_to_remove_port)
            peer_to_remove = (peer_to_remove_IP, peer_to_remove_port)

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
                    print Color.blue + \
                    strftime("[%Y-%m-%d %H:%M:%S]", gmtime()) + \
                    " ('" + peer_to_remove_IP + "', " + str(peer_to_remove_port) + \
                    ") removed in peer ('" + complaining_peer[0] + "'," + \
                    str(complaining_peer[1]) + ")" + Color.none
                    printing_lock.release()
                    peer_index_lock.acquire()
                    del peer_list[counter]
                    del private_list[counter]
                    if peer_index > 0:
                       peer_index -= 1
                    peer_index_lock.release()
                counter += 1

    # }}}

Prune_The_Cluster().start()

def SIGHUP_handler(signum, frame):
    # {{{

    global printing_lock
    printing_lock.acquire()
    print "Writting on source.log"
    logfile = open ("source.log", 'a')
    logfile.write(strftime("[%Y-%m-%d %H:%M:%S]", gmtime()) + " List of peers:\n")
    counter = 1
    for p in zip(peer_list, private_list):
        logfile.write(str(counter) + ": " + str(p) + "\n")
        counter += 1
    logfile.close()
    printing_lock.release()

    # }}}

signal.signal(signal.SIGHUP, SIGHUP_handler)
signal.siginterrupt(signal.SIGHUP, False)

print peer_socket.getsockname(), "Sending the rest of the stream ..."
while True:

    block = icecast_socket.recv(1024)
    tries = 0
    
    while len(block) < 1024:
        tries += 1
        if tries > 3:
            sys.stdout.write(".")
            sys.stdout.flush()
            time.sleep(1)
            icecast_socket.close()
            icecast_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            icecast_socket.connect((server_host, server_port))
            icecast_socket.sendall("GET /" + channel + " HTTP/1.1\r\n\r\n")
        block += icecast_socket.recv(1024-len(block))

 #   print icecast_socket.getsockname(), \
        Color.green + "<-" + Color.none, \
        icecast_socket.getpeername(), \
        block_number
         
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


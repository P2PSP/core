#!/usr/bin/python
# -*- coding: iso-8859-15 -*-

# No solicita retransmisión de bloques perdidos. Avisa al nodo fuente
# de los peers eliminados de la lista de peers. Posee un buffer para
# acomodar el jitter.

# {{{ Imports

import getopt
import sys
import socket
from blocking_socket import blocking_socket
from colors import Color
import struct

# }}}

IP_ADDR = 0
PORT = 1

source_name = "150.214.150.68"
source_port = 4552
player_port = 9999
peer_port = 0 # OS default behavior will be used for port binding
buffer_size = 32

def usage():
    # {{{

    print "This is " + sys.argv[0] + ", the peer node of a P2PSP network"
    print
    print "Parameters (and default values):"
    print
    print " -[-b]uffer_size=size of the peer buffer in blocks (" + str(buffer_size) + ")"
    pri

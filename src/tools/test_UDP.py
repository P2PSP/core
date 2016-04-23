#!/usr/bin/python
# -*- coding: iso-8859-15 -*-
#
# test_UDP.py

# {{{ imports

from socket import *
from threading import Thread
import sys
import argparse
import struct
import time
import signal
from time import gmtime, strftime
from struct import *

# }}}

IP_ADDR = 0
PORT = 1

class Destination:

    addr = "150.214.150.68"
    port = 4551

    def get(self):
        return (self.addr, self.port)

destination = Destination()
payload_size = 1024

# {{{ Args handing

parser = argparse.ArgumentParser(description="Tests UDP throughtput.")
parser.add_argument("--destination", help="Destination IP address:port. (Default = {})".format(destination.get()))
parser.add_argument("--size", help="Payload size. (Default = {})".format(payload_size))
args = parser.parse_args()
if args.destination:
    destination.addr = args.destination.split(":")[0]
    destination.port = int(args.destination.split(":")[1])
if args.size:
    payload_size = int(args.size)

# }}}

sent_packets = 0
last_sent = 0

class Packets_per_second(Thread):

    def __init__(self):
        Thread.__init__(self)

    def run(self):
        global sent_packets
        global last_sent
        iters = 0
        while True:
            time.sleep(1)
            iters += 1
            last_sent = sent_packets - last_sent
            print str(last_sent*payload_size*8/1000) + " Kbps" + " ( average = " + str(sent_packets*payload_size*8/(iters*1000)) + " Kbps )"
            last_sent = sent_packets

pack = Packets_per_second()
pack.daemon = True
pack.start()

address = (destination.addr, destination.port)
the_socket = socket(AF_INET, SOCK_DGRAM)
payload = '0'.zfill(payload_size)

while True:
    sent_packets = sent_packets + 1
    try:
	the_socket.sendto(payload, address)
    except:
	sys.exit(0)

#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os, sys, getopt
import time
import random
import shlex, subprocess

processes = []
DEVNULL = open(os.devnull, 'wb')

def checkdir():
    if not os.path.exists("./strpe-testing"):
        os.mkdir("./strpe-testing")

def usage():
    print "args error"

def run(runStr):
    proc = subprocess.Popen(shlex.split(runStr), stdout=DEVNULL, stderr=DEVNULL)
    processes.append(proc)

def killall():
    for proc in processes:
        proc.kill()

def runStream():
    run("/Applications/VLC.app/Contents/MacOS/VLC ../src/Big_Buck_Bunny_small.ogv --sout \"#duplicate{dst=standard{mux=ogg,dst=,access=http}}\"")
    time.sleep(1)

def runSplitter(trustedPeers):
    tps = ""
    for p in trustedPeers:
        tps += "\"{0}\" ".format(p)
    run("../src/splitter.py --source_port 8080 --strpe {0} --strpe_log strpe-testing/splitter.log".format(tps))
    time.sleep(1)

def runPeer(port, playerPort, trusted = False, malicious = False):
    #run peer
    runStr = "../src/peer.py --use_localhost --port {0} --player_port {1}".format(port, playerPort)
    if trusted:
        runStr += " --trusted"
    if malicious:
        runStr += " --malicious"
    if not malicious:
         runStr += " --strpe_log ./strpe-testing/peer{0}.log".format(port)
    run(runStr)
    time.sleep(1)
    #run netcat
    run("nc 127.0.0.1 {0}".format(playerPort))

def main(args):
    try:
        opts, args = getopt.getopt(args, "n:t:m:w:")
    except getopt.GetoptError:
        usage()
        sys.exit(2)
    nPeers = nTrusted = nMalicious = waitTimeInSeconds = 0
    for opt, arg in opts:
        if opt == "-n":
            nPeers = int(arg)
        elif opt == "-t":
            nTrusted = int(arg)
        elif opt == "-m":
            nMalicious = int(arg)
        elif opt == "-w":
            waitTimeInSeconds = int(arg)

    checkdir()

    port = 56000
    playerPort = 9999
    trustedPorts = []
    for _ in range(nTrusted):
        trustedPorts.append(random.randint(port, port + nPeers))

    print "running stream"
    runStream()
    print "running splitter"
    runSplitter(map(lambda x: "127.0.0.1:{0}".format(x), trustedPorts))
    print "running peers"
    for _ in range(nPeers + nTrusted):
        if port in trustedPorts:
            print "trusted peer with port {0}".format(port)
            runPeer(port, playerPort, True)
        else:
            print "regular peer with port {0}".format(port)
            runPeer(port, playerPort)

        port, playerPort = port + 1, playerPort + 1

    for _ in range(nMalicious):
        print "malicious peer with port {0}".format(port)
        runPeer(port, playerPort, False, True)
        port, playerPort = port + 1, playerPort + 1

    print "wait for {0} seconds".format(waitTimeInSeconds)
    time.sleep(waitTimeInSeconds)
    killall()
    return 0

if __name__ == "__main__":
    try:
        sys.exit(main(sys.argv[1:]))
    except KeyboardInterrupt:
        killall()

#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os, sys, getopt
import time
import random
import shlex, subprocess
import re

processes = []
DEVNULL = open(os.devnull, 'wb')

nPeers = nTrusted = nMalicious = 0

def checkdir():
    if not os.path.exists("./strpe-testing"):
        os.mkdir("./strpe-testing")

def usage():
    print "args error"

def run(runStr, out = DEVNULL):
    proc = subprocess.Popen(shlex.split(runStr), stdout=out, stderr=out)
    processes.append(proc)

def killall():
    for proc in processes:
        proc.kill()

def runStream():
    run("/Applications/VLC.app/Contents/MacOS/VLC ../src/Big_Buck_Bunny_small.ogv --sout \"#duplicate{dst=standard{mux=ogg,dst=,access=http}}\"")
    time.sleep(1)

def runSplitter(trustedPeers, ds = False):
    if len(trustedPeers) == 0:
        trustedPeers.append("127.0.0.1:1234")
    tps = ""
    for p in trustedPeers:
        tps += "\"{0}\" ".format(p)
    prefix = ""
    if ds: prefix = "ds"
    run("../src/splitter.py --buffer_size 1024 --source_port 8080 --strpe{0} {1} --strpe_log strpe-testing/splitter.log".format(prefix, tps))
    time.sleep(1)

def runPeer(port, playerPort, trusted = False, malicious = False, ds = False):
    #run peer
    strpeds = ""
    if ds: strpeds = "--strpeds"
    runStr = "../src/peer.py --use_localhost --port {0} --player_port {1} {2}".format(port, playerPort, strpeds)
    if trusted and not ds:
        runStr += " --trusted --checkall"
    if malicious:
        runStr += " --malicious --persistent"
    if not malicious:
         runStr += " --strpe_log ./strpe-testing/peer{0}.log".format(port)
    run(runStr, open("strpe-testing/peer{0}.out".format(port), "w"))
    time.sleep(1)
    #run netcat
    run("nc 127.0.0.1 {0}".format(playerPort))

def check(x):
    with open("./strpe-testing/splitter.log") as fh:
        for line in fh:
            pass
        result = re.match("(\d*.\d*)\t(\d*)\s(\d*).*", line)
        if result != None and int(result.group(3)) <= x:
            return True
    return False

def main(args):
    try:
        opts, args = getopt.getopt(args, "n:t:m:s")
    except getopt.GetoptError:
        usage()
        sys.exit(2)

    ds = False

    for opt, arg in opts:
        if opt == "-n":
            nPeers = int(arg)
        elif opt == "-t":
            nTrusted = int(arg)
        elif opt == "-m":
            nMalicious = int(arg)
        elif opt == "-s":
            ds = True


    nPeers = nPeers - nTrusted - nMalicious # for more friendly user input

    checkdir()

    port = 56000
    playerPort = 9999
    trustedPorts = []
    for _ in range(nTrusted):
        trustedPorts.append(random.randint(port, port + nPeers))

    print "running stream"
    runStream()
    print "running splitter"
    runSplitter(map(lambda x: "127.0.0.1:{0}".format(x), trustedPorts), ds)
    print "running peers"
    for _ in range(nPeers + nTrusted):
        if port in trustedPorts:
            print "trusted peer with port {0}".format(port)
            runPeer(port, playerPort, True, False, ds)
        else:
            print "regular peer with port {0}".format(port)
            runPeer(port, playerPort, False, False, ds)

        port, playerPort = port + 1, playerPort + 1

    for _ in range(nMalicious):
        print "malicious peer with port {0}".format(port)
        runPeer(port, playerPort, False, True, ds)
        port, playerPort = port + 1, playerPort + 1

    time.sleep(2)
    while not check(nPeers + nTrusted):
        time.sleep(2)

    print "finish!"

    killall()
    return 0

if __name__ == "__main__":
    try:
        sys.exit(main(sys.argv[1:]))
    except KeyboardInterrupt:
        killall()

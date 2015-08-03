#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os, sys, getopt
import re
import glob

def usage():
    print ""
    return

def calcAverageBufferCorrectnes(roundTime):
    fileList = glob.glob("./strpe-testing/peer*.log")
    correctnesSum = 0.0
    for f in fileList:
        correctnesSum += calcAverageInFile(f, roundTime)
    return correctnesSum / len(fileList)

def calcAverageInFile(inFile, roundTime):
    regex = re.compile("(\d*.\d*)\tbuffer\scorrectnes\s(\d*.\d*)")
    with open(inFile) as f:
        for line in f:
            result = regex.match(line)
            if result != None:
                ts = float(result.group(1))
                if ts >= roundTime:
                    return float(result.group(2))
    return 1

def main(args):
    inFile = ""
    nPeers = nMalicious = 0
    try:
        opts, args = getopt.getopt(args, "n:m:")
    except getopt.GetoptError:
        usage()
        sys.exit(2)
    for opt, arg in opts:
        if opt == "-n":
            nPeers = int(arg)
        elif opt == "-m":
            nMalicious = int(arg)

    regex = re.compile("(\d*.\d*)\t(\d*)\s(\d*).*")
    startParse = False
    roundOffset = 0
    with open("./strpe-testing/splitter.log") as f:
        for line in f:
            result = regex.match(line)
            if result != None:
                ts = float(result.group(1))
                currentRound = int(result.group(2))
                currentTeamSize = int(result.group(3))
                if currentTeamSize >= nPeers - nMalicious and not startParse:
                    startParse = True
                    roundOffset = currentRound
                if startParse:
                    malicious = nMalicious - (nPeers - currentTeamSize)
                    print "{0}\t{1}\t{2}\t{3}".format(currentRound - roundOffset + 1, malicious, currentTeamSize, calcAverageBufferCorrectnes(ts))
    return 0

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os, sys, getopt
import re
import glob

max_buffer_correctness = 0
min_buffer_correctness = 1
max_buffer_filling = 0
min_buffer_filling = 1

def usage():
    print ""
    return

def calcAverageBufferCorrectnes(roundTime):
    fileList = glob.glob("./strpe-testing/peer*.log")
    correctnesSum = fillingSum = 0.0
    for f in fileList:
        info = calcAverageInFile(f, roundTime)
        correctnesSum += info[0]
        fillingSum += info[1]
    return (correctnesSum / len(fileList), fillingSum / len(fileList))

def calcAverageInFile(inFile, roundTime):
    regex_correctness = re.compile("(\d*.\d*)\tbuffer\scorrectnes\s(\d*.\d*)")
    regex_filling = re.compile("(\d*.\d*)\tbuffer\sfilling\s(\d*.\d*)")
    correctness = -1.0
    filling = -1.0
    with open(inFile) as f:
        for line in f:
            result = regex_correctness.match(line)
            result2 = regex_filling.match(line)
            if result != None and correctness == -1.0:
                ts = float(result.group(1))
                if ts >= roundTime:
                    correctness = float(result.group(2))
            if result2 != None and filling == -1.0:
                ts = float(result2.group(1))
                if ts >= roundTime:
                    filling = float(result2.group(2))
            if correctness != -1.0 and filling != -1.0:
                return (correctness, filling)

    return (1.0, 1.0)

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
    print "round\t#malicious\tteamsize\tcorrectness\tfilling"
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
                    info = calcAverageBufferCorrectnes(ts)
                    print "{0}\t{1}\t{2}\t{3}\t{4}".format(currentRound - roundOffset + 1, malicious, currentTeamSize, info[0], info[1])
    return 0

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

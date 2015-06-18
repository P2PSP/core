#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os, sys
import time
from Crypto.Random import random
from Crypto.PublicKey import DSA
from Crypto.Hash import SHA256

N = 100

def sign(message, key):
    h = SHA256.new(message).digest()
    k = random.StrongRandom().randint(1,key.q-1)
    sig = key.sign(h,k)
    return sig

def check(message, key, sig):
    return key.verify(SHA256.new(message).digest(), sig)

def main(args):
    message = "Hello, P2PSP!" * 1024
    key = DSA.generate(1024)
    # measure the sign time
    start_time = time.time()
    for _ in xrange(N):
        sig = sign(message, key)
    print "key.sign x{0} times: {1}s".format(N, time.time() - start_time)

    #measure the verify time
    sig = sign(message, key)
    start_time = time.time()
    for _ in xrange(N):
        r = check(message, key, sig)
    print "key.verify x{0} times: {1}s".format(N, time.time() - start_time)

if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))

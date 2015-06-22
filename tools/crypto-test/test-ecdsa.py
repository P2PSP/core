#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os, sys
import time
from ecdsa import SigningKey

N = 100

def sign(message, key):
    return key.sign(message)

def check(message, key, sig):
    return key.verify(sig, message)

def main(args):
    message = "Hello, P2PSP!" * 1024
    sk = SigningKey.generate()
    vk = sk.get_verifying_key()
    # measure the sign time
    start_time = time.time()
    for _ in xrange(N):
        sig = sign(message, sk)
    print "key.sign x{0} times: {1}s".format(N, time.time() - start_time)

    #measure the verify time
    sig = sign(message, sk)
    start_time = time.time()
    for _ in xrange(N):
        r = check(message, vk, sig)
    print "key.verify x{0} times: {1}s".format(N, time.time() - start_time)


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))

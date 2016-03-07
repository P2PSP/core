#!/usr/bin/env python2

import os
import sys
import shutil
import platform

bin_dir = 'bin'
build_dir = 'build'
only_cmake = False

try:
    shutil.rmtree(bin_dir)
except:
    pass

try:
    shutil.rmtree(build_dir)
except:
    pass

if len(sys.argv) >= 2:
    if sys.argv[1] == 'clean':
        os.system('git clean -dfx')
        quit()
    elif sys.argv[1] == 'only-cmake':
        only_cmake = True

os.makedirs(build_dir)

sys_name = platform.system()

if sys_name == 'Linux':
    print '\nMaking for Linux...\n'
    if os.system('cd build && cmake .. && echo') == 0:
        if not only_cmake:
            os.system('cd build && make')

elif sys_name == 'Darwin':
    print '\nMaking for OS X...\n'

elif sys_name == 'Windows':
    print '\nMaking for Windows...\n'

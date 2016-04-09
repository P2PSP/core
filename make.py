#!/usr/bin/env python

from __future__ import print_function
import os
import sys
import shutil
import platform

bin_dir = 'bin'
build_dir = 'build'
only_cmake = False
cmake = 'cmake'

if len(sys.argv) >= 2:
    if sys.argv[1] == '-h':
        print("{clean|debug}")
        quit()
    if sys.argv[1] == 'clean':
        os.system('git clean -dfx')
        quit()
    if sys.argv[1] == 'debug':
        cmake = cmake + ' -DCMAKE_BUILD_TYPE=Debug'
    elif sys.argv[1] == 'only-cmake':
#        cmake = cmake + ' -DTRACE_SILENT_MODE'
        only_cmake = True

if not os.path.exists(bin_dir):
    try:
        shutil.rmtree(bin_dir)
    except:
        pass

if not os.path.exists(build_dir):
    try:
        shutil.rmtree(build_dir)
    except:
        pass
    os.makedirs(build_dir)

sys_name = platform.system()

if sys_name == 'Linux' or sys_name == 'Darwin':
    print('\nMaking for Linux...\n')
    command = 'cd build && ' + cmake + ' .. && echo'
    if os.system(command) == 0:
        command = 'cd build && make'
        if not only_cmake:
            os.system(command)

elif sys_name == 'Windows':
    print('\nMaking for Windows...\n')

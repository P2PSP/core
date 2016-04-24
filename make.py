#!/usr/bin/env python

from __future__ import print_function
import os
import sys
import shutil
import platform
import subprocess

bin_dir = 'bin'
build_dir = 'build'
only_cmake = False
build_debug = False
cmake = 'cmake'
make = 'make'

if len(sys.argv) >= 2:
    if sys.argv[1] == '-h':
        print("{clean|debug}")
        quit()
    if sys.argv[1] == 'clean':
        os.system('git clean -dfx')
        quit()
    if sys.argv[1] == 'debug':
        build_debug = True
        cmake = cmake + ' -DCMAKE_BUILD_TYPE=Debug'
        make = make + ' VERBOSE=1'
    if sys.argv[1] == 'release':
        cmake = cmake + ' -DCMAKE_BUILD_TYPE=Release'
        
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
    print('\nMaking for Linux...')
    number_of_cores = int(subprocess.Popen("nproc", stdout=subprocess.PIPE).stdout.read())
    print('Number of cores = ' + str(number_of_cores) + '\n')

    if build_debug:
        print('Building for Debug...\n')
    else:
        print('Building for Release...\n')

    command = 'cd build && ' + cmake + ' .. && echo'
    if os.system(command) == 0:
        command = 'cd build && make -j' + str(number_of_cores)
        if not only_cmake:
            os.system(command)

elif sys_name == 'Windows':
    print('\nMaking for Windows...\n')

#!/usr/bin/env python

from __future__ import print_function
import os
import sys
import shutil
import tarfile
import platform
import subprocess
import multiprocessing

bin_dir = 'bin'
build_dir = 'build'
only_cmake = False
build_debug = False
cmake = 'cmake'
make = 'make'

''' replace the url with updated link if any'''
url = 'https://netix.dl.sourceforge.net/project/boost/boost/1.63.0/boost_1_63_0.tar.bz2'

print("downloading boost libraries")
os.system("wget -O boost_1_63_0.tar.bz2 " + url)

''' extracts the downloaded boost libraries'''
def untar(filename):
    if (filename.endswith("tar.bz2")):
        tar = tarfile.open(filename)
        print("Extracting the files...")
        tar.extractall()
        tar.close()
        print("Successfully extracted in Current Directory")
    else:
        print("Not a tar.gz file")

untar("boost_1_63_0.tar.bz2")

'''Installing the boost libraries to a seperate directory '''
os.system("cd boost_1_63_0 && ./bootstrap.sh --prefix=boost_lib && ./b2 install")

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
    number_of_cores = multiprocessing.cpu_count()
    print('Number of cores = ' + str(number_of_cores) + '\n')

    if build_debug:
        print('Building for Debug...\n')
    else:
        print('Building for Release...\n')
        
    ''' below command sets the manually installed libraries rather than the system libraries'''
    command = 'cd build && cmake -DBOOST_NO_SYSTEM_PATHS=TRUE -DBOOST_ROOT="boost_1_63_0" -DBOOST_INCLUDEDIR="boost_1_63_0/boost_lib/include" -DBOOST_LIBRARYDIR="boost_1_63_0/boost_lib/lib" ..'
    if os.system(command) == 0:
        command = 'cd build && make -j' + str(number_of_cores)
        if not only_cmake:
            os.system(command)

elif sys_name == 'Windows':
    print('\nMaking for Windows...\n')

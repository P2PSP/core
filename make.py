#!/usr/bin/env python

import os
import sys
import shutil
import platform

build_dir = 'build'

try:
    shutil.rmtree(build_dir)
except:
    pass

os.makedirs(build_dir)

sys_name = platform.system()

if sys_name == 'Linux':
    print '\nMaking for Linux...\n'
    os.system('cd build && cmake .. && echo && make')
    
elif sys_name == 'Darwin':
    print '\nMaking for OS X...\n'
    
elif sys_name == 'Windows':
    print '\nMaking for Windows...\n'

'''
Created on Jun 1, 2015

@author: maniotrix
'''

import os
try:
    from gi.repository import Gtk
except Exception as msg:
    print(msg)

def get_user_interface(dire, fName):
        fName = find_file(dire, fName)
        builder = Gtk.Builder()
        builder.add_from_file(fName)
        return builder
    
def find_file(dire, fName):
        path = os.path.join(os.path.dirname(dire), fName)
        return path


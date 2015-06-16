'''
Created on Jun 1, 2015

@author: maniotrix
'''

import os
import traceback
try:
    from gi.repository import Gtk
    from common.decorators import exc_handler
except ImportError as msg:
    traceback.print_exc()


@exc_handler
def get_user_interface(dire, fName):
        fName = find_file(dire, fName)
        builder = Gtk.Builder()
        builder.add_from_file(fName)
        return builder

@exc_handler
def find_file(dire, fName):
        path = os.path.join(os.path.dirname(dire), fName)
        return path


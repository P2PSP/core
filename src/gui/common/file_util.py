"""
@package common
file_util module
"""
# This code is distributed under the GNU General Public License (see
# THE_GENERAL_GNU_PUBLIC_LICENSE.txt for extending this information).
# Copyright (C) 2014, the P2PSP team.
# http://www.p2psp.org
# The P2PSP.org project has been supported by the Junta de Andalucia
# through the Proyecto Motriz "Codificacion de Video Escalable y su
# Streaming sobre Internet" (P10-TIC-6548).

# {{{ Imports

import os
import traceback
try:
    from gi.repository import Gtk
    from gui.common.decorators import exc_handler
except ImportError as msg:
    traceback.print_exc()

# }}}

@exc_handler
def get_user_interface(dire, fName):

        """
        Get a "Gtk Builder" after  parsing a file containing a GtkBuilder UI
        definition and merges it with the current contents of builder.

        @param : dire (directory path)
        @param : fName (file name)
        @return : builder
        """

        fName = find_file(dire, fName)
        builder = Gtk.Builder()
        builder.add_from_file(fName)
        return builder

@exc_handler
def find_file(dire, fName):

        """
        Returns a file path after joining one or more path components.

        @param : dire (directory path)
        @param : fName (file name)ff
        @return : path
        """

        path = os.path.join(os.path.dirname(dire), fName)
        return path

@exc_handler
def file_size(path):

    """
    Returns size of the file at the given path.

    @param : path
    """
    f = open(path,"r")
    f.seek(0, os.SEEK_END)
    size = f.tell()
    return size

@exc_handler
def file_del(path):

    """
    Delete a file at the given path.

    @param : path
    """

    f = open(path,"w")
    del(f)



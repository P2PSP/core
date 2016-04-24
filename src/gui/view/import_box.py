"""
@package view
import_box module
"""
# This code is distributed under the GNU General Public License (see
# THE_GENERAL_GNU_PUBLIC_LICENSE.txt for extending this information).
# Copyright (C) 2014, the P2PSP team.
# http://www.p2psp.org

# The P2PSP.org project has been supported by the Junta de Andalucia
# through the Proyecto Motriz "Codificacion de Video Escalable y su
# Streaming sobre Internet" (P10-TIC-6548).

# {{{ Imports

import traceback
try:
    from gi.repository import Gtk
    from gui.common import file_util
    from gui.common.decorators import exc_handler
except ImportError as msg:
    traceback.print_exc()

# }}}

class Import_Box():

    """
    Create graphical interface of the Import Dialog Box.
    """

    @exc_handler
    def __init__(self):

        """
        Get the Gtk Builder for the Import Dialog Box from the respective glade
        file.

        Load all the necessary widgets from the glade file.

        Create a List_Store having 5 Strings as its parameters.
        Set the List_Store as the model of the list_view in Import Box.
        """

        self.interface = file_util.get_user_interface(__file__,
                                        '../data/glade/importbox.glade')
        self.load_widgets()

        ## List_Store to store channel data.
        self.list_store = Gtk.ListStore(str, str,str,str,str)
        self.listview.set_model(self.list_store)

        ## Name of columns in the Gtk ListView.
        self.column_string = None
        self.create_list_view()

    @exc_handler
    def load_widgets(self):

        """
        Get widgets from the glade file.
        """

        ## The Import Dialog Box.
        self.import_box = self.interface.get_object('ImportBox')

        ## File Chooser Buttton.
        self.file_chooser = self.interface.get_object('ImportFileChooserButon')

        ## List_View to display channels in the file to be imported.
        self.listview = self.interface.get_object('ImportChannelList')

        ## Import Button.
        self.import_button = self.interface.get_object('ImportButton')

        ## Cancel Button.
        self.cancel_button = self.interface.get_object('CancelButon')

    @exc_handler
    def add_channel_list_column(self, title, columnId):

        """
        This function adds a column to the list view.
        First it create the Gtk TreeViewColumn and then set
        some needed properties.

        @param : title (name of the column)
        @param : columnId (index of the column in the ListView)
        """

        column = Gtk.TreeViewColumn(title, Gtk.CellRendererText()
                , text=columnId)
        column.set_resizable(True)
        column.set_sort_column_id(columnId)
        self.listview.append_column(column)

    @exc_handler
    def create_list_view(self):

        """
        Specify the column names in the ListView.

        Add each imported channels to the ListView.
        """

        self.column_string = ["Description","Channel_Name","Splitter_Address","Splitter_Port","Thumbnail_Url",]
        for i in range(0,len(self.column_string)):
            self.add_channel_list_column(self.column_string[i],i)

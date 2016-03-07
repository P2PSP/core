"""
@package view
export_box module
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

class Export_Box():

    """
    Create graphical interface of the Export Dialog Box.
    """
    @exc_handler
    def __init__(self):

        """
        Get the Gtk Builder for the Export Dialog Box from the respective glade
        file.

        Load all the necessary widgets from the glade file.

        Create a List_Store having 5 Strings as its parameters.
        Set the List_Store as the model of the list_view in Export Box.
        """

        self.interface = file_util.get_user_interface(__file__,
                                        '../data/glade/exportbox.glade')
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

        ## The Export Dialog Box.
        self.export_box = self.interface.get_object('ExportBox')

        ## List_View to display channels in the file to be exported.
        self.listview = self.interface.get_object('ExportChannelList')

        ## Export button.
        self.export_button = self.interface.get_object('ExportButton')

        ## Cancel button.
        self.cancel_button = self.interface.get_object('CancelButon')

        ## Gtk Text Entry widget to show the location of exported file.
        self.text_entry = self.interface.get_object('FileNameEntry')


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

        Add each channels to be exported to the ListView.
        """

        self.column_string = ["Description","Channel_Name","Splitter_Address","Splitter_Port","Thumbnail_Url",]
        for i in range(0,len(self.column_string)):
            self.add_channel_list_column(self.column_string[i],i)

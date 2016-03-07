"""
@package controller
channel_export_controller module
"""
# This code is distributed under the GNU General Public License (see
# THE_GENERAL_GNU_PUBLIC_LICENSE.txt for extending this information).
# Copyright (C) 2014, the P2PSP team.
# http://www.p2psp.org

# The P2PSP.org project has been supported by the Junta de Andalucia
# through the Proyecto Motriz "Codificacion de Video Escalable y su
# Streaming sobre Internet" (P10-TIC-6548).

# {{{ Imports

from gui.view.export_box import Export_Box
from gui.common.json_exporter import JSON_Exporter
from gui.model.channel_encoder import Channel_Encoder
from gui.model.channel_store import Channel_Store
from gui.model.channel import Channel
from gui.common.decorators import exc_handler
from gi.repository import Gtk
import collections

# }}}

class Export_Controller():

    """
    Exports channels to an external file.

    This Task is achieved by creating a separate Box after selecting "Export
    Channels" SubMenu in File Menu.

    ".p2psp" is set as the extension of the exported file.

    """

    def __init__(self,main_window):

        """
        Get the reference of the main window.

        Intansiate Export Dialog Box.
        Connect the signals associated with the Box glade file.
        Set Box as transient for parent window.
        Set the dimensions of Box which are half of parent window.

        Display the data to export.

        @param : main_window
        """

        ## Parent window of this exporter_window.
        self.parent_window = main_window.window

        ## The Export Dialog Box
        self.box = Export_Box()
        self.box.interface.connect_signals(self.setup_signals())
        self.box.export_box.set_transient_for(self.parent_window)

        ## Width and Height of the parent window.
        width,height = self.parent_window.get_size()
        self.box.export_box.set_size_request(width/2,height/2)
        self.show_exported_data()
        self.box.export_box.show()


    @exc_handler
    def setup_signals(self):

        """
        Setup all the signals associated with main window with contoller
        methods. Every method is passed the reference of the widget and the
        signal data.

        @return : signals
        """

        signals = {
        'on_BrowseButton_clicked'                : self.save_to_file
        ,'on_ExportButton_clicked'               : self._export
        ,'on_CancelButton_clicked'               : self.cancel
                }
        return signals

    @exc_handler
    def show_exported_data(self):

        """
        Get the data to export from the Channel_Store.
        Channels are exported in the same order in which they were added to a
        Category.

        Then each channel's data is appended to list_store of the listview in
        the Export Dialog Box.
        """

        exported_data = Channel_Store.ALL.get_channels()
        if len(exported_data) !=0:
            for channel in exported_data:
                channel_data = collections.OrderedDict(
                                   sorted(exported_data[channel].__dict__.items()))

                self.box.list_store.append(channel_data.values())

    @exc_handler
    def add_filters(self, dialog):

        """
        Creates A Gtk FileFilter.
        File is exported with "p2psp" as extension.

        Filter is added to given Dialog Box.

        @param : dialog (Dialog Box)
        """

        filter_text = Gtk.FileFilter()
        filter_text.set_name("P2PSP Files")
        filter_text.add_mime_type("application/p2psp")
        dialog.add_filter(filter_text)

    @exc_handler
    def save_to_file(self,widget,data=None):

        """
        Get the location of the file where channel data is to be exported.

        Create a new Gtk FileChooser Dialog.

        Add File Filters to the Dialog.

        Set default name of the exported file.

        Get the response of the Dialog when it is closed.

        If the response is Gtk.ResponseType.Accept then set the text in Export
        Box's Textfield location of file.Also "Export" button in the Box is
        enabled.
        """

        dialog = Gtk.FileChooserDialog("Save data to JSON file"
                                      , self.box.export_box,Gtk.FileChooserAction.SAVE
                                      ,(Gtk.STOCK_CANCEL
                                      , Gtk.ResponseType.CANCEL
                                      , Gtk.STOCK_SAVE
                                      , Gtk.ResponseType.ACCEPT))
        dialog.set_default_size(800, 400)

        self.add_filters(dialog)
        Gtk.FileChooser.set_current_name(dialog,"Untitled.p2psp")
        Gtk.FileChooser.set_do_overwrite_confirmation(dialog, True)
        response = dialog.run()

        if response == Gtk.ResponseType.ACCEPT:
            filename= Gtk.FileChooser.get_filename(dialog)
            self.box.text_entry.set_text(filename)
            self.box.export_button.set_sensitive(True)
        dialog.destroy()

    @exc_handler
    def _export(self,widget,data=None):

        """
        Create A JSON Exporter.

        Get the file path from the TextField in Export Box.

        Export channel data to specified path.
        """

        exporter  = JSON_Exporter()
        path = self.box.text_entry.get_text()
        if path != '':
            exporter.to_JSON(path
                            ,Channel_Store.ALL.get_channels()
                            ,Channel_Encoder)
            self.box.export_box.destroy()

    @exc_handler
    def cancel(self,widget,data=None):

        """
        Close  Export Dialog Box.
        """

        self.box.export_box.destroy()



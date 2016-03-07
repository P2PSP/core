"""
@package controller
channel_import_controller module
"""
# This code is distributed under the GNU General Public License (see
# THE_GENERAL_GNU_PUBLIC_LICENSE.txt for extending this information).
# Copyright (C) 2014, the P2PSP team.
# http://www.p2psp.org

# The P2PSP.org project has been supported by the Junta de Andalucia
# through the Proyecto Motriz "Codificacion de Video Escalable y su
# Streaming sobre Internet" (P10-TIC-6548).

# {{{ Imports

from gui.view.import_box import Import_Box
from gui.common.json_importer import JSON_Importer
from gui.model.channel_store import Channel_Store
from gui.model.channel import Channel
from gui.common.decorators import exc_handler
from gui.common import  graphics_util
import collections

# }}}

class Import_Controller():

    """
    Imports channels from JSON file with "p2psp" as file extension.

    """

    def __init__(self,main_window):

        """
        Get the reference of the main window.

        Instantiate Import Dialog Box.
        Connect the signals associated with the Box.
        Set Box transient for main window.

        Set the dimensions which are half of parent window.

        @param : main_window

        """
        self.app_window = main_window
        
        ## Parent window of the Import Dialog Box.
        self.parent_window = main_window.window
        
        ## Import Dialog Box.
        self.box = Import_Box()

        ## Channels to import.
        self.imported_data = None
        self.box.interface.connect_signals(self.setup_signals())
        self.box.import_box.set_transient_for(self.parent_window)

        ## Width and Height of the parent window.
        width,height = self.parent_window.get_size()
        self.box.import_box.set_size_request(width/2,height/2)
        self.box.import_box.show()


    @exc_handler
    def setup_signals(self):

        """
        Setup all the signals associated with main window with contoller
        methods. Every method is passed the reference of the widget and the
        signal data.

        @return : signals
        """

        signals = {
        'on_ImportFileChooserButton_selection_changed'   : self.on_file_selected
        ,'on_ImportButton_clicked'               : self._import
        ,'on_CancelButton_clicked'               : self.cancel
                }
        return signals

    @exc_handler
    def on_file_selected(self,widget,data=None):

        """
        Clear the list_store of the list_view of the Import Dialog Box.
        Get the file path selected using Gtk FileChooserButton.

        Create a new JSON_Importer.

        Enable "Import" button.

        Channels are imported in the same order in which they have been written
        in the file.

        Each imported channel is appended in the liSt_view of the Import Box.
        """

        self.box.list_store.clear()
        _file = widget.get_filename()
        if _file == '':
            return
        importer = JSON_Importer()
        self.imported_data = importer.from_JSON(_file)
        if self.imported_data is not None:
            self.box.import_button.set_sensitive(True)
            for channel in self.imported_data:
                channel_data = collections.OrderedDict(
                                   sorted(self.imported_data[channel].items()))
                self.box.list_store.append(channel_data.values())

    @exc_handler
    def _import(self,widget,data=None):

        """
        Get the categoey in which the channels will be imported.

        Convert JSON format channels to "Channel" objects.

        Add the channels to category.

        Get the channel data which are to be displayed in IconView in main
        window.

        Properly scale the image thumbnail of the channel.
        Add the channels to the Iconview in the main window.

        Close the Import Dialog Box.
        """

        all_category = Channel_Store.ALL
        if self.imported_data is not None:
            for channel in self.imported_data:
                imported_channel = Channel(self.imported_data[channel])
                all_category.add(channel,imported_channel)
                (channel_name,image_url,desc) = (channel
                                ,imported_channel.get_thumbnail_url()
                                ,imported_channel.get_description())
                scaled_image = graphics_util.get_scaled_image(image_url,180)
                self.app_window.icon_list_store.append([scaled_image,channel_name,desc])
        self.box.import_box.destroy()

    @exc_handler
    def cancel(self,widget,data=None):

        """
        Closes Import Dialog Box.
        """

        self.box.import_box.destroy()



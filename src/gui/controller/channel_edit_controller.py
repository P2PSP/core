"""
@package controller
channel_edit_controller module
"""
# This code is distributed under the GNU General Public License (see
# THE_GENERAL_GNU_PUBLIC_LICENSE.txt for extending this information).
# Copyright (C) 2014, the P2PSP team.
# http://www.p2psp.org

# The P2PSP.org project has been supported by the Junta de Andalucia
# through the Proyecto Motriz "Codificacion de Video Escalable y su
# Streaming sobre Internet" (P10-TIC-6548).

# {{{ Imports

from gui.model.channel_store import Channel_Store
from gui.model.channel import Channel
from gui.view.edit_box import Edit_Box
from gui.common.decorators import exc_handler
from gui.common import url_util
from gui.common import graphics_util
from gi.repository import Gtk

# }}}

class Edit_Controller():

    """
    Edit channels.
    
    """
    
    def __init__(self,main_window):

        """
        Get the reference of the main window.

        Intansiate Edit Dialog Box.
        Connect the signals associated with the Box glade file.
        Set Box as transient for parent window.
        Set the dimensions of Box which are half of parent window.

        @param : main_window
        """
        
        self.parent_window = main_window.window
        self.app_view = main_window

        self.box = Edit_Box()
        self.box.interface.connect_signals(self.setup_signals())
        self.box.dialog.set_transient_for(self.parent_window)

        ## Width and Height of the parent window.
        width,height = self.parent_window.get_size()
        self.box.dialog.set_size_request(width/2,height/2)
        
        self.item  = self.app_view.channel_iconview.get_selected_items()[0]
        self.channel_key = self.app_view.icon_list_store[self.item][1]
        self.channel = Channel_Store.ALL.get_channel(self.channel_key)
        self.box.name.set_text(self.channel.name)
        self.box.description.set_text(self.channel.description)
        self.box.thumbnail.set_text("file://"+self.channel.thumbnail_url)
        self.box.address.set_text(self.channel.splitter_addr)
        self.box.port.set_value(int(self.channel.splitter_port))
        
        self.box.dialog.show()

    @exc_handler
    def setup_signals(self):

        """
        Setup all the signals associated with main window with contoller
        methods. Every method is passed the reference of the widget and the
        signal data.

        @return : signals
        """

        signals = {
        'on_OkButton_clicked'                    : self.edit
        ,'on_CancelButton_clicked'               : self.cancel
                }
        return signals 
        
        
    @exc_handler
    def edit(self,widget,data=None):
        
        
        #verify thumbnil url,address,port validity
        #if not verified show proper message.
        #elif verified:
        #currently implemented only for local thumbnail images.
        #get texts from all the entries.
        #create channel with given data.
        #add the channel to store
        #get channel data and display it in iconview
        
        """
        Verify channel configuration and add it to the iconview where channels
        are listed and also to the channel store.
        """
        
        name = self.box.name.get_text()
        desc = self.box.description.get_text()
        thumbnail = self.box.thumbnail.get_text()
        address = str(self.box.address.get_text())
        port = self.box.port.get_value_as_int()
        if name == "":
            msg_dialog = Gtk.MessageDialog(self.parent_window, 0, Gtk.MessageType.ERROR,
            Gtk.ButtonsType.CLOSE, "CHANNEL NAME IS EMPTY")
            msg_dialog.format_secondary_text("A proper name for channel should be provided.")
            msg_dialog.run()
            msg_dialog.destroy()
            return
        elif desc == "":
            msg_dialog = Gtk.MessageDialog(self.parent_window, 0, Gtk.MessageType.ERROR,
            Gtk.ButtonsType.CLOSE, "CHANNEL DESCRIPTION IS EMPTY")
            msg_dialog.format_secondary_text("Channel's details should be provided.")
            msg_dialog.run()
            msg_dialog.destroy()
            return
        elif url_util.verify_url(str(thumbnail)) == False:
            msg_dialog = Gtk.MessageDialog(self.parent_window, 0, Gtk.MessageType.ERROR,
            Gtk.ButtonsType.CLOSE, "INVALID URL")
            msg_dialog.format_secondary_text(str(thumbnail))
            msg_dialog.run()
            msg_dialog.destroy()
            return
        elif url_util.validate_ip(str(address)) == False:
            msg_dialog = Gtk.MessageDialog(self.parent_window, 0, Gtk.MessageType.ERROR,
            Gtk.ButtonsType.CLOSE, "INVALID IP")
            msg_dialog.format_secondary_text(str(address))
            msg_dialog.run()
            msg_dialog.destroy()
            return
        elif int(port) == 0:
            msg_dialog = Gtk.MessageDialog(self.parent_window, 0, Gtk.MessageType.ERROR,
            Gtk.ButtonsType.CLOSE, "INVALID PORT")
            msg_dialog.format_secondary_text(str(port))
            msg_dialog.run()
            msg_dialog.destroy()
            return
        else :
            self.channel.name = name
            self.channel.description = desc
            self.channel.thumbnail_url = url_util.get_path(str(thumbnail))
            self.channel.splitter_addr = address
            self.channel.splitter_port = port
            (name,image_url,desc) = (self.channel.get_name()
                                    ,self.channel.get_thumbnail_url()
                                    ,self.channel.get_description())
            scaled_image = graphics_util.get_scaled_image(image_url,180)
            self.app_view.icon_list_store[self.item][0] = scaled_image
            self.app_view.icon_list_store[self.item][1] = name
            self.app_view.icon_list_store[self.item][2] = desc
            if self.channel_key == name:
                self.box.dialog.destroy()
                return
            store = Channel_Store()
            store.get_default().replace_key(self.channel_key,name)
        self.box.dialog.destroy()

    @exc_handler
    def cancel(self,widget,data=None):
       
        """
        Close Edit Dialog Box.
        """
        self.box.dialog.destroy()

"""
@package view
main_window module
"""
# This code is distributed under the GNU General Public License (see
# THE_GENERAL_GNU_PUBLIC_LICENSE.txt for extending this information).
# Copyright (C) 2014, the P2PSP team.
# http://www.p2psp.org

# The P2PSP.org project has been supported by the Junta de Andalucia
# through the Proyecto Motriz "Codificacion de Video Escalable y su
# Streaming sobre Internet" (P10-TIC-6548).

# {{{ Imports

import sys
import traceback
try:
    from gi.repository import Gtk
    from gi.repository import Gdk
    from gi.repository.GdkPixbuf import Pixbuf
    from gui.common import file_util
    from gui.common.decorators import exc_handler
except ImportError as msg:
    traceback.print_exc()

# }}}

class Main_Window():

    """
    Used to create graphical interface of main window.
    """
    try:
        ## The default screen for the default display.
        SCREEN = Gdk.Screen.get_default()
    except Exception as msg:
        traceback.print_exc()

    @exc_handler
    def __init__(self):

        """
        Get the Gtk Builder for the main window glade file.

        Load all the necessary widgets from the glade file.

        Set the dimensions of the channel box according to the default screen
        size of the machine(this automatically sets the default size of the
        window when it opens).

        Create A List_Store with parameters PixBuf,String and String.
        Add the List_Store to the iconview.
        Configure Iconview.
        Configure Player Surface.

        """

        ## Gtk Builder of the main_window.
        self.interface = file_util.get_user_interface(__file__,
                                        '../data/glade/mainwindow.glade')
        self.load_widgets()
        self.window.connect("destroy",Gtk.main_quit)
        self.channel_box.set_size_request((self.SCREEN.get_width()/8)+50,
                                            self.SCREEN.get_height()/4)
        self.icon_list_store = Gtk.ListStore(Pixbuf, str,str)
        self.set_iconview_model(self.icon_list_store)
        self.configure_iconview()
        self.configure_player_surface()


    @exc_handler
    def load_widgets(self):

        """
        Get widgets from the glade file.
        """

        ## Main Window
        self.window = self.interface.get_object('MainWindow')

        ## Drawing Area where media is rendered.
        self.player_surface = self.interface.get_object('Surface')

        ## Widget to toggle visibility on channel icon_view.
        self.channel_revealer = self.interface.get_object('ToggleChannels')

        ## Media playback toggle button.
        self.playback_toggle_button = self.interface.get_object('TogglePlaybackButton')

        ## Media Playback stop button.
        self.playback_stop_button = self.interface.get_object('StopButton')

        ## Surface Fullscreen button.
        self.player_fullscreen_button = self.interface.get_object('FullscreenButton')

        ## Menu bar
        self.menu = self.interface.get_object('Menu')

        ## Widget to show channels
        self.channel_box = self.interface.get_object('ChannelGroupBox')

        ## Status boc of the player.
        self.status_box = self.interface.get_object('PlayerAndStatusBox')

        ## play icon image
        self.play_image = self.interface.get_object('PlayImage')

        ## pause icon image
        self.pause_image = self.interface.get_object('PauseImage')

        ## Progress Bar to update buffer status of the peer.
        self.buffer_status_bar = self.interface.get_object('ProgressBar')

        ## Label to update upload speed of the peer.
        self.up_speed_label = self.interface.get_object('UpSpeedlabel')

        ## Label to update download speed of the peer.
        self.down_speed_label = self.interface.get_object('DownSpeedlabel')

        ## Label to update Number of Peers in the Team.
        self.users_label = self.interface.get_object('Users_Label')

        ## widgets to display channels as icons.
        self.channel_iconview = self.interface.get_object('ChannelIconView')

        ## SubMenu to toggle visibility of channels.
        self.toggle_channel_box = self.interface.get_object('ViewChannelBox')
        
        ## fullscreen icon image
        self.fullscreen_image =  self.interface.get_object('FullscreenImage')

        ## leave fullscreen icon image
        self.unfullscreen_image = self.interface.get_object('UnFullscreenImage')
        
        ## The Popup Menu
        self.popup_menu = self.interface.get_object('ChannelPopupMenu')

    def configure_player_surface(self):

        """
        Set size of the player drawing area according to the default screen size
        of the machine.
        """

        self.player_surface.set_size_request(self.SCREEN.get_width()/4,
                                             self.SCREEN.get_height()/4)
        self.player_surface.show()

    def show(self):

        """
        Show all the child widgets of main window.
        However child widgets with property "not show all" are not affected.
        """

        self.window.show_all()

    def hide_all_but_surface(self):

        """
        Hide all the child widgets of the main_window except the player drawing
        area.
        """

        self.menu.hide()
        self.channel_box.hide()
        self.status_box.hide()

    def hide_status_box(self):

        """
        Hide Player status box.
        """

        self.status_box.hide()

    def set_iconview_model(self,model):

        """
        Set the model which is used to display icons in the icon_view.

        @param : model
        """

        self.channel_iconview.set_model(model)

    def configure_iconview(self):

        """
        Configure Iconview.

        Specify how  channel name, thumbnail url, channel details(shown as
        tooltip) will be displayed inside the icon_view.
        """

        self.channel_iconview.set_pixbuf_column(0)
        self.channel_iconview.set_text_column(1)
        self.channel_iconview.set_tooltip_column(2)
        self.channel_iconview.set_columns(0)
        self.channel_iconview.set_item_width(85)

    def show_status_box(self):

        """
        Show Player Status Box.
        """
        self.status_box.show()


    def hide_channels_box(self):

        """
        Hide Channels Box.
        """

        self.channel_box.hide()
        self.channel_revealer.set_label('<<')

    def show_channels_box(self):

        """
        Show Channels Box.
        """

        self.channel_box.show()
        self.channel_revealer.set_label('>>')

    def show_minimal_interface(self):

        """
        Hide Application Title Bar.
        """
        self.window.fullscreen()

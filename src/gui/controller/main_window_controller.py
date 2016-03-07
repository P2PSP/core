"""
@package controller
main_window_controller module
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
    from gui.common.decorators import exc_handler
    from gui.adapter.buffering_adapter import Buffering_Adapter
    from gui.adapter.speed_adapter import Speed_Adapter
    from gi.repository import Gdk
    from gi.repository import Gtk
    from gi.repository import GdkX11
    from gi.repository import GObject
    from gui.common import file_util
    from gui.model.peer_thread import Peer_Thread
    from gui.model import peer_thread
    from gui.model.channel import Channel
    from gui.model import channel_store
    from gui.model.channel_store import Channel_Store
    from gui.controller.channel_import_controller import Import_Controller
    from gui.controller.channel_export_controller import Export_Controller
    from gui.controller.channel_add_controller import Add_Controller
    from gui.controller.channel_edit_controller import Edit_Controller
    from gui.common import graphics_util
    from gui.common.json_exporter import JSON_Exporter
    from gui.common.json_importer import JSON_Importer
    from gui.model.channel_encoder import Channel_Encoder
except ImportError as msg:
    traceback.print_exc()

# }}}

class Main_Controller():

    """
    Controller which controls the signals from the main window. It is
    responsible for communication between models and  widgets in main window.
    It uses Adapters to update data from the core package to the
    """

    ## MRL of default local P2PSP Peer Stream.
    PLAYER_MRL = 'http://localhost:9999'
    try:
        ## Path of P2PSP logo.
        PLAYER_MEDIA_SOURCE = file_util.find_file(__file__,
                                                  "../data/images/p2psp.jpg")
    except Exception as msg:
        traceback.print_exc()

    def __init__(self,window,model):

        """
        Connects all the signals from the main window glade file. Adapters are
        provided  the widgets they have to update  parameters from core package.
        At last a  default peer is exported to import dhannels.

        @param : window (Main Window)
        @param : model (Models)
        """

        ## Whether Peer is active or not.(Here property with same name from
        ## Peer_Thread class could be also used).
        self.peer_active = False

        ## Whether player is paused.
        self.player_paused = False

        ## Whether player is fullscreen.
        self.player_fullscreen  = False

        ## Whether channel_Iconview  is revealed.
        self.channels_revealed = True

        ## Whether player status box is hidden.
        self.status_box_hidden = False

        ## The vlc player instance.
        self.vlc_player_instance = None

        ## Window id of the player window.
        self.win_id = None

        ## The Player itself.
        self.player = None

        ## The Main App Window
        self.app_window = window

        ## App Models
        self.app_model = model

        self.app_window.interface.connect_signals(self.setup_signals())
        self.app_window.player_surface.connect("realize",self._realized)

        ## Buffer Adapter
        self.buffer_adapter = Buffering_Adapter()

        ## Speed  Adapter
        self.speed_adapter = Speed_Adapter()
        try:
            self.buffer_adapter.set_widget(self.app_window.buffer_status_bar)
            self.speed_adapter.set_widget(self.app_window.down_speed_label
                                        ,self.app_window.up_speed_label
                                        ,self.app_window.users_label)
        except Exception as msg:
            traceback.print_exc()

        #self.show_monitor_channel()
        self.export_sample_monitor()
        
        
        self.restore_app_state()
        
        ## Current selection which is being played
        self.treepath_played = None

    @exc_handler
    def export_sample_monitor(self):

       """
       Exports  a monitor channel runinng on local machine. For that first we
       get monitor channel configuration data from channel store.
       After that the monitor data is exported to file in JSON format using
       JSON Exporter and Channel Encoder.
       """

       ## Data to export
       exported_data = channel_store.get_monitor_data()

       ## monitor channel
       monitor_channel = Channel(exported_data["monitor"])

       ## path where channel data is exported.
       path = file_util.find_file(__file__,
                                   "../data/channels/to_import_sample_data.p2psp")

       ## JSON Exporter
       exporter  = JSON_Exporter()
       exporter.to_JSON(path,{"monitor":monitor_channel},Channel_Encoder)

    
    def restore_app_state(self):
        
        """
        Restore channels present in last session of app.
        
        Channels are restored after importing channels from JSON File.
        """
        
        _file =file_util.find_file(__file__,
                                   "../data/channels/saved_channels")
        importer = JSON_Importer()
        self.restored_data = importer.from_JSON(_file)
        if self.restored_data is not None:
            all_category = Channel_Store.ALL
            for channel in self.restored_data:
                restored_channel = Channel(self.restored_data[channel])
                all_category.add(channel,restored_channel)
                (channel_name,image_url,desc) = (channel
                                ,restored_channel.get_thumbnail_url()
                                ,restored_channel.get_description())
                scaled_image = graphics_util.get_scaled_image(image_url,180)
                self.app_window.icon_list_store.append([scaled_image,channel_name,desc])
                
    @exc_handler
    def show_monitor_channel(self):#only for testing purpose

        """
        Show default channel in Channel Iconview when app starts.
        """
        monitor_data = channel_store.get_monitor_data()
        channel = Channel(monitor_data["monitor"])
        store = Channel_Store()
        store.get_default().add(channel.name,channel)
        (name,image_url,desc) = (channel.get_name()
                                ,channel.get_thumbnail_url()
                                ,channel.get_description())
        scaled_image = graphics_util.get_scaled_image(image_url,180)
        for i in range(0,1):
            self.app_window.icon_list_store.append([scaled_image,name,desc])

    @exc_handler
    def start_peer(self):

        """
        Progress Bar fraction is set to zero.
        A Peer Thread is started.
        """

        self.peer_active = True
        self.app_window.buffer_status_bar.set_fraction(0)
        self.app_window.buffer_status_bar.show()
        thread1 = Peer_Thread(1, "Peer Thread")
        thread1.start()
        print('thread started')


    @exc_handler
    def show(self):

        """
        Show main window.
        """
        self.app_window.show()


    @exc_handler
    def setup_signals(self):

        """
        Setup all the signals associated with main window with contoller
        methods. Every method is passed the reference of the widget and the
        signal data.

        @return : signals
        """

        ## Dictionary where signal's name from glade file is used as keys and
        ## controller's methods are values.
        signals = {
        'on_StopButton_clicked'                 : self.stop_player
        ,'on_TogglePlaybackButton_clicked'      : self.toggle_player_playback
        ,'on_ToggleChannels_button_press_event' : self.toggle_channel_box
        ,'on_FullscreenButton_clicked'          : self.toggle_player_fullscreen
        ,'on_ChannelIconView_button_press_event': self.handle_selected_channel
        ,'on_Import_activate'                   : self.import_channels
        ,'on_Export_activate'                   : self.export_channels
        ,'on_VolumeButton_value_changed'        : self.control_player_volume
        ,'on_Surface_key_press_event'           : self.toggle_status_box
        ,'on_ViewPlayerStatusBox_toggled'       : self.toggle_status_box
        ,'on_Add_activate'                      : self.add_channel
        ,'on_Play_activate'                     : self.handle_on_Play
        ,'on_Edit_activate'                     : self.handle_on_Edit
        ,'on_Remove_activate'                   : self.handle_on_Remove
        ,'on_PlayerEventBox_button_press_event' : self.handle_PlayerEventBox
                }
        return signals

    def add_channel(self,widget,data=None):

        """
        Call the Add Controller to add channels.
        """
        
        controller = Add_Controller(self.app_window)
        
    def handle_on_Play(self,widget,data=None):

        """
        Call the Play Controller to play channels.
        """
        
        self.play_selection()
        
    def handle_on_Edit(self,widget,data=None):
        
        """
        Call the Edit Controller to edit channels.
        """
        
        controller = Edit_Controller(self.app_window)

    def handle_on_Remove(self,widget,data=None):
        
        
        """
        Get the selected item in channel iconview.
        Get list store associated with the iconview.
        
        Remove channel from Channel Store and iconview's list store.
        
        If the channel is being played , stop the player.
        """
        
        selection = self.app_window.channel_iconview.get_selected_items()[0]
        model = self.app_window.icon_list_store
        channel_key = self.app_window.icon_list_store[selection][1]
        channel = Channel_Store.ALL.remove(channel_key)
        _iter = model.get_iter(selection)
        model.remove(_iter)
        if self.treepath_played == selection:
            self.stop_player(None,data=None)
        
        
    @exc_handler
    def import_channels(self,widget,data=None):

        """
        Call the Import Controller to import channels.
        """

        ## Channel Import Controller.
        controller = Import_Controller(self.app_window)

    @exc_handler
    def export_channels(self,widget,data=None):

        """
        Call the Export Controller to export channels.
        """

        ## Channel Export Controller.
        controller = Export_Controller(self.app_window)

    @exc_handler
    def toggle_player_type(self,win_id):

        """
        Toggle player media. This function is used to switch between displaying
        P2PSP logo and channel.
        """

        if self.peer_active :

            ## Player playing a channel
            self.player = self.vlc_player_instance.get_stream_player(self.win_id,
                                                            self.PLAYER_MRL)
        else:

            ## Player when playing image.
            self.player = self.vlc_player_instance.get_media_player(self.win_id,
                                                    self.PLAYER_MEDIA_SOURCE)
        GObject.idle_add(self.player.play)


    @exc_handler
    def stop_player(self, widget, data=None):

        """
        Stop the player's playback.
        Display P2PSP logo in Player window.
        Set gtk_play_image as toggle_playback_button image.
        Hide Buffer Progress Bar
        """

        GObject.idle_add(self.player.stop)
        self.peer_active = False
        self.player_paused = False
        GObject.idle_add(self.toggle_player_type,self.win_id)
        self.app_window.playback_toggle_button.set_image(self.app_window.play_image)
        self.app_window.buffer_status_bar.hide()


    def save_app_state(self):
        
        """
        App state saved.
        
        The channels in the default category is exported to a JSON File.
        This file is used to restore channels which have been there in the app
        while it was closed.
        """
        exporter  = JSON_Exporter()
        path = file_util.find_file(__file__,
                                   "../data/channels/saved_channels")
        if path != '':
            exporter.to_JSON(path
                            ,Channel_Store.ALL.get_channels()
                            ,Channel_Encoder)
    @exc_handler
    def quit(self):

        """
        Stop Player.
        Delete initially  exported data.
        """
        self.player.stop()
        path = file_util.find_file(__file__,
                                    "../data/channels/to_import_sample_data.p2psp")
        file_util.file_del(path)
        
        self.save_app_state()


    def end_callback(self):

        """
        Callback invoked when Player's window is resized or configured.
        """

        if self.peer_active == False:
            self.toggle_player_type(self.win_id)

    @exc_handler
    def toggle_player_playback(self, widget, data=None):

        """
        Handler for Player's Playback Button (Play/Pause).

        If any channel is selected in channel's list then play that. Otherwise
        play default channel.
        """

        if  len(self.app_window.channel_iconview.get_selected_items()) == 0 and self.peer_active == False:
            self.start_peer()
            self.app_window.playback_toggle_button.set_image(self.app_window.pause_image)
            self.toggle_player_type(self.win_id)
        elif self.peer_active == False and self.player_paused == False:
            self.play_selection(self.app_window.channel_iconview)
            self.app_window.playback_toggle_button.set_image(self.app_window.pause_image)

        elif self.peer_active == True and self.player_paused == True:
            self.player.play()
            self.app_window.playback_toggle_button.set_image(self.app_window.pause_image)
            self.player_paused = False

        elif self.peer_active == True and self.player_paused == False:
            self.player.pause()
            self.app_window.playback_toggle_button.set_image(self.app_window.play_image)
            self.player_paused = True
        else:
            pass

    @exc_handler
    def toggle_channel_box(self, widget, data=None):

        """
        Control Channel Iconview visibility.

        channel_revealer's label is also toggled between '<<' and '>>' through
        this handler.
        """

        if self.channels_revealed == True:
            self.app_window.hide_channels_box()
            self.channels_revealed = False
        elif self.channels_revealed == False:
            self.app_window.show_channels_box()
            self.channels_revealed = True

    
    @exc_handler
    def handle_PlayerEventBox(self, widget, data=None):
        if data.type == Gdk.EventType._2BUTTON_PRESS and data.button == 1:
            self.toggle_player_fullscreen(None,None)
            
    @exc_handler
    def toggle_player_fullscreen(self, widget, data=None):

        """
        Control fullscreen display of media playing in player's window.
        """
        if self.player_fullscreen == False:
            self.app_window.hide_all_but_surface()
            self.app_window.window.fullscreen()
            self.app_window.player_fullscreen_button.set_image(self.app_window.unfullscreen_image)
            self.player_fullscreen = True
            self.status_box_hidden = True
            self.app_window.player_surface.grab_focus()
        else:
            self.show()
            self.app_window.window.unfullscreen()
            self.app_window.player_fullscreen_button.set_image(self.app_window.fullscreen_image)
            self.player_fullscreen = False
            self.status_box_hidden = False

    def redraw_surface(self,widget,data=None):

        """
        Handles the callback when player's window is re-configured.
        """

        self.end_callback()

    @exc_handler
    def toggle_status_box(self,widget,data=None):

        """
        Handler for toggling player's status box.
        Check whether key pressed  is of type GDK_ESCAPE.
        """

        if self.player_fullscreen == True and data.keyval == Gdk.KEY_Escape:
            self.toggle_player_status_bar()
        elif self.player_fullscreen == False:
            self.toggle_player_status_bar()

    @exc_handler
    def toggle_player_status_bar(self):
        if self.status_box_hidden == False :
            self.app_window.hide_status_box()
            self.status_box_hidden = True
        else:
            self.app_window.show_status_box()
            self.status_box_hidden = False

    @exc_handler
    def handle_selected_channel(self,widget,data=None):

        """
        Plays selected channel from the channels list in Iconview widget.

        Channel when channel in the iconview is double clicked.
        Get the selected channel and play it.
        """

        if  len(self.app_window.channel_iconview.get_selected_items()) == 0:
            return
        if data.type == Gdk.EventType._2BUTTON_PRESS and data.button == 1:
            if  len(widget.get_selected_items()) == 0:
                return
            else:
                self.play_selection()
        elif data.type == Gdk.EventType.BUTTON_PRESS and data.button == 3:
            self.app_window.popup_menu.popup(None, None, 
                   None,
                   None, data.button, data.time)
            return

    @exc_handler
    def play_selection(self):

        """
        Play selected channel.

        Get the item which is selected in iconview.
        Get the reference key for that item from list_store.
        Get the channel corresponding to the item from channel_store.
        Extract channel configuration data from the channel.
        Configure Peer Thread with extracted data.

        Now stop playing what ever is being played.
        Hide Progress Bar if shown.
        Start Peer.
        Toggle playback button.
        Toggle player type.
        """

        item  = self.app_window.channel_iconview.get_selected_items()[0]
        self.treepath_played = item
        channel_key = self.app_window.icon_list_store[item][1]
        channel = Channel_Store.ALL.get_channel(channel_key)
        data = (channel.get_splitter_addr()
                ,int(channel.get_splitter_port()))
        peer_thread.configure_peer(data)
        self.player.stop()
        self.peer_active = False
        self.player_paused = False
        self.app_window.buffer_status_bar.hide()
        self.start_peer()
        self.app_window.playback_toggle_button.set_image(self.app_window.pause_image)
        self.toggle_player_type(self.win_id)


    @exc_handler
    def control_player_volume(self,widget,data=None):

        """
        Adjust volume of media which is being played.
        """

        self.player.audio_set_volume(int(data*100))

    @exc_handler
    def _realized(self,widget,data=None):

        """
        This function is called when Drawing Surface is  first
        realized along with the main window.

        Get the window id of the Surface.
            For Linux :  Window.get_xid()

        Render P2PSP logo on the Player Surface.
        Set Surface cursor Gdk.CursorType.ARROW.
        Connect "configure_event" of the Surface with "redraw_surface".
        """

        ## Gdk.CursorType.Arrow
        cursor = Gdk.Cursor.new(Gdk.CursorType.ARROW)
        self.vlc_player_instance = self.app_model.get_vlc_player_instance()
        self.win_id = widget.get_window().get_xid()
        self.toggle_player_type(self.win_id)
        widget.get_window().set_cursor(cursor)
        print('surface_cursor = '  + str(widget.get_window().get_cursor().__class__ ))
        self.app_window.player_surface.connect("configure_event",
                                                self.redraw_surface)

import traceback
try:
    from common.decorators import exc_handler
    from adapter.buffering_adapter import Buffering_Adapter
    from adapter.speed_adapter import Speed_Adapter
    from gi.repository import Gdk
    from gi.repository import Gtk
    from gi.repository import GdkX11
    from gi.repository import GObject
    import common.file_util as file_util
    from model.peer_thread import Peer_Thread
    from model import peer_thread
    from model.channel import Channel
    from model import channel_store
    from model.channel_store import Channel_Store
    from channel_import_controller import Import_Controller
    from channel_export_controller import Export_Controller
    import common.graphics_util as graphics_util
    from common.json_exporter import JSON_Exporter
    from model.channel_encoder import Channel_Encoder
except ImportError as msg:
    traceback.print_exc()

class Main_Controller():

    PLAYER_MRL = 'http://localhost:9999'
    try:
        PLAYER_MEDIA_SOURCE = file_util.find_file(__file__,
                                                  "../../data/images/p2psp.jpg")
    except Exception as msg:
        traceback.print_exc()

    def __init__(self,window,model):
        self.peer_active = False
        self.player_paused = False
        self.player_fullscreen  = False
        self.channels_revealed = True
        self.status_box_hidden = False
        self.vlc_player_instance = None
        self.win_id = None
        self.player = None
        self.app_window = window
        self.app_model = model
        self.app_window.interface.connect_signals(self.setup_signals())
        self.app_window.player_surface.connect("realize",self._realized)
        self.buffer_adapter = Buffering_Adapter()
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

    @exc_handler
    def export_sample_monitor(self):
        exported_data = channel_store.get_monitor_data()
        monitor_channel = Channel(exported_data["monitor"])
        path = file_util.find_file(__file__,
                                    "../../data/channels/to_import_sample_data.p2psp")
        exporter  = JSON_Exporter()
        exporter.to_JSON(path,{"monitor":monitor_channel},Channel_Encoder)

    @exc_handler
    def show_monitor_channel(self):#only for testing purpose
        monitor_data = channel_store.get_monitor_data()
        channel = Channel(monitor_data["monitor"])
        store = Channel_Store()
        store.get_default().add(channel.name,channel)
        (name,image_url,desc) = (channel.get_name()
                                ,channel.get_thumbnail_url()
                                ,channel.get_description())
        scaled_image = graphics_util.get_scaled_image(image_url,180)
        for i in range(0,20):
            self.app_window.icon_list_store.append([scaled_image,name,desc])

    @exc_handler
    def start_peer(self):
        self.peer_active = True
        self.app_window.buffer_status_bar.set_fraction(0)
        self.app_window.buffer_status_bar.show()
        thread1 = Peer_Thread(1, "Peer Thread")
        thread1.start()
        print('thread started')


    @exc_handler
    def show(self):
        self.app_window.show()


    @exc_handler
    def setup_signals(self):
        signals = {
        'on_StopButton_clicked'                 : self.stop_player
        ,'on_TogglePlaybackButton_clicked'      : self.toggle_player_playback
        ,'on_ToggleChannels_button_press_event' : self.toggle_channel_box
        ,'on_FullscreenButton_clicked'          : self.toggle_player_fullscreen
        ,'on_ChannelIconView_button_press_event': self.play_selected_channel
        ,'on_Import_activate'                   : self.import_channels
        ,'on_Export_activate'                   : self.export_channels
        ,'on_VolumeButton_value_changed'        : self.control_player_volume
        ,'on_Surface_key_press_event'           : self.toggle_status_box
                }
        return signals


    @exc_handler
    def import_channels(self,widget,data=None):
            controller = Import_Controller(self.app_window)

    @exc_handler
    def export_channels(self,widget,data=None):
        controller = Export_Controller(self.app_window)

    @exc_handler
    def toggle_player_type(self,win_id):
        if self.peer_active :
            self.player = self.vlc_player_instance.stream_player(self.win_id,
                                                            self.PLAYER_MRL)
        else:
            self.player = self.vlc_player_instance.media_player(self.win_id,
                                                    self.PLAYER_MEDIA_SOURCE)
        self.player.play()


    @exc_handler
    def stop_player(self, widget, data=None):
        GObject.idle_add(self.player.stop)
        self.peer_active = False
        self.player_paused = False
        GObject.idle_add(self.toggle_player_type,self.win_id)
        self.app_window.playback_toggle_button.set_image(self.app_window.play_image)
        self.app_window.buffer_status_bar.hide()

    @exc_handler
    def quit(self):
        self.player.stop()
        path = file_util.find_file(__file__,
                                    "../../data/channels/to_import_sample_data.p2psp")
        file_util.file_del(path)


    def end_callback(self):
        if self.peer_active == False:
            self.toggle_player_type(self.win_id)

    @exc_handler
    def toggle_player_playback(self, widget, data=None):
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
        if self.channels_revealed == True:
            self.app_window.channel_box.hide()
            self.app_window.channel_revealer.set_label('<<')
            self.channels_revealed = False
        elif self.channels_revealed == False:
            self.app_window.channel_box.show()
            self.app_window.channel_revealer.set_label('>>')
            self.channels_revealed = True

    @exc_handler
    def toggle_player_fullscreen(self, widget, data=None):
        if self.player_fullscreen == False:
            self.app_window.hide_all_but_surface()
            self.app_window.window.fullscreen()
            self.player_fullscreen = True
            self.status_box_hidden = True
            self.app_window.player_surface.grab_focus()
        else:
            self.show()
            self.app_window.window.unfullscreen()
            self.player_fullscreen = False
            self.status_box_hidden = False

    def redraw_surface(self,widget,data=None):
        self.end_callback()

    @exc_handler
    def toggle_status_box(self,widget,data=None):
        #check whether data.keyeval is GDK_ESCAPE
        if self.player_fullscreen == True and data.keyval == 65307:
            if self.status_box_hidden == False :
                self.app_window.hide_status_box()
                self.status_box_hidden = True
            else:
                self.app_window.show_status_box()
                self.status_box_hidden = False

    @exc_handler
    def play_selected_channel(self,widget,data=None):#implented only for testing purposes
        if data.type == Gdk.EventType._2BUTTON_PRESS:
            if  len(widget.get_selected_items()) == 0:
                return
            else:
                self.play_selection(widget)

    @exc_handler
    def play_selection(self,iconview):
        item  = iconview.get_selected_items()[0]
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
        self.player.audio_set_volume(int(data*100))

    @exc_handler
    def _realized(self,widget,data=None):
        cursor = Gdk.Cursor.new(Gdk.CursorType.ARROW)
        self.vlc_player_instance = self.app_model.get_vlc_player_instance()
        self.win_id = widget.get_window().get_xid()
        self.toggle_player_type(self.win_id)
        widget.get_window().set_cursor(cursor)
        print('surface_cursor = '  + str(widget.get_window().get_cursor().__class__ ))
        self.app_window.player_surface.connect("configure_event",
                                                self.redraw_surface)

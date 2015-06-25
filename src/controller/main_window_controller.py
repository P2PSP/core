import traceback
try:
    from common.decorators import exc_handler
    from adapter.buffering_adapter import Buffering_Adapter
    from adapter.speed_adapter import Speed_Adapter
    from gi.repository import Gdk
    from gi.repository import GdkX11
    import common.file_util as file_util
    from model.peer_thread import Peer_Thread
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
        ,'on_Surface_button_press_event'        : self.toggle_status_box
                }
        return signals


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
        self.player.stop()
        self.peer_active = False
        self.player_paused = False
        self.toggle_player_type(self.win_id)
        self.app_window.playback_toggle_button.set_image(self.app_window.play_image)
        self.app_window.buffer_status_bar.hide()

    @exc_handler
    def quit(self):
        self.player.stop()


    def end_callback(self):
        if self.peer_active == False:
            self.toggle_player_type(self.win_id)

    @exc_handler
    def toggle_player_playback(self, widget, data=None):
        if self.peer_active == False and self.player_paused == False:
            self.start_peer()
            self.app_window.playback_toggle_button.set_image(self.app_window.pause_image)
            self.toggle_player_type(self.win_id)

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
        else:
            self.show()
            self.app_window.window.unfullscreen()
            self.player_fullscreen = False
            self.status_box_hidden = False

    def redraw_surface(self,widget,data=None):
        self.end_callback()

    @exc_handler
    def toggle_status_box(self,widget,data=None):
        if self.player_fullscreen == True:
            if self.status_box_hidden == False :
                self.app_window.hide_status_box()
                self.status_box_hidden = True
            else:
                self.app_window.show_status_box()
                self.status_box_hidden = False

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

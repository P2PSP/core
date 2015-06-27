import sys
import traceback
try:
    from gi.repository import Gtk
    from gi.repository import Gdk
    from gi.repository.GdkPixbuf import Pixbuf
    import common.file_util as file_util
    from common.decorators import exc_handler
except ImportError as msg:
    traceback.print_exc()

class Main_Window():

    try:
        SCREEN = Gdk.Screen.get_default()
    except Exception as msg:
        traceback.print_exc()

    @exc_handler
    def __init__(self):
        self.interface = file_util.get_user_interface(__file__,
                                        '../../data/glade/mainwindow.glade')
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
        self.window = self.interface.get_object('MainWindow')
        self.player_surface = self.interface.get_object('Surface')
        self.channel_revealer = self.interface.get_object('ToggleChannels')
        self.playback_toggle_button = self.interface.get_object('TogglePlaybackButton')
        self.playback_stop_button = self.interface.get_object('StopButton')
        self.player_fullscreen_button = self.interface.get_object('FullscreenButton')
        self.menu = self.interface.get_object('Menu')
        self.channel_box = self.interface.get_object('ChannelGroupBox')
        self.status_box = self.interface.get_object('PlayerAndStatusBox')
        self.play_image = self.interface.get_object('PlayImage')
        self.pause_image = self.interface.get_object('PauseImage')
        self.buffer_status_bar = self.interface.get_object('ProgressBar')
        self.up_speed_label = self.interface.get_object('UpSpeedlabel')
        self.down_speed_label = self.interface.get_object('DownSpeedlabel')
        self.users_label = self.interface.get_object('Users_Label')
        self.channel_iconview = self.interface.get_object('ChannelIconView')

    def configure_player_surface(self):
        self.player_surface.set_size_request(self.SCREEN.get_width()/4,
                                             self.SCREEN.get_height()/4)
        self.player_surface.show()

    def show(self):
        self.window.show_all()

    def hide_all_but_surface(self):
        self.menu.hide()
        self.channel_box.hide()
        self.status_box.hide()

    def hide_status_box(self):
        self.status_box.hide()
        
    def set_iconview_model(self,model):
        self.channel_iconview.set_model(model)
        
    def configure_iconview(self):
        self.channel_iconview.set_pixbuf_column(0)
        self.channel_iconview.set_text_column(1)
        self.channel_iconview.set_tooltip_column(2)
        self.channel_iconview.set_columns(0)
        self.channel_iconview.set_item_width(85)

    def show_status_box(self):
        self.status_box.show()

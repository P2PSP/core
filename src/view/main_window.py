import sys
try:
    from gi.repository import GObject
    from gi.repository import Gtk
    import common.file_util as file_util
except Exception as msg:
    print(msg)
    
    
class Main_Window():
    
    
    def __init__(self):
        self.interface = file_util.get_user_interface('glade', '../data/glade/mainwindow.glade')
        self.load_widgets()
        self.window.connect("destroy",Gtk.main_quit)
        self.channel_box.set_size_request(350,600)
        self.configure_player_surface()
        
    def load_widgets(self):
        self.window = self.interface.get_object('MainWindow')
        self.player_surface = self.interface.get_object('Surface')
        self.channel_revealer = self.interface.get_object('ToggleChannels')
        self.playback_toggle_button = self.interface.get_object('TogglePlaybackButton')
        self.playback_stop_button = self.interface.get_object('StopButton')
        self.player_fullscreen_button = self.interface.get_object('FullscreenButton')
        self.menu = self.interface.get_object('Menu')
        self.channel_box = self.interface.get_object('ChannelScrolledWindow')
        self.status_box = self.interface.get_object('PlayerAndStatusBox')
        self.play_image = self.interface.get_object('PlayImage')
        self.pause_image = self.interface.get_object('PauseImage')
        self.monitor_image = self.interface.get_object('MonitorThumbnail')
        self.monitor_image.set_from_file(file_util.find_file('images','../data/images/monitor_thumbnail.png'))
        self.buffer_status_bar = self.interface.get_object('ProgressBar')
        self.up_speed_label = self.interface.get_object('UpSpeedlabel')
        self.down_speed_label = self.interface.get_object('DownSpeedlabel')
        self.users_label = self.interface.get_object('Users_Label')
        
    def configure_player_surface(self):
        self.player_surface.set_size_request(600,600)
        self.player_surface.show()
        
    def show(self):
        self.window.show_all()
        
    def hide_all_but_surface(self):
        self.menu.hide()
        self.channel_box.hide()
        self.status_box.hide()
        
    def hide_status_box(self):
        self.status_box.hide()
        
    def show_status_box(self):
        self.status_box.show()
        

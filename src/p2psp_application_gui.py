import threading , gui.file_util , core.peer as peer ,gui.vlc ,sys #, time , gui.vlc
from  gui.player import Player_Instance
from core.peer_ims import  Peer_IMS 
try:
    from gi.repository import GObject
    from gi.repository import Gtk
    from gi.repository import GdkX11
    from gi.repository import Gdk
except Exception as msg:
    print(msg)


class Peer_Thread (threading.Thread):
    def __init__(self, threadID, name):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
    def run(self):
        print "Starting " + self.name
        self.x=peer.Peer()
        print "Exiting " + self.name

class Main_Application():
    
    PLAYER_MRL = 'http://localhost:9999'
    Peer_IMS.USE_LOCALHOST = True 
    PLAYER_MEDIA_SOURCE = "../data/images/p2psp.jpg"
    
    
    def __init__(self):
        self.peer_active  = False
        self.player_paused = False
        self.player_fullscreen  = False
        self.channels_revealed = True
        self.status_box_hidden = False
        self.interface = gui.file_util.get_user_interface('glade', '../data/glade/P2PSP_GUI.glade')
        self.load_widgets()
        self.interface.connect_signals(self.setup_signals())
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
        self.monitor_image.set_from_file(gui.file_util.find_file('images','../data/images/monitor_thumbnail.png'))
        
    def start_peer(self):
        thread1 = Peer_Thread(1, "Peer Thread")
        thread1.start()
        self.peer_active = True
        print 'thread started'
        
    def show(self):
        self.window.show_all()
        
    def setup_signals(self):
        signals = {
        'on_StopButton_clicked'                 : self.stop_player
        ,'on_TogglePlaybackButton_clicked'      : self.toggle_player_playback
        ,'on_ToggleChannels_button_press_event' : self.toggle_channel_box
        ,'on_FullscreenButton_clicked'          : self.toggle_player_fullscreen
        ,'on_Surface_button_press_event'        : self.toggle_status_box
                   }
        return signals
    
    def configure_player_surface(self):
        self.player_surface.set_size_request(600,600)
        self.player_surface.show()
        self.player_surface.connect("realize",self._realized)
        self.player_surface.set_events(self.player_surface.get_events() |
                                       Gdk.EventMask.BUTTON_PRESS_MASK)
        
    def toggle_player_type(self,win_id):
        if self.peer_active :
            self.player = self.player_instance.stream_player(self.win_id,self.PLAYER_MRL)
        else:
            self.player = self.player_instance.media_player(self.win_id,self.PLAYER_MEDIA_SOURCE)
        self.player.play()
             
    def stop_player(self, widget, data=None):
        self.player.stop()
        self.peer_active = False
        self.toggle_player_type(self.win_id)
        self.playback_toggle_button.set_image(self.play_image)
        #self.player_instance.em.event_attach(gui.vlc.EventType.MediaPlayerEndReached,self.end_callback)
        
    def quit(self):
        #self.player_instance.em.event_detach(gui.vlc.EventType.MediaPlayerEndReached)
        self.player.stop()
        
    def end_callback(self):
        if self.peer_active == False:
            self.toggle_player_type(self.win_id)
        
    def toggle_player_playback(self, widget, data=None):
        if self.peer_active == False and self.player_paused == False:
            #self.player_instance.em.event_detach(gui.vlc.EventType.MediaPlayerEndReached)
            self.start_peer()
            self.playback_toggle_button.set_image(self.pause_image)
            self.toggle_player_type(self.win_id)
            
        elif self.peer_active == True and self.player_paused == True:
            self.player.play()
            self.playback_toggle_button.set_image(self.pause_image)
            self.player_paused = False
        elif self.peer_active == True and self.player_paused == False:
            self.player.pause()
            self.playback_toggle_button.set_image(self.play_image)
            self.player_paused = True
        else:
            pass
        
    def toggle_channel_box(self, widget, data=None):
        if self.channels_revealed == True:
            self.channel_box.hide()
            self.channel_revealer.set_label('<<')
            self.channels_revealed = False
        elif self.channels_revealed == False:
            self.channel_box.show()
            self.channel_revealer.set_label('>>')
            self.channels_revealed = True
        
    def hide_all_but_surface(self):
        self.menu.hide()
        self.channel_box.hide()
        self.status_box.hide()
        
    def toggle_player_fullscreen(self, widget, data=None):
        if self.player_fullscreen == False:
            self.window.fullscreen()
            self.hide_all_but_surface()
            self.player_fullscreen = True
            self.status_box_hidden = True
        else:
            self.window.unfullscreen()
            self.show()
            self.player_fullscreen = False
            self.status_box_hidden = False
            
    def redraw_surface(self,widget,data=None):
        self.end_callback()
            
    def hide_status_box(self):
        self.status_box.hide()
        
    def show_status_box(self):
        self.status_box.show()
        
    def toggle_status_box(self,widget,data=None):
        if self.player_fullscreen == True:
            if self.status_box_hidden == False :
                self.hide_status_box()
                self.status_box_hidden = True
            else:
                self.show_status_box()
                self.status_box_hidden = False
                                
    def _realized(self,widget,data=None):
        self.player_instance = Player_Instance()
        #self.player_instance.em.event_attach(gui.vlc.EventType.MediaPlayerEndReached,self.end_callback)
        self.win_id = widget.get_window().get_xid()
        self.toggle_player_type(self.win_id)
        self.player_surface.connect("configure_event", self.redraw_surface)
        
if __name__ == "__main__":
    #Gdk.threads_init()
    App = Main_Application()
    App.show()
    Gtk.main()
    App.quit()
    print "Exiting Gtk-Main Thread"
    sys.exit(0)

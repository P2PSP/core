#script tested with python2.7

import sys,os

module_path = os.path.join(os.path.dirname(__file__),"../../..")
sys.path.append(module_path)

import gui.common.file_util as file_util
from gui.common.decorators import exc_handler
from gi.repository import GdkX11
from gi.repository import Gtk
from gui.lib import vlc


path = file_util.find_file(__file__,
                                    "../../../gui/data/images/p2psp.jpg")
                                    
class Gtk3Player():
    """A VLC window.
    The player can be controlled through 'player', which
    is a vlc.MediaPlayer() instance.
    """
    def __init__(self):
        self.interface = file_util.get_user_interface(__file__,
                                        '../../../gui/data/glade/test_player_surface.glade')
        self.load_widgets()
        self.draw_area.set_size_request(300,300)
        self.draw_area.connect("realize",self._realized)
        self.window.connect("destroy",Gtk.main_quit)
        self.window.show()
    
    @exc_handler
    def load_widgets(self):
        self.window = self.interface.get_object('MainWindow')
        self.draw_area = self.interface.get_object('Surface')
        
    @exc_handler
    def _realized(self, widget, data=None):
        win_id = widget.get_window().get_xid()
        movie = path
        # Create instane of VLC and create reference to movie.
        self.vlcInstance = vlc.Instance()
        self.media = self.vlcInstance.media_new(movie, 'sub-filter=marq')
        self.player = self.vlcInstance.media_player_new()
        self.player.set_xwindow(win_id)
        self.player.set_media(self.media)
        self.player.play()
        
if __name__ == "__main__":
    player = Gtk3Player()
    Gtk.main()

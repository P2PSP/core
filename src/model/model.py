import traceback
try:
    from vlc_player import VLC_Player
except ImportError as msg:
    traceback.print_exc()
    
class Model():  
    
    def __init__(self):        
        self.vlc_player_instance = VLC_Player()
        
    def get_vlc_player_instance(self):
        return self.vlc_player_instance

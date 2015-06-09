try:
    from media.vlc_player import VLC_Player
except Exception as msg:
    print(msg)
    
class Model():  
    
    def __init__(self):        
        self.vlc_player_instance = VLC_Player()
        
    def get_vlc_player_instance(self):
        return self.vlc_player_instance

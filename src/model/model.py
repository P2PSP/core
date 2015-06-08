try:
    from media.player import Player_Instance
except Exception as msg:
    print(msg)
    
class Model():
    
    
    def __init__(self):
        
        self.player_instance = Player_Instance()
        
    def get_player_instance(self):
        return self.player_instance

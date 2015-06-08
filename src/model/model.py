try:
    from media.player import Player_Instance
    from wrapper.p2psp_peer import Peer_Thread
except Exception as msg:
    print(msg)
    
class Model():
    
    
    def __init__(self):
        
        self.player_instance = Player_Instance()
        self.peer_thread = Peer_Thread(1, "Peer Thread")
        
    def get_peer_thread(self):
        return self.peer_thread
        
    def get_player_instance(self):
        return self.player_instance

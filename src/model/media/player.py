'''
Created on May 31, 2015

@author: maniotrix
'''
from lib import vlc
class Player_Instance():
    '''
    classdocs
    '''

    MEDIA_SOURCE = ""
    def __init__(self):
        '''
        Constructor
        '''
        # Creates Vlc Instance
        self.vlcInstance = vlc.Instance("--no-xlib")
        self.player = self.vlcInstance.media_player_new()
        self.em = self.player.event_manager()
        
    def _get_media(self,Source):
        MEDIA_SOURCE = Source
        media = self.vlcInstance.media_new(MEDIA_SOURCE, 'sub-filter=marq')
        return media
        
    def _set_win_id(self,win_id):
        self.player.set_xwindow(win_id)
        
    def _set_mrl(self,mrl):
        self.player.set_mrl(mrl)
        
    def _set_media(self,Source):
        self.player.set_media(self._get_media(Source))
        
        
    def media_player(self,win_id,Source):
        self._set_win_id(win_id)
        self._set_media(Source)
        return self.player
    
    def stream_player(self,win_id,mrl):
        self._set_win_id(win_id)
        self._set_mrl(mrl)
        return self.player
        
        

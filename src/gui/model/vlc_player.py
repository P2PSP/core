"""
@package model
vlc_player module 
"""
# This code is distributed under the GNU General Public License (see
# THE_GENERAL_GNU_PUBLIC_LICENSE.txt for extending this information).
# Copyright (C) 2014, the P2PSP team.
# http://www.p2psp.org

# The P2PSP.org project has been supported by the Junta de Andalucia
# through the Proyecto Motriz "Codificacion de Video Escalable y su
# Streaming sobre Internet" (P10-TIC-6548).

# {{{ Imports

import traceback
try:
    from gui.lib import vlc
except ImportError as msg:
    traceback.print_exc()
    
# }}}


class VLC_Player():
    '''
    A wrapper over libvlc.
    This Class provides separate functions for playing both 
    file and network streams.
    '''
    
    ## file or network location
    MEDIA_SOURCE = ""
    
    def __init__(self):
        
        '''
        A new vlc "Instance" is created with 'Xlib' initialized for threads.
        Xlib (also known as libX11) is an X Window System protocol client 
        library for interacting with an X server. 
        A player is initialized from the same "Instance". 
        '''
        
        ## Single  Vlc Instance used to play any media. 
        self.vlcInstance = vlc.Instance("--no-xlib")
        ## Single player used to play any media.
        self.player = self.vlcInstance.media_player_new()
        self.player.video_set_mouse_input(False)
        
    def _get_media(self,Source):
        
        '''
        Get a new media from media source.
        
        @param: Source 
        @return: media 
        '''
        
        MEDIA_SOURCE = Source
        ## new vlc media from the media source.
        media = self.vlcInstance.media_new(MEDIA_SOURCE)
        return media
        
    def _set_win_id(self,win_id):
        
        """
        This function is used to provide vlc MediaPlayer the window id of the window where the
        video will be played.
        
        @param : win_id 
                    window id of the window where video will be rendered.
        """
        
        self.player.set_xwindow(win_id)
        
    def _set_mrl(self,mrl):
        
        """Set the MRL to play.

        @param mrl: The MRL
        """
        
        self.player.set_mrl(mrl)
        
    def _set_media(self,Source):
        
        '''Set the media that will be played by the media player.
        
        @param Source: the Media.
        '''
        
        self.player.set_media(self._get_media(Source))
        
        
    def get_media_player(self,win_id,Source):
        
        '''This Function is used to play local media.
        
        @param win_id : window id of the widget where video is displayed.
        @param Source : the Media.
        @return player: the Player
        '''
        
        self._set_win_id(win_id)
        self._set_media(Source)
        return self.player
    
    def get_stream_player(self,win_id,mrl):
        
        '''This Function is used to play network streams from specified urls.
        
        @param win_id : window id of the widget where video is displayed.
        @param Source : the Media.
        @return player: the Player
        '''
        
        self._set_win_id(win_id)
        self._set_mrl(mrl)
        return self.player

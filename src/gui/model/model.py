"""
@package model
model module 
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
    from gui.model.vlc_player import VLC_Player
except ImportError as msg:
    traceback.print_exc()
    
# }}}

class Model():  
    
    '''
    A class which provides models to controller.
    Currently only models in vlc_player module is provided. However it would be
    better if all the models from  "model" package needed in controllers were
    provided by this module.
    '''
    
    def __init__(self):        
        
        ## A VLC_Player model
        self.vlc_player_instance = VLC_Player()
        
    def get_vlc_player_instance(self):
        
        """
        This is used to get A VLC_Player model instance.
        
        @return : vlc_player_instance
        """
        
        return self.vlc_player_instance

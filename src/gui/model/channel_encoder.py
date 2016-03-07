"""
@package model
channel_encoder module 
"""
# This code is distributed under the GNU General Public License (see
# THE_GENERAL_GNU_PUBLIC_LICENSE.txt for extending this information).
# Copyright (C) 2014, the P2PSP team.
# http://www.p2psp.org

# The P2PSP.org project has been supported by the Junta de Andalucia
# through the Proyecto Motriz "Codificacion de Video Escalable y su
# Streaming sobre Internet" (P10-TIC-6548).

# {{{ Imports

import json
from gui.model.channel import Channel

# }}}

class Channel_Encoder(json.JSONEncoder):
    
    """
    A JSONEncoder specially to encode channels.
    """
    
    def default(self,obj):
        
        """
        Method inherited from JSONEncoder is overidden.
        
        @param : obj 
                A Channel
        @return : obj.__dict__
        """
        if isinstance(obj, Channel):
            return obj.__dict__
        else:
            return json.JSONEncoder.default(self, obj)

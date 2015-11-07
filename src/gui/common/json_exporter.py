"""
@package common
json_exporter module 
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
from gui.common.decorators import exc_handler

# }}}

class JSON_Exporter():
    
    """
    A wrapper to write data in JSON format to a specified file.
    """
    @exc_handler
    def to_JSON(self,path,channels,encoder):
        
        """
        Dumps channels to a JSON file using Channel_Encoder.
        
        @param : path
        @param : channels
        @param : encoder (Channel Encoder)
        """
        
        json_file = open(path,"w")
        json.dump(channels , json_file, indent = 4 , cls = encoder)
        json_file.close()

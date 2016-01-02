"""
@package common
json_importer module 
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

class JSON_Importer():
    
    """
    A wrapper to load data in JSON format from JSON files.
    """
    
    @exc_handler
    def from_JSON(self,path):
        
        """
        Returns data inside a given json file. If the path is invalid , 
        "NoneType" Object is returned.
        
        @param  : path
        @return : data (JSON data)
        """
        try:
            json_file = open(path,"r")
        except IOError:
            return None
        data = json.load(json_file)
        json_file.close()
        return data

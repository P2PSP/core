"""
@package model
peer_thread module 
"""
# This code is distributed under the GNU General Public License (see
# THE_GENERAL_GNU_PUBLIC_LICENSE.txt for extending this information).
# Copyright (C) 2014, the P2PSP team.
# http://www.p2psp.org

# The P2PSP.org project has been supported by the Junta de Andalucia
# through the Proyecto Motriz "Codificacion de Video Escalable y su
# Streaming sobre Internet" (P10-TIC-6548).

# {{{ Imports

import threading
import traceback

try:
    from peer import Peer
    from core import common
    from core.peer_ims_gui import Peer_IMS_GUI as Peer_IMS # Peer_IMS should use only the console :-/
    from gui.common.decorators import exc_handler
except ImportError as msg:
    traceback.print_exc()

# }}}

def configure_peer(data=None):
    
    """
    Configure peer's Splitter address and port.
    
    @param data : List containing Splitter address and port.
    """
    
    Peer_IMS.SPLITTER_ADDR = data[0]
    Peer_IMS.SPLITTER_PORT = data[1]

## Use localhost instead the IP of the addapter
Peer_IMS.USE_LOCALHOST = True

## Peer is not running in console mode.
common.CONSOLE_MODE = False

class Peer_Thread (threading.Thread):
    
    """
    Starts peers in new Thread.    
    """
    
    def __init__(self, threadID, name):
        
        """
        Initialise thread with parameters parameters.
        
        @param : threadID 
        @param : name 
                Thread name
        """
        threading.Thread.__init__(self)
        
        ## Whether peer is active or not
        self.peer_active = False
        self.threadID = threadID
        self.name = name

    @exc_handler
    def run(self):
        
        """
        Peer is now active. A new P2PSP Peer object is created.
        """
        
        print("Starting " + self.name)
        self.peer_active = True
        self._peer = Peer()
        print("Exiting " + self.name)

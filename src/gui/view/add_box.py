"""
@package view
add_box module
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
    from gui.common import file_util
    from gui.common.decorators import exc_handler
except ImportError as msg:
    traceback.print_exc()

# }}}

class Add_Box():


    """
    Create graphical interface of the Add Dialog Box.
    """
    
    @exc_handler
    def __init__(self):

        """
        Get the Gtk Builder for the Add Dialog Box from the respective glade
        file.

        Load all the necessary widgets from the glade file.

        """
        
        self.interface = file_util.get_user_interface(__file__,
                                        '../data/glade/add_dialog.glade')
        self.load_widgets()

    @exc_handler
    def load_widgets(self):

        """
        Get widgets from the glade file.
        """
        
        ## The Dialog box.
        self.dialog = self.interface.get_object('AddBox')

        ## Channel Name TextEntry
        self.name = self.interface.get_object('NameEntry')

        ## Channel Detail TextEntry
        self.description = self.interface.get_object('DescriptionEntry')

        ## Channel Thumbnail image TextEntry
        self.thumbnail = self.interface.get_object('ThumbnailEntry')

        ## Channel Address TextEntry
        self.address = self.interface.get_object('AddressEntry')

        ## Channel Port TextEntry
        self.port = self.interface.get_object('PortEntry')

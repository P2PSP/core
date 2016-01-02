"""
@package adapter
speed_adapter module 
"""
# This code is distributed under the GNU General Public License (see
# THE_GENERAL_GNU_PUBLIC_LICENSE.txt for extending this information).
# Copyright (C) 2014, the P2PSP team.
# http://www.p2psp.org

# The P2PSP.org project has been supported by the Junta de Andalucia
# through the Proyecto Motriz "Codificacion de Video Escalable y su
# Streaming sobre Internet" (P10-TIC-6548).

# {{{ Imports

try:
    from gui.common.decorators import exc_handler
except Exception as msg:
    print(msg)

# }}}

@exc_handler
def update_widget(down_speed,up_speed,users):

    """
    Update the download/upload speed of Peer.
    
    Update Number of Peers in the Team.
    
    @param : down_speed
    @param : up_speed
    @param : users
    """

    Speed_Adapter.DOWN_WIDGET.set_text(down_speed)
    Speed_Adapter.UP_WIDGET.set_text(up_speed)
    Speed_Adapter.USERS_WIDGET.set_text('Users Online: '+users)

class Speed_Adapter():

    """
    This Design Pattern is used to update the graphical user
    interface with the "download/upload speed" of a Peer and "Number of Peers in 
    a Team" from P2PSP Project.Objects of this class should be instantiated 
    inside a  controller.
    """

    ## Widget where the upload speed will be updated.
    UP_WIDGET = None

    ## Widget where the download speed will be updated.
    DOWN_WIDGET = None

    ## Widget where the Number of peers in the Team will be updated.
    USERS_WIDGET = None

    def set_widget(self,down_label,up_label,users_label):

        """
        Set the widgets used to update "download/upload speed" of a Peer
        and "Number of Peers in the Team".
        
        @param : down_label
        @param : up_label
        @param : users_label
        """

        Speed_Adapter.DOWN_WIDGET = down_label
        Speed_Adapter.UP_WIDGET = up_label
        Speed_Adapter.USERS_WIDGET = users_label

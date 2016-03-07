"""
@package adapter
buffering_adapter module
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
except ImportError as msg:
    print(msg)

# }}}

@exc_handler
def update_widget(BUFFER_STATUS):

    """
    Update the buffer status of the peer which is being played by the player.

    Set Progress Bar progress fraction to buffer status.

    When the buffer status is 100% hide the Progress Bar.
    @param : BUFFER_STATUS (of Peer)
    """

    Buffering_Adapter.WIDGET.set_fraction(float(BUFFER_STATUS)/100)
    if BUFFER_STATUS == 100:
        Buffering_Adapter.WIDGET.hide()

class Buffering_Adapter():

    """
    This Design Pattern is used to update the graphical user
    interface with the buffer status of a Peer in P2PSP Project.Objects of this
    class should be instantiated inside a  controller.
    """

    ## Widget where the buffer status will be updated.
    WIDGET = None

    def set_widget(self,progress_bar):

        """
        Set the widget used to update buffer status of a Peer.

        @param : progress_bar
        """

        Buffering_Adapter.WIDGET = progress_bar

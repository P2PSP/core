# The P2PSP.org project has been supported by the Junta de Andalucia
# through the Proyecto Motriz "Codificacion de Video Escalable y su
# Streaming sobre Internet" (P10-TIC-6548).

from __future__ import print_function
from time import gmtime, strftime

def _print_(*args, **kwargs):
    """Prints the time and the rest of the message."""
    print(strftime("%H:%M:%S", gmtime()), *args, **kwargs)

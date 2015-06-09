from __future__ import print_function
from time import gmtime, strftime

def _print_(*args, **kwargs):
    """Prints the time and the rest of the message."""
    print(strftime("%H:%M:%S", gmtime()), *args, **kwargs)

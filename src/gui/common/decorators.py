"""
@package common
decorators module 
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
from functools import wraps

# }}}

def exc_handler(_function):
    
    """
    Used to decorate functions within  try-except block.
    
    @param  : _function
    @return : function_
            Decorated function
    """
    @wraps(_function)
    def function_(*args,**kwargs):
        try:
            func = _function(*args,**kwargs)
            return func
        except Exception as msg:
            traceback.print_exc()
    return function_

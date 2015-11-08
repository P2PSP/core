"""
@package common
url_util module
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
import socket
from urllib.parse import urlparse
try:
    from gui.common.decorators import exc_handler
except ImportError as msg:
    traceback.print_exc()

# }}}

URL_SCHEMES = ['http','https','file']

@exc_handler
def verify_url(url):

    """
    Verify the given url. Http,Https and File are the only url schemes used for
    thumbnail image.
    
    @param : url
    """
    
    parser = urlparse(url)
    url_scheme = parser.scheme
    for scheme in URL_SCHEMES:
        if url_scheme == scheme:
            break
    else :
        return False
    
    return True
    
@exc_handler
def get_path(url):

    """
    Extract path from a url.
    
    @param : url
    """
    
    parser = urlparse(url)
    url_scheme = parser.scheme
    if str(url_scheme) == 'file':
        return parser.path
    else:
        return url

@exc_handler
def get_scheme(url):

    """
    Extract scheme from a url.
    
    @param : url
    """
    
    parser = urlparse(url)
    return parser.scheme

@exc_handler
def validate_ip(ip_addr):

    """
    Validate an IPv4 or IPv6 address.
    
    @param : ip_addr
    """
    
    try:
        socket.inet_aton(ip_addr)
        return True
    except socket.error :
        pass
    try:
        socket.inet_pton(socket.AF_INET6 , ip_addr)
        return True
    except socket.error :
        return False

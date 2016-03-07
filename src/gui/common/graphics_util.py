"""
@package common
graphics_util module 
"""
# This code is distributed under the GNU General Public License (see
# THE_GENERAL_GNU_PUBLIC_LICENSE.txt for extending this information).
# Copyright (C) 2014, the P2PSP team.
# http://www.p2psp.org

# The P2PSP.org project has been supported by the Junta de Andalucia
# through the Proyecto Motriz "Codificacion de Video Escalable y su
# Streaming sobre Internet" (P10-TIC-6548).

# {{{ Imports
from gi.repository import Gdk
from gi.repository.GdkPixbuf import Pixbuf
from gui.common.decorators import exc_handler
from . import file_util

p2psp_logo_path = file_util.find_file(__file__,
                                    '../../data/images/monitor_thumbnail.png')

# }}}

@exc_handler
def get_scaled_image(path,image_width):
    
    """
    Get a image scaled according to specified image_width.
    
    A new GDK Pixbuf is obtained for the given image path.
    New height of image is calculated according to specified image width.
    
    Pixbuf is scaled simply with parameters : 
                destination image_width
                destination image_height
                the interpolation of the transformation(GDK Interp_Type)
    
    @param : path (Image location)
    @param : image_width
    
    @return : scaled_pix
    """
    default_image_width = image_width
    try:
        pixbuf = Pixbuf.new_from_file(path)
    except Exception as msg:
        return get_scaled_image(p2psp_logo_path,image_width)
    pix_w = pixbuf.get_width()
    pix_h = pixbuf.get_height()
    new_h = (pix_h * default_image_width) / pix_w
    scaled_pix = pixbuf.scale_simple(default_image_width, new_h, 1)
    
    return scaled_pix

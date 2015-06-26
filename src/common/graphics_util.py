
from gi.repository import Gdk
from gi.repository.GdkPixbuf import Pixbuf
from decorators import exc_handler

default_image_width = 100
@exc_handler
def get_scaled_image(path):
    pixbuf = Pixbuf.new_from_file(path)
    pix_w = pixbuf.get_width()
    pix_h = pixbuf.get_height()
    new_h = (pix_h * default_image_width) / pix_w
    scaled_pix = pixbuf.scale_simple(default_image_width, new_h, 1)
    
    return scaled_pix

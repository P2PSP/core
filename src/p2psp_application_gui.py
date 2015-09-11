"""
@package src
p2psp_application_gui module
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
    from gi.repository import GObject
    from gi.repository import Gtk
    from controller.main_window_controller import Main_Controller
    from view.main_window import Main_Window
    from model.model import Model
    from common.decorators import exc_handler
except Exception as msg:
    traceback.print_exc()

# }}}

@exc_handler
def main_app():

    """
    Before using Python threads, or libraries using threads, must apply
    GObject.threads_init().This is needed because GTK+ isn't thread safe.Only
    one thread,the main thread, is allowed to call GTK+ code at all times.
    This function isn't provided by gobject but initializes thread support
    in PyGObject (it was called gobject.threads_init() in pygtk).
    Contrary to the naming actually it is gi.threads_init().

    GObject.idle_add() takes the function and arguments that will get passed to
    the function and asks the main loop to schedule its execution in the main
    thread.

    Instantiate models and views , then pass it to the main_controller.
    """

    GObject.threads_init()
    App_Model = Model()
    App_Window = Main_Window()
    App = Main_Controller(App_Window,App_Model)
    App.show()
    Gtk.main()
    App.quit()
    print("Exiting Gtk-Main Thread")

if __name__ == "__main__":
     main_app()

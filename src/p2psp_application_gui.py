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

@exc_handler
def main_app():
    GObject.threads_init()
    App_Model = Model()
    App_Window = Main_Window()
    App = Main_Controller(App_Window,App_Model)
    App.show()
    Gtk.main()
    App.quit()
    print "Exiting Gtk-Main Thread"
    
if __name__ == "__main__":
     main_app()

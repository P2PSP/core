try:
    from gi.repository import GObject
    from gi.repository import Gtk
    from controller.main_window_controller import Main_Controller
    from view.main_window import Main_Window
    from model.model import Model
except Exception as msg:
    print(msg)

GObject.threads_init()
App_Model = Model()
App_Window = Main_Window()
App = Main_Controller(App_Window,App_Model)
App.show()
Gtk.main()
App.quit()
print "Exiting Gtk-Main Thread"

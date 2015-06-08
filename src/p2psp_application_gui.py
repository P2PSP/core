try:
    from gi.repository import GObject
    from gi.repository import Gtk
    from controller.main_window_controller import Main_Controller
    from view.main_window import Main_Window
except Exception as msg:
    print(msg)
    
GObject.threads_init()
App_Window = Main_Window()
App = Main_Controller(App_Window)
App.show()
Gtk.main()
App.quit()
print "Exiting Gtk-Main Thread"

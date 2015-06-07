try:
    from gi.repository import GObject
    from gi.repository import Gtk
    from controller.main_window_controller import Main_Controller
except Exception as msg:
    print(msg)
    
GObject.threads_init()
App = Main_Controller()
App.show()
Gtk.main()
App.quit()
print "Exiting Gtk-Main Thread"

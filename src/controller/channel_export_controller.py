from view.export_box import Export_Box
from common.json_exporter import JSON_Exporter
from model.channel_encoder import Channel_Encoder
from model.channel_store import Channel_Store
from model.channel import Channel
from common.decorators import exc_handler
from gi.repository import Gtk
import collections

class Export_Controller():
    
    def __init__(self,main_window):
        self.app_window = main_window
        self.parent_window = main_window.window
        self.box = Export_Box()
        self.box.interface.connect_signals(self.setup_signals())
        self.box.export_box.set_transient_for(self.parent_window)
        width,height = self.parent_window.get_size()
        self.box.export_box.set_size_request(width/2,height/2)
        self.show_exported_data()
        self.box.export_box.show()
        
        
    @exc_handler
    def setup_signals(self):
        signals = {
        'on_BrowseButton_clicked'                : self.save_to_file
        ,'on_ExportButton_clicked'               : self._export
        ,'on_CancelButton_clicked'               : self.cancel
                }
        return signals
        
    @exc_handler
    def show_exported_data(self):
        exported_data = Channel_Store.ALL.get_channels()
        if len(exported_data) !=0:
            for channel in exported_data:
                channel_data = collections.OrderedDict(
                                   sorted(exported_data[channel].__dict__.items()))
                
                self.box.list_store.append(channel_data.values())
    
    @exc_handler
    def add_filters(self, dialog):
        #Add json file filter
        filter_text = Gtk.FileFilter()
        filter_text.set_name("Json Files")
        filter_text.add_mime_type("application/json")
        dialog.add_filter(filter_text)
        
    @exc_handler
    def save_to_file(self,widget,data=None):
        dialog = Gtk.FileChooserDialog("Save your text file", self.box.export_box,
                                      Gtk.FileChooserAction.SAVE,
                                       (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                                        Gtk.STOCK_SAVE, Gtk.ResponseType.ACCEPT))
        dialog.set_default_size(800, 400)

        self.add_filters(dialog)

        Gtk.FileChooser.set_do_overwrite_confirmation(dialog, True) 
        response = dialog.run()
            
        if response == Gtk.ResponseType.ACCEPT:
            filename= Gtk.FileChooser.get_filename(dialog)
            self.box.text_entry.set_text(filename)
        dialog.destroy()
        
    @exc_handler
    def _export(self,widget,data=None):
        exporter  = JSON_Exporter()
        path = self.box.text_entry.get_text()
        if path != '':
            exporter.to_JSON(path
                            ,Channel_Store.ALL.get_channels()
                            ,Channel_Encoder)
        self.box.export_box.destroy()
    
    @exc_handler
    def cancel(self,widget,data=None):
        self.box.export_box.destroy()
        


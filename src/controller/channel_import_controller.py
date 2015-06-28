from view.import_box import Import_Box
from common.json_importer import JSON_Importer
from model.channel_store import Channel_Store
from model.channel import Channel
from common.decorators import exc_handler
import common.graphics_util as graphics_util
import collections
class Import_Controller():
    
    def __init__(self,main_window):
        self.app_window = main_window
        self.parent_window = main_window.window
        self.box = Import_Box()
        self.box.interface.connect_signals(self.setup_signals())
        self.box.import_box.set_transient_for(self.parent_window)
        width,height = self.parent_window.get_size()
        self.box.import_box.set_size_request(width/2,height/2)
        self.box.import_box.show()
        
        
    @exc_handler
    def setup_signals(self):
        signals = {
        'on_ImportFileChooserButton_selection_changed'   : self.on_file_selected
        ,'on_ImportButton_clicked'               : self._import
        ,'on_CancelButton_clicked'               : self.cancel
                }
        return signals
        
    @exc_handler
    def on_file_selected(self,widget,data=None):
        self.box.list_store.clear()
        _file = widget.get_filename()
        importer = JSON_Importer()
        self.imported_data = importer.from_JSON(_file)
        if self.imported_data is not None:
            for channel in self.imported_data:
                channel_data = collections.OrderedDict(
                                   sorted(self.imported_data[channel].items()))
                self.box.list_store.append(channel_data.values())
        
    @exc_handler
    def _import(self,widget,data=None):
        all_category = Channel_Store.ALL
        if self.imported_data is not None:
            for channel in self.imported_data:
                imported_channel = Channel(self.imported_data[channel])
                all_category.add(channel,imported_channel)
                (channel_name,image_url,desc) = (channel
                                ,imported_channel.get_thumbnail_url()
                                ,imported_channel.get_description())
                scaled_image = graphics_util.get_scaled_image(image_url,180)
                self.app_window.icon_list_store.append([scaled_image,channel_name,desc])
        self.box.import_box.destroy()
    
    @exc_handler
    def cancel(self,widget,data=None):
        self.box.import_box.destroy()
        


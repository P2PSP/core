
from category import Category
import common.file_util as file_util

path = file_util.find_file(__file__,
                                    '../../data/images/monitor_thumbnail.png')

def get_monitor_data():
    
   data = {"monitor":
           {"name" : "monitor"
           ,"thumbnail_url" : path
           ,"description" : "P2PSP monitor"
           ,"splitter_addr" : "127.0.0.1"
           ,"splitter_port" : "4552"
           }
          }
   return data
   
class Channel_Store():
    
    ALL = Category("all") #default category
    
    def __init__(self):
        self.categories = {}
        self._set_default(Channel_Store.ALL)
        
    def _set_default(self,category):
        self.categories[category.name] = category
        
    def get_default(self):
        return self.categories["all"]
        
    def append(self,category):
        self.categories[category.name] = category
        
        
        

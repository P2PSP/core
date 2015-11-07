"""
@package model
channel_store module 
"""
# This code is distributed under the GNU General Public License (see
# THE_GENERAL_GNU_PUBLIC_LICENSE.txt for extending this information).
# Copyright (C) 2014, the P2PSP team.
# http://www.p2psp.org

# The P2PSP.org project has been supported by the Junta de Andalucia
# through the Proyecto Motriz "Codificacion de Video Escalable y su
# Streaming sobre Internet" (P10-TIC-6548).

# {{{ Imports

from gui.model.category import Category
from gui.common import file_util

# }}}

## path to the thumbnail of the default peer.
path = file_util.find_file(__file__,
                                    '../data/images/monitor_thumbnail.png')

def get_monitor_data():
    
   """
   Returns a default monitor peer's data.
   
   @return : data
   """
 
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
    
    """
    Channels are stored in different categories. This class uses a dictionary to
    store categories. 
    """
    
    ## default category to store all the channels
    ALL = Category("all") 
    
    def __init__(self):
        
        """
        An empty dictionary of categories is created.Category name is used as 
        the key in dictionary.
        'ALL' category is set as the deafult category.
        """
        
        self.categories = {}
        self._set_default(Channel_Store.ALL)
        
    def _set_default(self,category):
        
        """
        Sets a category as default.
        
        @param : category
        """
        
        self.categories[category.name] = category
        
    def get_default(self):
        
        """
        Returns the default catgory.
        
        """
        
        return self.categories["all"]
        
    def append(self,category):
        
        """
        Append a category to the existing categories.
        
        @param : category
        """
        
        self.categories[category.name] = category
        
        
        

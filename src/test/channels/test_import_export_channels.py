#script tested with python2.7

import sys,os
module_path = os.path.join(os.path.dirname(__file__),"../..")
sys.path.append(module_path)

from gui.model.category import Category
from gui.model.channel import Channel
from gui.common.json_importer import JSON_Importer
from gui.common.json_exporter import JSON_Exporter
from gui.model.channel_encoder import Channel_Encoder
from core._print_ import _print_
import gui.common.file_util as file_util

import unittest
import json

def get_data():
    
   data = {"monitor":
           { "name" : "monitor"
           ,"thumbnail_url" : "http:/xyz.com"
           ,"description" : "monitor"
           ,"splitter_addr" : "localhost"
           ,"splitter_port" : "4552" }
           }
   return data
   
path = file_util.find_file(__file__,
                                    "../../gui/data/channels/sample_data.p2psp")

#unittests are sorted according to their name and then run.
#edit tearDown method to retain exported channels file  and vice-versa.
class Import_Export_Test(unittest.TestCase):
    
    exported_data = None
    imported_data = None
    
    def tearDown(self):
        if Import_Export_Test.imported_data is None:
            pass
        else:
            file_util.file_del(path)
            #pass
            
    def test_01_delete_channels_data(self):
    
        print("\n")
        _print_("deleting existing sample_data...")
        file_util.file_del(path)
        size = file_util.file_size(path)
        self.assertEqual(0,size)
        
        print("----------------------------------------------------------------------")
        
    def test_02_export_channels(self):
    
        Import_Export_Test.exported_data = get_data()
        
        monitor_channel = Channel(Import_Export_Test.exported_data["monitor"])
        
        test_category = Category("test")
        test_category.add("monitor",monitor_channel)
        
        Import_Export_Test.exported_data["monitor1"] = get_data()["monitor"]
        test_category.add("monitor1",monitor_channel)
        
        exporter  = JSON_Exporter()
        exporter.to_JSON(path,test_category.get_channels(),Channel_Encoder)
        print("\n")
        _print_("exporting channels to json file = " 
               + path 
               + "\n"
               +json.dumps(Import_Export_Test.exported_data
               ,indent = 4 , cls = Channel_Encoder))
        
        size = file_util.file_size(path)
        self.assertNotEqual(0,size)
        
        print("----------------------------------------------------------------------")
        
    def test_03_import_channels(self):
        importer = JSON_Importer()
        Import_Export_Test.imported_data = importer.from_JSON(path)
        print("\n")
        _print_("importing channels from json file = " 
               + path 
               + "\n"
               +json.dumps(Import_Export_Test.imported_data,indent = 4))
        
        self.assertEqual(Import_Export_Test.exported_data
                        ,Import_Export_Test.imported_data)
        
        print("----------------------------------------------------------------------")


if __name__ == "__main__":
    suite = unittest.TestLoader().loadTestsFromTestCase(Import_Export_Test)
    unittest.TextTestRunner(verbosity=2).run(suite)

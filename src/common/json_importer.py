import json
from common.decorators import exc_handler

class JSON_Importer():
    
    @exc_handler
    def from_JSON(self,path):
        json_file = open(path,"r")
        data = json.load(json_file)
        json_file.close()
        return data

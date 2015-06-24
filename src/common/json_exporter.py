import json
from common.decorators import exc_handler

class JSON_Exporter():
    
    @exc_handler
    def to_JSON(self,path,channels,encoder):
        json_file = open(path,"w")
        json.dump(channels , json_file, indent = 4 , cls = encoder)
        json_file.close()

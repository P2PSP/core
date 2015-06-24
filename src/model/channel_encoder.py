import json
from channel import Channel

class Channel_Encoder(json.JSONEncoder):
    
    def default(self,obj):
        if isinstance(obj, Channel):
            return obj.__dict__
        else:
            return json.JSONEncoder.default(self, obj)

#from collections import defaultdict
class Category():

    def __init__(self,name):
        self.name = name
        self.channels = {}

    def get_channels(self):
        return self.channels

    def set_name(self,name):
        self.name = name

    def get_name(self):
        return self.name

    def add(self,key,channel):
        self.channels[key] = channel

    def remove(self,key):
        del(self.channels[key])

    def get_channel(self,key):
        return self.channels[key]


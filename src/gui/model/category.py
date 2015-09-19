"""
@package model
category module 
"""
# This code is distributed under the GNU General Public License (see
# THE_GENERAL_GNU_PUBLIC_LICENSE.txt for extending this information).
# Copyright (C) 2014, the P2PSP team.
# http://www.p2psp.org

# The P2PSP.org project has been supported by the Junta de Andalucia
# through the Proyecto Motriz "Codificacion de Video Escalable y su
# Streaming sobre Internet" (P10-TIC-6548).

class Category():
    
    """
    Store channels in different categories.
    Data Structure used is a Dictionary.
    """
    
    def __init__(self,name):
        
        """
        Initialise with category name and a empty dictionary.
        
        @param : name 
                Category name
        """
        
        self.name = name
        self.channels = {}

    def get_channels(self):
        return self.channels

    def set_name(self,name):
        self.name = name

    def get_name(self):
        return self.name

    def add(self,key,channel):
        
        """
        Appends a new channel to the existing channels.
        
        @param : key 
                key of the channel in dictionary
        @param : channel
                Channel Object
        """
        
        self.channels[key] = channel

    def remove(self,key):
        
        """
        Removes a channel from  the existing channels.
        
        @param : key 
                key of the channel in dictionary
        """
        
        del(self.channels[key])

    def replace_key(self,prev_key,key):
        self.add(key,self.get_channel(prev_key))
        self.remove(prev_key)
        
    def get_channel(self,key):
        return self.channels[key]


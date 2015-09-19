"""
@package model
channel module 
"""
# This code is distributed under the GNU General Public License (see
# THE_GENERAL_GNU_PUBLIC_LICENSE.txt for extending this information).
# Copyright (C) 2014, the P2PSP team.
# http://www.p2psp.org

# The P2PSP.org project has been supported by the Junta de Andalucia
# through the Proyecto Motriz "Codificacion de Video Escalable y su
# Streaming sobre Internet" (P10-TIC-6548).

class Channel():
    
    """
    Stores A particular channel's data or configuration.
    """
    
    def __init__(self,data):
        
        """
        Initialise channel with given data.
        """
        
        ## Channel name
        self.name = data["name"]
        
        ## Channel details
        self.description = data["description"]
        
        ## Channel thumbnail_url
        self.thumbnail_url = data["thumbnail_url"]
        
        ## Channel Splitter Address
        self.splitter_addr = data["splitter_addr"]
        
        ## Channel Splitter Port
        self.splitter_port = data["splitter_port"]

    def set_name(self,name):
        self.name = name

    def get_name(self):
        return self.name

    def set_thumbnail_url(self,url):
        self.thumbnail_url = url

    def get_thumbnail_url(self):
        return self.thumbnail_url

    def set_description(self,description):
        self.description = description

    def get_description(self):
        return self.description

    def set_splitter_addr(self,addr):
        self.splitter_addr = addr

    def get_splitter_addr(self):
        return self.splitter_addr

    def set_splitter_port(self,port):
        self.splitter_port = port

    def get_splitter_port(self):
        return self.splitter_port

class Channel():

    def __init__(self,data):
        self.name = data["name"]
        self.description = data["description"]
        self.thumbnail_url = data["thumbnail_url"]
        self.splitter_addr = data["splitter_addr"]
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

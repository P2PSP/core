import threading

try:
    import core.peer as peer
    import core.common as common
    from core.peer_ims import  Peer_IMS
except ImportError as msg:
    print(msg)

Peer_IMS.USE_LOCALHOST = True
common.CONSOLE_MODE = False

class Peer_Thread (threading.Thread):
    def __init__(self, threadID, name):
        threading.Thread.__init__(self)
        self.peer_active = False
        self.threadID = threadID
        self.name = name
    def run(self):
        try:
            print "Starting " + self.name
            self.peer_active = True
            self.x=peer.Peer()
            print "Exiting " + self.name
        except Exception as msg:
            print(msg)

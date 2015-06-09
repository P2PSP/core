import threading

try:
    import core.peer as peer
    from core.peer_ims import  Peer_IMS
except Exception as msg:
    print(msg)

Peer_IMS.USE_LOCALHOST = True

class Peer_Thread (threading.Thread):
    def __init__(self, threadID, name):
        threading.Thread.__init__(self)
        self.peer_active = False
        self.threadID = threadID
        self.name = name
    def run(self):
        print "Starting " + self.name
        self.peer_active = True
        self.x=peer.Peer()
        print "Exiting " + self.name

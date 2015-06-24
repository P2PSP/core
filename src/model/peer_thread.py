import threading
import traceback

try:
    import core.peer as peer
    import core.common as common
    from core.peer_ims import  Peer_IMS
    from common.decorators import exc_handler
except ImportError as msg:
    traceback.print_exc()

Peer_IMS.USE_LOCALHOST = True
common.CONSOLE_MODE = False

class Peer_Thread (threading.Thread):
    def __init__(self, threadID, name):
        threading.Thread.__init__(self)
        self.peer_active = False
        self.threadID = threadID
        self.name = name

    @exc_handler
    def run(self):
        print("Starting " + self.name)
        self.peer_active = True
        self.x=peer.Peer()
        print("Exiting " + self.name)

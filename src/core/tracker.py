#!/usr/bin/env python3
import socket
import select
class tracker():
SPLITTER_LIST=[]
PEER_LIST=[]
    def __init__(self):
        self.sock=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.sock.bind(('',8000))
        self.sock.listen(5)
		
		
    def listen():
        while 1:
            read,write,error=select.select(SPLITTER_LIST[],[],[],0)
            for sock in read:
                if sock == self.sock:
                    (sockfd,addr)=self.sock.accept()                    
                    SPLITTER_LIST.append(sockfd)
                

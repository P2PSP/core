#!/usr/bin/env python3
import socket
import select
SPLITTER_LIST=[]
Resend_list=[]
TO_FIRST_SPLITTER=[]
TO_OTHER_SPLITTERS=[]
class Tracker():
    def __init__(self):
        self.sock=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.sock.bind(('',8000))
        self.sock.listen(5)
		#Tracker socket listens on port 8000
		
    def listen(self):
        while 1:
        #Efficiently wait for sockets to be read or written to.
            if len(Resend_list) != 0:
                try:
                    Resend_list[0].send("First Splitter")
                except:
                    pass
                else:
                    Resend_list.clear()
            read,write,error=select.select(SPLITTER_LIST,SPLITTER_LIST,[],0)
            for sock in read:
                if sock == self.sock:
                    (sockfd,addr)=self.sock.accept()
                    SPLITTER_LIST.append(sockfd)
                    if len(SPLITTER_LIST)==1:
                        try:
                            sockfd.send("First Splitter")
                        #The first splitter that is appended to SPLITTER_LIST  needs to know that it is the first splitter
                        except:
                            Resend_list.append(sockfd)
                            #If the message could not be sent, send again in the next iteration
                else:
                    if sock == SPLITTER_LIST[0]:
                        TO_OTHER_SPLITTERS.append(sock.recv(1024))
                    else:
                        """A header is attached to the data being sent to the underlying splitter
                        so that when we receive the response from the splitter we know who to send it to"""
                        TO_FIRST_SPLITTER.append(sock.recv(1024)+"!@#$!@#$"+str(sock.getpeername()))
                        #Not sure how to include the header. Suggestions welcome
                        
                
                
                
            
            for sock in write:
                if sock == SPLITTER_LIST[0]:
                    for items in TO_FIRST_SPLITTER:
                        try:
                            sock.send(items)
                        except:
                            pass
                        else:
                            TO_FIRST_SPLITTER.remove(items)
                
                else:
                    for items in TO_OTHER_SPLITTERS:
                        s=items.split("!@#$!@#$")
                        if s[1] == str(sock.getpeername()):
                            sock.send(s[0])
                        
                        
                        
if __name__ == "__main__":
    track=Tracker()
    track.listen()
    
                    
                        
                
                
                
                
                

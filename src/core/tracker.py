#!/usr/bin/env python3
import socket
class tracker():
	def __init__(self):
		self.sock=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
		self.sock.bind(('',8000))
		self.sock.listen(5)

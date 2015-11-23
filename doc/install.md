P2PSP usage
===========

# As user:

# Windows

1. Install (as Administrator) [Python 3](https://www.python.org/downloads).

2. Install [P2PSP](https://github.com/P2PSP/p2psp) (download ZIP file).

3. Install [VLC](http://www.videolan.org/vlc/download-windows.html)

# As contributor:

# Windows

1. Install [Git](https://git-scm.com/download/win).

2. Install (as Administrator) [Python 3](https://www.python.org/downloads).

1. Download P2PSP:

As a contributor of P2PSP:

	'''
	git clone git@github.com:P2PSP/p2psp.git
	'''

(remember that you will need to upload your public key in GitHub in order to push)

As an user of P2PSP:

	'''
	git clone https://github.com/P2PSP/p2psp.git
	'''

2. Run a splitter (optional, if you are going to watch an existing channel):

	'''
	cd p2psp/src
	python3 splitter.py --source_addr 150.214.150.60 --source_port 4551 --channel BBB-134.ogv
	'''

3. Run a peer:

	'''
	cd p2psp/src
	python3 peer.py --splitter_addr 192.168.6.109 &
	vlc http://localhost:9999 &
	'''


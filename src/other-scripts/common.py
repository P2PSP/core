# Constants common for the splitter, the peer and the gatherer, such as the block size.

class Config:

    buffer_size = 256
    block_size = 1024
    header_size = 1024*20 # This should be long enough for the video
                          # header
    channel = '134.ogg'
    source_hostname = '150.214.150.68'
    #source_hostname = 'localhost'
    source_port = 4551
    #source_port = 8000
    #splitter_hostname = '150.214.150.68'
    splitter_hostname = 'localhost'
    splitter_port = 4552
    peer_port = 9999 # Port to communicate a peer with the player

# Common configuration staff
class Config:

    buffer_size = 256
    block_size = 1024
    header_size = 1024*20 # Number of bytes of the stream's
                          # header. This should be long enough for the
                          # video header.
    #header_size = 1024*200 # Number of bytes of the stream's
                          # header. This should be long enough for the
                          # video header.
    #channel = '134.ogg'
    channel = '480.ogg'
    source_hostname = '150.214.150.68'
    #source_hostname = '127.0.0.1'
    source_port = 4551
    #source_port = 8000
    #splitter_hostname = '150.214.150.68'
    splitter_hostname = '127.0.0.1'
    splitter_port = 4552
    listening_port = 9999 # Port to communicate a peer with the player
    splitter_port = 8888
    block_format_string = "H" + str(block_size) + "s" # "H1024s
    cluster_timeout = 1 # Seconds
    peer_unreliability_threshold = 64
    trusted_hostname = splitter_hostname
    trusted_port = splitter_port + 1
    #trusted_peer_port = splitter_port + 1

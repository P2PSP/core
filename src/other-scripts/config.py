# Common configuration staff
class Config:

    # Number of bytes in a chunk
    chunk_size = 1024

    # Number of chunks in the buffer
    buffer_size = 256

    # Number of bytes of the stream header
    header_size = 1024*20 

    # Name of the channel served by the Icecast
    channel = '134.ogg'
    #channel = '480.ogg'

    # Host name where is Icecast server is running
    source_host = '150.214.150.68'
    #source_host = '127.0.0.1'

    # Port where the Icecast server is listening
    source_port = 4551
    #source_port = 8000

    # Host where the Splitter is running
    #splitter_host = '150.214.150.68'
    splitter_host = '127.0.0.1'

    # Port where the Splitter is listening
    splitter_port = 4552

    # Port where the Peer is listening to the player
    peer_listening_port = 9999 # Port to communicate a peer with the player
    splitter_listening_port = 8888
    chunk_format_string = "H" + str(chunk_size) + "s" # "H1024s
    cluster_timeout = 1 # Seconds
    peer_unreliability_threshold = 8
    peer_complaining_threshold = 8
    trusted_host = splitter_host
    trusted_port = splitter_port + 1
    #trusted_peer_port = splitter_port + 1

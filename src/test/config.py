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

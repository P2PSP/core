from monitor_fns import Monitor_FNS

# Lost chunks Recovery Set of Rules
class Monitor_LRS(Monitor_FNS):
    # {{{

    def __init__(self):
        # {{{

        Monitor_FNS.__init__(self)

        sys.stdout.write(Color.yellow)
        print ("Monitor LRS")
        sys.stdout.write(Color.none)

        # }}}

    def receive_the_buffersize(self):
        # {{{

        message = self.splitter_socket.recv(struct.calcsize("H"))
        buffer_size = struct.unpack("H", message)[0]
        self.buffer_size = socket.ntohs(buffer_size)
        print ("buffer_size =", self.buffer_size)
        # Monitor peers that implements the LRS use a smaller buffer
        # in order to complains before the rest of peers reach them in
        # their buffers.
        self.buffer_size /= 2

        # }}}

    # }}}

# This code is distributed under the GNU General Public License (see
# THE_GENERAL_GNU_PUBLIC_LICENSE.txt for extending this information).
# Copyright (C) 2015, the P2PSP team
# http://www.p2psp.org

# The P2PSP.org project has been supported by the Junta de Andalucia
# through the Proyecto Motriz "Codificacion de Video Escalable y su
# Streaming sobre Internet" (P10-TIC-6548).

# {{{ Imports
import sys
import struct
import socket
from splitter_dbs import Splitter_DBS
from color import Color
# }}}

# NTS: NAT Traversal Set of rules
class Splitter_NTS(Splitter_DBS):
    # {{{


    def __init__(self):
        Splitter_DBS.__init__(self)
        sys.stdout.write(Color.yellow)
        print("Using NTS")
        sys.stdout.write(Color.none)

    def say_goodbye(self, node, sock):
        # {{{

        sock.sendto(b'G', node)

        # }}}

    def handle_a_peer_arrival(self, connection):
        # {{{

        # {{{ In the DBS, the splitter sends to the incomming peer the
        # list of peers. Notice that the transmission of the list of
        # peers (something that could need some time if the team is
        # big or if the peer is slow) is done in a separate thread. This
        # helps to avoid DoS (Denial of Service) attacks.
        # }}}

        new_peer = connection[1]
        if __debug__:
            print("NTS: sending [send hello to %s]" % (new_peer,))
            counter = 0
        message = struct.pack("4sH", socket.inet_aton(new_peer[0]), \
                              socket.htons(new_peer[1]))
        for peer in self.peer_list:
            self.team_socket.sendto(message, peer)
            if __debug__:
                print("NTS: [%5d]" % counter, peer)
                counter += 1
        return Splitter_DBS.handle_a_peer_arrival(self, connection)

        # }}}

    def moderate_the_team(self):
        # {{{

        while self.alive:
            # {{{

            try:
                message, sender = self.receive_message()
            except:
                message = b'?'
                sender = ("0.0.0.0", 0)

            if len(message) == 2:

                # {{{ The peer complains about a lost chunk.

                # In this situation, the splitter counts the number of
                # complains. If this number exceeds a threshold, the
                # unsupportive peer is expelled from the
                # team.

                lost_chunk_number = self.get_lost_chunk_number(message)
                self.process_lost_chunk(lost_chunk_number, sender)

                # }}}

            else:
                # {{{ The peer wants to leave the team.

                try:
                    if struct.unpack("s", message)[0] == 'G': # 'G'oodbye
                        self.process_goodbye(sender)
                except Exception as e:
                    print("LRS: ", e)
                    print(message)

                # }}}

            # }}}

        # }}}

    # }}}

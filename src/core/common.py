"""
@package core
common module
"""

from core.color import Color

class Common:

    MAX_CHUNK_NUMBER = 65536
    #MAX_CHUNK_NUMBER = 2048
    #COUNTERS_TIMING = 0.1
    COUNTERS_TIMING = 1
    PEER_ID_LENGTH = 7                # Size of the IDs used in NTS
                                      # for incorporating peers
    HELLO_PACKET_TIMING = 1           # Time between continuously sent
                                      # packets
    MAX_PEER_ARRIVING_TIME = 15       # Maximum time after peer
                                      # retries incorporation
    MAX_TOTAL_INCORPORATION_TIME = 60 # Peers needing longer to
                                      # incorporate are removed from
                                      # team
    MAX_PREDICTED_PORTS = 20          # Number of probable source
                                      # ports that will be tried
    CONSOLE_MODE = True

    # IMS is enables by defining an IP multicast address
    DBS = 0b00000000                  # DBS magic number
    ACS = 0b00000001                  # ACS magic number
    LRS = 0b00000010                  # LRS magic number
    NTS = 0b00000100                  # NIS magic number
    DIS = 0b00001000                  # DIS magic number

    IMS_COLOR = Color.red
    DBS_COLOR = Color.green
    ACS_COLOR = Color.blue
    LRS_COLOR = Color.cyan
    NTS_COLOR = Color.purple
    DIS_COLOR = Color.yellow

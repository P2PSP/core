
#ifndef P2PSP_CORE_PEER_IMS_H
#define P2PSP_CORE_PEER_IMS_H

namespace p2psp {

class PeerIMS {
  // Port used to serve the player.
  static const unsigned short kPlayerPort = 9999;

  // Address of the splitter.
  constexpr static const char kSplitterAddr[] = "127.0.0.1";

  // Port of the splitter.
  static const unsigned short kSplitterPort = 4552;

  // TCP->UDP port used to communicate.
  static const unsigned short kPort = 0;

  // Use localhost instead the IP of the addapter
  static const bool kUseLocalhost = false;

  // ?
  static const int kBufferStatus = 0;

  static const bool kShowBuffer = false;

 public:
};
}

#endif  // P2PSP_CORE_PEER_IMS_H

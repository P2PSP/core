
#include "peer_ims.h"

namespace p2psp {
PeerIMS::PeerIMS() {
  // Default values
  player_port = kPlayerPort;
  splitter_addr = kSplitterAddr;
  splitter_port = kSplitterPort;
  port = kPort;
  use_localhost = kUseLocalhost;
  buffer_status = kBufferStatus;
  show_buffer = kShowBuffer;

  buffer_size_ = 0;
  chunk_size_ = 0;
  chunks_ = std::vector<char>();
  header_size_in_chunks_ = 0;
  mcast_addr_ = "0.0.0.0";
  mcast_port_ = 0;
  message_format_ = 0;
  played_chunk_ = 0;
  player_alive_ = 0;
  player_socket_ = 0;
  received_counter_ = 0;
  received_flag_ = std::vector<bool>();
  recvfrom_counter_ = 0;
  splitter_ = 0;
  splitter_socket_ = 0;
  team_socket_ = 0;
}

PeerIMS::~PeerIMS() {}
}
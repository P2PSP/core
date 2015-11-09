
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

  unsigned int buffer_size_;
  unsigned int chunk_size_;
  unsigned int chunks_;
  unsigned int header_size_in_chunks_;
  unsigned int mcast_addr_;
  unsigned int mcast_port_;
  unsigned int message_format_;
  unsigned int played_chunk_;
  unsigned int player_alive_;
  unsigned int player_socket_;
  unsigned int received_counter_;
  unsigned int received_flag_;
  unsigned int recvfrom_counter_;
  unsigned int splitter_;
  unsigned int splitter_socket_;
  unsigned int team_socket_;

 public:
  void wait_for_the_player();
  void connect_to_the_splitter();
  void disconnect_from_the_splitter();
  void receive_the_mcast_endpoint();
  void receive_the_header();
  void receive_the_chunk_size();
  void receive_the_header_size();
  void receive_the_buffer_size();
  void listen_to_the_team();
  void unpack_message();  // TODO: (message)
  void receive_the_next_message();
  void process_message();  // TODO: (message, sender)
  void process_next_message();
  void buffer_data();
  void find_next_chunk();
  void play_chunk();
  void play_next_chunk();  // TODO: (chunk)
  void play();
  void keep_the_buffer_full();
  void run();
};
}

#endif  // P2PSP_CORE_PEER_IMS_H

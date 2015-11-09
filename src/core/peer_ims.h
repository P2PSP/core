
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
  PeerIMS();
  ~PeerIMS();

  /**
   *  Setup "player_socket" and wait for the player
   */
  void WaitForThePlayer();

  /**
   *  Setup "splitter" and "splitter_socket"
   */
  void ConnectToTheSplitter();
  void DisconnectFromTheSplitter();
  void ReceiveTheMcasteEndpoint();
  void ReceiveTheHeader();
  void ReceiveTheChunkSize();
  void ReceiveTheHeaderSize();
  void ReceiveTheBufferSize();

  /**
   *  Create "team_socket" (UDP) for using the multicast channel
   */
  void ListenToTheTeam();
  void UnpackMessage();  // TODO: (message)
  void ReceiveTheNextMessage();
  void ProcessMessage();  // TODO: (message, sender)
  void ProcessNextMessage();

  /**
   *  Buffering
   */
  void BufferData();
  void FindNextChunk();
  void PlayChunk();
  void PlayNextChunk();  // TODO: (chunk)
  void Play();
  void KeepTheBufferFull();
  void Run();
};
}

#endif  // P2PSP_CORE_PEER_IMS_H

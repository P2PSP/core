
#ifndef P2PSP_CORE_PEER_IMS_H
#define P2PSP_CORE_PEER_IMS_H

#include <vector>
#include <string>
#include <tuple>
#include <boost/asio.hpp>
#include <boost/array.hpp>
#include <boost/date_time/posix_time/posix_time.hpp>
#include <boost/thread/thread.hpp>
#include <arpa/inet.h>
#include "../util/trace.h"

namespace p2psp {

class PeerIMS {
  // Default port used to serve the player.
  static const unsigned short kPlayerPort = 9999;

  // Default address of the splitter.
  static constexpr char kSplitterAddr[] = "127.0.0.1";

  // Default port of the splitter.
  static const unsigned short kSplitterPort = 4552;

  // Default TCP->UDP port used to communicate.
  static const unsigned short kPort = 0;

  // Default use localhost instead the IP of the addapter
  static const bool kUseLocalhost = false;

  // Default ?
  static const int kBufferStatus = 0;

  // Default
  static const bool kShowBuffer = false;

  // Port used to serve the player.
  unsigned short player_port_;

  // Address of the splitter.
  boost::asio::ip::address splitter_addr_;

  // Port of the splitter.
  unsigned short splitter_port_;

  // TCP->UDP port used to communicate.
  unsigned short port_;

  // Use localhost instead the IP of the addapter
  bool use_localhost_;

  // ?
  int buffer_status_;

  bool show_buffer_;

  unsigned int buffer_size_;
  unsigned int chunk_size_;
  std::vector<char> chunks_;
  unsigned int header_size_in_chunks_;
  boost::asio::ip::address mcast_addr_;
  unsigned short mcast_port_;

  std::shared_ptr<char> played_chunk_;  // Dynamic pointer
  bool player_alive_;

  unsigned int received_counter_;
  std::vector<bool> received_flag_;
  unsigned int recvfrom_counter_;

  // Service for I/O operations
  boost::asio::io_service io_service_;

  // Used to listen to the player
  boost::asio::ip::tcp::socket player_socket_;

  // Used to listen to the splitter
  boost::asio::ip::tcp::socket splitter_socket_;

  // Used to communicate with the rest of the team
  boost::asio::ip::udp::socket team_socket_;

  // Acceptor used to listen to incoming connections.
  boost::asio::ip::tcp::acceptor acceptor_;

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

  /**
   *  Getter/setters
   */
  std::string GetMcastAddr();
  void SetShowBuffer(bool);
};
}

#endif  // P2PSP_CORE_PEER_IMS_H

//
// This code is distributed under the GNU General Public License (see
// THE_GENERAL_GNU_PUBLIC_LICENSE.txt for extending this information).
// Copyright (C) 2014, the P2PSP team.
// http://www.p2psp.org
//
// IMS: Ip Multicasting Set of rules

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
#include <ctime>
#include "../util/trace.h"
#include "common.h"

using namespace boost::asio;

namespace p2psp {

struct Chunk {
  std::vector<char> data;
  bool received;
};

class PeerIMS {
 protected:
  // Default port used to serve the player.
  static const uint16_t kPlayerPort = 9999;

  // Default address of the splitter.
  static constexpr char kSplitterAddr[] = "127.0.0.1";

  // Default port of the splitter.
  static const uint16_t kSplitterPort = 4552;

  // Default TCP->UDP port used to communicate.
  static const uint16_t kPort = 0;

  // Default use localhost instead the IP of the addapter
  static const bool kUseLocalhost = false;

  // Default ?
  static const int kBufferStatus = 0;

  // Default
  static const bool kShowBuffer = false;

  // Port used to serve the player.
  uint16_t player_port_;

  // Address of the splitter.
  ip::address splitter_addr_;

  // Port of the splitter.
  uint16_t splitter_port_;

  // TCP->UDP port used to communicate.
  uint16_t port_;

  // Use localhost instead the IP of the addapter
  bool use_localhost_;

  // ?
  int buffer_status_;

  // Initialized to -1 in clases that don't use it
  int sendto_counter_;

  bool show_buffer_;

  int buffer_size_;
  int chunk_size_;
  std::vector<Chunk> chunks_;
  int header_size_in_chunks_;
  ip::address mcast_addr_;
  uint16_t mcast_port_;

  int played_chunk_;
  bool player_alive_;

  int received_counter_;
  std::vector<bool> received_flag_;
  int recvfrom_counter_;

  ip::udp::endpoint splitter_;

  // Service for I/O operations
  io_service io_service_;

  // Used to listen to the player
  ip::tcp::socket player_socket_;

  // Used to listen to the splitter
  ip::tcp::socket splitter_socket_;

  // Used to communicate with the rest of the team
  ip::udp::socket team_socket_;

  // Acceptor used to listen to incoming connections.
  ip::tcp::acceptor acceptor_;

  // Thread to start the peer
  std::unique_ptr<boost::thread> thread_;

  // DBS variables
  std::vector<ip::udp::endpoint> peer_list_;

 public:
  PeerIMS();
  ~PeerIMS();

  /**
   *  This function must be called after constructing a new object.
   */
  virtual void Init();

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
  void ReceiveTheNextMessage(std::vector<char>*, ip::udp::endpoint);
  int ProcessMessage(std::vector<char>, ip::udp::endpoint);
  int ProcessNextMessage();

  /**
   *  Buffering
   */
  void BufferData();
  int FindNextChunk();
  void PlayChunk(int);
  void PlayNextChunk();  // TODO: (chunk)
  void Play();
  void KeepTheBufferFull();
  void Run();
  void Start();

  /**
   *  Getter/setters
   */
  std::string GetMcastAddr();
  bool IsPlayerAlive();
  int GetPlayedChunk();
  int GetChunkSize();
  int GetSendtoCounter();
  std::vector<ip::udp::endpoint>* GetPeerList();
  int GetRecvfromCounter();
  void SetShowBuffer(bool);
  void SetSendtoCounter(int);
};
}

#endif  // P2PSP_CORE_PEER_IMS_H

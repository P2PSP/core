//
//  splitter_ims.h
//  P2PSP
//
//  This code is distributed under the GNU General Public License (see
//  THE_GENERAL_GNU_PUBLIC_LICENSE.txt for extending this information).
//  Copyright (C) 2014, the P2PSP team.
//  http://www.p2psp.org
//
//  IMS: IP Multicast Set of rules.
//

#ifndef P2PSP_CORE_SPLITTER_IMS_H_
#define P2PSP_CORE_SPLITTER_IMS_H_

#include <stdio.h>
#include <string>
#include <tuple>
#include <sstream>
#include <boost/asio.hpp>

namespace p2psp {

class SplitterIMS {
 private:
  const int kBufferSize;          // Buffer size in chunks
  const std::string kChannel;     // Default channel
  const int kChunkSize;           // Chunk size in bytes (larger than MTU)
  const int kHeaderSize;          // Chunks/header
  const int kPort;                // Listening port
  const std::string kSourceAddr;  // Streaming server's host
  const int kSourcePort;          // Streaming server's listening port
  const std::string kMCastAddr;   // All Systems on this subnet
  const int kTTL;                 // Time To Live of multicast packets

  /*
   An IMS splitter runs 2 threads. The main one serves the
   chunks to the team. The other controls peer arrivals. This
   variable is true while the player is receiving data.
   */
  bool alive_;

  // Number of the served chunk.
  int chunk_number_;

  // Service for I/O operations
  boost::asio::io_service io_service_;

  // Used to listen to the incomming peers.
  boost::asio::ip::tcp::socket peer_connection_socket_;

  // Acceptor used to listen for incoming connections.
  boost::asio::ip::tcp::acceptor acceptor_;

  // Used to listen the team messages.
  int team_socket_;  // TODO: Socket descriptor?

  // Used to talk to the source
  int source_socket_;  // TODO: Socket descriptor?

  // Some other useful definitions.
  std::tuple<std::string, int> source_;
  std::string GET_message_;
  std::string chunk_number_format_;
  std::tuple<std::string, int> mcast_channel_;

  int recvfrom_counter_;
  int sendto_counter_;
  int header_load_counter_;

 public:
  SplitterIMS();
  ~SplitterIMS();
  void SendTheHeader(int peer_serve_socket);
  void SendTheBufferSize(int peer_serve_socket);
  void SendTheChunkSize(int peer_serve_socket);
  void SendTheMcastChannel(int peer_serve_socket);
  void SendTheHeaderSize(int peer_serve_socket);
  void SendConfiguration(int sock);
  void HandleAPeerArrival(std::tuple<int, std::string> connection);
  void HandleArrivals();
  void SetupPeerConnectionSocket();
  void SetupTeamSocket();
  void RequestTheVideoFromTheSource();
  void ConfigureSockets();
  void LoadTheVideoHeader();
  void ReceiveNextChunk();  // TODO: Return chunk
  void ReceiveChunk();      // TODO: Return chunk
  void SendChunk(std::string message, std::string destination);
  void ReceiveTheHeader();

  // TODO: run method and Thread management
};
}

#endif  // defined P2PSP_CORE_SPLITTER_IMS_H_
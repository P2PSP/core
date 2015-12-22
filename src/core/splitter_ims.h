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
#include <boost/array.hpp>
#include <boost/thread/thread.hpp>
#include <iostream>
#include "../util/trace.h"
#include <arpa/inet.h>
#include "common.h"

namespace p2psp {

class SplitterIMS {
 protected:
  const int kBufferSize = 256;                 // Buffer size in chunks
  const std::string kChannel = "BBB-134.ogv";  // Default channel
  const int kChunkSize = 1024;        // Chunk size in bytes (larger than MTU)
  const int kHeaderSize = 10;         // Chunks/header
  const unsigned short kPort = 4552;  // Listening port
  const std::string kSourceAddr = "150.214.150.68";  // Streaming server's host
  const int kSourcePort = 4551;  // Streaming server's listening port
  const std::string kMCastAddr = "224.0.0.1";  // All Systems on this subnet
  const int kTTL = 1;  // Time To Live of multicast packets

  int buffer_size_;
  std::string channel_;
  int chunk_size_;
  int header_size_;
  unsigned short port_;
  std::string source_addr_;
  unsigned short source_port_;
  std::string mcast_addr_;
  int ttl_;

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
  boost::asio::ip::udp::socket team_socket_;

  // Used to talk to the source
  boost::asio::ip::tcp::socket source_socket_;

  // The video header
  boost::asio::streambuf header_;

  // Some other useful definitions.
  std::tuple<std::string, int> source_;
  std::string GET_message_;
  std::string chunk_number_format_;
  boost::asio::ip::udp::endpoint mcast_channel_;

  int recvfrom_counter_;
  int sendto_counter_;
  int header_load_counter_;

  // Thread to start the Splitter
  std::unique_ptr<boost::thread> thread_;

  // Thread management
  virtual void Run();

 public:
  SplitterIMS();
  ~SplitterIMS();
  void SendTheHeader(
      std::shared_ptr<boost::asio::ip::tcp::socket> &peer_serve_socket);
  void SendTheBufferSize(
      std::shared_ptr<boost::asio::ip::tcp::socket> &peer_serve_socket);
  void SendTheChunkSize(
      std::shared_ptr<boost::asio::ip::tcp::socket> &peer_serve_socket);
  void SendTheMcastChannel(
      std::shared_ptr<boost::asio::ip::tcp::socket> &peer_serve_socket);
  void SendTheHeaderSize(
      std::shared_ptr<boost::asio::ip::tcp::socket> &peer_serve_socket);
  virtual void SendConfiguration(
      std::shared_ptr<boost::asio::ip::tcp::socket> &sock);
  virtual void HandleAPeerArrival(
      std::shared_ptr<boost::asio::ip::tcp::socket> serve_socket);
  void HandleArrivals();
  void SetupPeerConnectionSocket();
  virtual void SetupTeamSocket();
  void RequestTheVideoFromTheSource();
  void ConfigureSockets();
  void LoadTheVideoHeader();
  size_t ReceiveNextChunk(boost::asio::streambuf &chunk);
  size_t ReceiveChunk(boost::asio::streambuf &chunk);
  virtual void SendChunk(std::vector<char> &message,
                         boost::asio::ip::udp::endpoint destination);
  void ReceiveTheHeader();

  // Thread management
  virtual void Start();

  // Getters
  bool isAlive();
  int GetRecvFromCounter();
  int GetSendToCounter();
  int GetChunkSize();

  // Setters
  void SetAlive(bool alive);
  void SetBufferSize(int buffer_size);
  void SetChannel(std::string channel);
  void SetChunkSize(int chunk_size);
  void SetHeaderSize(int header_size);
  void SetPort(int port);
  void SetSourceAddr(std::string source_addr);
  void SetSourcePort(int source_port);
};
}

#endif  // defined P2PSP_CORE_SPLITTER_IMS_H_
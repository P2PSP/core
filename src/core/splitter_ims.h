//
//  splitter_ims.h
//  P2PSP
//
//  This code is distributed under the GNU General Public License (see
//  THE_GENERAL_GNU_PUBLIC_LICENSE.txt for extending this information).
//  Copyright (C) 2016, the P2PSP team.
//  http://www.p2psp.org
//
//  IMS: IP Multicast Set of rules.
//

#ifndef P2PSP_CORE_SPLITTER_IMS_H_
#define P2PSP_CORE_SPLITTER_IMS_H_

#include <arpa/inet.h>
#include <stdio.h>
#include <boost/array.hpp>
#include <boost/asio.hpp>
#include <boost/thread/thread.hpp>
#include <iostream>
#include <sstream>
#include <string>
#include <tuple>
//#include "../util/trace.h"
#include "common.h"

namespace p2psp {

  class SplitterIMS {

  public:

    SplitterIMS();
    ~SplitterIMS();

    void SendTheHeader(const std::shared_ptr<boost::asio::ip::tcp::socket> &peer_serve_socket);
    void SendTheBufferSize(const std::shared_ptr<boost::asio::ip::tcp::socket> &peer_serve_socket);
    void SendTheChunkSize(const std::shared_ptr<boost::asio::ip::tcp::socket> &peer_serve_socket);
    void SendTheMcastChannel(const std::shared_ptr<boost::asio::ip::tcp::socket> &peer_serve_socket);
    void SendTheHeaderSize(const std::shared_ptr<boost::asio::ip::tcp::socket> &peer_serve_socket);
    virtual void SendConfiguration(const std::shared_ptr<boost::asio::ip::tcp::socket> &sock);
    virtual void HandleAPeerArrival(std::shared_ptr<boost::asio::ip::tcp::socket> serve_socket);
    void HandleArrivals();
    void SetupPeerConnectionSocket();
    virtual void SetupTeamSocket();
    void RequestTheVideoFromTheSource();
    void ConfigureSockets();
    void LoadTheVideoHeader();
    size_t ReceiveNextChunk(boost::asio::streambuf &chunk);
    virtual size_t ReceiveChunk(boost::asio::streambuf &chunk);
    virtual void SendChunk(const std::vector<char> &message, const boost::asio::ip::udp::endpoint &destination);
    void ReceiveTheHeader();

    // TODO: SendChunk can be used instead if the increment of sendto_counter
    // doesn't matter
    void SayGoodbye();

    // Thread management
    virtual void Start();

    // Getters
    bool isAlive();
    int GetRecvFromCounter();
    int GetSendToCounter();
    int GetChunkSize();
    int GetTeamPort(); // GetPort()
    int GetBufferSize();
    std::string GetChannel();
    int GetHeaderSize();
    std::string GetMcastAddr();
    std::string GetSourceAddr();
    int GetSourcePort();
    int GetTTL();

    // Setters
    void SetAlive(bool alive);
    void SetBufferSize(int buffer_size);
    void SetChannel(std::string channel);
    void SetChunkSize(int chunk_size);
    void SetHeaderSize(int header_size);
    void SetTeamPort(int team_port);
    void SetSourceAddr(std::string source_addr);
    void SetSourcePort(int source_port);
    void SetGETMessage(std::string channel);

    // Default getters
    static int GetDefaultChunkSize();
    static int GetDefaultTeamPort(); // GetDefaultPort()
    static int GetDefaultBufferSize();
    static std::string GetDefaultChannel();
    static int GetDefaultHeaderSize();
    static std::string GetDefaultMcastAddr();
    static std::string GetDefaultSourceAddr();
    static int GetDefaultSourcePort();
    static int GetDefaultTTL();

  protected:
    static const int kBufferSize;          // Buffer size in chunks
    static const std::string kChannel;     // Default channel
    static const int kChunkSize;           // Chunk size in bytes (larger than MTU)
    static const int kHeaderSize;          // Chunks/header
    static const unsigned short kPort;     // Listening port
    static const std::string kSourceAddr;  // Streaming server's host
    static const int kSourcePort;          // Streaming server's listening port
    static const std::string kMCastAddr;   // All Systems on this subnet
    static const int kTTL;                 // Time To Live of multicast packets

    int buffer_size_;
    std::string channel_;
    int chunk_size_;
    int header_size_;
    unsigned short team_port_;
    std::string source_addr_;
    unsigned short source_port_;
    std::string mcast_addr_;
    int ttl_;

    /*
      An IMS splitter runs 2 threads. The main one serves the chunks to
      the team. The other controls peer arrivals. This variable is true
      while the consumer is receiving data.
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

  };
}

#endif  // defined P2PSP_CORE_SPLITTER_IMS_H_

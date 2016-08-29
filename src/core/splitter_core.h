//
//  splitter_core.h -- Core
//
//  This code is distributed under the GNU General Public License (see
//  THE_GENERAL_GNU_PUBLIC_LICENSE.txt for extending this information).
//  Copyright (C) 2016, the P2PSP team.
//  http://www.p2psp.org
//

#ifndef P2PSP_CORE_SPLITTER_CORE_H_
#define P2PSP_CORE_SPLITTER_CORE_H_

#include <arpa/inet.h>
#include <stdio.h>
#include <boost/array.hpp>
#include <boost/asio.hpp>
#include <boost/asio/buffer.hpp>
#include <boost/thread/thread.hpp>
#include <iostream>
#include <sstream>
#include <string>
#include <tuple>
//include <vector>
#include "../util/trace.h"
#include "common.h"

namespace p2psp {

  class Splitter_core {

  public:

    Splitter_core();
    ~Splitter_core();

    void Init();
    void SendBufferSize(const std::shared_ptr<boost::asio::ip::tcp::socket> &peer_serve_socket);
    void SendChunkSize(const std::shared_ptr<boost::asio::ip::tcp::socket> &peer_serve_socket);
    void SendChannel(const std::shared_ptr<boost::asio::ip::tcp::socket> &peer_serve_socket);
    void SendSourceEndpoint(const std::shared_ptr<boost::asio::ip::tcp::socket> &peer_serve_socket);
    void SendHeaderSize(const std::shared_ptr<boost::asio::ip::tcp::socket> &peer_serve_socket);
    virtual void SendConfiguration(const std::shared_ptr<boost::asio::ip::tcp::socket> &sock);
    virtual void HandleAPeerArrival(std::shared_ptr<boost::asio::ip::tcp::socket> serve_socket);
    void HandleArrivals();
    void SetupPeerConnectionSocket();
    virtual void SetupTeamSocket();
    void RequestTheVideoFromTheSource();
    void ConfigureSockets();
    size_t ReceiveNextChunk(boost::asio::streambuf &chunk); // Ojo con ReceiveChunk
    virtual size_t ReceiveChunk(boost::asio::streambuf &chunk);
    virtual void SendChunk(const std::vector<char> &message, const boost::asio::ip::udp::endpoint &destination);

    // TODO: SendChunk can be used instead if the increment of sendto_counter
    // doesn't matter

    // Thread management
    virtual void Start();

    // Getters
    bool isAlive();
    int GetRecvFromCounter();
    int GetChunkSize();
    int GetSplitterPort();
    int GetBufferSize();
    std::string GetChannel();
    std::string GetSourceAddr();
    int GetSourcePort();
    int GetSendToCounter();
    
    // Setters
    void SetAlive(bool alive);
    void SetBufferSize(int buffer_size);
    void SetChannel(std::string channel);
    void SetChunkSize(int chunk_size);
    void SetSplitterPort(int splitter_port);
    void SetSourceAddr(std::string source_addr);
    void SetSourcePort(int source_port);
    void SetGETMessage(std::string channel);

    // Default getters
    static int GetDefaultChunkSize();
    static int GetDefaultSplitterPort();
    static int GetDefaultBufferSize();
    static std::string GetDefaultChannel();
    static std::string GetDefaultSourceAddr();
    static int GetDefaultSourcePort();

    static HEADER_SIZE_TYPE GetDefaultHeaderSize();
    void SetHeaderSize(HEADER_SIZE_TYPE header_size);
    HEADER_SIZE_TYPE GetHeaderSize();
    
  protected:
    static const int kBufferSize;          // Buffer size in chunks
    static const std::string kChannel;     // Default channel
    static const int kChunkSize;           // Chunk size in bytes (larger than MTU)
    static const unsigned short kSplitterPort;     // Listening port
    static const std::string kSourceAddr;  // Streaming server's host
    static const int kSourcePort;          // Streaming server's listening port
    static const int kHeaderSize;        // Bytes/header

    int buffer_size_;
    std::string channel_;
    int chunk_size_;
    unsigned short splitter_port_;
    std::string source_addr_;
    unsigned short source_port_;
    int header_size_;
    
    /*
      An splitter runs 2 threads. The main one serves the chunks to
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

    // Some other useful definitions.
    std::tuple<std::string, int> source_;
    std::string GET_message_;
    std::string chunk_number_format_;

    int recvfrom_counter_;
    int sendto_counter_;

    // Thread to start the Splitter
    std::unique_ptr<boost::thread> thread_;

    // Thread management
    virtual void Run();

    void ReceiveReadyForReceivingChunks(const std::shared_ptr<boost::asio::ip::tcp::socket> &sock);

  };
}

#endif  // defined P2PSP_CORE_SPLITTER_CORE_H_

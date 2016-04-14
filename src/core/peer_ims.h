//
//  peer_ims.h
//  P2PSP
//
//  This code is distributed under the GNU General Public License (see
//  THE_GENERAL_GNU_PUBLIC_LICENSE.txt for extending this information).
//  Copyright (C) 2016, the P2PSP team.
//  http://www.p2psp.org
//
//  IMS: Ip Multicasting Set of rules
//

#ifndef P2PSP_CORE_PEER_IMS_H
#define P2PSP_CORE_PEER_IMS_H

#include <arpa/inet.h>
#include <boost/array.hpp>
#include <boost/asio.hpp>
#include <boost/date_time/posix_time/posix_time.hpp>
#include <boost/thread/thread.hpp>
#include <ctime>
#include <string>
#include <tuple>
#include <vector>
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

    // Default port used to serve the consumer.
    static const uint16_t kConsumerPort = 9999;

    // Default address of the splitter.
    static constexpr char kSplitterAddr[] = "127.0.0.1";

    // Default port of the splitter.
    static const uint16_t kSplitterPort = 4552;

    // Default TCP->UDP port used to communicate.
    static const uint16_t kTeamPort = 0;

    // Default use localhost instead the IP of the addapter
    static const bool kUseLocalhost = false;

    // Default ?
    static const int kBufferStatus = 0;

    // Default
    static const bool kShowBuffer = false;

    static const int kChunkIndexSize = 2;
  
    // Port used to serve the consumer.
    uint16_t consumer_port_;

    // Address of the splitter.
    ip::address splitter_addr_;

    // Port of the splitter.
    uint16_t splitter_port_;

    // TCP->UDP port used to communicate.
    uint16_t team_port_;

    // Use localhost instead the IP of the addapter
    bool use_localhost_;

    // ?
    int buffer_status_;

    // Initialized to -1 in clases that don't use it
    int sendto_counter_;

    bool show_buffer_;

    int buffer_size_;
    unsigned int message_size_;
  
    int chunk_size_;
    std::vector<Chunk> chunks_;
    int header_size_in_chunks_;
    ip::address mcast_addr_;
    uint16_t mcast_port_;

    int consumed_chunk_;
    bool consumer_alive_;

    int received_counter_;
    std::vector<bool> received_flag_;
    int recvfrom_counter_;

    ip::udp::endpoint splitter_;

    // Service for I/O operations
    io_service io_service_;

    // Acceptor used to listen to incoming connections.
    ip::tcp::acceptor acceptor_;

    // Used to listen to the consumer
    ip::tcp::socket consumer_socket_;

    // Used to listen to the splitter
    ip::tcp::socket splitter_socket_;

    // Used to communicate with the rest of the team
    ip::udp::socket team_socket_;

    // Thread group to join all threads
    boost::thread_group thread_group_;

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
     *  Setup "consumer_socket" and wait for the consumer
     */
    virtual void WaitForTheConsumer();

    /**
     *  Setup "splitter" and "splitter_socket"
     */
    virtual void ConnectToTheSplitter() throw(boost::system::system_error);
    virtual void DisconnectFromTheSplitter();
    virtual void ReceiveTheMcasteEndpoint();
    virtual void ReceiveTheHeader();
    virtual void ReceiveTheChunkSize();
    virtual void ReceiveTheHeaderSize();
    virtual void ReceiveTheBufferSize();

    /**
     *  Create "team_socket" (UDP) for using the multicast channel
     */
    virtual void ListenToTheTeam();
    virtual void ReceiveTheNextMessage(std::vector<char>&, ip::udp::endpoint&);
    virtual int ProcessMessage(const std::vector<char>&,
			       const ip::udp::endpoint&);
    virtual int ProcessNextMessage();

    /**
     *  Buffering
     */
    virtual void BufferData();
    virtual int FindNextChunk();
    virtual void ConsumeChunk(int);
    virtual void ConsumeNextChunk();
    virtual void KeepTheBufferFull();

    /**
     *  Thread management
     */
    virtual void Run();
    virtual void Start();

    /**
     *  Getter/setters
     */
    virtual std::string GetMcastAddr();
    virtual bool IsConsumerAlive();
    virtual int GetConsumedChunk();
    virtual int GetChunkSize();
    virtual int GetSendtoCounter();
    virtual std::vector<ip::udp::endpoint>* GetPeerList();
    virtual int GetRecvfromCounter();
    virtual void SetShowBuffer(bool);
    virtual void SetSendtoCounter(int);
    virtual void SetConsumerPort(uint16_t);
    virtual void SetSplitterAddr(std::string);
    virtual void SetSplitterPort(uint16_t);
    virtual void SetTeamPort(uint16_t);
    virtual void SetUseLocalhost(bool);
  };
}

#endif  // P2PSP_CORE_PEER_IMS_H

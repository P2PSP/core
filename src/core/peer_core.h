//
//  peer_core.h - Peer core.
//
//  This code is distributed under the GNU General Public License (see
//  THE_GENERAL_GNU_PUBLIC_LICENSE.txt for extending this information).
//
//  Copyright (C) 2016, the P2PSP team.
//  http://www.p2psp.org
//
//

#ifndef P2PSP_CORE_PEER_CORE_H
#define P2PSP_CORE_PEER_CORE_H

#include <arpa/inet.h>
#include <boost/array.hpp>
#include <boost/asio.hpp>
#include <boost/date_time/posix_time/posix_time.hpp>
#include <boost/thread/thread.hpp>
#include <ctime>
#include <fstream>
#include <string>
#include <tuple>
#include <vector>
#include "../util/trace.h"
#include "common.h"

using namespace boost::asio;

namespace p2psp {

  struct Chunk {
    std::vector<char> data;
    int received;
  };

  class Peer_core {

  protected:

    static constexpr char kSplitterAddr[] = "127.0.0.1";
    static const uint16_t kSplitterPort = 8001;
    static const uint16_t kTeamPort = 0;
    static const bool kUseLocalhost = false; // Default use localhost instead the IP of the addapter
    static const int kChunkIndexSize = 2;

    ip::address splitter_addr_;
    uint16_t splitter_port_;
    uint16_t team_port_;
    bool use_localhost_;
    int buffer_status_;
    int sendto_counter_; // Initialized to -1 in clases that don't use it
    int buffer_size_;
    unsigned int message_size_;
    int chunk_size_;
    std::vector<Chunk> chunks_;
    int played_chunk_;
    bool player_alive_;
    int received_counter_;
    std::vector<bool> received_flag_;
    int recvfrom_counter_;
    ip::udp::endpoint splitter_;
    io_service io_service_;
    ip::tcp::socket splitter_socket_;
    ip::udp::socket team_socket_;
    boost::thread_group thread_group_;
    int previous_chunk_number_ = 0;
    int latest_chunk_number_ = 0;
    bool kLogging = false;
    std::string kLogFile;
    bool logging_;
    std::ofstream log_file_;
    ip::udp::endpoint me_;
    //char magic_flags_;
    ip::address source_addr_;
    uint16_t source_port_;
    //int header_length_;
    //boost::array<char, 80> channel_;
    Chunk *chunk_ptr;

  public:

    Peer_core();
    ~Peer_core();

    virtual void Init();

    virtual void        SetSplitterAddr(ip::address splitter_addr);
    virtual ip::address GetSplitterAddr();
    static  ip::address GetDefaultSplitterAddr();
    virtual void        SetSplitterPort(uint16_t);
    static  uint16_t    GetDefaultSplitterPort();
    virtual uint16_t    GetSplitterPort();
    virtual void        ConnectToTheSplitter() throw(boost::system::system_error);
    virtual void        DisconnectFromTheSplitter(void);
    std::string GetSourceAddr();
    uint16_t GetSourcePort();
    static uint16_t GetDefaultTeamPort();
    virtual void    SetTeamPort(uint16_t);
    //virtual uint16_t GetTeamPort();

    //virtual void ReceiveHeaderLength(void);
    /*virtual void ReceiveHeader(void);
    virtual int  GetHeaderSize();*/

    //void ReceiveChannel();
    virtual void ReceiveChunkSize(void);
    virtual int GetChunkSize();

    virtual void ReceiveBufferSize(void);
    virtual int  GetBufferSize();

    virtual void ReceiveNextMessage(std::vector<char>& message, ip::udp::endpoint& sender);

    /*virtual void ReceiveMagicFlags(void);
      virtual char GetMagicFlags();*/

    virtual int  ProcessNextMessage();
    virtual int  ProcessMessage(const std::vector<char>&,
			       const ip::udp::endpoint&);
    virtual void BufferData();
    virtual void KeepTheBufferFull();
    virtual void PlayNextChunk(int chunk_number); // Ojo, possible overlaping with PlayChunk()
    virtual bool PlayChunk(/*std::vector<char> chunk*/int chunk_number); // Ojo, possible overlaping with PlayNextChunk()
    virtual int  GetPlayedChunk();

    virtual void Run();
    virtual void Start();

    virtual void LogMessage(const std::string&);
    virtual std::string BuildLogMessage(const std::string&);

    virtual int  GetRecvfromCounter();
    virtual void SetSendtoCounter(int);
    virtual int  GetSendtoCounter();

    virtual bool IsPlayerAlive(); // Ojo, defined in Player class?
    
    virtual void SetUseLocalHost(bool);
    bool GetUseLocalHost();
    //virtual int GetNumberOfPeers();// { return 0; }
    //void  ReceiveSourceEndpoint();
    // bool AmIAMonitor() { return false; }
    //void ReceiveTheListOfPeers() {}
    
    //static uint16_t GetDefaultPlayerPort();
    virtual void Complain(unsigned short);

    unsigned int GetRealSplitterPort() {
      return splitter_socket_.local_endpoint().port();
    }
    
  };
}

#endif  // P2PSP_CORE_PEER_CORE_H

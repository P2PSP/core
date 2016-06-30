//
//  peer_ims.h -- P2PSP's IP multicast transmission
//
//  This code is distributed under the GNU General Public License (see
//  THE_GENERAL_GNU_PUBLIC_LICENSE.txt for extending this information).
//
//  Copyright (C) 2016, the P2PSP team.
//  http://www.p2psp.org
//
//  IMS: Ip Multicasting Set of rules
//

#ifndef P2PSP_CORE_PEER_IMS_H
#define P2PSP_CORE_PEER_IMS_H

#include "peer_core.h"

namespace p2psp {

  class Peer_IMS {

  protected:

    bool show_buffer_; // Quitar
    int buffer_size_;
    unsigned int message_size_;
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
    io_service io_service_;                               // Service for I/O operations
    ip::tcp::acceptor acceptor_;                          // Acceptor used to listen to incoming connections.
    ip::tcp::socket player_socket_;                       // Used to listen to the player
    ip::tcp::socket splitter_socket_;                     // Used to listen to the splitter
    ip::udp::socket team_socket_;                         // Used to communicate with the rest of the team
    boost::thread_group thread_group_;                    // Thread group to join all threads
    std::vector<ip::udp::endpoint> peer_list_;            // DBS variables
    int previous_chunk_number_=0;
    int latest_chunk_number_ = 0;
    bool kLogging = false;
    std::string kLogFile;
    bool logging_;
    std::ofstream log_file_;
    ip::udp::endpoint me_;
    int number_of_peers_;

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
    virtual void WaitForThePlayer();

    /**
     *  Setup "splitter" and "splitter_socket"
     */
    virtual void ConnectToTheSplitter() throw(boost::system::system_error);
    virtual void DisconnectFromTheSplitter();
    virtual void ReceiveTheMcastChannel();
    virtual void ReceiveTheHeader();
    virtual void ReceiveTheChunkSize();
    virtual void ReceiveTheHeaderSize();
    virtual void ReceiveTheBufferSize();
    void ReceiveMagicFlags();
    virtual void ReceiveMyEndpoint();
    //virtual void ReceiveTheNumberOfPeers();

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
    virtual void PlayChunk(int);
    virtual void PlayNextChunk(int chunk_number);
    virtual void KeepTheBufferFull();

    /**
     *  Thread management
     */
    virtual void Run();
    virtual void Start();

    /**
     * Log Messages
     */
    virtual void LogMessage(const std::string&);
    virtual std::string BuildLogMessage(const std::string&);

    /**
     *  Getters/setters
     */
    virtual char GetMagicFlags();
    //virtual std::string GetMcastAddr();
    virtual ip::address GetMcastAddr();
    virtual bool IsPlayerAlive();
    virtual int GetPlayedChunk();
    virtual int GetChunkSize();
    virtual std::vector<ip::udp::endpoint>* GetPeerList();
    virtual int GetRecvfromCounter();
    virtual void SetShowBuffer(bool);
    virtual void SetSendtoCounter(int);
    virtual int  GetSendtoCounter();
    virtual void     SetPlayerPort(uint16_t);
    virtual uint16_t GetPlayerPort();
    //virtual void       SetSplitterAddr(std::string);
    virtual void        SetSplitterAddr(ip::address splitter_addr);
    virtual ip::address GetSplitterAddr();
    virtual void     SetSplitterPort(uint16_t);
    virtual uint16_t GetSplitterPort();
    virtual void     SetTeamPort(uint16_t);
    virtual uint16_t GetTeamPort();
    virtual void SetUseLocalHost(bool);
    bool GetUseLocalHost();
    virtual int GetHeaderSize();
    virtual int GetBufferSize();
    int GetNumberOfPeers() { return 0; }
    // bool AmIAMonitor() { return false; }
    //void ReceiveTheListOfPeers() {}
    
    static uint16_t GetDefaultPlayerPort();
    static uint16_t GetDefaultTeamPort();
    static ip::address GetDefaultSplitterAddr();
    static uint16_t GetDefaultSplitterPort();

  };
}

#endif  // P2PSP_CORE_PEER_IMS_H

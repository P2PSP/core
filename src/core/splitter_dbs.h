//
//  splitter_dbs.h -- Data Broadcasting Set of rules
//
//  This code is distributed under the GNU General Public License (see
//  THE_GENERAL_GNU_PUBLIC_LICENSE.txt for extending this information).
//  Copyright (C) 2016, the P2PSP team.
//  http://www.p2psp.org
//

#ifndef P2PSP_CORE_SPLITTER_DBS_H_
#define P2PSP_CORE_SPLITTER_DBS_H_

#include <boost/unordered_map.hpp>
#include "splitter_core.h"

namespace p2psp {
  class Splitter_DBS : public Splitter_core {
  protected:
    static const int kMaxChunkLoss; // Chunk losses threshold to reject a peer from the team
    static const int kNumberOfMonitors;

    int max_number_of_chunk_loss_;
    //int max_number_of_monitors_;
    int number_of_monitors_;

    int peer_number_;

    // The list of peers in the team
    std::vector<boost::asio::ip::udp::endpoint> peer_list_;

    // Outgoing peers
    std::vector<boost::asio::ip::udp::endpoint> outgoing_peer_list_;

    // Destination peers of the chunk, indexed by a chunk
    // number. Used to find the peer to which a chunk has been sent
    std::vector<boost::asio::ip::udp::endpoint> destination_of_chunk_;

    // TODO: Endpoint doesn't implement hash_value, decide if string can be used
    // instead
    boost::unordered_map<boost::asio::ip::udp::endpoint, int,
      std::size_t (*)(const boost::asio::ip::udp::endpoint &)>
      losses_;

    // Thread management
    virtual void Run() override;

    // Hasher for unordered_maps
    static std::size_t GetHash(const boost::asio::ip::udp::endpoint &endpoint) {
      std::ostringstream stream;
      stream << endpoint;
      std::hash<std::string> hasher;
      return hasher(stream.str());
    };

  public:
    Splitter_DBS();
    ~Splitter_DBS();
    void SendTheNumberOfPeers(const std::shared_ptr<boost::asio::ip::tcp::socket> &peer_serve_socket);
    virtual void SendTheListOfPeers(const std::shared_ptr<boost::asio::ip::tcp::socket> &peer_serve_socket);
    //void SendThePeerEndpoint(const std::shared_ptr<boost::asio::ip::tcp::socket> &peer_serve_socket);
    void SendConfiguration(const std::shared_ptr<boost::asio::ip::tcp::socket> &sock) override;
    virtual void InsertPeer(const boost::asio::ip::udp::endpoint &peer);
    virtual void HandleAPeerArrival(std::shared_ptr<boost::asio::ip::tcp::socket> serve_socket) override;
    size_t ReceiveMessage(std::vector<char> &message, boost::asio::ip::udp::endpoint &endpoint);
    uint16_t GetLostChunkNumber(const std::vector<char> &message);
    boost::asio::ip::udp::endpoint GetLosser(int lost_chunk_number);
    virtual void RemovePeer(const boost::asio::ip::udp::endpoint &peer);
    virtual void IncrementPeerUnsupportivity(const boost::asio::ip::udp::endpoint &peer);
    virtual void ProcessLostChunk(int lost_chunk_number, const boost::asio::ip::udp::endpoint &sender);
    void ProcessGoodbye(const boost::asio::ip::udp::endpoint &peer);
    virtual void ModerateTheTeam();
    void SetupTeamSocket() override;
    virtual void ResetCounters();
    void ResetCountersThread();
    virtual void ComputeNextPeerNumber(boost::asio::ip::udp::endpoint &peer);
    void SayGoodbye(const boost::asio::ip::udp::endpoint &peer);

    // Thread management
    virtual void Start() override;

    // Getters
    std::vector<boost::asio::ip::udp::endpoint> GetPeerList();
    int GetMaxNumberOfChunkLoss();
    int GetNumberOfMonitors();
    int GetLoss(const boost::asio::ip::udp::endpoint &peer);
    //int GetSendToCounter();

    void SetMaxNumberOfChunkLoss(int max_number_of_chunk_loss);
    void SetNumberOfMonitors(int number_of_monitors);

    // Default getters
    static int GetDefaultMaxNumberOfChunkLoss();
    static int GetDefaultNumberOfMonitors();
  };
}

#endif  // defined P2PSP_CORE_SPLITTER_DBS_H_

//
//  splitter_ims.h
//  P2PSP
//
//  This code is distributed under the GNU General Public License (see
//  THE_GENERAL_GNU_PUBLIC_LICENSE.txt for extending this information).
//  Copyright (C) 2014, the P2PSP team.
//  http://www.p2psp.org
//
//  DBS: Data Broadcasting Set of rules
//

#ifndef P2PSP_CORE_SPLITTER_DBS_H_
#define P2PSP_CORE_SPLITTER_DBS_H_

#include <stdio.h>
#include <string>
#include <boost/asio.hpp>
#include <boost/unordered_map.hpp>
#include "../util/trace.h"
#include "splitter_ims.h"

namespace p2psp {
class SplitterDBS : public SplitterIMS {
 private:
  // Hasher for unordered_map losses_
  static std::size_t GetHash(const boost::asio::ip::udp::endpoint &endpoint) {
    std::ostringstream stream;
    stream << endpoint;
    std::hash<std::string> hasher;
    return hasher(stream.str());
  };

 protected:
  const int kMaxChunkLoss =
      32;  // Chunk losses threshold to reject a peer from the team
  const int kMonitorNumber = 1;

  int max_chunk_loss_;
  int monitor_number_;

  int peer_number_;

  // The list of peers in the team
  std::vector<boost::asio::ip::udp::endpoint> peer_list_;

  // Destination peers of the chunk, indexed by a chunk
  // number. Used to find the peer to which a chunk has been sent
  std::vector<boost::asio::ip::udp::endpoint> destination_of_chunk_;

  // TODO: Endpoint doesn't implement hash_value, decide if string can be used
  // instead
  boost::unordered_map<boost::asio::ip::udp::endpoint, int,
                       std::size_t (*)(const boost::asio::ip::udp::endpoint &)>
      losses_;

  std::vector<char> magic_flags_;

 public:
  SplitterDBS();
  ~SplitterDBS();
  void SendMagicFlags(
      std::shared_ptr<boost::asio::ip::tcp::socket> &peer_serve_socket);
  void SendTheListSize(
      std::shared_ptr<boost::asio::ip::tcp::socket> &peer_serve_socket);
  void SendTheListOfPeers(
      std::shared_ptr<boost::asio::ip::tcp::socket> &peer_serve_socket);
  void SendThePeerEndpoint(
      std::shared_ptr<boost::asio::ip::tcp::socket> &peer_serve_socket);
  void InsertPeer(boost::asio::ip::udp::endpoint peer);
  void ReceiveMessage();
  void GetLostChunkNumber();  // TODO: Decide type for 'message' argument
  void GetLosser(int lost_chunk_number);
  void RemovePeer(boost::asio::ip::udp::endpoint peer);
  void IncrementUnsupportivityOfPeer(boost::asio::ip::udp::endpoint peer);
  void ProcessLostChunk(int lost_chunk_number,
                        boost::asio::ip::udp::endpoint sender);
  void ProcessGoodbye(boost::asio::ip::udp::endpoint peer);
  void ModerateTheTeam();
  void SetupTeamSocket();
  void ResetCounters();
  void ResetCountersThread();
  void ComputeNextPeerNumber();
};
}

#endif  // defined P2PSP_CORE_SPLITTER_DBS_H_

//
//  splitter_ems.h
//  P2PSP
//
//  This code is distributed under the GNU General Public License (see
//  THE_GENERAL_GNU_PUBLIC_LICENSE.txt for extending this information).
//  Copyright (C) 2016, the P2PSP team.
//  http://www.p2psp.org
//
//  EMS: Endpoint Masquerading Set of Rules
//

#ifndef P2PSP_CORE_SPLITTER_EMS_H_
#define P2PSP_CORE_SPLITTER_EMS_H_

#include <stdio.h>
#include <string>
#include <boost/asio.hpp>
#include <boost/unordered_map.hpp>
#include "splitter_dbs.h"
#include "common.h"
#include <boost/tuple/tuple.hpp>



namespace p2psp {
class SplitterEMS : public SplitterDBS {
 protected:

  // The list of peers in the team listed by public address
  std::vector<boost::asio::ip::udp::endpoint> peer_list_;

  // HashTable of public to private endpoints
  boost::unordered_map<boost::asio::ip::udp::endpoint, boost::asio::ip::udp::endpoint,
                       std::size_t (*)(const boost::asio::ip::udp::endpoint &)>
      peer_pairs_;
  // Destination peers of the chunk, indexed by a chunk
  // number. Used to find the peer to which a chunk has been sent
  std::vector<boost::asio::ip::udp::endpoint> destination_of_chunk_;

  // TODO: Endpoint doesn't implement hash_value, decide if string can be used
  // instead
  boost::unordered_map<boost::asio::ip::udp::endpoint, int,
                       std::size_t (*)(const boost::asio::ip::udp::endpoint &)>
      losses_;

  char magic_flags_;

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
  SplitterEMS();
  ~SplitterEMS();
  virtual void SendTheListOfPeers(
      const std::shared_ptr<boost::asio::ip::tcp::socket> &peer_serve_socket);
  virtual void InsertPeer(const boost::asio::ip::udp::endpoint &peer);
  virtual void HandleAPeerArrival(
      std::shared_ptr<boost::asio::ip::tcp::socket> serve_socket) override;
  boost::asio::ip::udp::endpoint GetLosser(int lost_chunk_number);
  virtual void RemovePeer(const boost::asio::ip::udp::endpoint &peer);
  virtual void ProcessLostChunk(int lost_chunk_number,
                                const boost::asio::ip::udp::endpoint &sender);

  // Thread management
  virtual void Start() override;

  // Getters
  std::vector<boost::asio::ip::udp::endpoint> GetPeerList();

};
}

#endif  // defined P2PSP_CORE_SPLITTER_EMS_H_

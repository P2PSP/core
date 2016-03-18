//
//  splitter_dbs.h
//  P2PSP
//
//  This code is distributed under the GNU General Public License (see
//  THE_GENERAL_GNU_PUBLIC_LICENSE.txt for extending this information).
//  Copyright (C) 2016, the P2PSP team.
//  http://www.p2psp.org
//
//  NTS: NAT Traversal Set of rules
//

#ifndef P2PSP_CORE_SPLITTER_NTS_H_
#define P2PSP_CORE_SPLITTER_NTS_H_

#include <stdio.h>
#include <string>
#include <queue>
#include <mutex>
#include <thread>
#include <condition_variable>
#include <boost/asio.hpp>
#include <boost/unordered_map.hpp>
#include "../util/trace.h"
#include "splitter_dbs.h"
#include "common.h"
#include "common_nts.h"

namespace p2psp {

// source_port_to_splitter is the public source port to splitter
// and source_ports_to_monitors are the source ports towards monitors.
struct ArrivingPeerInfo {
  std::shared_ptr<boost::asio::ip::tcp::socket> serve_socket_;
  boost::asio::ip::address peer_address_;
  uint16_t source_port_to_splitter_;
  std::vector<uint16_t> source_ports_to_monitors_;
  timepoint_t arrive_time_;
};

struct IncorporatingPeerInfo {
  boost::asio::ip::udp::endpoint peer_;
  timepoint_t incorporation_time_;
  uint16_t source_port_to_splitter_;
  std::vector<uint16_t> source_ports_to_monitors_;
  std::shared_ptr<boost::asio::ip::tcp::socket> serve_socket_;
};

class SplitterNTS : public SplitterDBS {
 protected:
  // The IDs of the peers in the team.
  std::map<boost::asio::ip::udp::endpoint, std::string> ids_;

  // The source port steps (smallest difference of the source ports
  // when connecting to different endpoints) of the peers in the team.
  std::map<boost::asio::ip::udp::endpoint, uint16_t> port_steps_;

  // The last known allocated source port for each peer in the team.
  std::map<boost::asio::ip::udp::endpoint, uint16_t> last_source_port_;

  // The arriving peers. Key: ID. Value: ArrivingPeerInfo
  std::map<std::string, ArrivingPeerInfo> arriving_peers_;

  // The peers that are being incorporated, have closed their TCP
  // connection to splitter and try to connect to all existing peers.
  // They will be removed from team if (taking too long to connect to peers.
  // key: peer_id; value: IncorporatingPeerInfo
  // The source port values are set when the peer retries incorporation.
  std::map<std::string, IncorporatingPeerInfo> incorporating_peers_;

  // This socket is closed and created again when a new peer arrives,
  // and all incorporated peers with port_step != 0 send a message to this
  // socket to determine the currently allocated source port
  std::shared_ptr<boost::asio::ip::udp::socket> extra_socket_;

  // This message queue stores tuples (message, destination) that will be sent
  // in a dedicated thread instead of the main thread, with a delay between
  // each message to avoid network congestion.
  std::queue<message_t> message_queue_;
  // TODO: Use chunk_received_mutex_ and message_queue_event_ here as well?
  std::mutex message_queue_mutex_;
  std::condition_variable message_queue_event_;

  // An event that is set for each chunk received by the source
  std::mutex chunk_received_mutex_;
  std::condition_variable chunk_received_event_;

  std::thread check_timeout_thread_;
  std::thread listen_extra_socket_thread_;
  std::thread send_message_thread_;

  virtual void EnqueueMessage(unsigned int count, const message_t& message);

  virtual size_t ReceiveChunk(boost::asio::streambuf &chunk) override;
  virtual void SendMessageThread();
  virtual std::string GenerateId();
  virtual void SendTheListOfPeers(
      const std::shared_ptr<boost::asio::ip::tcp::socket> &peer_serve_socket);
  virtual void SendTheListOfPeers2(
      const std::shared_ptr<boost::asio::ip::tcp::socket> &peer_serve_socket,
      const boost::asio::ip::udp::endpoint& peer);
  virtual void CheckArrivingPeerTime();
  virtual void CheckIncorporatingPeerTime();
  virtual void CheckTimeoutThread();
  virtual void ListenExtraSocketThread();
  virtual void HandleAPeerArrival(
      std::shared_ptr<boost::asio::ip::tcp::socket> serve_socket) override;
  virtual void IncorporatePeer(const std::string& peer_id);
  virtual void SendNewPeer(const std::string& peer_id,
      const boost::asio::ip::udp::endpoint& new_peer,
      const std::vector<uint16_t>& source_ports_to_monitors);
  virtual void RetryToIncorporatePeer(const std::string& peer_id);
  virtual void UpdatePortStep(const boost::asio::ip::udp::endpoint peer,
      uint16_t source_port);
  virtual void RemovePeer(const boost::asio::ip::udp::endpoint& peer) override;
  virtual void ModerateTheTeam() override;

 public:
  SplitterNTS();
  ~SplitterNTS();
};
}

#endif  // defined P2PSP_CORE_SPLITTER_NTS_H_

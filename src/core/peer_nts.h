//
//  peer_nts.h
//  P2PSP
//
//  This code is distributed under the GNU General Public License (see
//  THE_GENERAL_GNU_PUBLIC_LICENSE.txt for extending this information).
//  Copyright (C) 2016, the P2PSP team.
//  http://www.p2psp.org
//
//  NTS: NAT Traversal Set of rules
//

#ifndef P2PSP_CORE_PEER_NTS_H
#define P2PSP_CORE_PEER_NTS_H

#include "peer_dbs.h"
#include "common.h"
#include "common_nts.h"
#include <cstdint>
#include <list>
#include <set>
#include <vector>
#include <mutex>
#include <thread>
#include <condition_variable>

namespace p2psp {

struct HelloMessage {
  message_t message_;
  timepoint_t time_;
  std::vector<uint16_t> ports_;
};

class PeerNTS : public PeerDBS {
 protected:
  std::string peer_id_;
  std::mutex hello_messages_lock_;
  std::list<HelloMessage> hello_messages_;
  std::condition_variable hello_messages_event_;
  std::mutex hello_messages_event_mutex_;
  // A list of peer_ids that contains the peers that were in the team when
  // starting incorporation and that are not connected yet
  std::list<std::string> initial_peer_list_;

  std::thread send_hello_thread_;

  virtual void SayHello(const ip::udp::endpoint& peer) override;
  virtual void SendHello(const ip::udp::endpoint& peer,
      std::vector<uint16_t> additional_ports = {});

  // Parameter: message_data = (message, destination)
  // Send a general message continuously until acknowledge is received
  virtual void SendMessage(const message_t& message_data);

  virtual void ReceiveId();
  virtual void SendHelloThread();
  virtual void SendMessage(std::string message,
      boost::asio::ip::udp::endpoint endpoint);
  virtual void StartSendHelloThread();
  virtual void ReceiveTheListOfPeers2();
  virtual void DisconnectFromTheSplitter() override;
  virtual void TryToDisconnectFromTheSplitter();

  virtual std::set<uint16_t> GetFactors(uint16_t n);

  // Get the number of possible products of a factor and another integer
  // that are less or equal to the original number n.
  virtual uint16_t CountCombinations(const std::set<uint16_t>& factors);

  virtual std::set<uint16_t> GetProbablePortDiffs(uint16_t port_diff,
      uint16_t peer_number);

  // Predict probable source ports that the arriving peer will use
  // to communicate with this peer
  virtual std::vector<uint16_t> GetProbableSourcePorts(
      uint16_t source_port_to_splitter, uint16_t port_diff,
      uint16_t peer_number);

  // Handle NTS messages; pass other messages to base class
  virtual int ProcessMessage(const std::vector<char>& message,
      const ip::udp::endpoint& sender) override;

 public:
  PeerNTS();
  ~PeerNTS();
  virtual void Init() override;
};
}

#endif  // P2PSP_CORE_PEER_NTS_H

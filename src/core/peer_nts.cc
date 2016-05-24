//
//  peer_nts.cc
//  P2PSP
//
//  This code is distributed under the GNU General Public License (see
//  THE_GENERAL_GNU_PUBLIC_LICENSE.txt for extending this information).
//  Copyright (C) 2016, the P2PSP team.
//  http://www.p2psp.org
//
//  NTS: NAT Traversal Set of rules
//

#include "peer_nts.h"
#include "common_nts.h"
#include "common.h"
#include "../util/trace.h"
#include <ctime>
#include <chrono>
#include <thread>
#include <numeric>
#include <boost/algorithm/string/join.hpp>
#include <boost/range/algorithm_ext/push_back.hpp>

namespace p2psp {

PeerNTS::PeerNTS(){
    magic_flags_ = Common::kNTS;
}

PeerNTS::~PeerNTS(){
  if (this->send_hello_thread_.joinable()) {
    this->send_hello_thread_.join();
  }
}

void PeerNTS::Init() { LOG("Initialized"); }

bool operator==(const HelloMessage& msg1, const HelloMessage& msg2) {
  return msg1.message_ == msg2.message_;
}

bool operator==(const HelloMessage& msg1, const message_t& msg2) {
  return msg1.message_ == msg2;
}

void PeerNTS::SayHello(const ip::udp::endpoint& peer) {
  // Do nothing, as this is handled later in the program by SendHello
}

void PeerNTS::SendHello(const ip::udp::endpoint& peer,
    std::vector<uint16_t> additional_ports) {
  std::lock_guard<std::mutex> guard(this->hello_messages_lock_);
  std::string message = this->peer_id_;
  message_t hello_data = std::make_pair(message, peer);
  if (!CommonNTS::Contains(this->hello_messages_, hello_data)) {
    additional_ports.push_back(peer.port());
    this->hello_messages_.push_back(HelloMessage{hello_data,
        std::chrono::steady_clock::now(), additional_ports});
  }
}

void PeerNTS::SendMessage(const message_t& message_data) {
  std::lock_guard<std::mutex> guard(this->hello_messages_lock_);
  if (!CommonNTS::Contains(this->hello_messages_, message_data)) {
    this->hello_messages_.push_back(HelloMessage{message_data,
        std::chrono::steady_clock::now(),
        std::vector<uint16_t>(1, message_data.second.port())});
    // Directly start packet sending
    this->hello_messages_event_.notify_all();
  }
}

void PeerNTS::ReceiveId() {
  LOG("Requesting peer ID from splitter");
  this->peer_id_ = CommonNTS::ReceiveString(this->splitter_socket_,
      CommonNTS::kPeerIdLength);
  LOG("ID received: " << this->peer_id_);
}

void PeerNTS::SendHelloThread() {
  while (this->player_alive_) {
    // Continuously send hello UDP packets to arriving peers
    // until a connection is established
    timepoint_t now = std::chrono::steady_clock::now();
    std::list<HelloMessage> messages_to_remove;
    // Make local copies as entries may be removed
    std::list<HelloMessage> hello_messages = this->hello_messages_;
    for (const HelloMessage& hello_message : hello_messages) {
      // Check for timeout
      if (now - hello_message.time_
          > CommonNTS::kMaxPeerArrivingTime) {
        messages_to_remove.push_back(hello_message);
        continue;
      }
      std::string message = hello_message.message_.first;
      ip::udp::endpoint peer = hello_message.message_.second;
      if (message == this->peer_id_) {
        DEBUG("Sending [hello (" << message << ")] to " << peer
            << " (trying " << hello_message.ports_.size()
            << " ports)");
      } else {
        DEBUG("Sending message (" << message.substr(0, CommonNTS::kPeerIdLength)
            << ") of length " << message.size() << " to " << peer
            << " (trying " << hello_message.ports_.size()
            << " ports)");
      }
      for (uint16_t port : hello_message.ports_) {
        this->SendMessage(message, ip::udp::endpoint(peer.address(), port));
        // Avoid network congestion
        std::this_thread::sleep_for(std::chrono::milliseconds(1));
      }
    }
    // Remove messages that timed out
    {
      std::lock_guard<std::mutex> guard(this->hello_messages_lock_);
      for (const HelloMessage& hello_message : messages_to_remove) {
        if (CommonNTS::Contains(this->hello_messages_, hello_message)) {
          LOG("Removed message "
              << hello_message.message_.first.substr(0,
              CommonNTS::kPeerIdLength) << " to "
              << hello_message.message_.second << " due to timeout");
          this->hello_messages_.remove(hello_message);
        }
      }
    }

    std::unique_lock<std::mutex> lock(this->hello_messages_event_mutex_);
    this->hello_messages_event_.wait_until(lock,
        std::chrono::steady_clock::now() + CommonNTS::kHelloPacketTiming);

  }
}

void PeerNTS::SendMessage(std::string message,
    boost::asio::ip::udp::endpoint endpoint) {
  try {
    this->team_socket_.send_to(buffer(message), endpoint);
  } catch (std::exception e) {
    ERROR(e.what());
  }
}

void PeerNTS::StartSendHelloThread() {
  this->player_alive_ = true; // PeerIMS sets this variable in buffer_data()
  // Start the hello packet sending thread
  this->send_hello_thread_ = std::thread(&PeerNTS::SendHelloThread, this);
}

void PeerNTS::ReceiveTheListOfPeers2() {
  // The monitor peer endpoints have already been received
  if (this->peer_list_.size() != (unsigned int)this->number_of_monitors_) {
    ERROR("this->peer_list_.size() != this->number_of_monitors_");
  }

  LOG("Requesting the number of peers from splitter");
  // Add number_of_monitors as the monitor peers were already received

  this->number_of_peers_ = CommonNTS::Receive<uint16_t>(this->splitter_socket_)
      + this->number_of_monitors_;
  LOG("The size of the team is " << this->number_of_peers_
      << " (apart from me)");

  // Skip the monitor peers
  for (int i = 0; i < this->number_of_peers_ - this->number_of_monitors_; i++) {
    std::string peer_id = CommonNTS::ReceiveString(this->splitter_socket_,
        CommonNTS::kPeerIdLength);
    ip::address IP_addr = ip::address_v4(
        CommonNTS::Receive<uint32_t>(this->splitter_socket_));
    uint16_t port_to_splitter =
        CommonNTS::Receive<uint16_t>(this->splitter_socket_);
    uint16_t port_step = CommonNTS::Receive<uint16_t>(this->splitter_socket_);
    ip::udp::endpoint peer(IP_addr, port_to_splitter);

    this->initial_peer_list_.push_back(peer_id);

    // Try different probable ports for the existing peer
    std::vector<uint16_t> probable_source_ports;
    if (port_step > 0) {
      for (int port = port_to_splitter + port_step; port < 65536 &&
          port <= port_to_splitter+(int)CommonNTS::kMaxPredictedPorts*port_step;
          port += port_step) {
        probable_source_ports.push_back(port);
      }
    }
    this->SendHello(peer, probable_source_ports);
    LOG("[hello] sent to " << peer);
  }

  // Directly start packet sending
  this->hello_messages_event_.notify_all();

  LOG("List of peers received");
}

void PeerNTS::DisconnectFromTheSplitter() {
  try {
    this->TryToDisconnectFromTheSplitter();
  } catch(const std::exception& e) {
    ERROR(e.what());
    ERROR("Probably the splitter removed this peer due to timeout");
    this->player_alive_ = false;
    exit(1);
  }
}

void PeerNTS::TryToDisconnectFromTheSplitter() {
  this->StartSendHelloThread();

  // CommonNTS::Receive the generated ID for this peer from splitter
  this->ReceiveId();

  // Note: This peer is *not* the monitor peer.

  // Send UDP packets to splitter and monitor peers
  // to create working NAT entries and to determine the
  // source port allocation type of the NAT of this peer
  this->SendHello(this->splitter_);
  for (auto peer_iter = this->peer_list_.begin();
      peer_iter != peer_list_.end() &&
      peer_iter != this->peer_list_.begin() + this->number_of_monitors_;
      ++peer_iter) {
    this->SendHello(*peer_iter);
  }
  // Directly start packet sending
  this->hello_messages_event_.notify_all();

  // CommonNTS::Receive the list of peers, except the monitor peer, with their
  // peer IDs and send hello messages
  this->ReceiveTheListOfPeers2();

  // Wait for getting connected to all currently known peers
  timepoint_t incorporation_time = std::chrono::steady_clock::now();
  // A timeout < MAX_PEER_ARRIVING_TIME has to be set for this->team_socket_
  // The monitor is not in initial_peer_list
  while (this->initial_peer_list_.size() > 0) {
    if (std::chrono::steady_clock::now() - incorporation_time
        > CommonNTS::kMaxPeerArrivingTime) {
      // Retry incorporation into the team
      LOG("Retrying incorporation with " << this->initial_peer_list_.size()
          << " peers left: "
          << boost::algorithm::join(this->initial_peer_list_, ", "));
      incorporation_time = std::chrono::steady_clock::now();
      // Cleaning hello messages
      {
        std::lock_guard<std::mutex> guard(this->hello_messages_lock_);
        this->hello_messages_.clear();
      }
      // Resetting peer lists
      this->initial_peer_list_.clear();
      this->peer_list_.resize(this->number_of_monitors_); // Leave monitors
      // Recreate the socket
      // Similar to PeerDBS.listen_to_the_team, binds to a random port
      this->team_socket_.close();
      // to allow override in symsp_peer
      this->team_socket_ = ip::udp::socket(this->io_service_);
      this->team_socket_.open(ip::udp::v4());
      this->team_socket_.set_option(ip::udp::socket::reuse_address(true));
      // This is the maximum time the peer will wait for a chunk
      // (from the splitter or from another peer).
      this->team_socket_.bind(ip::udp::endpoint(ip::udp::v4(), 0));
      this->team_socket_.set_option(socket_base::linger(true, 1));
      // Say hello to splitter again, to retry incorporation
      // 'N' for 'not incorporated'
      this->SendMessage(std::make_pair(this->peer_id_ + 'N', this->splitter_));
      // Say hello to monitors again, to keep the NAT entry alive
      for (auto peer_iter = this->peer_list_.begin();
          peer_iter != this->peer_list_.end() &&
          peer_iter != this->peer_list_.begin() + this->number_of_monitors_;
          ++peer_iter) {
        this->SendMessage(std::make_pair(this->peer_id_ + 'N', *peer_iter));
      }
      // CommonNTS::Receive all peer endpoints and send hello messages
      this->ReceiveTheListOfPeers2();
    }

    // Process messages to establish connections to peers
    this->ProcessNextMessage();
  }

  // Close the TCP socket
  PeerDBS::DisconnectFromTheSplitter();
  // The peer is now successfully incorporated; inform the splitter
  this->SendMessage(std::make_pair(this->peer_id_ + 'Y', this->splitter_));
  LOG("Incorporation successful");
}

std::set<uint16_t> PeerNTS::GetFactors(uint16_t n) {
  std::set<uint16_t> factors;
  for (int i = (int)sqrtf(n); i>=1; i--) {
    if (n%i == 0) {
      factors.insert(i);
      factors.insert(n/i);
    }
  }
  return factors;
}

uint16_t PeerNTS::CountCombinations(const std::set<uint16_t>& factors) {
  // Get the number of possible products of a factor and another integer
  // that are less or equal to the original number n.
  // Example: the number is 10, the factors are 1, 2, 5, 10.
  // Products <=10: 1*1, ..., 1*10, 2*1, ..., 2*5, 5*1, 5*2, 10*1.
  // So for each factor there are "n/factor" products:

  return std::accumulate(factors.begin(), factors.end(), 0);
}

std::set<uint16_t> PeerNTS::GetProbablePortDiffs(uint16_t port_diff,
    uint16_t peer_number) {
  // The actual port prediction happens here:
  // port_diff is the measured source port difference so the NAT could have
  // any factor of port_diff as its actual port_step. This function assumes
  // different port_step values and calculates a few resulting source port
  // differences, assuming some ports are skipped (already taken).

  std::set<uint16_t> factors = this->GetFactors(port_diff);
  uint16_t num_combinations = this->CountCombinations(factors);
  float count_factor = CommonNTS::kMaxPredictedPorts/(float)num_combinations;

  std::set<uint16_t> port_diffs;
  for (uint16_t port_step : factors) {
    for (int skips = (int) ceilf(port_diff/port_step*count_factor)+1;
        skips >= 0; skips--) {
      port_diffs.insert(port_step * (peer_number + skips));
    }
  }
  return port_diffs;
}

std::vector<uint16_t> PeerNTS::GetProbableSourcePorts(
    uint16_t source_port_to_splitter, uint16_t port_diff,
    uint16_t peer_number) {
  // Predict probable source ports that the arriving peer will use
  // to communicate with this peer

  std::vector<uint16_t> probable_source_ports;
  if (port_diff <= 0) {
    // Constant source port (Cone NAT)
    return probable_source_ports;
  }

  // Port prediction:
  for (uint16_t probable_port_diff
      : this->GetProbablePortDiffs(port_diff, peer_number)) {
    if (source_port_to_splitter + probable_port_diff < 65536) {
      probable_source_ports.push_back(
          source_port_to_splitter + probable_port_diff);
    }
  }
  return probable_source_ports;
}

int PeerNTS::ProcessMessage(const std::vector<char>& message_bytes,
    const ip::udp::endpoint& sender) {
  // Handle NTS messages; pass other messages to base class
  std::string message(message_bytes.data(), message_bytes.size());
  std::istringstream msg_str(message);

  if (sender == this->splitter_ &&
      message.size() == CommonNTS::kPeerIdLength + 10) {
    // say [hello to (X)] received from splitter
    std::string peer_id =
        CommonNTS::ReceiveString(msg_str, CommonNTS::kPeerIdLength);
    ip::address IP_addr = ip::address_v4(CommonNTS::Receive<uint32_t>(msg_str));
    uint16_t source_port_to_splitter = CommonNTS::Receive<uint16_t>(msg_str);
    uint16_t port_diff = CommonNTS::Receive<uint16_t>(msg_str);
    uint16_t peer_number = CommonNTS::Receive<uint16_t>(msg_str);

    // Endpoint to splitter
    ip::udp::endpoint peer(IP_addr, source_port_to_splitter);
    LOG("Received [send hello to " << peer_id << ' ' << peer << ']');
    LOG("port_diff = " << port_diff);
    LOG("peer_number = " << peer_number);
    // Here the port prediction happens:
    std::vector<uint16_t> additional_ports = this->GetProbableSourcePorts(
        source_port_to_splitter, port_diff, peer_number);
    DEBUG("Probable source ports: " << source_port_to_splitter << " and ["
        << CommonNTS::Join(additional_ports, ", ") << ']');
    this->SendHello(peer, additional_ports);
    // Directly start packet sending
    this->hello_messages_event_.notify_all();
  } else if (sender == this->splitter_ &&
      message.size() == CommonNTS::kPeerIdLength + 12) {
    // say [hello to (X)] received from splitter
    std::string peer_id =
        CommonNTS::ReceiveString(msg_str, CommonNTS::kPeerIdLength);
    ip::address IP_addr = ip::address_v4(CommonNTS::Receive<uint32_t>(msg_str));
    uint16_t source_port_to_splitter = CommonNTS::Receive<uint16_t>(msg_str);
    uint16_t port_diff = CommonNTS::Receive<uint16_t>(msg_str);
    uint16_t peer_number = CommonNTS::Receive<uint16_t>(msg_str);
    uint16_t extra_splitter_port = CommonNTS::Receive<uint16_t>(msg_str);

    // Endpoint to splitter
    ip::udp::endpoint peer(IP_addr, source_port_to_splitter);
    LOG("Received [send hello to " << peer_id << ' ' << peer << ']');
    LOG("port_diff = " << port_diff);
    LOG("peer_number = " << peer_number);
    // Here the port prediction happens:
    std::vector<uint16_t> additional_ports = this->GetProbableSourcePorts(
        source_port_to_splitter, port_diff, peer_number);
    DEBUG("Probable source ports: " << source_port_to_splitter << " and ["
        << CommonNTS::Join(additional_ports, ", ") << ']');
    this->SendHello(peer, additional_ports);
    // Send to extra splitter port to determine currently allocated
    // source port
    this->SendHello(ip::udp::endpoint(this->splitter_.address(),
        extra_splitter_port));
    // Directly start packet sending
    this->hello_messages_event_.notify_all();
  } else if (message == this->peer_id_ || (sender == this->splitter_ &&
      message.size() == CommonNTS::kPeerIdLength + 2) ||
      (sender == this->splitter_ &&
      message.size() == CommonNTS::kPeerIdLength + 3) ||
      message.size() == CommonNTS::kPeerIdLength + 1) { // All sent msg sizes
    // Acknowledge received; stop sending the message
    {
      std::lock_guard<std::mutex> guard(this->hello_messages_lock_);
      for (const HelloMessage& hello_message : this->hello_messages_) {
        if (message == hello_message.message_.first
            && sender.address() == hello_message.message_.second.address()
            && CommonNTS::Contains(hello_message.ports_,
            sender.port())) {
          DEBUG("Received acknowledge from " << sender);
          // TODO: Check if message_data as a reference is ok here
          this->hello_messages_.remove(hello_message);
          return -1;
        }
      }
    }
    WARNING("Received acknowledge " << message << " from unknown host "
        << sender);
  } else if (message.size() == CommonNTS::kPeerIdLength) {
    std::string peer_id =
        CommonNTS::ReceiveString(msg_str, CommonNTS::kPeerIdLength);
    LOG("Received [hello (ID " << message << ")] from " << sender);
    // Send acknowledge
    this->SendMessage(message, sender);

    std::ostringstream msg_str2;
    msg_str2 << message;
    if (!CommonNTS::Contains(this->peer_list_, sender)) {
      LOG("Appending peer " << peer_id << ' ' << sender << " to list");
      this->peer_list_.push_back(sender);
      this->debt_[sender] = 0;
      // Send source port information to splitter
      CommonNTS::Write<uint16_t>(msg_str2, sender.port());
      message_t message_data = std::make_pair(msg_str2.str(), this->splitter_);
      this->SendMessage(message_data);

      if (CommonNTS::Contains(this->initial_peer_list_, peer_id)) {
        this->initial_peer_list_.remove(peer_id);
      }
    }
  } else if (message == "H") {
    LOG("Received [DBS hello] from " << sender);
    // Ignore hello messages that are sent by PeerDBS instances in
    // CommonNTS::ReceiveTheListOfPeers() before a PeerNTS instance is created
  } else if (sender != this->splitter_
      && !CommonNTS::Contains(this->peer_list_, sender)) {
    DEBUG("Ignoring message of length " << message.size() << " from unknown "
        << sender);
  } else if (this->initial_peer_list_.size() == 0) {
    // Start receiving chunks when fully incorporated
    return PeerDBS::ProcessMessage(message_bytes, sender);
  }

  // No chunk number, as no chunk was received
  return -1;
}

}

//
//  splitter_nts.cc
//  P2PSP
//
//  This code is distributed under the GNU General Public License (see
//  THE_GENERAL_GNU_PUBLIC_LICENSE.txt for extending this information).
//  Copyright (C) 2016, the P2PSP team.
//  http://www.p2psp.org
//
//  NTS: NAT Traversal Set of rules
//

#include "splitter_nts.h"
#include "common_nts.h"
#include "common.h"
#include "../util/trace.h"
#include <cassert>
#include <thread>
#include <random>

using namespace boost::asio;

namespace p2psp {

uint16_t gcd(uint16_t a, uint16_t b) {
    return b == 0 ? a : gcd(b, a % b);
}

SplitterNTS::SplitterNTS() : SplitterLRS(),
    max_message_size_(this->chunk_size_ + 2) {
  this->magic_flags_ = Common::kNTS;

  // The thread regularly checks if (peers are waiting to be incorporated
  // for too long and removes them after a timeout
  this->check_timeout_thread_ =
      std::thread(&SplitterNTS::CheckTimeoutThread, this);

  // The thread listens to this->extra_socket_ and reports source ports
  this->listen_extra_socket_thread_ =
      std::thread(&SplitterNTS::ListenExtraSocketThread, this);

  this->send_message_thread_ =
      std::thread(&SplitterNTS::SendMessageThread, this);

  LOG("Initialized NTS");
}

SplitterNTS::~SplitterNTS() {
  if (this->check_timeout_thread_.joinable()) {
    this->check_timeout_thread_.join();
  }
  if (this->listen_extra_socket_thread_.joinable()) {
    this->listen_extra_socket_thread_.join();
  }
  if (this->send_message_thread_.joinable()) {
    this->send_message_thread_.join();
  }
}

void SplitterNTS::EnqueueMessage(unsigned int count, const message_t& message) {
  {
    std::unique_lock<std::mutex> lock(this->message_queue_mutex_);
    for (unsigned int i = 0; i < count; i++) {
      this->message_queue_.push(message);
    }
  }
  this->message_queue_event_.notify_all();
}

size_t SplitterNTS::ReceiveChunk(boost::asio::streambuf &chunk) {
  size_t bytes_transferred = SplitterLRS::ReceiveChunk(chunk);
  this->chunk_received_event_.notify_all();
  return bytes_transferred;
}

void SplitterNTS::SendMessageThread() {
  while (this->alive_) {
    // Wait for an enqueued message
    message_t message_data;
    {
      std::unique_lock<std::mutex> lock(this->message_queue_mutex_);
      while (this->message_queue_.empty()) {
        this->message_queue_event_.wait(lock);
      }
      message_data = this->message_queue_.front();
      this->message_queue_.pop();
    }
    // Send the message
    try {
      this->team_socket_.send_to(buffer(message_data.first),
        message_data.second);
    } catch (std::exception e) {
      ERROR(e.what());
    }
    // Wait for a chunk from source to avoid network congestion
    std::unique_lock<std::mutex> lock(chunk_received_mutex_);
    this->chunk_received_event_.wait(lock);
  }
}

std::string SplitterNTS::GenerateId() {
  // Generate a random ID for a newly arriving peer
  // This has about the same number of combinations as a 32 bit integer
  static std::random_device rd;
  static std::mt19937 gen(rd());
  static std::uniform_int_distribution<> distr(0, 35);

  std::ostringstream str;
  for (int i = 0; i < CommonNTS::kPeerIdLength; i++) {
    char c = (char) distr(gen);
    str << (char)(c >= 10 ? c-10+'A' : c+'0');
  }
  std::string id = str.str();
  return id;
}

void SplitterNTS::SendTheListOfPeers(
    const std::shared_ptr<boost::asio::ip::tcp::socket> &peer_serve_socket) {
  // For NTS, send only the monitor peers, as the other peers' endpoints
  // are sent together with their IDs when a PeerNTS instance has been
  // created from the PeerDBS instance, in SendTheListOfPeers2()

  LOG("Sending the monitors as the list of peers");
  // Send the number of monitors
  std::ostringstream msg_str;
  CommonNTS::Write<uint16_t>(msg_str, this->max_number_of_monitors_);
  peer_serve_socket->send(buffer(msg_str.str()));
  // Send a peer list size equal to the number of monitor peers
  msg_str.str(std::string());
  CommonNTS::Write<uint16_t>(msg_str,
      std::min((unsigned int) this->max_number_of_monitors_,
      (unsigned int) this->peer_list_.size()));
  peer_serve_socket->send(buffer(msg_str.str()));
  // Send the monitor endpoints
  for (std::vector<ip::udp::endpoint>::iterator peer_iter =
      this->peer_list_.begin(); peer_iter != this->peer_list_.end()
      && peer_iter != this->peer_list_.begin() + this->max_number_of_monitors_;
      ++peer_iter) {
    msg_str.str(std::string());
    CommonNTS::Write<uint32_t>(msg_str,
        (uint32_t)peer_iter->address().to_v4().to_ulong());
    CommonNTS::Write<uint16_t>(msg_str, (uint16_t)peer_iter->port());
    peer_serve_socket->send(buffer(msg_str.str()));
  }
}

void SplitterNTS::SendTheListOfPeers2(
    const std::shared_ptr<ip::tcp::socket> &peer_serve_socket,
    const ip::udp::endpoint& peer) {
  // Send all peers except the monitor peers with their peer ID
  // plus all peers currently being incorporated
  uint16_t number_of_other_peers = this->peer_list_.size()
      - this->max_number_of_monitors_ + this->incorporating_peers_.size();
  if (CommonNTS::Contains(this->peers_, peer)) {
    // Then peer is also in this->incorporating_peers_
    // Do not send the peer endpoint to itself
    number_of_other_peers = std::max(0, number_of_other_peers - 1);
  }
  LOG("Sending the list of peers except monitors (" << number_of_other_peers
      << " peers)");
  std::ostringstream msg_str;
  CommonNTS::Write<uint16_t>(msg_str, number_of_other_peers);
  peer_serve_socket->send(buffer(msg_str.str()));

  for (std::vector<ip::udp::endpoint>::iterator peer_iter =
      this->peer_list_.begin() + this->max_number_of_monitors_;
      peer_iter != this->peer_list_.end(); ++peer_iter) {
    // Also send the port step of the existing peer, in case
    // it is behind a sequentially allocating NAT
    const PeerInfo& peer_info = this->peers_[*peer_iter];
    msg_str.str(std::string());
    msg_str << peer_info.id_;
    CommonNTS::Write<uint32_t>(msg_str,
        (uint32_t)peer_iter->address().to_v4().to_ulong());
    CommonNTS::Write<uint16_t>(msg_str, peer_info.last_source_port_);
    CommonNTS::Write<uint16_t>(msg_str, peer_info.port_step_);
    peer_serve_socket->send(buffer(msg_str.str()));
  }
  // Send the peers currently being incorporated
  for (const auto& peer_iter : this->incorporating_peers_) {
    const std::string& peer_id = peer_iter.first;
    // Do not send the peer endpoint to itself
    if (CommonNTS::Contains(this->peers_, peer)
        && peer_id == this->peers_[peer].id_) {
      continue;
    }
    LOG("Sending peer " << peer_id << " to " << peer);
    const ip::udp::endpoint& peer = peer_iter.second.peer_;
    const PeerInfo& peer_info = this->peers_[peer];
    msg_str.str(std::string());
    msg_str << peer_id;
    CommonNTS::Write<uint32_t>(msg_str,
        (uint32_t)peer.address().to_v4().to_ulong());
    CommonNTS::Write<uint16_t>(msg_str, peer_info.last_source_port_);
    CommonNTS::Write<uint16_t>(msg_str, peer_info.port_step_);
    peer_serve_socket->send(buffer(msg_str.str()));
  }
}

void SplitterNTS::CheckArrivingPeerTime() {
  // Remove peers that are waiting to be incorporated too long

  timepoint_t now = std::chrono::steady_clock::now();
  std::list<std::string> peers_to_remove;
  // Build list of arriving peers to remove
  for (const auto& peer_iter : this->arriving_peers_) {
    const std::string& peer_id = peer_iter.first;
    if (now - this->arriving_peers_[peer_id].arrive_time_
        > CommonNTS::kMaxPeerArrivingTime) {
      peers_to_remove.push_back(peer_id);
    }
  }
  // Actually remove the peers
  for (const std::string& peer_id : peers_to_remove) {
    LOG("Removed arriving peer " << peer_id << " due to timeout");
    ArrivingPeerInfo& peer_info = this->arriving_peers_[peer_id];
    // Close socket
    peer_info.serve_socket_->close();
    // Remove peer
    this->arriving_peers_.erase(peer_id);
  }
}

void SplitterNTS::CheckIncorporatingPeerTime() {
  // Remove peers that try to connect to the existing peers too long

  timepoint_t now = std::chrono::steady_clock::now();
  std::list<std::string> peers_to_remove;
  // Build list of incorporating peers to remove
  for (const auto& peer_iter : this->incorporating_peers_) {
    const std::string& peer_id = peer_iter.first;
    if (now - this->incorporating_peers_[peer_id].incorporation_time_
      > CommonNTS::kMaxTotalIncorporationTime) {
      peers_to_remove.push_back(peer_id);
    }
  }
  // Actually remove the peers
  for (const std::string& peer_id : peers_to_remove) {
    LOG("Removed incorporating peer " << peer_id << " due to timeout");
    IncorporatingPeerInfo& peer_info =
        this->incorporating_peers_[peer_id];
    // Close TCP socket
    peer_info.serve_socket_->close();
    // Remove peer
    this->incorporating_peers_.erase(peer_id);
  }
}

void SplitterNTS::CheckTimeoutThread() {
  while (this->alive_) {
    std::this_thread::sleep_for(CommonNTS::kMaxPeerArrivingTime);
    // Check timeouts
    std::unique_lock<std::mutex> lock(arriving_incorporating_peers_mutex_);
    this->CheckArrivingPeerTime();
    this->CheckIncorporatingPeerTime();
  }
}

void SplitterNTS::ListenExtraSocketThread() {
  // The thread listens to this->extra_socket_ to determine the currently
  // allocated source port of incorporated peers behind SYMSP NATs

  // Wait until socket is created
  while (this->alive_
      && (!this->extra_socket_ || !this->extra_socket_->is_open())) {
    std::this_thread::sleep_for(std::chrono::seconds(1));
  }

  std::vector<char> message_bytes(CommonNTS::kPeerIdLength);
  std::string message;
  ip::udp::endpoint sender;

  while (this->alive_) {
    // Receive messages
    try {
      size_t bytes_transferred =
          this->extra_socket_->receive_from(buffer(message_bytes), sender);
      message = std::string(message_bytes.data(), bytes_transferred);
    } catch (std::exception e) {
      ERROR(e.what());
      continue;
    }

    if (message.size() == CommonNTS::kPeerIdLength) {
      // Send acknowledge
      try {
        this->extra_socket_->send_to(buffer(message), sender);
      } catch (std::exception e) {
        ERROR(e.what());
      }

      std::string peer_id(message.data(), CommonNTS::kPeerIdLength);

      const ip::udp::endpoint* peer = nullptr;
      // TODO: use std::find or boost::multi_index to optimize this loop
      for (auto peer_iter = this->peers_.begin();
          peer_iter != this->peers_.end(); ++peer_iter) {
        if (peer_id == peer_iter->second.id_) {
          peer = &peer_iter->first;
          break;
        }
      }
      if (peer == nullptr) {
        DEBUG("Peer ID " << peer_id << " unknown");
        continue;
      }
      // Check sender address
      if (sender.address() != peer->address()) {
        DEBUG("Peer " << peer_id << " switched from " << peer->address()
            << " to " << sender.address() << ", ignoring");
        continue;
      }
      // Update source port information
      LOG("Received current source port " << sender.port() << " of peer "
          << peer_id);
      this->UpdatePortStep(*peer, sender.port());
    } else {
      DEBUG("Ignoring packet of length " << message.size() << " from "
          << sender);
    }
  }
}

void SplitterNTS::HandleAPeerArrival(
    std::shared_ptr<ip::tcp::socket> serve_socket) {
  // This method implements the NAT traversal algorithms.

  ip::tcp::endpoint new_peer_tcp = serve_socket->remote_endpoint();
  ip::udp::endpoint new_peer(new_peer_tcp.address(), new_peer_tcp.port());
  LOG("Accepted connection from peer " << new_peer);
  this->SendConfiguration(serve_socket);
  this->SendTheListOfPeers(serve_socket);
  // Send the generated ID to peer
  std::string peer_id = this->GenerateId();
  LOG("Sending ID " << peer_id << " to peer " << new_peer);
  serve_socket->send(buffer(peer_id));
  std::unique_lock<std::mutex> lock(arriving_incorporating_peers_mutex_);
  if (this->peer_list_.size() < (unsigned int) this->max_number_of_monitors_) {
    // Directly incorporate the monitor peer into the team.
    // The source ports are all set to the same, as the monitor peers
    // should be publicly accessible
    this->peers_[new_peer] = PeerInfo{peer_id, .port_step_ = 0,
        .last_source_port_ = new_peer.port()};
    this->SendNewPeer(peer_id, new_peer,
        std::vector<uint16_t>(this->max_number_of_monitors_, new_peer.port()), 0);
    this->InsertPeer(new_peer);
    serve_socket->close();
  } else {
    this->arriving_peers_[peer_id] = ArrivingPeerInfo{serve_socket,
        new_peer.address(), 0,
        std::vector<uint16_t>(this->max_number_of_monitors_, 0),
        std::chrono::steady_clock::now()};
    // Splitter will continue with IncorporatePeer() as soon as the
    // arriving peer has sent UDP packets to splitter and monitor
  }
}

void SplitterNTS::IncorporatePeer(const std::string& peer_id) {
  const ArrivingPeerInfo& peer_info = this->arriving_peers_[peer_id];

  LOG("Incorporating the peer " << peer_id << ". Source ports: "
      << peer_info.source_port_to_splitter_ << ", "
      << CommonNTS::Join(peer_info.source_ports_to_monitors_, ", "));

  ip::udp::endpoint new_peer(peer_info.peer_address_,
      peer_info.source_port_to_splitter_);
  if (this->peer_list_.size() >= (unsigned int) this->max_number_of_monitors_) {
    try {
      // Send the endpoints of the incorporated peers to the new peer
      this->SendTheListOfPeers2(peer_info.serve_socket_, new_peer);
    } catch (std::exception e) {
      ERROR(e.what());
    }
  }

  // The peer is in the team, but is not connected to all peers yet,
  // so add to the list of incorporating peers.
  // arriving_incorporating_peers_mutex_ is already locked in ProcessMessage()
  this->incorporating_peers_[peer_id] = IncorporatingPeerInfo{new_peer,
      std::chrono::steady_clock::now(), peer_info.source_port_to_splitter_,
      peer_info.source_ports_to_monitors_, peer_info.serve_socket_,
      (uint16_t)-1, 0};
  for (uint16_t source_port_to_monitor : peer_info.source_ports_to_monitors_) {
    this->UpdatePortStep(new_peer, source_port_to_monitor);
  }

  // Send the new peer endpoint to the incorporated peers
  this->SendNewPeer(peer_id, new_peer, peer_info.source_ports_to_monitors_,
      this->incorporating_peers_[peer_id].port_step_);

  this->arriving_peers_.erase(peer_id);
}

void SplitterNTS::SendNewPeer(const std::string& peer_id,
    const ip::udp::endpoint& new_peer,
    const std::vector<uint16_t>& source_ports_to_monitors, uint16_t port_step) {

  // Recreate this->extra_socket_, listening to a random port
  // TODO: is the extra_socket recreated too often?
  if (this->extra_socket_)
  {
    this->extra_socket_->close();
  }
  this->extra_socket_.reset(new ip::udp::socket(this->io_service_));
  this->extra_socket_->open(ip::udp::v4());
  try {
    this->extra_socket_->bind(ip::udp::endpoint(ip::udp::v4(), 0));
  } catch (std::exception e) {
    ERROR(e.what());
  }
  // Do not block the thread forever:
  this->extra_socket_->set_option(socket_base::linger(true, 1));
  uint16_t extra_listen_port = this->extra_socket_->local_endpoint().port();
  DEBUG("Listening to the extra port " << extra_listen_port);
  DEBUG("Sending [send hello to " << new_peer << ']');
  // The peers start port prediction at the minimum known source port,
  // counting up using their peer_number
  std::vector<uint16_t> source_ports(source_ports_to_monitors);
  source_ports.push_back(new_peer.port());
  uint16_t min_known_source_port = *std::min_element(source_ports.begin(),
      source_ports.end());
  // Send packets to all peers;
  unsigned int peer_number = 0;
  for (auto peer_iter = this->peer_list_.begin();
      peer_iter != this->peer_list_.end(); ++peer_iter, ++peer_number) {
    std::ostringstream msg_str;
    msg_str << peer_id;
    if (peer_number < (unsigned int) this->max_number_of_monitors_) {
      // Send only the endpoint of the peer to the monitor,
      // as the arriving peer and the monitor already communicated
      CommonNTS::Write<uint32_t>(msg_str,
          (uint32_t)new_peer.address().to_v4().to_ulong());
      CommonNTS::Write<uint16_t>(msg_str,
          source_ports_to_monitors[peer_number]);
    } else {
      // Send all information necessary for port prediction to the
      // existing peers
      CommonNTS::Write<uint32_t>(msg_str,
          (uint32_t)new_peer.address().to_v4().to_ulong());
      CommonNTS::Write<uint16_t>(msg_str, min_known_source_port);
      CommonNTS::Write<uint16_t>(msg_str, port_step);
      // Splitter is "peer number 0", thus add 1
      CommonNTS::Write<uint16_t>(msg_str, peer_number+1);
      if (this->peers_[*peer_iter].port_step_ != 0) {
        // Send the port of this->extra_socket_ to determine the
        // currently allocated source port of the incorporated peer
        CommonNTS::Write<uint16_t>(msg_str, extra_listen_port);
      }
    }

    // Hopefully one of these packets arrives
    this->EnqueueMessage(3, std::make_pair(msg_str.str(), *peer_iter));
  }

  // Send packets to peers currently being incorporated
  for (const auto& peer_iter : this->incorporating_peers_) {
    const std::string& inc_peer_id = peer_iter.first;
    if (inc_peer_id == peer_id) {
      // Do not send the peer endpoint to the peer itself
      continue;
    }
    LOG("Sending peer " << new_peer << " to " << inc_peer_id);
    const ip::udp::endpoint& peer = peer_iter.second.peer_;
    std::ostringstream msg_str;
    msg_str << peer_id;
    CommonNTS::Write<uint32_t>(msg_str,
        (uint32_t)new_peer.address().to_v4().to_ulong());
    CommonNTS::Write<uint16_t>(msg_str, min_known_source_port);
    CommonNTS::Write<uint16_t>(msg_str, port_step);
    // Send the length of the peer_list as peer_number
    CommonNTS::Write<uint16_t>(msg_str, this->peer_list_.size()+1);
    // Hopefully one of these packets arrives
    this->EnqueueMessage(3, std::make_pair(msg_str.str(), peer));
  }
}

void SplitterNTS::RetryToIncorporatePeer(const std::string& peer_id) {
  // Update source port information
  // arriving_incorporating_peers_mutex_ is already locked in ProcessMessage()
  const IncorporatingPeerInfo& peer_info = this->incorporating_peers_[peer_id];
  const ip::udp::endpoint& peer = peer_info.peer_;
  this->UpdatePortStep(peer, peer_info.source_port_to_splitter_);
  for (uint16_t source_port_to_monitor : peer_info.source_ports_to_monitors_) {
    this->UpdatePortStep(peer, source_port_to_monitor);
  }
  // Update peer lists
  ip::udp::endpoint new_peer(peer.address(),
      peer_info.source_port_to_splitter_);
  this->incorporating_peers_[peer_id].peer_ = new_peer;
  this->incorporating_peers_[peer_id].source_port_to_splitter_ = 0;
  this->incorporating_peers_[peer_id].source_ports_to_monitors_ =
      std::vector<uint16_t>(this->max_number_of_monitors_, 0);

  // Send the updated endpoint to the existing peers
  this->SendNewPeer(peer_id, new_peer, peer_info.source_ports_to_monitors_,
      peer_info.port_step_);

  // Send all peers to the retrying peer
  try {
    this->SendTheListOfPeers2(peer_info.serve_socket_, new_peer);
  } catch (std::exception e) {
    ERROR(e.what());
  }
}

void SplitterNTS::UpdatePortStep(const ip::udp::endpoint peer,
    uint16_t source_port) {
  if (CommonNTS::Contains(this->peers_, peer)) {
    PeerInfo& peer_info = this->peers_[peer];
    // Set last known source port
    peer_info.last_source_port_ = source_port;

    this->UpdatePortStep(peer, peer_info.port_step_, source_port);
  } else {
    for (std::pair<const std::string, IncorporatingPeerInfo>& peer_iter
        : this->incorporating_peers_) {
      IncorporatingPeerInfo& peer_info = peer_iter.second;
      if (peer_info.peer_ == peer) {
        // Set last known source port
        peer_info.last_source_port_ = source_port;
        this->UpdatePortStep(peer, peer_info.port_step_, source_port);
        return;
      }
    }
    // TODO: Better error handling
    ERROR("While updating port step: Peer " << peer << " not found.");
    throw new std::exception();
  }
}

void SplitterNTS::UpdatePortStep(const ip::udp::endpoint peer,
    uint16_t& port_step, uint16_t source_port) {
  // Skip check if (measured port step is 0
  if (port_step == 0) {
    return;
  }
  if (port_step == (uint16_t)-1) {
    port_step = 0;
  }
  // Update source port information
  uint16_t port_diff = std::abs(peer.port() - source_port);
  uint16_t previous_port_step = port_step;
  port_step = gcd(previous_port_step, port_diff);
  DEBUG("Previous port step: " << previous_port_step
      << ". Port diff: " << peer.port() << " - " << source_port
      << ". New port step: " << port_step);
  if (port_step != previous_port_step) {
    LOG("Updated port step of peer " << peer << " from " << previous_port_step
        << " to " << port_step);
  }
}

void SplitterNTS::RemovePeer(const ip::udp::endpoint& peer) {
  SplitterLRS::RemovePeer(peer);

  try {
    this->peers_.erase(peer);
  } catch (std::exception e) {
    TRACE(e.what());
    // ignore
  }
}

void SplitterNTS::ModerateTheTeam() {
  while (this->alive_) {
    std::vector<char> message_bytes(this->max_message_size_);
    ip::udp::endpoint sender;
    std::string message;

    try {
      // Allow for long messages
      size_t bytes_transferred = this->ReceiveMessage(message_bytes, sender);
      DEBUG("Message length = " << bytes_transferred);
      message_bytes.resize(bytes_transferred);
      message = std::string(message_bytes.data(), bytes_transferred);
    } catch (std::exception e) {
      ERROR(e.what());
      continue;
    }

    std::istringstream msg_str(message);

    if (message.size() == 2) {
      // The peer complains about a lost chunk.

      // In this situation, the splitter counts the number of
      // complains. If this number exceeds a threshold, the
      // unsupportive peer is expelled from the
      // team.

      uint16_t lost_chunk_number = this->GetLostChunkNumber(message_bytes);
      this->ProcessLostChunk(lost_chunk_number, sender);

    } else if (message == "G") { // 'G'oodbye
      // The peer wants to leave the team.
      this->ProcessGoodbye(sender);

    } else if (message.size() == CommonNTS::kPeerIdLength) {
      // Packet is from the arriving peer itself
      std::string peer_id = message;

      LOG("Received [hello, I'm " << peer_id << "] from " << sender);

      // Send acknowledge
      this->EnqueueMessage(1, std::make_pair(message, sender));

      std::unique_lock<std::mutex> lock(arriving_incorporating_peers_mutex_);
      if (!CommonNTS::Contains(this->arriving_peers_, peer_id)) {
        DEBUG("Peer ID " << peer_id << " is not an arriving peer");
        continue;
      }

      if (this->arriving_peers_[peer_id].peer_address_ != sender.address()) {
        DEBUG("ID " << peer_id << ": peer address over TCP ("
            << this->arriving_peers_[peer_id].peer_address_ << ") and UDP ("
            << sender.address() << ") is different");
      }

      uint16_t source_port_to_splitter = sender.port();
      ArrivingPeerInfo& peer_info = this->arriving_peers_[peer_id];

      // Update peer information
      LOG("Updating peer " << peer_id);

      peer_info.source_port_to_splitter_ = source_port_to_splitter;

      LOG("source port to splitter = " << peer_info.source_port_to_splitter_)
      LOG("source ports to monitors = "
          << CommonNTS::Join(peer_info.source_ports_to_monitors_, ", "));

      if (peer_info.source_port_to_splitter_ != 0
          && !CommonNTS::Contains(peer_info.source_ports_to_monitors_, 0)) {
        // Source ports are known, incorporate the peer
        this->IncorporatePeer(peer_id);
      }

    } else if (std::find(this->peer_list_.begin(),
        this->peer_list_.begin() + this->max_number_of_monitors_, sender)
        != this->peer_list_.begin() + this->max_number_of_monitors_
        && message.size() == CommonNTS::kPeerIdLength + 2) {

      // Message is from monitor
      std::string peer_id =
          CommonNTS::ReceiveString(msg_str, CommonNTS::kPeerIdLength);
      LOG("Received forwarded hello (ID " << peer_id << ") from " << sender);

      // Send acknowledge
      this->EnqueueMessage(1, std::make_pair(message, sender));

      std::unique_lock<std::mutex> lock(arriving_incorporating_peers_mutex_);
      if (!CommonNTS::Contains(this->arriving_peers_, peer_id)) {
        DEBUG("Peer ID " << peer_id << " is not an arriving peer");
        continue;
      }
      ArrivingPeerInfo& peer_info = this->arriving_peers_[peer_id];

      uint16_t source_port_to_monitor = CommonNTS::Receive<uint16_t>(msg_str);

      // Get monitor number
      uint16_t index = CommonNTS::Index(this->peer_list_, sender);
      // Update peer information
      peer_info.source_ports_to_monitors_[index] =
          source_port_to_monitor;

      if (peer_info.source_port_to_splitter_ != 0
          && !CommonNTS::Contains(peer_info.source_ports_to_monitors_, 0)) {
        // All source ports are known, incorporate the peer
        this->IncorporatePeer(peer_id);
      }

    } else if (message.size() == CommonNTS::kPeerIdLength + 2) {

      // Received source port of a peer from another peer
      std::string peer_id =
          CommonNTS::ReceiveString(msg_str, CommonNTS::kPeerIdLength);
      LOG("Received source port of peer " << peer_id << " from " << sender);

      // Send acknowledge
      this->EnqueueMessage(1, std::make_pair(message, sender));

      const ip::udp::endpoint* peer = nullptr;
      // TODO: use std::find or boost::multi_index to optimize this loop
      for (auto peer_iter = this->peers_.begin(); peer_iter != this->peers_.end();
          ++peer_iter) {
        if (peer_id == peer_iter->second.id_) {
          peer = &peer_iter->first;
          break;
        }
      }
      if (peer == nullptr) {
        DEBUG("Peer ID " << peer_id << " unknown");
        continue;
      }

      uint16_t source_port = CommonNTS::Receive<uint16_t>(msg_str);

      // Update source port information
      this->UpdatePortStep(*peer, source_port);

    } else if (message.size() == CommonNTS::kPeerIdLength + 1) {

      // A peer succeeded or failed to be incorporated into the team
      std::string peer_id =
          CommonNTS::ReceiveString(msg_str, CommonNTS::kPeerIdLength);

      // Send acknowledge
      this->EnqueueMessage(1, std::make_pair(message, sender));

      std::unique_lock<std::mutex> lock(arriving_incorporating_peers_mutex_);
      if (!CommonNTS::Contains(this->incorporating_peers_, peer_id)) {
        DEBUG("Unknown peer " << peer_id);
        continue;
      }

      // Check sender address
      if (sender.address() !=
          this->incorporating_peers_[peer_id].peer_.address()) {
        DEBUG("Peer " << peer_id << " switched from "
            << this->incorporating_peers_[peer_id].peer_.address() << " to "
            << sender.address() << ", ignoring");
        continue;
      }

      if (message[message.size() - 1] == 'Y') {
        LOG("Peer " << peer_id << " successfully incorporated");

        // Close TCP socket
        this->incorporating_peers_[peer_id].serve_socket_->close();
        this->InsertPeer(this->incorporating_peers_[peer_id].peer_);
        this->peers_[this->incorporating_peers_[peer_id].peer_] =
            PeerInfo{peer_id,
            .port_step_ = this->incorporating_peers_[peer_id].port_step_,
            .last_source_port_ =
            this->incorporating_peers_[peer_id].last_source_port_};
        this->incorporating_peers_.erase(peer_id);

      } else {
        IncorporatingPeerInfo& peer_info = this->incorporating_peers_[peer_id];

        if (sender.port() == peer_info.peer_.port()) {
          // This could be due to a duplicate UDP packet
          DEBUG("Peer " << peer_id
              << " retries incorporation from same port, ignoring");
          continue;
        }

        LOG("Peer " << peer_id << " retries incorporation from " << sender);

        uint16_t source_port_to_splitter = sender.port();

        // Update peer information
        peer_info.source_port_to_splitter_ = source_port_to_splitter;

        if (peer_info.source_port_to_splitter_ != 0
            && !CommonNTS::Contains(peer_info.source_ports_to_monitors_, 0)) {
          // All source ports are known, incorporate the peer
          this->RetryToIncorporatePeer(peer_id);
        }
      }

    } else if (std::find(this->peer_list_.begin(),
        this->peer_list_.begin() + this->max_number_of_monitors_, sender)
        != this->peer_list_.begin() + this->max_number_of_monitors_
        && message.size() == CommonNTS::kPeerIdLength + 3) {

      // Message is from monitor
      std::string peer_id =
          CommonNTS::ReceiveString(msg_str, CommonNTS::kPeerIdLength);
      LOG("Received forwarded retry hello (ID " << peer_id << ')');

      // Send acknowledge
      this->EnqueueMessage(1, std::make_pair(message, sender));
      std::unique_lock<std::mutex> lock(arriving_incorporating_peers_mutex_);
      if (!CommonNTS::Contains(this->incorporating_peers_, peer_id)) {
        DEBUG("Peer ID " << peer_id << " is not an incorporating peer");
        continue;
      }
      IncorporatingPeerInfo& peer_info = this->incorporating_peers_[peer_id];

      uint16_t source_port_to_monitor = CommonNTS::Receive<uint16_t>(msg_str);

      // Get monitor number
      uint16_t index = CommonNTS::Index(this->peer_list_, sender);

      // Update peer information
      peer_info.source_ports_to_monitors_[index] = source_port_to_monitor;

      if (peer_info.source_port_to_splitter_ != 0
          && !CommonNTS::Contains(peer_info.source_ports_to_monitors_, 0)) {
        // All source ports are known, incorporate the peer
        this->RetryToIncorporatePeer(peer_id);
      }
    } else {
      DEBUG("Ignoring packet of length " << message.size() << " from "
          << sender);
    }
  }
}
}

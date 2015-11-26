//
//  splitter_ims.h
//  P2PSP
//
//  This code is distributed under the GNU General Public License (see
//  THE_GENERAL_GNU_PUBLIC_LICENSE.txt for extending this information).
//  Copyright (C) 2014, the P2PSP team.
//  http://www.p2psp.org
//
//  IMS: IP Multicast Set of rules.
//

#include "splitter_dbs.h"

namespace p2psp {
using namespace std;
using namespace boost;

SplitterDBS::SplitterDBS()
    : SplitterIMS(), magic_flags_(1), losses_(0, &SplitterDBS::GetHash) {
  // TODO: Check if there is a better way to replace kMcastAddr with 0.0.0.0
  mcast_addr_ = "0.0.0.0";
  max_chunk_loss_ = kMaxChunkLoss;
  monitor_number_ = kMonitorNumber;

  peer_number_ = 0;
  destination_of_chunk_.reserve(buffer_size_);
  magic_flags_ = Common::kDBS;

  LOG("max_chunk_loss = " << max_chunk_loss_);
  LOG("mcast_addr = " << mcast_addr_);
  LOG("Initialized");
}

SplitterDBS::~SplitterDBS() {}

void SplitterDBS::SendMagicFlags(
    std::shared_ptr<boost::asio::ip::tcp::socket> &peer_serve_socket) {
  char message[1];

  message[0] = magic_flags_;
  peer_serve_socket->send(asio::buffer(message));
  LOG("Magic flags = " << bitset<8>(message[0]));
}

void SplitterDBS::SendTheListSize(
    std::shared_ptr<boost::asio::ip::tcp::socket> &peer_serve_socket) {
  char message[2];

  LOG("Sending the number of monitors " << monitor_number_);
  (*(uint16_t *)&message) = htons(monitor_number_);
  peer_serve_socket->send(asio::buffer(message));

  LOG("Sending a list of peers of size " << to_string(peer_list_.size()));
  (*(uint16_t *)&message) = htons(peer_list_.size());
  peer_serve_socket->send(asio::buffer(message));
}

void SplitterDBS::SendTheListOfPeers(
    std::shared_ptr<boost::asio::ip::tcp::socket> &peer_serve_socket) {
  SendTheListSize(peer_serve_socket);

  // TODO: Find a __debug__ flag in c++
  int counter = 0;
  // End TODO

  char message[6];
  in_addr addr;

  for (std::vector<asio::ip::udp::endpoint>::iterator it = peer_list_.begin();
       it != peer_list_.end(); ++it) {
    inet_aton(it->address().to_string().c_str(), &addr);
    (*(in_addr *)&message) = addr;
    (*(uint16_t *)(message + 4)) = htons(it->port());
    peer_serve_socket->send(asio::buffer(message));

    // TODO: Find a __debug__ flag in c++
    LOG(to_string(counter) << ", (" << it->address().to_string() << ", "
                           << to_string(it->port()) << ")");
    counter++;
    // End TODO
  }
}

void SplitterDBS::SendThePeerEndpoint(
    std::shared_ptr<boost::asio::ip::tcp::socket> &peer_serve_socket) {
  asio::ip::tcp::endpoint peer_endpoint = peer_serve_socket->remote_endpoint();

  char message[6];
  in_addr addr;
  inet_aton(peer_endpoint.address().to_string().c_str(), &addr);
  (*(in_addr *)&message) = addr;
  (*(uint16_t *)(message + 4)) = htons(peer_endpoint.port());
  peer_serve_socket->send(asio::buffer(message));
}

void SplitterDBS::SendConfiguration(
    std::shared_ptr<boost::asio::ip::tcp::socket> &sock) {
  SplitterIMS::SendConfiguration(sock);
  SendThePeerEndpoint(sock);
  SendMagicFlags(sock);
}

void SplitterDBS::InsertPeer(boost::asio::ip::udp::endpoint peer) {
  if (find(peer_list_.begin(), peer_list_.end(), peer) == peer_list_.end()) {
    peer_list_.push_back(peer);
  }

  losses_[peer] = 0;
  LOG("Inserted peer (" << peer.address().to_string() << ", "
                        << to_string(peer.port()) << ")");
}

void SplitterDBS::HandleAPeerArrival(
    std::shared_ptr<boost::asio::ip::tcp::socket> serve_socket) {
  /* In the DBS, the splitter sends to the incomming peer the
   list of peers. Notice that the transmission of the list of
   peers (something that could need some time if the team is
   big or if the peer is slow) is done in a separate thread. This
   helps to avoid DoS (Denial of Service) attacks.
   */

  asio::ip::tcp::endpoint incoming_peer = serve_socket->remote_endpoint();

  LOG("Accepted connection from peer ("
      << incoming_peer.address().to_string() << ", "
      << to_string(incoming_peer.port()) << ")");

  SendConfiguration(serve_socket);
  SendTheListOfPeers(serve_socket);
  serve_socket->close();
  InsertPeer(boost::asio::ip::udp::endpoint(incoming_peer.address(),
                                            incoming_peer.port()));

  // TODO: In original code, incoming_peer is returned, but is not used
}

size_t SplitterDBS::ReceiveMessage(std::vector<char> &message,
                                   boost::asio::ip::udp::endpoint &endpoint) {
  system::error_code ec;

  size_t bytes_transferred =
      team_socket_.receive_from(asio::buffer(message), endpoint, 0, ec);

  if (ec) {
    LOG("Unexepected error: " << ec.message());
  }

  return bytes_transferred;
}

void SplitterDBS::IncrementUnsupportivityOfPeer(
    boost::asio::ip::udp::endpoint peer) {
  bool peerExists = true;
  std::stringstream ss;
  ss << "(" << peer.address().to_string() + ", " + to_string(peer.port()) + ")";

  try {
    losses_[peer] += 1;
  } catch (std::exception e) {
    LOG("The unsupportive peer " << ss.str() << " does not exist!");
    peerExists = false;
  }

  if (peerExists) {
    LOG(ss.str() << " has lost " << to_string(losses_[peer]) << " chunks");

    if (losses_[peer] > max_chunk_loss_) {
      // TODO: Check this condition in original code, is it correct?
      if (find(peer_list_.begin(), peer_list_.begin() + monitor_number_,
               peer) == peer_list_.end()) {
        LOG(ss.str() << " removed");
        RemovePeer(peer);
      }
    }
  }
}

void SplitterDBS::ProcessLostChunk(int lost_chunk_number,
                                   boost::asio::ip::udp::endpoint sender) {
  asio::ip::udp::endpoint destination = GetLosser(lost_chunk_number);
  std::stringstream ssSender;
  ssSender << "("
           << sender.address().to_string() + ", " + to_string(sender.port()) +
                  ")";
  std::stringstream ssDestination;
  ssDestination << "("
                << destination.address().to_string() + ", " +
                       to_string(destination.port()) + ")";

  // TODO: Find a __debug__ flag in c++
  LOG(ssSender.str() << " complains about lost chunk "
                     << to_string(lost_chunk_number) << " sent to "
                     << ssDestination.str());
  if (find(peer_list_.begin() + monitor_number_, peer_list_.end(),
           destination) != peer_list_.end()) {
    LOG("Lost chunk index = " << lost_chunk_number);
  }
  // End TODO

  IncrementUnsupportivityOfPeer(destination);
}

uint16_t SplitterDBS::GetLostChunkNumber(std::vector<char> &message) {
  // TODO: Check if this is totally correct
  return ntohs(*(uint16_t *)message.data());
}

asio::ip::udp::endpoint SplitterDBS::GetLosser(int lost_chunk_number) {
  return destination_of_chunk_[lost_chunk_number % buffer_size_];
}

void SplitterDBS::RemovePeer(asio::ip::udp::endpoint peer) {
  try {
    peer_list_.erase(remove(peer_list_.begin(), peer_list_.end(), peer),
                     peer_list_.end());
    peer_number_--;

    losses_.erase(peer);

  } catch (std::exception e) {
    LOG("Error: " << e.what());
  }
}

void SplitterDBS::ProcessGoodbye(boost::asio::ip::udp::endpoint peer) {
  LOG("Received 'goodbye' from " << peer);

  // TODO: stdout flush?

  RemovePeer(peer);
}

void SplitterDBS::ModerateTheTeam() {
  std::vector<char> message(2);
  asio::ip::udp::endpoint sender;

  while (alive_) {
    size_t bytes_transferred = ReceiveMessage(message, sender);

    if (bytes_transferred == 2) {
      /*
       The peer complains about a lost chunk.

       In this situation, the splitter counts the number of
       complains. If this number exceeds a threshold, the
       unsupportive peer is expelled from the
       team.
       */

      uint16_t lost_chunk_number = GetLostChunkNumber(message);
      ProcessLostChunk(lost_chunk_number, sender);

    } else {
      /*
       The peer wants to leave the team.

       A !2-length payload means that the peer wants to go
       away.
       */

      ProcessGoodbye(sender);
    }
  }
}

void SplitterDBS::SetupTeamSocket() {
  system::error_code ec;
  asio::ip::udp::endpoint endpoint(asio::ip::udp::v4(), port_);

  team_socket_.open(asio::ip::udp::v4());

  asio::socket_base::reuse_address reuseAddress(true);
  team_socket_.set_option(reuseAddress, ec);
  team_socket_.bind(endpoint);

  if (ec) {
    LOG("Error: " << ec.message());
  }
}

void SplitterDBS::ResetCounters() {
  unordered::unordered_map<asio::ip::udp::endpoint, int>::iterator it;
  for (it = losses_.begin(); it != losses_.end(); ++it) {
    losses_[it->first] = it->second / 2;
  }
}

void SplitterDBS::ResetCountersThread() {
  while (alive_) {
    ResetCounters();

    // TODO: Use Common.COUNTERS_TIMING instead of a hard coded number
    this_thread::sleep(posix_time::milliseconds(1000));
  }
}

void SplitterDBS::ComputeNextPeerNumber() {
  peer_number_ = (peer_number_ + 1) % peer_list_.size();
}

void SplitterDBS::Run() {
  ReceiveTheHeader();

  /* A DBS splitter runs 4 threads. The main one and the
   "handle_arrivals" thread are equivalent to the daemons used
   by the IMS splitter. "moderate_the_team" and
   "reset_counters_thread" are new.
   */

  LOG("waiting for the monitor peers ...");

  std::shared_ptr<asio::ip::tcp::socket> connection =
      make_shared<asio::ip::tcp::socket>(boost::ref(io_service_));
  acceptor_.accept(*connection);
  HandleAPeerArrival(connection);

  // Threads
  thread t1(bind(&SplitterIMS::HandleArrivals, this));
  thread t2(bind(&SplitterDBS::ModerateTheTeam, this));
  thread t3(bind(&SplitterDBS::ResetCountersThread, this));

  vector<char> message(sizeof(uint16_t) + chunk_size_);
  asio::ip::udp::endpoint peer;

  while (alive_) {
    asio::streambuf chunk;
    size_t bytes_transferred = ReceiveChunk(chunk);
    try {
      peer = peer_list_.at(peer_number_);

      (*(uint16_t *)message.data()) = htons(chunk_number_);

      copy(asio::buffer_cast<const char *>(chunk.data()),
           asio::buffer_cast<const char *>(chunk.data()) + chunk.size(),
           message.data() + sizeof(uint16_t));

      SendChunk(message, peer);

      destination_of_chunk_[chunk_number_ % buffer_size_] = peer;
      chunk_number_ = (chunk_number_ + 1) % Common::kMaxChunkNumber;
      ComputeNextPeerNumber();
    } catch (const std::out_of_range &oor) {
      LOG("The monitor peer has died!");
    }

    chunk.consume(bytes_transferred);
  }
}

void SplitterDBS::Start() {
  LOG("Start");
  thread_.reset(new boost::thread(boost::bind(&SplitterDBS::Run, this)));
}
}
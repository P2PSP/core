//
//  splitter_dbs.cc
//  P2PSP
//
//  This code is distributed under the GNU General Public License (see
//  THE_GENERAL_GNU_PUBLIC_LICENSE.txt for extending this information).
//  Copyright (C) 2016, the P2PSP team.
//  http://www.p2psp.org
//
//  DBS: Data Broadcasting Set of rules
//

#include "splitter_dbs.h"
#include "../util/trace.h"

namespace p2psp {
  using namespace std;
  using namespace boost;

  const int SplitterDBS::kMaxChunkLoss =
      32;  // Chunk losses threshold to reject a peer from the team
  const int SplitterDBS::kMonitorNumber = 1;

  SplitterDBS::SplitterDBS() : SplitterIMS(), losses_(0, &SplitterDBS::GetHash) {
    // TODO: Check if there is a better way to replace kMcastAddr with 0.0.0.0
    mcast_addr_ = "0.0.0.0";
    max_number_of_chunk_loss_ = kMaxChunkLoss;
    max_number_of_monitors_ = kMonitorNumber;

    peer_number_ = 0;
    destination_of_chunk_.reserve(buffer_size_);
    magic_flags_ = Common::kDBS;

    TRACE("max_number_of_chunk_loss = " << max_number_of_chunk_loss_);
    TRACE("mcast_addr = " << mcast_addr_);
    TRACE("Initialized DBS");
  }

  SplitterDBS::~SplitterDBS() {}

  char SplitterDBS::GetMagicFlags() {
    return magic_flags_;
  }

  void SplitterDBS::SendMagicFlags(
                                   const std::shared_ptr<boost::asio::ip::tcp::socket> &peer_serve_socket) {
    char message[1];

    message[0] = magic_flags_;
    peer_serve_socket->send(asio::buffer(message));
    LOG("Magic flags = " << bitset<8>(message[0]));
  }

  void SplitterDBS::SendTheListSize(
                                    const std::shared_ptr<boost::asio::ip::tcp::socket> &peer_serve_socket) {
    char message[2];

    TRACE("Sending the number of monitors " << max_number_of_monitors_);
    (*(uint16_t *)&message) = htons(max_number_of_monitors_);
    peer_serve_socket->send(asio::buffer(message));

    TRACE("Sending a list of peers of size " << to_string(peer_list_.size()));
    (*(uint16_t *)&message) = htons(peer_list_.size());
    peer_serve_socket->send(asio::buffer(message));
  }

  void SplitterDBS::SendTheListOfPeers(
                                       const std::shared_ptr<boost::asio::ip::tcp::socket> &peer_serve_socket) {
    SendTheListSize(peer_serve_socket);

    int counter = 0;

    char message[6];
    in_addr addr;

    for (std::vector<asio::ip::udp::endpoint>::iterator it = peer_list_.begin();
         it != peer_list_.end(); ++it) {
      inet_aton(it->address().to_string().c_str(), &addr);
      (*(in_addr *)&message) = addr;
      (*(uint16_t *)(message + 4)) = htons(it->port());
      peer_serve_socket->send(asio::buffer(message));

      TRACE(to_string(counter) << ", " << *it);
      counter++;
    }
  }

  void SplitterDBS::SendThePeerEndpoint(
                                        const std::shared_ptr<boost::asio::ip::tcp::socket> &peer_serve_socket) {
    asio::ip::tcp::endpoint peer_endpoint = peer_serve_socket->remote_endpoint();

    char message[6];
    in_addr addr;
    inet_aton(peer_endpoint.address().to_string().c_str(), &addr);
    (*(in_addr *)&message) = addr;
    (*(uint16_t *)(message + 4)) = htons(peer_endpoint.port());
    peer_serve_socket->send(asio::buffer(message));
  }

  void SplitterDBS::SendConfiguration(
                                      const std::shared_ptr<boost::asio::ip::tcp::socket> &sock) {
    SplitterIMS::SendConfiguration(sock);
    SendThePeerEndpoint(sock);
    SendMagicFlags(sock);
  }

  void SplitterDBS::InsertPeer(const boost::asio::ip::udp::endpoint &peer) {
    if (find(peer_list_.begin(), peer_list_.end(), peer) != peer_list_.end()) {
      peer_list_.erase(find(peer_list_.begin(), peer_list_.end(), peer));
    }
    peer_list_.push_back(peer);
    losses_[peer] = 0;
    TRACE("Inserted peer " << peer);
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

    TRACE("Accepted connection from peer " << incoming_peer);

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
      ERROR("Unexepected error: " << ec.message());
    }

    return bytes_transferred;
  }

  void SplitterDBS::IncrementUnsupportivityOfPeer(
                                                  const boost::asio::ip::udp::endpoint &peer) {
    bool peerExists = true;

    try {
      losses_[peer] += 1;
    } catch (std::exception e) {
      TRACE("The unsupportive peer " << peer << " does not exist!");
      peerExists = false;
    }

    if (peerExists) {
      TRACE("" << peer << " has lost " << to_string(losses_[peer]) << " chunks");

      if (losses_[peer] > max_number_of_chunk_loss_) {
        TRACE("" << peer << " removed");
        RemovePeer(peer);
      }
    }
  }

  void SplitterDBS::ProcessLostChunk(
                                     int lost_chunk_number, const boost::asio::ip::udp::endpoint &sender) {
    asio::ip::udp::endpoint destination = GetLosser(lost_chunk_number);

    TRACE("" << sender << " complains about lost chunk "
          << to_string(lost_chunk_number) << " sent to " << destination);

    if (find(peer_list_.begin() + max_number_of_monitors_, peer_list_.end(),
             destination) != peer_list_.end()) {
      TRACE("Lost chunk index = " << lost_chunk_number);
    }

    IncrementUnsupportivityOfPeer(destination);
  }

  uint16_t SplitterDBS::GetLostChunkNumber(const std::vector<char> &message) {
    // TODO: Check if this is totally correct
    return ntohs(*(uint16_t *)message.data());
  }

  asio::ip::udp::endpoint SplitterDBS::GetLosser(int lost_chunk_number) {
    return destination_of_chunk_[lost_chunk_number % buffer_size_];
  }

  void SplitterDBS::RemovePeer(const asio::ip::udp::endpoint &peer) {
    // If peer_list_ contains the peer, remove it
    if (find(peer_list_.begin(), peer_list_.end(), peer) != peer_list_.end()) {
      peer_list_.erase(remove(peer_list_.begin(), peer_list_.end(), peer),
                       peer_list_.end());

      // In order to avoid negative peer_number_ value while peer_list_ still
      // contains any peer (in Python this is not necessary because negative
      // indexes can be used)
      if (peer_list_.size() > 0) {
        peer_number_ = (peer_number_ - 1) % peer_list_.size();
      } else {
        peer_number_--;
      }
    }

    losses_.erase(peer);
  }

  void SplitterDBS::ProcessGoodbye(const boost::asio::ip::udp::endpoint &peer) {
    TRACE("Received 'goodbye' from " << peer);

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
    asio::ip::udp::endpoint endpoint(asio::ip::udp::v4(), team_port_);

    team_socket_.open(asio::ip::udp::v4());

    asio::socket_base::reuse_address reuseAddress(true);
    team_socket_.set_option(reuseAddress, ec);
    team_socket_.bind(endpoint);

    if (ec) {
      ERROR(ec.message());
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
      this_thread::sleep(posix_time::seconds(Common::kCountersTiming));
    }
  }

  void SplitterDBS::ComputeNextPeerNumber(asio::ip::udp::endpoint &peer) {
    peer_number_ = (peer_number_ + 1) % peer_list_.size();
  }

  void SplitterDBS::Run() {
    ReceiveTheHeader();

    /* A DBS splitter runs 4 threads. The main one and the
       "handle_arrivals" thread are equivalent to the daemons used
       by the IMS splitter. "moderate_the_team" and
       "reset_counters_thread" are new.
    */

    TRACE("waiting for the monitor peers ...");

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
        ComputeNextPeerNumber(peer);
      } catch (const std::out_of_range &oor) {
        TRACE("The monitor peer has died!");
        exit(-1);
      }

      chunk.consume(bytes_transferred);
    }
  }

  std::vector<boost::asio::ip::udp::endpoint> SplitterDBS::GetPeerList() {
    return peer_list_;
  }

  int SplitterDBS::GetLoss(const boost::asio::ip::udp::endpoint &peer) {
    return losses_[peer];
  }

  void SplitterDBS::SetMaxNumberOfChunkLoss(int max_number_of_chunk_loss) {
    max_number_of_chunk_loss_ = max_number_of_chunk_loss;
  }

  int SplitterDBS::GetMaxNumberOfChunkLoss() {
    return max_number_of_chunk_loss_;
  }

  void SplitterDBS::SetMaxNumberOfMonitors(int max_number_of_monitors) {
    max_number_of_monitors_ = max_number_of_monitors;
  }

  int SplitterDBS::GetMaxNumberOfMonitors() {
    return max_number_of_monitors_;
  }

  void SplitterDBS::Start() {
    TRACE("Start");
    thread_.reset(new boost::thread(boost::bind(&SplitterDBS::Run, this)));
  }

  int SplitterDBS::GetDefaultMaxNumberOfChunkLoss() {
    return kMaxChunkLoss;
  }

  int SplitterDBS::GetDefaultMaxNumberOfMonitors() {
    return kMonitorNumber;
  }
}

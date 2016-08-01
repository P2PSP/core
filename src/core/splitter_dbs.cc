//
//  splitter_dbs.cc -- Data Broadcasting Set of rules
//
//  This code is distributed under the GNU General Public License (see
//  THE_GENERAL_GNU_PUBLIC_LICENSE.txt for extending this information).
//  Copyright (C) 2016, the P2PSP team.
//  http://www.p2psp.org
//

#include "splitter_dbs.h"
#include "../util/trace.h"

namespace p2psp {
  using namespace std;
  using namespace boost;

  const int Splitter_DBS::kMaxChunkLoss = 32;  // Chunk losses threshold to reject a peer from the team
  const int Splitter_DBS::kNumberOfMonitors = 1;

  Splitter_DBS::Splitter_DBS() : Splitter_core(), losses_(0, &Splitter_DBS::GetHash) {
    // TODO: Check if there is a better way to replace kMcastAddr with 0.0.0.0
    max_number_of_chunk_loss_ = kMaxChunkLoss;
    number_of_monitors_ = kNumberOfMonitors;

    peer_number_ = 0;
    destination_of_chunk_.reserve(buffer_size_);
#if defined __DEBUG__ || defined __PARAMS__
    TRACE("max_number_of_chunk_loss = "
	  << max_number_of_chunk_loss_);
#endif
#if defined __DEBUG__ || defined __SORS__
    TRACE("Splitter_DBS constructor");
#endif
  }

  Splitter_DBS::~Splitter_DBS() {}

  void Splitter_DBS::SendTheNumberOfPeers(const std::shared_ptr<boost::asio::ip::tcp::socket> &peer_serve_socket) {
    char message[2];

#if defined __DEBUG__ || defined __CHURN__
    TRACE("Sending the number of monitors "
	  << number_of_monitors_);
#endif
    (*(uint16_t *)&message) = htons(number_of_monitors_);
    peer_serve_socket->send(asio::buffer(message));
    
#if defined __DEBUG__ || defined __CHURN__
    TRACE("Sending a list of peers of size "
	  << to_string(peer_list_.size()));
#endif
    (*(uint16_t *)&message) = htons(peer_list_.size());
    peer_serve_socket->send(asio::buffer(message));
  }

  void Splitter_DBS::SendTheListOfPeers(const std::shared_ptr<boost::asio::ip::tcp::socket> &peer_serve_socket) {
    SendTheNumberOfPeers(peer_serve_socket);

    int counter = 0;
    char message[6];
    in_addr addr;

#if defined __DEBUG__ || defined __CHURN__
    TRACE("Peer list length = "
	  << peer_list_.size());
#endif
    
    for (std::vector<asio::ip::udp::endpoint>::iterator it = peer_list_.begin();
         it != peer_list_.end(); ++it) {
      inet_aton(it->address().to_string().c_str(), &addr);
      (*(in_addr *)&message) = addr;
      (*(uint16_t *)(message + 4)) = htons(it->port());
      peer_serve_socket->send(asio::buffer(message));

#if defined __DEBUG__ || defined __CHURN__
      TRACE(to_string(counter)
	    << ", "
	    << *it);
#endif      
      counter++;
    }
  }

  /*void Splitter_DBS::SendThePeerEndpoint(const std::shared_ptr<boost::asio::ip::tcp::socket> &peer_serve_socket) {
    asio::ip::tcp::endpoint peer_endpoint = peer_serve_socket->remote_endpoint();

    char message[6];
    in_addr addr;
    inet_aton(peer_endpoint.address().to_string().c_str(), &addr);
    (*(in_addr *)&message) = addr;
    (*(uint16_t *)(message + 4)) = htons(peer_endpoint.port());
    peer_serve_socket->send(asio::buffer(message));
    }*/

  void Splitter_DBS::InsertPeer(const boost::asio::ip::udp::endpoint &peer) {
    if (find(peer_list_.begin(), peer_list_.end(), peer) != peer_list_.end()) {
      peer_list_.erase(find(peer_list_.begin(), peer_list_.end(), peer));
    }
    peer_list_.push_back(peer);
    losses_[peer] = 0;
#if defined __DEBUG__ || defined __CHURN__
    TRACE("Inserted peer "
	  << peer);
#endif
  }

  void Splitter_DBS::SendConfiguration(const std::shared_ptr<boost::asio::ip::tcp::socket> &sock) {
#if defined __DEBUG__ || defined __CHURN__
    TRACE("Sending Configuration");
#endif
    Splitter_core::SendConfiguration(sock);
    SendTheListOfPeers(sock);

    //SendThePeerEndpoint(sock);
  }

  void Splitter_DBS::HandleAPeerArrival(std::shared_ptr<boost::asio::ip::tcp::socket> serve_socket) {
    /* In the DBS, the splitter sends to the incomming peer the
       list of peers. Notice that the transmission of the list of
       peers (something that could need some time if the team is
       big or if the peer is slow) is done in a separate thread. This
       helps to avoid DoS (Denial of Service) attacks.
    */

    asio::ip::tcp::endpoint incoming_peer = serve_socket->remote_endpoint();

#if defined __DEBUG__ || defined __CHURN__
    TRACE("Accepted connection from peer "
	  << incoming_peer);
#endif
    
    SendConfiguration(serve_socket);
    //SendTheListOfPeers(serve_socket);
    ReceiveReadyForReceivingChunks(serve_socket);
    serve_socket->close();
    boost::asio::ip::udp::endpoint incoming_peer_udp(incoming_peer.address(), incoming_peer.port());
    InsertPeer(incoming_peer_udp);

    // TODO: In original code, incoming_peer is returned, but is not used
  }

  size_t Splitter_DBS::ReceiveMessage(std::vector<char> &message, boost::asio::ip::udp::endpoint &endpoint) {
    system::error_code ec;

    size_t bytes_transferred =
      team_socket_.receive_from(asio::buffer(message), endpoint, 0, ec);

    if (ec) {
      ERROR("Unexepected error: "
	    << ec.message());
    }

    return bytes_transferred;
  }

  void Splitter_DBS::IncrementPeerUnsupportivity(const boost::asio::ip::udp::endpoint &peer) {
    bool peerExists = true;

    try {
      losses_[peer] += 1;
    } catch (std::exception e) {
      TRACE("The unsupportive peer "
	    << peer
	    << " does not exist!");
      peerExists = false;
    }

    if (peerExists) {

#if defined __DEBUG__ || defined __LOST_CHUNKS__
      TRACE(""
	    << peer
	    << " has lost "
	    << to_string(losses_[peer])
	    << " chunks");
#endif
      
      if (losses_[peer] > max_number_of_chunk_loss_) {

#if defined __DEBUG__ || defined __LOST_CHUNKS__
	TRACE(""
	      << peer
	      << " removed by unsupportive");
#endif
	
        RemovePeer(peer);
      }
    }
  }

  void Splitter_DBS::ProcessLostChunk(int lost_chunk_number, const boost::asio::ip::udp::endpoint &sender) {
    asio::ip::udp::endpoint destination = GetLosser(lost_chunk_number);

#if defined __DEBUG__ || defined __LOST_CHUNKS__
    TRACE(""
	  << sender
	  << " complains about lost chunk "
          << to_string(lost_chunk_number)
	  << " sent to "
	  << destination);

    if (find(peer_list_.begin() + number_of_monitors_, peer_list_.end(), destination) != peer_list_.end()) {
      TRACE("Lost chunk index = "
	    << lost_chunk_number);
    }
#endif

    IncrementPeerUnsupportivity(destination);
  }

  uint16_t Splitter_DBS::GetLostChunkNumber(const std::vector<char> &message) {
    // TODO: Check if this is totally correct
    return ntohs(*(uint16_t *)message.data());
  }

  asio::ip::udp::endpoint Splitter_DBS::GetLosser(int lost_chunk_number) {
    return destination_of_chunk_[lost_chunk_number % buffer_size_];
  }

  void Splitter_DBS::RemovePeer(const asio::ip::udp::endpoint &peer) {
    // If peer_list_ contains the peer, remove it
    if (find(peer_list_.begin(), peer_list_.end(), peer) != peer_list_.end()) {
      peer_list_.erase(remove(peer_list_.begin(), peer_list_.end(), peer), peer_list_.end());

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

  void Splitter_DBS::ProcessGoodbye(const boost::asio::ip::udp::endpoint &peer) {
#if defined __DEBUG__ || defined __CHURN__
    TRACE("Received 'goodbye' from "
	  << peer);
#endif
    
    // TODO: stdout flush?

    if (find(outgoing_peer_list_.begin(), outgoing_peer_list_.end(),peer) == outgoing_peer_list_.end()){
      if (find(peer_list_.begin(), peer_list_.end(), peer) != peer_list_.end()){
	outgoing_peer_list_.push_back(peer);
#if defined __DEBUG__ || defined __CHURN__
	TRACE("Marked for deletion: " << peer);
#endif
      }
    }


    //SayGoodbye(peer);
    //RemovePeer(peer);

  }

  void Splitter_DBS::SayGoodbye(const boost::asio::ip::udp::endpoint &peer) {
    std::string goodbye("G");
    team_socket_.send_to(boost::asio::buffer(goodbye), peer);

#if defined __DEBUG__ || defined __CHURN__
    TRACE("[Goodbye] sent to "
	  << "("
	  << peer.address().to_string()
	  << ","
	  << std::to_string(peer.port())
	  << ")");
#endif
    
  }

  void Splitter_DBS::ModerateTheTeam() {
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

  void Splitter_DBS::SetupTeamSocket() {
    system::error_code ec;
    asio::ip::udp::endpoint endpoint(asio::ip::udp::v4(), splitter_port_);

    team_socket_.open(asio::ip::udp::v4());

    asio::socket_base::reuse_address reuseAddress(true);
    team_socket_.set_option(reuseAddress, ec);
    team_socket_.bind(endpoint);

    if (ec) {
      ERROR(ec.message());
    }
  }

  void Splitter_DBS::ResetCounters() {
    unordered::unordered_map<asio::ip::udp::endpoint, int>::iterator it;
    for (it = losses_.begin(); it != losses_.end(); ++it) {
      losses_[it->first] = it->second / 2;
    }
  }

  void Splitter_DBS::ResetCountersThread() {
    while (alive_) {
      ResetCounters();
      this_thread::sleep(posix_time::seconds(Common::kCountersTiming));
    }
  }

  void Splitter_DBS::ComputeNextPeerNumber(asio::ip::udp::endpoint &peer) {
    if (peer_list_.size() > 0)
      peer_number_ = (peer_number_ + 1) % peer_list_.size();
  }

  void Splitter_DBS::Run() {
    ConfigureSockets();
    RequestTheVideoFromTheSource();

    /* A DBS splitter runs 4 threads. The main one and the
       "handle_arrivals" thread are equivalent to the daemons used
       by the IMS splitter. "moderate_the_team" and
       "reset_counters_thread" are new.
    */

#if defined __DEBUG__ || defined __CHURN__
    TRACE("waiting for the monitor peers ...");
#endif
    
    std::shared_ptr<asio::ip::tcp::socket> connection = make_shared<asio::ip::tcp::socket>(boost::ref(io_service_));
    acceptor_.accept(*connection);
    HandleAPeerArrival(connection);

    // Threads
    thread t1(bind(&Splitter_core::HandleArrivals, this));
    thread t2(bind(&Splitter_DBS::ModerateTheTeam, this));
    thread t3(bind(&Splitter_DBS::ResetCountersThread, this));

    vector<char> message(sizeof(uint16_t) + chunk_size_);
    asio::ip::udp::endpoint peer;

    while (alive_) {
      asio::streambuf chunk;
      size_t bytes_transferred = ReceiveChunk(chunk);
      try {
        peer = peer_list_.at(peer_number_);

        (*(uint16_t *)message.data()) = htons(chunk_number_);

        copy(asio::buffer_cast<const char *>(chunk.data()),
             asio::buffer_cast<const char *>(chunk.data()) + chunk.size(), message.data() + sizeof(uint16_t));

        SendChunk(message, peer);

        destination_of_chunk_[chunk_number_ % buffer_size_] = peer;
        chunk_number_ = (chunk_number_ + 1) % Common::kMaxChunkNumber;
        ComputeNextPeerNumber(peer);
      } catch (const std::out_of_range &oor) {
        ERROR("The monitor peer has died!");
        exit(-1);
      }

      if (peer_number_ == 0){
	for (unsigned int i=0; i<outgoing_peer_list_.size(); i++){
	  SayGoodbye(outgoing_peer_list_[i]);
	  RemovePeer(outgoing_peer_list_[i]);
	}
	outgoing_peer_list_.clear();
      }
      
      chunk.consume(bytes_transferred);
    }
  }

  std::vector<boost::asio::ip::udp::endpoint> Splitter_DBS::GetPeerList() {
    return peer_list_;
  }

  int Splitter_DBS::GetLoss(const boost::asio::ip::udp::endpoint &peer) {
    return losses_[peer];
  }

  void Splitter_DBS::SetMaxNumberOfChunkLoss(int max_number_of_chunk_loss) {
    max_number_of_chunk_loss_ = max_number_of_chunk_loss;
  }

  int Splitter_DBS::GetMaxNumberOfChunkLoss() {
    return max_number_of_chunk_loss_;
  }

  int Splitter_DBS::GetDefaultMaxNumberOfChunkLoss() {
    return kMaxChunkLoss;
  }

  void Splitter_DBS::SetNumberOfMonitors(int number_of_monitors) {
    number_of_monitors_ = number_of_monitors;
  }

  int Splitter_DBS::GetNumberOfMonitors() {
    return number_of_monitors_;
  }

  int Splitter_DBS::GetDefaultNumberOfMonitors() {
    return kNumberOfMonitors;
  }

  void Splitter_DBS::Start() {
    thread_.reset(new boost::thread(boost::bind(&Splitter_DBS::Run, this)));
  }

}

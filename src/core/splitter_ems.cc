//
//  splitter_ems.cc
//  P2PSP
//
//  This code is distributed under the GNU General Public License (see
//  THE_GENERAL_GNU_PUBLIC_LICENSE.txt for extending this information).
//  Copyright (C) 2016, the P2PSP team.
//  http://www.p2psp.org
//
//   EMS: Endpoint Masquerading Set of Rules
//

#include "splitter_ems.h"
#include "../util/trace.h"

namespace p2psp {
  using namespace std;
  using namespace boost;


  SplitterEMS::SplitterEMS() /*: SplitterIMS(), losses_(0, &SplitterEMS::GetHash)*/ {
    // TODO: Check if there is a better way to replace kMcastAddr with 0.0.0.0
    /*mcast_addr_ = "0.0.0.0";
    max_number_of_chunk_loss_ = kMaxChunkLoss;
    max_number_of_monitors_ = kMonitorNumber;

    peer_number_ = 0;
    destination_of_chunk_.reserve(buffer_size_);
    magic_flags_ = Common::kEMS;

    TRACE("max_number_of_chunk_loss = " << max_number_of_chunk_loss_);
    TRACE("mcast_addr = " << mcast_addr_);
    TRACE("Initialized EMS");*/
  }

  SplitterEMS::~SplitterEMS() {}



  void SplitterEMS::SendTheListOfPeers(
                                       const std::shared_ptr<boost::asio::ip::tcp::socket> &peer_serve_socket) {
    SendTheListSize(peer_serve_socket);

    asio::ip::address target_address = peer_serve_socket->remote_endpoint().address();
    int counter = 0;

    char message[6];
    in_addr addr;

    for (std::vector<asio::ip::udp::endpoint>::iterator it = peer_list_.begin();
         it != peer_list_.end(); ++it) {

      asio::ip::udp::endpoint peer_endpoint = *it;
      if (it->address() == target_address) {
        peer_endpoint = peer_pairs_[*it];
      }

      inet_aton(peer_endpoint.address().to_string().c_str(), &addr);
      (*(in_addr *)&message) = addr;
      (*(uint16_t *)(message + 4)) = htons(peer_endpoint.port());
      peer_serve_socket->send(asio::buffer(message));

      TRACE(to_string(counter) << ", " << *it);
      counter++;
    }
  }

  //TODO:implement after deciding on message format
  void SplitterEMS::InsertPeer(const boost::asio::ip::udp::endpoint &peer) {
    if (find(peer_list_.begin(), peer_list_.end(), peer) != peer_list_.end()) {
      peer_list_.erase(find(peer_list_.begin(), peer_list_.end(), peer));
    }

    peer_list_.push_back(peer);
    //peer_pairs_.insert(peer);
    losses_[peer] = 0;

    TRACE("Inserted peer " << peer);
  }


/* TODO::handle arrival after deciding on message format of hello from peer*/
  void SplitterEMS::HandleAPeerArrival(
                                       std::shared_ptr<boost::asio::ip::tcp::socket> serve_socket) {
    /* In the DB_S, the splitter sends to the incomming peer the
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

  void SplitterEMS::ProcessLostChunk(
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

  //TODO:corrrect type mismatch with GetHash
  void SplitterEMS::RemovePeer(const asio::ip::udp::endpoint &peer) {
    // If peer_list_ contains the peer, remove it
    if (find(peer_list_.begin(), peer_list_.end(), peer) != peer_list_.end()) {
      peer_list_.erase(remove(peer_list_.begin(), peer_list_.end(), peer),
                       peer_list_.end());


      //remove peer from public-private hashtable
      //peer_pairs_.erase(GetHash(peer));

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


  void SplitterEMS::Run() {
    ReceiveTheHeader();

    /* A DB_S splitter runs 4 threads. The main one and the
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
    thread t2(bind(&SplitterEMS::ModerateTheTeam, this));
    thread t3(bind(&SplitterEMS::ResetCountersThread, this));

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

  std::vector<boost::asio::ip::udp::endpoint> SplitterEMS::GetPeerList() {
    //TODO:investigate if private/public address should be returned...i think public?
    return peer_list_;
  }

  void SplitterEMS::Start() {
    TRACE("Start");
    thread_.reset(new boost::thread(boost::bind(&SplitterEMS::Run, this)));
  }

}

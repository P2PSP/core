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


  SplitterEMS::SplitterEMS() {

    magic_flags_ = Common::kEMS;

    TRACE("Initialized EMS");
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

    //recieve local ip of peer
    TRACE("Accepted connection from peer " << incoming_peer);
    boost::array<char, 6> buffer;
    char *raw_data = buffer.data();
    boost::asio::ip::address ip_addr;
    boost::asio::ip::udp::endpoint peer;
    int port;

    read((*serve_socket), boost::asio::buffer(buffer));
    in_addr ip_raw = *(in_addr *)(raw_data);
    ip_addr = boost::asio::ip::address::from_string(inet_ntoa(ip_raw));
    port = ntohs(*(short *)(raw_data + 4));

    boost::asio::ip::udp::endpoint peer_local_endpoint_ = boost::asio::ip::udp::endpoint(ip_addr, port);

    TRACE("peer local endpoint = (" << peer_local_endpoint_.address().to_string() << ","
          << std::to_string(peer_local_endpoint_.port()) << ")");


    SendConfiguration(serve_socket);
    SendTheListOfPeers(serve_socket);
    serve_socket->close();
    InsertPeer(boost::asio::ip::udp::endpoint(incoming_peer.address(),
                                              incoming_peer.port()));
    AddPeerToDictionary(boost::asio::ip::udp::endpoint(incoming_peer.address(),
                                              incoming_peer.port()), peer_local_endpoint_);
    // TODO: In original code, incoming_peer is returned, but is not used
  }

  void SplitterEMS::AddPeerToDictionary(const boost::asio::ip::udp::endpoint &peer,
    const boost::asio::ip::udp::endpoint &local){
      peer_pairs_[peer] = local;
  }
  //TODO:corrrect type mismatch with GetHash
  /*void SplitterEMS::RemovePeer(const asio::ip::udp::endpoint &peer) {
    // If peer_list_ contains the peer, remove it
    if (find(peer_list_.begin(), peer_list_.end(), peer) != peer_list_.end()) {
      peer_list_.erase(remove(peer_list_.begin(), peer_list_.end(), peer),
                       peer_list_.end());


      //remove peer from public-private hashtable
      peer_pairs_.erase(GetHash(peer));

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
  }*/


  std::vector<boost::asio::ip::udp::endpoint> SplitterEMS::GetPeerList() {
    //TODO:investigate if private/public address should be returned...i think public?
    return peer_list_;
  }

}

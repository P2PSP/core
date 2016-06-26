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


  SplitterEMS::SplitterEMS() : SplitterDBS(), peer_pairs_(0, &SplitterDBS::GetHash){

    magic_flags_ = Common::kEMS;

    TRACE("Initialized EMS");
  }

  SplitterEMS::~SplitterEMS(){}



  void SplitterEMS::SendTheListOfPeers(
                                       const std::shared_ptr<boost::asio::ip::tcp::socket> &peer_serve_socket) {
    SendTheListSize(peer_serve_socket);

    asio::ip::address target_address = peer_serve_socket->remote_endpoint().address();
    int counter = 0;

    char message[6];
    in_addr addr;


    for (std::vector<asio::ip::udp::endpoint>::iterator it = peer_list_.begin();
         it != peer_list_.end(); ++it) {
      LOG("sending peer number : [" << std::to_string(counter) << "]");
      asio::ip::udp::endpoint peer_endpoint = boost::asio::ip::udp::endpoint(it->address(),
                                                                             it->port());
      if (it->address() == target_address) {
        peer_endpoint = peer_pairs_[peer_endpoint];
        LOG("target peer at" << target_address.to_string() << " is in a private network with peer sent as("
              << peer_endpoint.address().to_string() << "," << std::to_string(peer_endpoint.port()) << ")");
      } else  {
        LOG("sent peer("
              << peer_endpoint.address().to_string() << "," << std::to_string(peer_endpoint.port()) << ")");
      }

      inet_aton(peer_endpoint.address().to_string().c_str(), &addr);
      (*(in_addr *)&message) = addr;
      (*(uint16_t *)(message + 4)) = htons(peer_endpoint.port());
      peer_serve_socket->send(asio::buffer(message));

      TRACE(to_string(counter) << ", " << *it);
      counter++;
    }
  }

  /*void SplitterEMS::SendTheListOfPeers(
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
  }*/



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
    SplitterEMS::peer_pairs_.emplace(boost::asio::ip::udp::endpoint(incoming_peer.address(),
                                              incoming_peer.port()), peer_local_endpoint_);
    InsertPeer(boost::asio::ip::udp::endpoint(incoming_peer.address(),
                                              incoming_peer.port()));
  }

  

  std::vector<boost::asio::ip::udp::endpoint> SplitterEMS::GetPeerList() {
    //TODO:investigate if private/public address should be returned...i think public?
    return peer_list_;
  }



}

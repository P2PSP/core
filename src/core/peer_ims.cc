  

//
//  peer_ims.cc
//  P2PSP
//
//  This code is distributed under the GNU General Public License (see
//  THE_GENERAL_GNU_PUBLIC_LICENSE.txt for extending this information).
//  Copyright (C) 2016, the P2PSP team.
//  http://www.p2psp.org
//
//  IMS: Ip Multicasting Set of rules
//

#define _1_ // Temporal!!!

#include "peer_ims.h"

namespace p2psp {

  constexpr char PeerIMS::kSplitterAddr[];

  PeerIMS::PeerIMS()
    : io_service_(),
      acceptor_(io_service_),
      player_socket_(io_service_),
      splitter_socket_(io_service_),
      team_socket_(io_service_) {

    magic_flags_ = Common::kIMS;

    // Default values
    player_port_ = kPlayerPort;
    splitter_addr_ = ip::address::from_string(kSplitterAddr);
    splitter_port_ = kSplitterPort;
    team_port_ = kTeamPort;
    use_localhost_ = kUseLocalhost;
    buffer_status_ = kBufferStatus;
    show_buffer_ = kShowBuffer;

    // Initialized in PeerIMS::ReceiveTheBufferSize()
    buffer_size_ = 0;

    // Initialized in PeerIMS::ReceiveTheChunkSize()
    chunk_size_ = 0;
    chunks_ = std::vector<Chunk>();

    // Initialized in PeerIMS::ReceiveTheHeaderSize()
    header_size_in_chunks_ = 0;

    // Initialized in PeerIMS::ReceiveTheMcasteEndpoint()
    mcast_addr_ = ip::address::from_string("0.0.0.0");
    mcast_port_ = 0;

    played_chunk_ = 0;
    player_alive_ = false;

    received_counter_ = 0;
    received_flag_ = std::vector<bool>();
    recvfrom_counter_ = 0;

    sendto_counter_ = -1;
  }

  PeerIMS::~PeerIMS() {}

  void PeerIMS::Init() {};

  void Peer_IMS::ReceiveMcastChannel() {
    // {{{

    boost::array<char, 6> buffer;
    read(splitter_socket_, ::buffer(buffer));

    char *raw_data = buffer.data();

    in_addr ip_raw = *(in_addr *)(raw_data);
    mcast_addr_ = ip::address::from_string(inet_ntoa(ip_raw));
    mcast_port_ = ntohs(*(short *)(raw_data + 4));

    TRACE("mcast_endpoint = ("
	  << mcast_addr_.to_string()
	  << ","
          << std::to_string(mcast_port_)
	  << ")");

    // }}}
  }

  void Peer_IMS::ListenToTheTeam() {
    // {{{

    ip::udp::endpoint endpoint(ip::address_v4::any(), mcast_port_);
    team_socket_.open(endpoint.protocol());
    team_socket_.set_option(ip::udp::socket::reuse_address(true));
    team_socket_.bind(endpoint);
    team_socket_.set_option(ip::multicast::join_group(mcast_addr_));

    TRACE("Listening to the mcast_channel = ("
	  << mcast_addr_.to_string()
	  << ","
          << std::to_string(mcast_port_)
          << ")");

    // }}}
  }

  int PeerIMS::ProcessMessage(const std::vector<char> &message,
                              const ip::udp::endpoint &sender) {
    // {{{

    // Ojo, an attacker could send a packet smaller and pollute the buffer,
    // althought this is difficult in IP multicst. This method should be
    // inheritaged to solve this issue.

    uint16_t chunk_number = ntohs(*(short *)message.data());

    chunks_[chunk_number % buffer_size_] = {
      std::vector<char>(message.data() + sizeof(uint16_t),
                        message.data() + message.size()),
      true};

    received_counter_++;

    return chunk_number;

    // }}}
  }

  //std::string PeerIMS::GetMcastAddr() {
  ip::address PeerIMS::GetMcastAddr() {
    // {{{

    //return mcast_addr_.to_string();
    return mcast_addr_;

    // }}}
  }

}

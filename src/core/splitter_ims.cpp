//
//  splitter_ims.cpp
//  P2PSP
//
//  This code is distributed under the GNU General Public License (see
//  THE_GENERAL_GNU_PUBLIC_LICENSE.txt for extending this information).
//  Copyright (C) 2014, the P2PSP team.
//  http://www.p2psp.org
//
//  IMS: IP Multicast Set of rules.
//

#include "splitter_ims.h"

namespace p2psp {
SplitterIMS::SplitterIMS()
    : kBufferSize(256),
      kChannel("BBB-134.ogv"),
      kChunkSize(1024),
      kHeaderSize(10),
      kPort(4552),
      kSourceAddr("150.214.150.68"),
      kSourcePort(4551),
      kMCastAddr("224.0.0.1"),
      kTTL(1),
      peer_connection_socket_(io_service_),
      acceptor_(io_service_) {
  alive_ = true;
  chunk_number_ = 0;

  team_socket_ = 0;
  source_socket_ = 0;

  // Auxiliar stringstream
  std::stringstream ss;

  // Initialize source_
  ss << kSourceAddr;
  source_ = {ss.str(), kSourcePort};
  ss.str("");

  // Initialize GET_message_
  ss << "GET /" << kChannel << " HTTP/1.1\r\n"
     << "\r\n";
  GET_message_ = ss.str();
  ss.str("");

  // Initialize chunk_number_format_
  chunk_number_format_ = "H";

  // Initialize mcast_channel_
  ss << kMCastAddr;
  mcast_channel_ = {ss.str(), kPort};
  ss.str("");

  // Initialize counters
  recvfrom_counter_ = 0;
  sendto_counter_ = 0;
  header_load_counter_ = 0;
}

SplitterIMS::~SplitterIMS() {}

void SplitterIMS::SetupPeerConnectionSocket() {
  boost::asio::ip::tcp::resolver resolver(io_service_);

  // TODO: Remove hard coded strings and use variables instead
  boost::asio::ip::tcp::endpoint endpoint =
      *resolver.resolve({"127.0.0.1", "4552"});
  acceptor_.open(endpoint.protocol());
  acceptor_.set_option(boost::asio::ip::tcp::acceptor::reuse_address(true));
  acceptor_.bind(endpoint);
  acceptor_.listen();
}
}

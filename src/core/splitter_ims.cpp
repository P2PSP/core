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
      io_service_(),
      peer_connection_socket_(io_service_),
      source_socket_(io_service_),
      acceptor_(io_service_) {
  alive_ = true;
  chunk_number_ = 0;

  team_socket_ = 0;

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

void SplitterIMS::ConfigureSockets() {
  try {
    SetupPeerConnectionSocket();
  } catch (int e) {
    // TODO: Print error and exit
  }

  try {
    SetupTeamSocket();
  } catch (int e) {
    // TODO: Print error and exit
  }
}

void SplitterIMS::SetupTeamSocket() {}

void SplitterIMS::RequestTheVideoFromTheSource() {
  boost::system::error_code ec;
  boost::asio::ip::tcp::endpoint endpoint(
      boost::asio::ip::address::from_string(kSourceAddr), kSourcePort);

  source_socket_.connect(endpoint, ec);

  if (ec) {
    // TODO: print(e)
    std::cout << "Error: " << ec.message() << std::endl;

    // TODO: print(sockname, "\b: unable to connect to the source ", source)
    source_socket_.close();
    exit(-1);
  }

  // TODO: print(sockname, "connected to", source)

  source_socket_.send(boost::asio::buffer(GET_message_));

  // TODO: print(sockname, "IMS: GET_message =", GET_message_)
}

void SplitterIMS::ReceiveNextChunk() {
  boost::system::error_code ec;
  boost::asio::streambuf chunk;

  size_t bytes_transferred = boost::asio::read(
      source_socket_, chunk, boost::asio::transfer_exactly(kChunkSize), ec);

  if (ec) {
    // TODO: Use a print class to show errors
    std::cout << "Error: " << ec.message() << std::endl;
  }

  // Remove data that was read.
  chunk.consume(bytes_transferred);

  // TODO: Return chunk, decide type (streambuf, vector, string...)
}
}

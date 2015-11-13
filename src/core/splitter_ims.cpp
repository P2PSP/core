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
    : mcast_channel_(boost::asio::ip::address::from_string(kMCastAddr), kPort),
      io_service_(),
      peer_connection_socket_(io_service_),
      source_socket_(io_service_),
      team_socket_(io_service_, mcast_channel_.protocol()),
      acceptor_(io_service_) {
  buffer_size_ = kBufferSize;
  channel_ = kChannel;
  chunk_size_ = kChunkSize;
  header_size_ = kHeaderSize;
  port_ = kPort;
  source_addr_ = kSourceAddr;
  source_port_ = kSourcePort;
  mcast_addr_ = kMCastAddr;
  ttl_ = kTTL;

  alive_ = true;
  chunk_number_ = 0;

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

  // Initialize counters
  recvfrom_counter_ = 0;
  sendto_counter_ = 0;
  header_load_counter_ = 0;
}

SplitterIMS::~SplitterIMS() {}

void SplitterIMS::SetupPeerConnectionSocket() {
  // TODO: Remove hard coded strings and use variables instead
  boost::asio::ip::tcp::endpoint endpoint(
      boost::asio::ip::address::from_string("127.0.0.1"), port_);
  acceptor_.open(endpoint.protocol());
  acceptor_.set_option(boost::asio::ip::tcp::acceptor::reuse_address(true));
  acceptor_.bind(endpoint);
  acceptor_.listen();
}

void SplitterIMS::ConfigureSockets() {
  try {
    SetupPeerConnectionSocket();
  } catch (int e) {
    LOG(e);
    LOG(peer_connection_socket_.local_endpoint().address().to_string() +
        "\b: unable to bind the port " + std::to_string(port_));
    exit(-1);
  }

  try {
    SetupTeamSocket();
  } catch (int e) {
    LOG(e);
    // TODO: print getsockname unable to bind to (gethostname, port)
    exit(-1);
  }
}

void SplitterIMS::SetupTeamSocket() {
  boost::system::error_code ec;

  // Implements the IPPROTO_IP/IP_MULTICAST_TTL socket option.
  boost::asio::ip::multicast::hops ttl(ttl_);
  team_socket_.set_option(ttl);

  boost::asio::socket_base::reuse_address reuseAddress(true);
  team_socket_.set_option(reuseAddress, ec);

  if (ec) {
    LOG("Error: " + ec.message());
  }

  // TODO: Check if reuse_port option exists
}

void SplitterIMS::RequestTheVideoFromTheSource() {
  boost::system::error_code ec;
  boost::asio::ip::tcp::endpoint endpoint(
      boost::asio::ip::address::from_string(source_addr_), source_port_);

  source_socket_.connect(endpoint, ec);

  if (ec) {
    LOG("Error: " << ec.message());
    LOG(source_socket_.local_endpoint().address().to_string() +
        "\b: unable to connect to the source (" + source_addr_ + ", " +
        std::to_string(source_port_) + ")");

    source_socket_.close();
    exit(-1);
  }

  LOG(source_socket_.local_endpoint().address().to_string() +
      " connected to (" + source_addr_ + ", " + std::to_string(source_port_) +
      ")");

  source_socket_.send(boost::asio::buffer(GET_message_));

  LOG(source_socket_.local_endpoint().address().to_string() +
      "IMS: GET_message = " + GET_message_);
}

size_t SplitterIMS::ReceiveNextChunk(boost::asio::streambuf &chunk) {
  boost::system::error_code ec;

  size_t bytes_transferred = boost::asio::read(
      source_socket_, chunk, boost::asio::transfer_exactly(chunk_size_), ec);

  if (ec) {
    LOG("Error: " + ec.message());
  }

  return bytes_transferred;
}

void SplitterIMS::LoadTheVideoHeader() {
  LOG("Loading the video header");
  for (int i = 0; i < header_size_; i++) {
    ReceiveNextChunk(header_);
  }
}

void SplitterIMS::ReceiveTheHeader() {
  LOG("Requesting the stream header ...");

  ConfigureSockets();
  RequestTheVideoFromTheSource();
  LoadTheVideoHeader();

  LOG("Stream header received!");
}

void SplitterIMS::SendChunk(boost::asio::streambuf &message,
                            boost::asio::ip::udp::endpoint destination) {
  boost::system::error_code ec;

  size_t bytes_transferred =
      team_socket_.send_to(message.data(), destination, 0, ec);

  // Sent data is removed from message
  message.consume(bytes_transferred);

  sendto_counter_++;
}

void SplitterIMS::SendTheMcastChannel(
    boost::asio::ip::tcp::socket &peer_serve_socket) {
  LOG("Communicating the multicast channel (" + mcast_addr_ + ", " +
      std::to_string(port_) + ")");

  char message[6];
  in_addr addr;
  inet_aton(mcast_addr_.c_str(), &addr);
  (*(in_addr *)&message) = addr;
  (*(unsigned short *)(message + 4)) = htons(port_);
  peer_serve_socket.send(boost::asio::buffer(message));
}

void SplitterIMS::SendTheHeaderSize(
    boost::asio::ip::tcp::socket &peer_serve_socket) {
  LOG("Communicating the header size " + std::to_string(header_size_));

  boost::system::error_code ec;
  char message[2];
  (*(unsigned short *)&message) = htons(header_size_);
  peer_serve_socket.send(boost::asio::buffer(message), 0, ec);

  if (ec) {
    LOG("Error: " + ec.message());
  }
}

void SplitterIMS::SendTheChunkSize(
    boost::asio::ip::tcp::socket &peer_serve_socket) {
  LOG("Sending a chunk_size of " + std::to_string(chunk_size_) + " bytes");

  boost::system::error_code ec;
  char message[2];
  (*(unsigned short *)&message) = htons(chunk_size_);
  peer_serve_socket.send(boost::asio::buffer(message), 0, ec);

  if (ec) {
    LOG("Error: " + ec.message());
  }
}

void SplitterIMS::SendConfiguration(boost::asio::ip::tcp::socket &sock) {
  SendTheMcastChannel(sock);
  SendTheHeaderSize(sock);
  SendTheChunkSize(sock);
}

void SplitterIMS::HandleAPeerArrival(
    boost::asio::ip::tcp::socket &serve_socket) {
  LOG(serve_socket.local_endpoint().address().to_string() +
      "\b: IMS: accepted connection from peer (" +
      serve_socket.remote_endpoint().address().to_string() + ", " +
      std::to_string(serve_socket.remote_endpoint().port()) + ")");

  SendConfiguration(serve_socket);
  serve_socket.close();
}

void SplitterIMS::Run() {
  LOG("Run");

  ReceiveTheHeader();

  boost::asio::ip::tcp::socket serve_socket(io_service_);
  acceptor_.accept(serve_socket);
  HandleAPeerArrival(serve_socket);
}

void SplitterIMS::Start() {
  LOG("Start");
  boost::thread t(boost::bind(&SplitterIMS::Run, this));
  boost::this_thread::sleep(boost::posix_time::milliseconds(20000));
  LOG("Exiting");
}
}

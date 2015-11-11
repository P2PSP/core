
#include "peer_ims.h"
#include <iostream>

namespace p2psp {

constexpr char PeerIMS::kSplitterAddr[];

PeerIMS::PeerIMS()
    : io_service_(),
      acceptor_(io_service_),
      player_socket_(io_service_),
      splitter_socket_(io_service_),
      team_socket_(io_service_) {
  // Default values
  player_port_ = kPlayerPort;
  splitter_addr_.assign(kSplitterAddr);
  splitter_port_ = kSplitterPort;
  port_ = kPort;
  use_localhost_ = kUseLocalhost;
  buffer_status_ = kBufferStatus;
  show_buffer_ = kShowBuffer;

  buffer_size_ = 0;
  chunk_size_ = 0;
  chunks_ = std::vector<char>();

  // Initialized in PeerIMS::ReceiveTheHeaderSize()
  header_size_in_chunks_ = 0;

  // Initialized in PeerIMS::ReceiveTheMcasteEndpoint()
  mcast_addr_ = "0.0.0.0";
  mcast_port_ = 0;

  played_chunk_ = 0;
  player_alive_ = false;

  received_counter_ = 0;
  received_flag_ = std::vector<bool>();
  recvfrom_counter_ = 0;
  splitter_ = {splitter_addr_, std::to_string(splitter_port_)};
}

PeerIMS::~PeerIMS() {}

void PeerIMS::WaitForThePlayer() {
  std::string port = std::to_string(player_port_);
  boost::asio::ip::tcp::resolver resolver(io_service_);
  boost::asio::ip::tcp::endpoint endpoint = *resolver.resolve({"", port});

  acceptor_.open(endpoint.protocol());
  acceptor_.set_option(boost::asio::ip::tcp::acceptor::reuse_address(true));
  acceptor_.bind(endpoint);
  acceptor_.listen();
  // TODO: Log.D("Waiting for the player at", player_socket_.local_endpoint())
  acceptor_.accept(player_socket_);
  // TODO: Log.D("The player is", player_socket_.local_endpoint())
}

void PeerIMS::ConnectToTheSplitter() {
  std::string my_ip;

  // splitter_ = {splitter_addr_, std::to_string(splitter_port_)};

  // TCP endpoint object to connect to splitter
  boost::asio::ip::tcp::endpoint splitter_tcp_endpoint(
      boost::asio::ip::address::from_string(splitter_addr_), splitter_port_);
  // UDP endpoint object to connect to splitter
  boost::asio::ip::udp::endpoint splitter_udp_endpoint(
      boost::asio::ip::address::from_string(splitter_addr_), splitter_port_);

  boost::asio::ip::tcp::endpoint tcp_endpoint;

  // TODO: Log.D("use_localhost =", use_localhost)
  if (use_localhost_) {
    my_ip = "0.0.0.0";
  } else {
    boost::asio::ip::udp::socket s(io_service_);
    try {
      s.connect(splitter_udp_endpoint);
    } catch (boost::system::system_error e) {
      // TODO: print(e)
    }

    my_ip = s.remote_endpoint().address().to_string();
    s.close();
  }

  // TODO: Log.D("Connecting to the splitter at", splitter_, "from", my_ip)
  if (port_ != 0) {
    // TODO: Log.D("I'm using port", port_)
    tcp_endpoint = boost::asio::ip::tcp::endpoint(
        boost::asio::ip::address::from_string(my_ip), port_);
    splitter_socket_.set_option(
        boost::asio::ip::udp::socket::reuse_address(true));
    splitter_socket_.bind(tcp_endpoint);
  } else {
    tcp_endpoint = boost::asio::ip::tcp::endpoint(
        boost::asio::ip::address::from_string(my_ip), 0);
    // splitter_socket_.bind(tcp_endpoint);
  }

  try {
    splitter_socket_.connect(splitter_tcp_endpoint);
  } catch (boost::system::system_error e) {
    // TODO: print(e)

    // TODO: if (true) {
    // Log.D(e);
    //} else {
    // print(e)
    //}
    exit(-1);
  }

  // TODO: Log.D("Connected to the splitter at", splitter_tcp_endpoint)
}

void PeerIMS::DisconnectFromTheSplitter() { splitter_socket_.close(); }

void PeerIMS::ReceiveTheMcasteEndpoint() {
  boost::array<char, 6> buffer;
  boost::asio::read(splitter_socket_, boost::asio::buffer(buffer));

  // Reverse ip/port endianness
  char* raw_data = buffer.c_array();
  std::reverse(raw_data, raw_data + 4);
  std::reverse(raw_data + 4, raw_data + 6);

  // New IPv4 address
  boost::asio::ip::address_v4 ip(*(unsigned int*)raw_data);
  unsigned short port = *(short*)(raw_data + 4);

  mcast_addr_ = ip.to_string();
  mcast_port_ = port;

  // TODO: Log.D("mcast_endpoint =", mcast_addr_ + mcast_port_)
}

void PeerIMS::ReceiveTheHeaderSize() {
  boost::array<char, 2> buffer;
  boost::asio::read(splitter_socket_, boost::asio::buffer(buffer));

  // Reverse header size endianness
  char* raw_data = buffer.c_array();
  std::reverse(raw_data, raw_data + buffer.size());

  header_size_in_chunks_ = *(short*)(raw_data);

  // TODO: Log.D("header_size (in chunks) =", header_size_in_chunks_)
}

void PeerIMS::ReceiveTheChunkSize() {
  boost::array<char, 2> buffer;
  boost::asio::read(splitter_socket_, boost::asio::buffer(buffer));

  // Reverse chunk size endianness
  char* raw_data = buffer.c_array();
  std::reverse(raw_data, raw_data + buffer.size());

  chunk_size_ = *(short*)(raw_data);

  // TODO: Log.D("chunk_size (bytes) =", chunk_size_)
}
}
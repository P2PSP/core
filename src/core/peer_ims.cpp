
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

  // Initialized in PeerIMS::ReceiveTheBufferSize()
  buffer_size_ = 0;

  // Initialized in PeerIMS::ReceiveTheChunkSize()
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

  LOG("Waiting for the player at (" + endpoint.address().to_string() + "," +
      std::to_string(endpoint.port()) + ")");
  acceptor_.accept(player_socket_);

  LOG("The player is (" +
      player_socket_.remote_endpoint().address().to_string() + "," +
      std::to_string(player_socket_.remote_endpoint().port()) + ")");
}

void PeerIMS::ConnectToTheSplitter() {
  std::string my_ip;

  // TCP endpoint object to connect to splitter
  boost::asio::ip::tcp::endpoint splitter_tcp_endpoint(
      boost::asio::ip::address::from_string(splitter_addr_), splitter_port_);
  // UDP endpoint object to connect to splitter
  boost::asio::ip::udp::endpoint splitter_udp_endpoint(
      boost::asio::ip::address::from_string(splitter_addr_), splitter_port_);

  boost::asio::ip::tcp::endpoint tcp_endpoint;

  LOG("use_localhost = " + std::string((use_localhost_ ? "True" : "False")));
  if (use_localhost_) {
    my_ip = "0.0.0.0";
  } else {
    boost::asio::ip::udp::socket s(io_service_);
    try {
      s.connect(splitter_udp_endpoint);
    } catch (boost::system::system_error e) {
      LOG(e.what());
    }

    my_ip = s.local_endpoint().address().to_string();
    s.close();
  }

  splitter_socket_.open(splitter_tcp_endpoint.protocol());

  LOG("Connecting to the splitter at (" +
      splitter_tcp_endpoint.address().to_string() + "," +
      std::to_string(splitter_tcp_endpoint.port()) + ") from " + my_ip);
  if (port_ != 0) {
    LOG("I'm using port" + std::to_string(port_));
    tcp_endpoint = boost::asio::ip::tcp::endpoint(
        boost::asio::ip::address::from_string(my_ip), port_);
    splitter_socket_.set_option(
        boost::asio::ip::udp::socket::reuse_address(true));
  } else {
    tcp_endpoint = boost::asio::ip::tcp::endpoint(
        boost::asio::ip::address::from_string(my_ip), 0);
  }

  splitter_socket_.bind(tcp_endpoint);

  try {
    splitter_socket_.connect(splitter_tcp_endpoint);
  } catch (boost::system::system_error e) {
    if (IFF_DEBUG) {
      LOG(e.what());
    } else {
      LOG(e.what());
    }
    exit(-1);
  }

  LOG("Connected to the splitter at (" +
      splitter_tcp_endpoint.address().to_string() + "," +
      std::to_string(splitter_tcp_endpoint.port()) + ")");
}

void PeerIMS::DisconnectFromTheSplitter() { splitter_socket_.close(); }

void PeerIMS::ReceiveTheMcasteEndpoint() {
  boost::array<char, 6> buffer;
  boost::asio::read(splitter_socket_, boost::asio::buffer(buffer));

  char* raw_data = buffer.c_array();

  in_addr ip_raw = *(in_addr*)(raw_data);
  mcast_addr_ = inet_ntoa(ip_raw);
  mcast_port_ = ntohs(*(short*)(raw_data + 4));

  LOG("mcast_endpoint = (" + mcast_addr_ + "," + std::to_string(mcast_port_) +
      ")");
}

void PeerIMS::ReceiveTheHeaderSize() {
  boost::array<char, 2> buffer;
  boost::asio::read(splitter_socket_, boost::asio::buffer(buffer));

  header_size_in_chunks_ = ntohs(*(short*)(buffer.c_array()));

  LOG("header_size (in chunks) = " + std::to_string(header_size_in_chunks_));
}

void PeerIMS::ReceiveTheChunkSize() {
  boost::array<char, 2> buffer;
  boost::asio::read(splitter_socket_, boost::asio::buffer(buffer));

  chunk_size_ = ntohs(*(short*)(buffer.c_array()));

  LOG("chunk_size (bytes) = " + std::to_string(chunk_size_));
}

void PeerIMS::ReceiveTheHeader() {
  int header_size_in_bytes = header_size_in_chunks_ * chunk_size_;
  std::vector<char> header(header_size_in_bytes);

  boost::system::error_code ec;
  boost::asio::streambuf chunk;

  boost::asio::read(splitter_socket_, chunk,
                    boost::asio::transfer_exactly(header_size_in_bytes), ec);
  if (ec) {
    LOG("Error: " + ec.message());
  }

  try {
    boost::asio::write(player_socket_, chunk);
  } catch (std::exception e) {
    LOG(e.what());
    LOG("error sending data to the player");
    LOG("len(data) =" + std::to_string(chunk.size()));
    // FIX: boost::this_thread::sleep(boost::posix_time::seconds(1));
  }

  LOG("Received " + std::to_string(header_size_in_bytes) + "bytes of header");
}

void PeerIMS::ReceiveTheBufferSize() {
  boost::array<char, 2> buffer;
  boost::asio::read(splitter_socket_, boost::asio::buffer(buffer));

  buffer_size_ = ntohs(*(short*)(buffer.c_array()));

  LOG("buffer_size_ = " + std::to_string(buffer_size_));
}
}
//
//  splitter_core.cc -- Core
//
//  This code is distributed under the GNU General Public License (see
//  THE_GENERAL_GNU_PUBLIC_LICENSE.txt for extending this information).
//  Copyright (C) 2016, the P2PSP team.
//  http://www.p2psp.org
//

//#define __DEBUG_CHUNKS__

#include "splitter_core.h"
#include "../util/trace.h"

namespace p2psp {
  using namespace std;
  using namespace boost;

  const int Splitter_core::kBufferSize = 256;                 // Buffer size in chunks
  const std::string Splitter_core::kChannel = "test.ogg";     // Default channel
  const int Splitter_core::kChunkSize = 1024;                 // Chunk size in bytes (larger than MTU)
  const unsigned short Splitter_core::kSplitterPort = 8001;   // Listening port
  const std::string Splitter_core::kSourceAddr = "127.0.0.1"; // Streaming server's host
  const int Splitter_core::kSourcePort = 8000;                // Streaming server's listening port
  const int Splitter_core::kHeaderSize = 8192;

  Splitter_core::Splitter_core()
    : io_service_(),
      peer_connection_socket_(io_service_),
      acceptor_(io_service_),
      team_socket_(io_service_),
      source_socket_(io_service_) {
    buffer_size_ = kBufferSize;
    channel_ = kChannel;
    chunk_size_ = kChunkSize;
    splitter_port_ = kSplitterPort;
    source_addr_ = kSourceAddr;
    source_port_ = kSourcePort;
    header_size_ = kHeaderSize;

    alive_ = true;
    chunk_number_ = 0;

    SetGETMessage(channel_);

    // Initialize chunk_number_format_
    chunk_number_format_ = "H";

    // Initialize counters
    recvfrom_counter_ = 0;
    sendto_counter_ = 0;

    TRACE("IMS initialized");
  }

  Splitter_core::~Splitter_core() {}

  int Splitter_core::GetDefaultHeaderSize() {
    return kHeaderSize;
  }

  void Splitter_core::SetupPeerConnectionSocket() {
    asio::ip::tcp::endpoint endpoint(asio::ip::tcp::v4(), splitter_port_);
    acceptor_.open(endpoint.protocol());
    acceptor_.set_option(asio::ip::tcp::acceptor::reuse_address(true));
    acceptor_.bind(endpoint);
    acceptor_.listen();
  }

  void Splitter_core::SendChannel(const std::shared_ptr<boost::asio::ip::tcp::socket> &peer_serve_socket) {

    //system::error_code ec;
    char message[2];

    TRACE("channel size = "
	  << channel_.length());

    (*(uint16_t *)&message) = htons(channel_.length());
    //peer_serve_socket->send(asio::buffer(message), 0, ec);

    /*if (ec) {
      ERROR(ec.message());
      }*/
    boost::asio::write(*peer_serve_socket, boost::asio::buffer(message, 2));
    //char data[19];
    //boost::asio::write(*peer_serve_socket, boost::asio::buffer(data,19));

    TRACE("channel ="
	  << channel_);

    //boost::system::error_code ignored_error;
    boost::asio::write(*peer_serve_socket, boost::asio::buffer(channel_,channel_.length())/*,boost::asio::transfer_all(), ignored_error*/);

    //char message[80];

    //peer_serve_socket->send(asio::buffer(channel_));
    TRACE("Transmitted channel = "
	  << channel_);
  }

  void Splitter_core::ConfigureSockets() {
    try {
      SetupPeerConnectionSocket();
    } catch (system::system_error &error) {
      ERROR(error.what());
      ERROR(acceptor_.local_endpoint().address().to_string()
	    + "\b: unable to bind the port "
	    + to_string(splitter_port_));
      exit(-1);
    }

    try {
      SetupTeamSocket();
    } catch (int e) {
      TRACE(e);
      // TODO: print getsockname unable to bind to (gethostname, port)
      exit(-1);
    }
  }

  void Splitter_core::SetupTeamSocket() {}
  /*  system::error_code ec;

    team_socket_.open(mcast_channel_.protocol());

    // Implements the IPPROTO_IP/IP_MULTICAST_TTL socket option.
    asio::ip::multicast::hops ttl(ttl_);
    team_socket_.set_option(ttl);

    asio::socket_base::reuse_address reuseAddress(true);
    team_socket_.set_option(reuseAddress, ec);

    if (ec) {
      ERROR(ec.message());
    }

    // TODO: Check if reuse_port option exists
    }*/

  void Splitter_core::RequestTheVideoFromTheSource() {
    system::error_code ec;
    asio::ip::tcp::endpoint endpoint(asio::ip::address::from_string(source_addr_), source_port_);

    source_socket_.connect(endpoint, ec);

    if (ec) {
      ERROR(ec.message());
      ERROR(source_socket_.local_endpoint().address().to_string()
	    << "\b: unable to connect to the source ("
	    << source_addr_
	    << ", "
	    << to_string(source_port_)
	    << ")");

      source_socket_.close();
      exit(-1);
    }

    TRACE(source_socket_.local_endpoint().address().to_string()
	  << " connected to ("
	  << source_addr_
	  << ", "
	  << to_string(source_port_)
	  << ")");

    source_socket_.send(asio::buffer(GET_message_));

    TRACE(source_socket_.local_endpoint().address().to_string()
	  << "IMS: GET_message = "
	  << GET_message_);
  }

  size_t Splitter_core::ReceiveNextChunk(asio::streambuf &chunk) {
    system::error_code ec;

    size_t bytes_transferred = asio::read(source_socket_, chunk, asio::transfer_exactly(chunk_size_), ec);

    // TRACE("Success! Bytes transferred: " << bytes_transferred);

    if (ec) {
      ERROR("Error receiving next chunk: "
	    << ec.message()
	    << " bytes received: "
	    << bytes_transferred
	    << " != "
	    << chunk_size_);
      TRACE("No data in the server!");
      source_socket_.close();
      /*
      header_load_counter_ = header_size_;

      header_.consume(header_.size());
      this_thread::sleep(posix_time::seconds(1));
      source_socket_.connect(
                             asio::ip::tcp::endpoint(asio::ip::address::from_string(source_addr_),
                                                     source_port_),
                             ec);
      source_socket_.send(asio::buffer(GET_message_));
      */
      RequestTheVideoFromTheSource();
    }

    return bytes_transferred;
  }

  size_t Splitter_core::ReceiveChunk(asio::streambuf &chunk) {
    size_t bytes_transferred = ReceiveNextChunk(chunk);

    /*if (header_load_counter_ > 0) {
      ostream header_stream_(&header_);
      header_stream_.write(asio::buffer_cast<const char *>(chunk.data()), chunk.size());
      header_load_counter_--;
      TRACE("Loaded"
	    << to_string(chunk.size())
	    << " bytes of header");
	    }*/
    recvfrom_counter_++;

    return bytes_transferred;
  }


  void Splitter_core::SendChunk(const vector<char> &message, const asio::ip::udp::endpoint &destination) {
    system::error_code ec;

    // TRACE(std::to_string(ntohs(*(unsigned short *)message.data())));

    // size_t bytes_transferred =
    team_socket_.send_to(asio::buffer(message), destination, 0, ec);

#if defined __DEBUG_CHUNKS__
    TRACE(chunk_number_
	  << " -> "
	  << destination);
#endif

    // TRACE("Bytes transferred: " << to_string(bytes_transferred));

    if (ec) {
      ERROR("Error sending chunk: "
	    << ec.message());
    }

    sendto_counter_++;
  }

  void Splitter_core::SendChunkSize(const std::shared_ptr<boost::asio::ip::tcp::socket> &peer_serve_socket) {
    TRACE("Sending a chunk_size of "
	  << to_string(chunk_size_)
	  << " bytes");

    system::error_code ec;
    char message[2];
    (*(uint16_t *)&message) = htons(chunk_size_);
    peer_serve_socket->send(asio::buffer(message), 0, ec);

    if (ec) {
      ERROR(ec.message());
    }
  }

  void Splitter_core::SendBufferSize(const std::shared_ptr<boost::asio::ip::tcp::socket> &peer_serve_socket) {
    TRACE("Sending a buffer_size of "
	  << to_string(buffer_size_)
	  << " bytes");

    system::error_code ec;
    char message[2];
    (*(uint16_t *)&message) = htons(buffer_size_);
    peer_serve_socket->send(asio::buffer(message), 0, ec);

    if (ec) {
      ERROR(ec.message());
    }
  }

  void Splitter_core::SetHeaderSize(HEADER_SIZE_TYPE header_size) {
    this->header_size_ = header_size;
  }

  HEADER_SIZE_TYPE Splitter_core::GetHeaderSize(void) {
    return this->header_size_;
  }

  void Splitter_core::SendHeaderSize(const std::shared_ptr<boost::asio::ip::tcp::socket> &peer_serve_socket) {
    TRACE("Sending a header size of "
	  << to_string(header_size_)
	  << " bytes");

    system::error_code ec;
    char message[2];
    (*(uint16_t *)&message) = htons(header_size_);
    peer_serve_socket->send(asio::buffer(message), 0, ec);

    if (ec) {
      ERROR(ec.message());
    }
  }

  void Splitter_core::SendConfiguration(const std::shared_ptr<boost::asio::ip::tcp::socket> &sock) {
    SendSourceEndpoint(sock);
    SendChannel(sock);
    SendHeaderSize(sock);
    SendChunkSize(sock);
    SendBufferSize(sock);
  }

  void Splitter_core::HandleAPeerArrival(std::shared_ptr<boost::asio::ip::tcp::socket>) {}

  void Splitter_core::HandleArrivals() {
    std::shared_ptr<asio::ip::tcp::socket> peer_serve_socket;
    thread_group threads;

    while (alive_) {
      peer_serve_socket =
        make_shared<asio::ip::tcp::socket>(boost::ref(io_service_));
      acceptor_.accept(*peer_serve_socket);
      threads.create_thread(bind(&Splitter_core::HandleAPeerArrival, this, peer_serve_socket));
    }

    TRACE("Exiting handle arrivals");
  }

  void Splitter_core::SendSourceEndpoint(const std::shared_ptr<boost::asio::ip::tcp::socket> &peer_serve_socket) {
    TRACE("Communicating the source endpoing ("
	  << source_addr_
	  << ", "
	  << to_string(source_port_)
	  << ")");

    char message[6];
    in_addr addr;
    inet_aton(source_addr_.c_str(), &addr);
    (*(in_addr *)&message) = addr;
    (*(uint16_t *)(message + 4)) = htons(source_port_);
    peer_serve_socket->send(asio::buffer(message));
  }

  bool Splitter_core::isAlive() { return alive_; }

  void Splitter_core::SetAlive(bool alive) { alive_ = alive; }

  int Splitter_core::GetRecvFromCounter() { return recvfrom_counter_; }

  int Splitter_core::GetSendToCounter() { return sendto_counter_; }

  int Splitter_core::GetChunkSize() { return chunk_size_; }

  int Splitter_core::GetSplitterPort() { return splitter_port_; };

  void Splitter_core::SetBufferSize(int buffer_size) { buffer_size_ = buffer_size; }

  int Splitter_core::GetBufferSize() { return buffer_size_; }

  void Splitter_core::SetChannel(std::string channel) {
    channel_ = channel;
    SetGETMessage(channel_);
  }

  std::string Splitter_core::GetChannel() {
    return channel_;
  }

  std::string Splitter_core::GetSourceAddr() {
    return source_addr_;
  }

  int Splitter_core::GetSourcePort() {
    return source_port_;
  }

  void Splitter_core::SetGETMessage(std::string channel) {
    std::stringstream ss;
    ss << "GET /" << channel << " HTTP/1.1\r\n"
       << "\r\n";
    GET_message_ = ss.str();
    ss.str("");
  }

  void Splitter_core::SetChunkSize(int chunk_size) { chunk_size_ = chunk_size; }

  void Splitter_core::SetSplitterPort(int splitter_port) { splitter_port_ = splitter_port; }

  void Splitter_core::SetSourceAddr(std::string source_addr) {
    source_addr_ = source_addr;
  }

  void Splitter_core::SetSourcePort(int source_port) { source_port_ = source_port; }

  void Splitter_core::Start() {}; /*{
    TRACE("Start");
    thread_.reset(new boost::thread(boost::bind(&Splitter_core::Run, this)));
    }*/

  void Splitter_core::Run() {}

  int Splitter_core::GetDefaultChunkSize() {
    return kChunkSize;
  }

  int Splitter_core::GetDefaultSplitterPort() {
    return kSplitterPort;
  }

  int Splitter_core::GetDefaultBufferSize() {
    return kBufferSize;
  }

  std::string Splitter_core::GetDefaultChannel() {
    return kChannel;
  }

  std::string Splitter_core::GetDefaultSourceAddr() {
    return kSourceAddr;
  }

  int Splitter_core::GetDefaultSourcePort() {
    return kSourcePort;
  }

}

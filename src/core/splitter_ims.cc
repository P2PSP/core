//
//  splitter_ims.cc
//  P2PSP
//
//  This code is distributed under the GNU General Public License (see
//  THE_GENERAL_GNU_PUBLIC_LICENSE.txt for extending this information).
//  Copyright (C) 2016, the P2PSP team.
//  http://www.p2psp.org
//
//  IMS: IP Multicast Set of rules.
//

#include "splitter_ims.h"
#include "../util/trace.h"

namespace p2psp {
  using namespace std;
  using namespace boost;

  const int SplitterIMS::kBufferSize = 256;                 // Buffer size in chunks
  const std::string SplitterIMS::kChannel = "test.ogg";     // Default channel
  const int SplitterIMS::kChunkSize = 1024;                 // Chunk size in bytes (larger than MTU)
  const int SplitterIMS::kHeaderSize = 10;                  // Chunks/header
  const unsigned short SplitterIMS::kPort = 8001;           // Listening port
  const std::string SplitterIMS::kSourceAddr = "127.0.0.1"; // Streaming server's host
  const int SplitterIMS::kSourcePort = 8000;                // Streaming server's listening port
  const std::string SplitterIMS::kMCastAddr = "224.0.0.1";  // All Systems on this subnet
  const int SplitterIMS::kTTL = 1;                          // Time To Live of multicast packets

  SplitterIMS::SplitterIMS()
    : io_service_(),
      peer_connection_socket_(io_service_),
      acceptor_(io_service_),
      team_socket_(io_service_),
      source_socket_(io_service_),
      mcast_channel_(boost::asio::ip::address::from_string(kMCastAddr), kPort) {
    buffer_size_ = kBufferSize;
    channel_ = kChannel;
    chunk_size_ = kChunkSize;
    header_size_ = kHeaderSize;
    team_port_ = kPort;
    source_addr_ = kSourceAddr;
    source_port_ = kSourcePort;
    mcast_addr_ = kMCastAddr;
    ttl_ = kTTL;

    alive_ = true;
    chunk_number_ = 0;

    SetGETMessage(channel_);

    // Initialize chunk_number_format_
    chunk_number_format_ = "H";

    // Initialize counters
    recvfrom_counter_ = 0;
    sendto_counter_ = 0;
    header_load_counter_ = 0;
    TRACE("Initialized IMS");
  }

  SplitterIMS::~SplitterIMS() {}

  void SplitterIMS::SetupPeerConnectionSocket() {
    asio::ip::tcp::endpoint endpoint(asio::ip::tcp::v4(), team_port_);
    acceptor_.open(endpoint.protocol());
    acceptor_.set_option(asio::ip::tcp::acceptor::reuse_address(true));
    acceptor_.bind(endpoint);
    acceptor_.listen();
  }

  void SplitterIMS::ConfigureSockets() {
    try {
      SetupPeerConnectionSocket();
    } catch (system::system_error &error) {
      ERROR(error.what());
      ERROR(acceptor_.local_endpoint().address().to_string() +
            "\b: unable to bind the port " + to_string(team_port_));
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

  void SplitterIMS::SetupTeamSocket() {
    system::error_code ec;

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
  }

  void SplitterIMS::RequestTheVideoFromTheSource() {
    system::error_code ec;
    asio::ip::tcp::endpoint endpoint(asio::ip::address::from_string(source_addr_),
                                     source_port_);

    source_socket_.connect(endpoint, ec);

    if (ec) {
      ERROR(ec.message());
      ERROR(source_socket_.local_endpoint().address().to_string()
            << "\b: unable to connect to the source (" << source_addr_ << ", "
            << to_string(source_port_) << ")");

      source_socket_.close();
      exit(-1);
    }

    TRACE(source_socket_.local_endpoint().address().to_string()
          << " connected to (" << source_addr_ << ", " << to_string(source_port_)
          << ")");

    source_socket_.send(asio::buffer(GET_message_));

    TRACE(source_socket_.local_endpoint().address().to_string()
          << "IMS: GET_message = " << GET_message_);
  }

  size_t SplitterIMS::ReceiveNextChunk(asio::streambuf &chunk) {
    system::error_code ec;

    size_t bytes_transferred = asio::read(
                                          source_socket_, chunk, asio::transfer_exactly(chunk_size_), ec);

    // TRACE("Success! Bytes transferred: " << bytes_transferred);

    if (ec) {
      ERROR("Error receiving next chunk: "
            << ec.message() << " bytes transferred: " << bytes_transferred);
      TRACE("No data in the server!");
      source_socket_.close();
      header_load_counter_ = header_size_;
      header_.consume(header_.size());
      this_thread::sleep(posix_time::seconds(1));
      source_socket_.connect(
                             asio::ip::tcp::endpoint(asio::ip::address::from_string(source_addr_),
                                                     source_port_),
                             ec);
      source_socket_.send(asio::buffer(GET_message_));
    }

    return bytes_transferred;
  }

  size_t SplitterIMS::ReceiveChunk(asio::streambuf &chunk) {
    size_t bytes_transferred = ReceiveNextChunk(chunk);

    if (header_load_counter_ > 0) {
      ostream header_stream_(&header_);
      header_stream_.write(asio::buffer_cast<const char *>(chunk.data()),
                           chunk.size());
      header_load_counter_--;
      TRACE("Loaded" << to_string(chunk.size()) << " bytes of header");
    }
    recvfrom_counter_++;

    return bytes_transferred;
  }

  void SplitterIMS::LoadTheVideoHeader() {
    TRACE("Loading the video header");
    for (int i = 0; i < header_size_; i++) {
      ReceiveNextChunk(header_);
    }
  }

  void SplitterIMS::ReceiveTheHeader() {
    TRACE("Requesting the stream header ...");

    ConfigureSockets();
    RequestTheVideoFromTheSource();
    LoadTheVideoHeader();

    TRACE("Stream header received!");
  }

  void SplitterIMS::SendChunk(const vector<char> &message,
                              const asio::ip::udp::endpoint &destination) {
    system::error_code ec;

    // TRACE(std::to_string(ntohs(*(unsigned short *)message.data())));

    // size_t bytes_transferred =
    team_socket_.send_to(asio::buffer(message), destination, 0, ec);

    TRACE(chunk_number_ << " -> " << destination);

    // TRACE("Bytes transferred: " << to_string(bytes_transferred));

    if (ec) {
      ERROR("Error sending chunk: " << ec.message());
    }

    sendto_counter_++;
  }

  void SplitterIMS::SendTheMcastChannel(
                                        const std::shared_ptr<boost::asio::ip::tcp::socket> &peer_serve_socket) {
    TRACE("Communicating the multicast channel (" << mcast_addr_ << ", "
          << to_string(team_port_) << ")");

    char message[6];
    in_addr addr;
    inet_aton(mcast_addr_.c_str(), &addr);
    (*(in_addr *)&message) = addr;
    (*(uint16_t *)(message + 4)) = htons(team_port_);
    peer_serve_socket->send(asio::buffer(message));
  }

  void SplitterIMS::SendTheHeaderSize(
                                      const std::shared_ptr<boost::asio::ip::tcp::socket> &peer_serve_socket) {
    TRACE("Communicating the header size " << to_string(header_size_));

    system::error_code ec;
    char message[2];
    (*(uint16_t *)&message) = htons(header_size_);
    peer_serve_socket->send(asio::buffer(message), 0, ec);

    if (ec) {
      ERROR(ec.message());
    }
  }

  void SplitterIMS::SendTheChunkSize(
                                     const std::shared_ptr<boost::asio::ip::tcp::socket> &peer_serve_socket) {
    TRACE("Sending a chunk_size of " << to_string(chunk_size_) << " bytes");

    system::error_code ec;
    char message[2];
    (*(uint16_t *)&message) = htons(chunk_size_);
    peer_serve_socket->send(asio::buffer(message), 0, ec);

    if (ec) {
      ERROR(ec.message());
    }
  }

  void SplitterIMS::SendTheHeader(
                                  const std::shared_ptr<boost::asio::ip::tcp::socket> &peer_serve_socket) {
    TRACE("Sending a header of " << to_string(header_.size()) << " bytes");

    system::error_code ec;
    peer_serve_socket->send(header_.data(), 0, ec);

    if (ec) {
      ERROR(ec.message());
    }
  }

  void SplitterIMS::SendTheBufferSize(
                                      const std::shared_ptr<boost::asio::ip::tcp::socket> &peer_serve_socket) {
    TRACE("Sending a buffer_size of " << to_string(buffer_size_) << " bytes");

    system::error_code ec;
    char message[2];
    (*(uint16_t *)&message) = htons(buffer_size_);
    peer_serve_socket->send(asio::buffer(message), 0, ec);

    if (ec) {
      ERROR(ec.message());
    }
  }

  void SplitterIMS::SendConfiguration(
                                      const std::shared_ptr<boost::asio::ip::tcp::socket> &sock) {
    SendTheMcastChannel(sock);
    SendTheHeaderSize(sock);
    SendTheChunkSize(sock);
    SendTheHeader(sock);
    SendTheBufferSize(sock);
  }

  void SplitterIMS::HandleAPeerArrival(
                                       std::shared_ptr<asio::ip::tcp::socket> serve_socket) {
    TRACE(serve_socket->local_endpoint().address().to_string()
          << "\b: IMS: accepted connection from peer ("
          << serve_socket->remote_endpoint().address().to_string() << ", "
          << to_string(serve_socket->remote_endpoint().port()) << ")");

    SendConfiguration(serve_socket);
    serve_socket->close();
  }

  void SplitterIMS::HandleArrivals() {
    std::shared_ptr<asio::ip::tcp::socket> peer_serve_socket;
    thread_group threads;

    while (alive_) {
      peer_serve_socket =
        make_shared<asio::ip::tcp::socket>(boost::ref(io_service_));
      acceptor_.accept(*peer_serve_socket);
      threads.create_thread(
                            bind(&SplitterIMS::HandleAPeerArrival, this, peer_serve_socket));
    }

    TRACE("Exiting handle arrivals");
  }

  void SplitterIMS::Run() {
    TRACE("Run");

    ReceiveTheHeader();

    // asio::ip::tcp::socket serve_socket(io_service_);
    std::shared_ptr<asio::ip::tcp::socket> serve_socket =
      make_shared<asio::ip::tcp::socket>(boost::ref(io_service_));
    acceptor_.accept(*serve_socket);
    HandleAPeerArrival(serve_socket);

    thread t(bind(&SplitterIMS::HandleArrivals, this));

    asio::streambuf chunk;

    vector<char> message(sizeof(uint16_t) + chunk_size_);
    size_t bytes_transferred;

    while (alive_) {
      bytes_transferred = ReceiveChunk(chunk);
      TRACE(to_string(bytes_transferred) << " bytes received");

      (*(uint16_t *)message.data()) = htons(chunk_number_);

      copy(asio::buffer_cast<const char *>(chunk.data()),
           asio::buffer_cast<const char *>(chunk.data()) + chunk.size(),
           message.data() + sizeof(uint16_t));

      SendChunk(message, mcast_channel_);

      chunk_number_ = (chunk_number_ + 1) % Common::kMaxChunkNumber;
      TRACE("Chunk number: " << to_string(chunk_number_));
      chunk.consume(bytes_transferred);
    }
  }

  void SplitterIMS::SayGoodbye() {
    char message[1];
    message[0] = '\0';

    asio::ip::udp::endpoint destination(
                                        asio::ip::address::from_string("127.0.0.1"), team_port_);

    system::error_code ec;

    size_t bytes_transferred =
      team_socket_.send_to(asio::buffer(message), destination, 0, ec);

    TRACE("Bytes transferred saying goodbye: " << to_string(bytes_transferred));

    if (ec) {
      ERROR("Error saying goodbye: " << ec.message());
    }
  }

  bool SplitterIMS::isAlive() { return alive_; }

  void SplitterIMS::SetAlive(bool alive) { alive_ = alive; }

  int SplitterIMS::GetRecvFromCounter() { return recvfrom_counter_; }

  int SplitterIMS::GetSendToCounter() { return sendto_counter_; }

  int SplitterIMS::GetChunkSize() { return chunk_size_; }

  int SplitterIMS::GetTeamPort() { return team_port_; };

  void SplitterIMS::SetBufferSize(int buffer_size) { buffer_size_ = buffer_size; }

  int SplitterIMS::GetBufferSize() { return buffer_size_; }

  void SplitterIMS::SetChannel(std::string channel) {
    channel_ = channel;
    SetGETMessage(channel_);
  }

  std::string SplitterIMS::GetChannel() {
    return channel_;
  }

  int SplitterIMS::GetHeaderSize() {
    return header_size_;
  }

  std::string SplitterIMS::GetMcastAddr() {
    return mcast_addr_;
  }

  std::string SplitterIMS::GetSourceAddr() {
    return source_addr_;
  }

  int SplitterIMS::GetSourcePort() {
    return source_port_;
  }

  int SplitterIMS::GetTTL() {
    return ttl_;
  }

  void SplitterIMS::SetGETMessage(std::string channel) {
    std::stringstream ss;
    ss << "GET /" << channel << " HTTP/1.1\r\n"
       << "\r\n";
    GET_message_ = ss.str();
    ss.str("");
  }

  void SplitterIMS::SetChunkSize(int chunk_size) { chunk_size_ = chunk_size; }

  void SplitterIMS::SetHeaderSize(int header_size) { header_size_ = header_size; }

  void SplitterIMS::SetTeamPort(int team_port) { team_port_ = team_port; }

  void SplitterIMS::SetSourceAddr(std::string source_addr) {
    source_addr_ = source_addr;
  }

  void SplitterIMS::SetSourcePort(int source_port) { source_port_ = source_port; }

  void SplitterIMS::Start() {
    TRACE("Start");
    thread_.reset(new boost::thread(boost::bind(&SplitterIMS::Run, this)));
  }

  int SplitterIMS::GetDefaultChunkSize() {
    return kChunkSize;
  }

  int SplitterIMS::GetDefaultTeamPort() {
    return kPort;
  }

  int SplitterIMS::GetDefaultBufferSize() {
    return kBufferSize;
  }

  std::string SplitterIMS::GetDefaultChannel() {
    return kChannel;
  }

  int SplitterIMS::GetDefaultHeaderSize() {
    return kHeaderSize;
  }

  std::string SplitterIMS::GetDefaultMcastAddr() {
    return kMCastAddr;
  }

  std::string SplitterIMS::GetDefaultSourceAddr() {
    return kSourceAddr;
  }

  int SplitterIMS::GetDefaultSourcePort() {
    return kSourcePort;
  }

  int SplitterIMS::GetDefaultTTL() {
    return kTTL;
  }
}

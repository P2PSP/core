
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
  splitter_addr_ = boost::asio::ip::address::from_string(kSplitterAddr);
  splitter_port_ = kSplitterPort;
  port_ = kPort;
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
  mcast_addr_ = boost::asio::ip::address::from_string("0.0.0.0");
  mcast_port_ = 0;

  played_chunk_ = 0;
  player_alive_ = false;

  received_counter_ = 0;
  received_flag_ = std::vector<bool>();
  recvfrom_counter_ = 0;
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
  boost::asio::ip::tcp::endpoint splitter_tcp_endpoint(splitter_addr_,
                                                       splitter_port_);
  // UDP endpoint object to connect to splitter
  boost::asio::ip::udp::endpoint splitter_udp_endpoint(splitter_addr_,
                                                       splitter_port_);

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

  char *raw_data = buffer.c_array();

  in_addr ip_raw = *(in_addr *)(raw_data);
  mcast_addr_ = boost::asio::ip::address::from_string(inet_ntoa(ip_raw));
  mcast_port_ = ntohs(*(short *)(raw_data + 4));

  LOG("mcast_endpoint = (" + mcast_addr_.to_string() + "," +
      std::to_string(mcast_port_) + ")");
}

void PeerIMS::ReceiveTheHeaderSize() {
  boost::array<char, 2> buffer;
  boost::asio::read(splitter_socket_, boost::asio::buffer(buffer));

  header_size_in_chunks_ = ntohs(*(short *)(buffer.c_array()));

  LOG("header_size (in chunks) = " + std::to_string(header_size_in_chunks_));
}

void PeerIMS::ReceiveTheChunkSize() {
  boost::array<char, 2> buffer;
  boost::asio::read(splitter_socket_, boost::asio::buffer(buffer));

  chunk_size_ = ntohs(*(short *)(buffer.c_array()));

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

  buffer_size_ = ntohs(*(short *)(buffer.c_array()));

  LOG("buffer_size_ = " + std::to_string(buffer_size_));
}

void PeerIMS::ListenToTheTeam() {
  boost::asio::ip::udp::endpoint endpoint(boost::asio::ip::address_v4::any(),
                                          mcast_port_);

  team_socket_.open(endpoint.protocol());
  team_socket_.set_option(boost::asio::ip::udp::socket::reuse_address(true));
  team_socket_.bind(endpoint);

  team_socket_.set_option(boost::asio::ip::multicast::join_group(mcast_addr_));

  // TODO: handle timeout
  LOG("Listening to the mcast_channel = (" + mcast_addr_.to_string() + "," +
      std::to_string(mcast_port_) + ")");
}

void PeerIMS::BufferData() {
  // The peer dies if the player disconnects.
  player_alive_ = true;

  // The last chunk sent to the player.
  played_chunk_ = 0;

  // Counts the number of executions of the recvfrom() function.
  recvfrom_counter_ = 0;

  // The buffer of chunks is a structure that is used to delay the playback of
  // the chunks in order to accommodate the network jittter. Two components are
  // needed: (1) the "chunks" buffer that stores the received chunks and (2) the
  // "received" buffer that stores if a chunk has been received or not. Notice
  // that each peer can use a different buffer_size: the smaller the buffer
  // size, the lower start-up time, the higher chunk-loss ratio. However, for
  // the sake of simpliticy, all peers will use the same buffer size.

  chunks_.resize(buffer_size_);
  received_counter_ = 0;

  // Wall time (execution time plus waiting time).
  clock_t start_time = clock();

  // We will send a chunk to the player when a new chunk is received. Besides,
  // those slots in the buffer that have not been filled by a new chunk will not
  // be send to the player. Moreover, chunks can be delayed an unknown time.
  // This means that (due to the jitter) after chunk X, the chunk X+Y can be
  // received (instead of the chunk X+1). Alike, the chunk X-Y could follow the
  // chunk X. Because we implement the buffer as a circular queue, in order to
  // minimize the probability of a delayed chunk overwrites a new chunk that is
  // waiting for traveling the player, we wil fill only the half of the circular
  // queue.

  LOG("(" + team_socket_.local_endpoint().address().to_string() + "," +
      std::to_string(team_socket_.local_endpoint().port()) + ")" +
      "\b: buffering = 000.00%");
  TraceSystem::logStream().flush();

  // First chunk to be sent to the player.  The process_next_message() procedure
  // returns the chunk number if a packet has been received or -2 if a time-out
  // exception has been arised.

  int chunk_number = ProcessNextMessage();
  while (chunk_number < 0) {
    chunk_number = ProcessNextMessage();
    LOG(std::to_string(chunk_number));
  }
  played_chunk_ = chunk_number;
  LOG("First chunk to play " + std::to_string(played_chunk_));
  LOG("(" + team_socket_.local_endpoint().address().to_string() + "," +
      std::to_string(team_socket_.local_endpoint().port()) + ")" +
      "\b: buffering (\b" + std::to_string(100.0 / buffer_size_));
  // TODO: Justify: .rjust(4)

  // Now, fill up to the half of the buffer.

  float BUFFER_STATUS = 0.0f;
  for (int x = 0; x < buffer_size_ / 2; x++) {
    // TODO Format string
    // LOG("{:.2%}\r".format((1.0*x)/(buffer_size_/2)), end='');
    BUFFER_STATUS = (100 * x) / (buffer_size_ / 2.0f) + 1;

    // if(!Common.CONSOLE_MODE){
    //    GObject.idle_add(buffering_adapter.update_widget,BUFFER_STATUS)
    // }else{
    //    pass
    //}
    // LOG("!", end='')
    TraceSystem::logStream().flush();

    while (ProcessNextMessage() < 0)
      ;
  }

  LOG("");
  LOG("latency = " +
      std::to_string((clock() - start_time) / (float)CLOCKS_PER_SEC) +
      " seconds");
  LOG("buffering done.");
  TraceSystem::logStream().flush();
}

int PeerIMS::ProcessNextMessage() {
  // (Chunk number + chunk payload) length
  std::vector<char> message(sizeof(unsigned short) + chunk_size_);
  boost::asio::ip::udp::endpoint sender;

  try {
    ReceiveTheNextMessage(&message, sender);
  } catch (std::exception e) {
    return -2;
  }

  return ProcessMessage(message, sender);
}

void PeerIMS::ReceiveTheNextMessage(std::vector<char> *message,
                                    boost::asio::ip::udp::endpoint sender) {
  LOG("Waiting for a chunk at (" +
      team_socket_.local_endpoint().address().to_string() + "," +
      std::to_string(team_socket_.local_endpoint().port()) + ")");

  team_socket_.receive_from(boost::asio::buffer(*message), sender);
  recvfrom_counter_ += 1;

  LOG("Received a message from (" + sender.address().to_string() + "," +
      std::to_string(sender.port()) + ") of length " +
      std::to_string(message->size()));

  // TODO: if(DEBUG){
  if (message->size() < 10) {
    LOG("Message content =" + std::string(message->data()));
  }
  //}
}

int PeerIMS::ProcessMessage(std::vector<char> message,
                            boost::asio::ip::udp::endpoint sender) {
  // Ojo, an attacker could send a packet smaller and pollute the buffer,
  // althought this is difficult in IP multicst. This method should be
  // inheritaged to solve this issue.

  unsigned short chunk_number = ntohs(*(short *)message.data());

  chunks_[chunk_number % buffer_size_] = {
      std::vector<char>(message.data() + sizeof(unsigned short),
                        message.data() + message.size()),
      true};

  received_counter_ += 1;

  return chunk_number;
}

std::string PeerIMS::GetMcastAddr() { return mcast_addr_.to_string(); }

void PeerIMS::SetShowBuffer(bool show_buffer) { show_buffer_ = show_buffer; }
}
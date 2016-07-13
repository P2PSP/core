//
//  splitter_ims.cc -- Ip Multicast Set of rules
//
//  This code is distributed under the GNU General Public License (see
//  THE_GENERAL_GNU_PUBLIC_LICENSE.txt for extending this information).
//  Copyright (C) 2016, the P2PSP team.
//  http://www.p2psp.org
//

#include "splitter_ims.h"
#include "../util/trace.h"

namespace p2psp {
  using namespace std;
  using namespace boost;

  const std::string Splitter_IMS::kMCastAddr = "224.0.0.1";  // All Systems on this subnet
  const unsigned short Splitter_IMS::kMcastPort = 8001;
  const int Splitter_IMS::kTTL = 1;                          // Time To Live of multicast packets

  Splitter_IMS::Splitter_IMS()
    : mcast_group_(boost::asio::ip::address::from_string(kMCastAddr), kMcastPort) {

    /*mcast_addr_ = kMCastAddr;
      mcast_port_ = kMcastPort;*/
    ttl_ = kTTL;

    TRACE("IMS initialized");
  }

  Splitter_IMS::~Splitter_IMS() {}


  void Splitter_IMS::SetupTeamSocket() {
    system::error_code ec;

    TRACE("mcast_group = " << mcast_group_);
    team_socket_.open(mcast_group_.protocol());

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

  void Splitter_IMS::SendMcastGroup(const std::shared_ptr<boost::asio::ip::tcp::socket> &peer_serve_socket) {
    TRACE("Communicating the multicast group ("
	  << mcast_group_.address().to_string()//mcast_addr_
	  << ", "
	  << to_string(mcast_group_.port())
	  << ")");

    char message[6];
    in_addr addr;
    inet_aton(/*mcast_addr_*/mcast_group_.address().to_string().c_str(), &addr);
    (*(in_addr *)&message) = addr;
    (*(uint16_t *)(message + 4)) = htons(mcast_group_.port());
    peer_serve_socket->send(asio::buffer(message));
  }

  void Splitter_IMS::SendConfiguration(const std::shared_ptr<boost::asio::ip::tcp::socket> &sock) {
    Splitter_core::SendConfiguration(sock);
    SendMcastGroup(sock);
  }

  void Splitter_IMS::HandleAPeerArrival(std::shared_ptr<asio::ip::tcp::socket> serve_socket) {
    TRACE(serve_socket->local_endpoint().address().to_string()
	  << "\b: IMS: accepted connection from peer ("
          << serve_socket->remote_endpoint().address().to_string() << ", "
          << to_string(serve_socket->remote_endpoint().port())
	  << ")");

    SendConfiguration(serve_socket);
    serve_socket->close();
  }

  void Splitter_IMS::Run() {
    TRACE("Run");

    ConfigureSockets();
    RequestTheVideoFromTheSource();

    // asio::ip::tcp::socket serve_socket(io_service_);
    std::shared_ptr<asio::ip::tcp::socket> serve_socket =
      make_shared<asio::ip::tcp::socket>(boost::ref(io_service_));
    acceptor_.accept(*serve_socket);
    HandleAPeerArrival(serve_socket);

    thread t(bind(&Splitter_IMS::HandleArrivals, this));

    asio::streambuf chunk;

    vector<char> message(sizeof(uint16_t) + chunk_size_);
    size_t bytes_transferred;

    while (alive_) {
      bytes_transferred = ReceiveChunk(chunk);

      (*(uint16_t *)message.data()) = htons(chunk_number_);

      copy(asio::buffer_cast<const char *>(chunk.data()),
           asio::buffer_cast<const char *>(chunk.data()) + chunk.size(),
	   message.data() + sizeof(uint16_t));

      TRACE("---- > mcast_group = " << mcast_group_);
      SendChunk(message, mcast_group_);

      chunk_number_ = (chunk_number_ + 1) % Common::kMaxChunkNumber;
      chunk.consume(bytes_transferred);
    }
  }

  std::string Splitter_IMS::GetMcastAddr() {
    return mcast_group_.address().to_string()/*mcast_addr_*/;
  }

  unsigned short Splitter_IMS::GetMcastPort() {
    return mcast_group_.port();
  }

  int Splitter_IMS::GetTTL() {
    return ttl_;
  }

  void Splitter_IMS::Start() {
    TRACE("Start");
    thread_.reset(new boost::thread(boost::bind(&Splitter_IMS::Run, this)));
  }

  std::string Splitter_IMS::GetDefaultMcastAddr() {
    return kMCastAddr;
  }

  int Splitter_IMS::GetDefaultTTL() {
    return kTTL;
  }

  unsigned short Splitter_IMS::GetDefaultMcastPort() {
    return kMcastPort;
  }

  void Splitter_IMS::SetMcastAddr(std::string addr) {
    //mcast_addr_ = mcast_addr;
    /*boost::asio::ip::udp::endpoint
      tmp(boost::asio::ip::address::from_string(addr),
	  mcast_group_.port());
	  mcast_group_ = tmp;*/
    mcast_group_.address(boost::asio::ip::address::from_string(addr));
  }

  void Splitter_IMS::SetMcastPort(unsigned short port) {
    //mcast_port_ = mcast_port;
    /*mcast_group_.port() = port;
    boost::asio::ip::udp::endpoint
      tmp(mcast_group_.address(),
	  port);
	  mcast_group_ = tmp;*/
    mcast_group_.port(port);
  }

}


#include "peer_dbs.h"

namespace p2psp {

PeerDBS::PeerDBS() {
  LOG("max_chunk_debt =" << std::to_string(kMaxChunkDebt));
  LOG("Initialized");
}

PeerDBS::~PeerDBS() {}

void PeerDBS::SayHello(ip::udp::endpoint node) {
  std::vector<char> hello(1);
  hello[0] = 'H';

  team_socket_.send_to(buffer(hello), node);

  LOG("[Hello] sent to "
      << "(" << node.address().to_string() << "," << std::to_string(node.port())
      << ")");
}

void PeerDBS::SayGoodbye(ip::udp::endpoint node) {
  std::vector<char> goodbye(1);
  goodbye[0] = 'G';

  team_socket_.send_to(buffer(goodbye), node);

  LOG("[Goodbye] sent to "
      << "(" << node.address().to_string() << "," << std::to_string(node.port())
      << ")");
}

void PeerDBS::ReceiveMagicFlags() {
  std::vector<char> magic_flags(1);
  ip::udp::endpoint sender;

  team_socket_.receive_from(buffer(magic_flags), sender);

  LOG("Magic flags =" << std::bitset<8>(magic_flags[0]));
}

void PeerDBS::ReceiveTheNumberOfPeers() {
  boost::array<char, 2> buffer;

  // sys.stdout.write(Color.green)
  LOG("Requesting the number of monitors and peers to ("
      << splitter_socket_.remote_endpoint().address().to_string() << ","
      << std::to_string(splitter_socket_.remote_endpoint().port()) << ")");
  read(splitter_socket_, ::buffer(buffer));
  number_of_monitors_ = ntohs(*(short *)(buffer.c_array()));
  LOG("The number of monitors is " << number_of_monitors_);
  read(splitter_socket_, ::buffer(buffer));
  number_of_peers_ = ntohs(*(short *)(buffer.c_array()));
  LOG("The size of the team is " << number_of_peers_ << " (apart from me)");
}

void PeerDBS::ReceiveTheListOfPeers() {
  boost::array<char, 6> buffer;
  char *raw_data;
  ip::address ip_addr;
  ip::udp::endpoint peer;
  int port;

  // sys.stdout.write(Color.green)
  LOG("Requesting" << number_of_peers_ << " peers to ("
                   << splitter_socket_.remote_endpoint().address().to_string()
                   << ","
                   << std::to_string(splitter_socket_.remote_endpoint().port())
                   << ")");
  // number_of_peers =
  // socket.ntohs(struct.unpack("H",self.splitter_socket.recv(struct.calcsize("H")))[0])
  //_print_("The size of the team is", number_of_peers, "(apart from me)")

  int tmp = number_of_peers_;

  raw_data = buffer.c_array();

  in_addr ip_raw = *(in_addr *)(raw_data);
  mcast_addr_ = ip::address::from_string(inet_ntoa(ip_raw));
  mcast_port_ = ntohs(*(short *)(raw_data + 4));

  while (tmp > 0) {
    read(splitter_socket_, ::buffer(buffer));
    in_addr ip_raw = *(in_addr *)(raw_data);
    ip_addr = ip::address::from_string(inet_ntoa(ip_raw));
    port = ntohs(*(short *)(raw_data + 4));

    peer = ip::udp::endpoint(ip_addr, port);
    LOG("[hello] sent to (" << peer.address().to_string() << ","
                            << std::to_string(peer.port()) << ")");
    SayHello(peer);

    // TODO: Find a __debug__ flag in c++
    /*if(true){
      LOG("[%5d]" % tmp, peer);
    }else{*/
    LOG(std::to_string((number_of_peers_ - tmp) / number_of_peers_));

    peer_list_.push_back(peer);
    debt_[peer] = 0;
    tmp--;
    //}
  }

  LOG("List of peers received");
}

void PeerDBS::ReceiveMyEndpoint() {
  boost::array<char, 6> buffer;
  char *raw_data;
  ip::address ip_addr;
  ip::udp::endpoint peer;
  int port;

  read(splitter_socket_, ::buffer(buffer));
  in_addr ip_raw = *(in_addr *)(raw_data);
  ip_addr = ip::address::from_string(inet_ntoa(ip_raw));
  port = ntohs(*(short *)(raw_data + 4));

  me_ = ip::udp::endpoint(ip_addr, port);

  LOG("me = (" << me_.address().to_string() << "," << std::to_string(me_.port())
               << ")");
}

void PeerDBS::ListenToTheTeam() {
  ip::udp::endpoint endpoint(ip::address_v4::any(),
                             splitter_socket_.local_endpoint().port());

  team_socket_.open(endpoint.protocol());
  team_socket_.set_option(ip::udp::socket::reuse_address(true));
  team_socket_.bind(endpoint);

  // This is the maximum time the peer will wait for a chunk
  // (from the splitter or from another peer).
  team_socket_.set_option(socket_base::linger(true, 30));
}
}
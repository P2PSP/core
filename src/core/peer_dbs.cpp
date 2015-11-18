
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
}

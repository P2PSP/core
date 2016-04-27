//
//  peer_strpeds.cc
//  P2PSP
//
//  This code is distributed under the GNU General Public License (see
//  THE_GENERAL_GNU_PUBLIC_LICENSE.txt for extending this information).
//  Copyright (C) 2016, the P2PSP team.
//  http://www.p2psp.org
//

#include "peer_strpeds.h"

namespace p2psp {

void PeerSTRPEDS::Init() {
  // message_format variable is not used in C++
  // self.message_format += '40s40s'
  bad_peers_ = std::vector<ip::udp::endpoint>();

  LOG("Initialized");
}

bool PeerSTRPEDS::IsCurrentMessageFromSplitter() {
  return current_sender_ == splitter_;
}
void PeerSTRPEDS::ReceiveTheNextMessage(std::vector<char> &message,
                                        ip::udp::endpoint &sender) {
  PeerIMS::ReceiveTheNextMessage(message, sender);
  current_sender_ = sender;
}
void PeerSTRPEDS::ReceiveDsaKey() {
  std::vector<char> message(256+256+256+40);
  read(splitter_socket_, ::buffer(message));

  TRACE("Ready to receive DSA Key");

  char *y = new char[256];
  char *g = new char[256];
  char *p = new char[256];
  char *q = new char[40];

  std::copy(message.data(), message.data() + 256, y);
  std::copy(message.data() + 256, message.data() + 256 + 256, g);
  std::copy(message.data() + 256 + 256, message.data() + 256 + 256 +256, p);
  std::copy(message.data() + 256 + 256 + 256, message.data() + 256 + 256 +256 + 40, q);

  dsa_key = DSA_new();

  BN_hex2bn(&dsa_key->pub_key,y);
  BN_hex2bn(&dsa_key->g,g);
  BN_hex2bn(&dsa_key->p,p);
  BN_hex2bn(&dsa_key->q,q);


  delete[] y; delete[] g; delete[] p; delete[] q;

  TRACE("DSA key received");

}

void PeerSTRPEDS::ProcessBadMessage(const std::vector<char> &message,
                                    const ip::udp::endpoint &sender) {
  LOG("bad peer: " << sender);
  bad_peers_.push_back(sender);
  peer_list_.erase(std::find(peer_list_.begin(), peer_list_.end(), sender));
}

bool PeerSTRPEDS::IsControlMessage(std::vector<char> message) {
  return message.size() != (1026 + 40 + 40);
}

bool PeerSTRPEDS::CheckMessage(std::vector<char> message,
                               ip::udp::endpoint sender) {
  if (std::find(bad_peers_.begin(), bad_peers_.end(), sender) ==
      bad_peers_.end()) {
    return false;
  }

  if (!IsControlMessage(message)) {

	  uint16_t chunk_number = *(uint16_t *)(message.data());

	  std::vector<char> chunk(chunk_size_);
	  std::copy(message.data() + sizeof(uint16_t), message.data() + sizeof(uint16_t) + chunk_size_, chunk.data());

	  char* sigr[40];
	  std::copy(message.data() + sizeof(uint16_t) + chunk_size_, message.data() + sizeof(uint16_t) + chunk_size_ + 40, sigr);
	  char* sigs[40];
	  std::copy(message.data() + sizeof(uint16_t) + chunk_size_ + 40, message.data() + sizeof(uint16_t) + chunk_size_ + 40 + 40, sigs);

	  std::vector<char> h(256);
	  std::vector<char> m(2+1024+40+40);
	  boost::asio::ip::udp::endpoint dst = team_socket_.local_endpoint();

	  (*(uint16_t *)m.data()) = htons(chunk_number);

	  std::copy(chunk.data(), chunk.data() + chunk.size(), m.data() + sizeof(uint16_t));

	  (*(boost::asio::ip::udp::endpoint *)(m.data() + chunk.size() + sizeof(uint16_t))) = dst;

	  Common::sha256(m, h);

	  return DSA_verify(0, (unsigned char *)h.data() , h.size(), signature, strlen(reinterpret_cast<char*>(signature)), dsa_key);
  }

  return true;
}

int PeerSTRPEDS::HandleBadPeersRequest() {
  std::string bad("bad");
  std::vector<char> header(5);
  std::vector<char> msg(8);
  std::copy(bad.begin(), bad.end(), header.begin());
  *((uint16_t *)(header.data() + bad.size())) = (uint16_t)bad_peers_.size();

  team_socket_.send_to(buffer(header), splitter_);

  for (std::vector<ip::udp::endpoint>::iterator peer = bad_peers_.begin();
       peer != bad_peers_.end(); ++peer) {
    char *raw_ip = (char *)((*peer).address().to_v4().to_ulong());
    in_addr net_ip;
    inet_aton(raw_ip, &net_ip);

    std::memcpy(msg.data(), &net_ip, sizeof(net_ip));
    int port = peer->port();
    std::memcpy(msg.data() + sizeof(net_ip), &port, sizeof(port));

    team_socket_.send_to(buffer(msg), splitter_);
  }

  return -1;
}

int PeerSTRPEDS::ProcessMessage(const std::vector<char> &message,
                                const ip::udp::endpoint &sender) {
  if (std::find(bad_peers_.begin(), bad_peers_.end(), sender) ==
      bad_peers_.end()) {
    return -1;
  }

  if (IsCurrentMessageFromSplitter() || CheckMessage(message, sender)) {
    if (IsControlMessage(message) and (message[0] == 'B')) {
      return HandleBadPeersRequest();
    } else {
      return PeerDBS::ProcessMessage(message, sender);
    }
  } else {
    ProcessBadMessage(message, sender);
  }

  return -1;
}
}

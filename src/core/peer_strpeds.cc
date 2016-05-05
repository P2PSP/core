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
  message_size_=kChunkIndexSize+chunk_size_+40+40;

}

void PeerSTRPEDS::ProcessBadMessage(const std::vector<char> &message,
                                    const ip::udp::endpoint &sender) {
  LOG("bad peer: " << sender);
  bad_peers_.push_back(sender);
  peer_list_.erase(std::find(peer_list_.begin(), peer_list_.end(), sender));
}

bool PeerSTRPEDS::IsControlMessage(std::vector<char> message) {
	TRACE("Control message: " <<  message.size());
	return message.size() != (sizeof(uint16_t) + chunk_size_ + 40 + 40);
}

bool PeerSTRPEDS::CheckMessage(std::vector<char> message,
                               ip::udp::endpoint sender) {
  TRACE("Check Message");
  if (std::find(bad_peers_.begin(), bad_peers_.end(), sender) !=
      bad_peers_.end()) {
	  TRACE("Sender is in bad peer list");
    return false;
  }

  if (!IsControlMessage(message)) {

	  uint16_t chunk_number = ntohs(*(short *)message.data());
	  std::vector<char> chunk(chunk_size_);
	  std::copy(message.data() + sizeof(uint16_t), message.data() + sizeof(uint16_t) + chunk_size_, chunk.data());

	  char* sigr = new char[40];
	  std::copy(message.data() + sizeof(uint16_t) + chunk_size_, message.data() + sizeof(uint16_t) + chunk_size_ + 40, sigr);
	  char* sigs = new char[40];
	  std::copy(message.data() + sizeof(uint16_t) + chunk_size_ + 40, message.data() + sizeof(uint16_t) + chunk_size_ + 40 + 40, sigs);

	  std::vector<char> h(32);
	  std::vector<char> m(2 + 1024 + 4 + 2);
	  boost::asio::ip::udp::endpoint dst = sender;//team_socket_.local_endpoint();

	  (*(uint16_t *)m.data()) = htons(chunk_number);

	  std::copy(chunk.data(), chunk.data() + chunk_size_, m.data() + sizeof(uint16_t));

	  in_addr addr;
	  inet_aton(dst.address().to_string().c_str(), &addr);

	  (*(in_addr *)(m.data() + chunk_size_ + sizeof(uint16_t))) = addr;
	  (*(uint16_t *)(m.data() + chunk_size_ + sizeof(uint16_t) + 4)) = htons(dst.port());

	  LOG("chunk " + std::to_string(htons(chunk_number)) +" -> " + std::to_string(chunk_number) + "dst= " + dst.address().to_string() + ":" + std::to_string(dst.port()));
	  Common::sha256(m, h);

	  /*
	  std::string str(h.begin(), h.end());
	  LOG("HASH= " + str);

	  LOG(" ----- MESSAGE ----- ")
	  std::string b(m.begin(), m.end());
	  LOG(b);
	  LOG(" ---- FIN MESSAGE ----")
	   */

	  DSA_SIG* sig = DSA_SIG_new();

	  BN_hex2bn(&sig->r, sigr);
	  BN_hex2bn(&sig->s, sigs);

	  if (DSA_do_verify((unsigned char*)h.data(), h.size(), sig, dsa_key)){
		  DSA_SIG_free(sig);
		  delete[] sigr; delete[] sigs;
		  TRACE("Sender is clean: sign verified");
		  return true;
	  }else{
		  TRACE("Sender is bad: sign doesn't match");
		  return false;
	  }
  }
  TRACE("Sender sent a control message: " + std::to_string(message.size()));
  return true;
}

int PeerSTRPEDS::HandleBadPeersRequest() {
  std::string bad("bad");
  std::vector<char> header(5);
  std::vector<char> msg(8);

  std::copy(bad.begin(), bad.end(), header.begin());

  *((uint16_t *)(header.data() + bad.size())) = (uint16_t)bad_peers_.size();

  std::string str(header.begin(),header.end());
  TRACE("BAD = " + str + " peer size= " + std::to_string(bad_peers_.size()));

  team_socket_.send_to(buffer(header), splitter_);

  TRACE("Bad Header sent to the splitter");

  std::vector<ip::udp::endpoint>::iterator peer;
  for ( peer = bad_peers_.begin(); peer != bad_peers_.end(); peer++) {
    in_addr net_ip;
    inet_aton((*peer).address().to_string().c_str(), &net_ip);
    std::memcpy(msg.data(), &net_ip, sizeof(net_ip));
    int port = htons(peer->port());
    LOG("PUERTO: " + std::to_string(port));
    std::memcpy(msg.data() + sizeof(net_ip), &port, sizeof(port));
    team_socket_.send_to(buffer(msg), splitter_);
  }

  return -1;
}

int PeerSTRPEDS::ProcessMessage(const std::vector<char> &message,
                                const ip::udp::endpoint &sender) {
  if (std::find(bad_peers_.begin(), bad_peers_.end(), sender) !=
      bad_peers_.end()) {
	  TRACE("Sender is in the bad peer list");
    return -1;
  }


  if (IsCurrentMessageFromSplitter() || CheckMessage(message, sender)) {
    if (IsControlMessage(message) and (message[0] == 'B')) {
    	TRACE("Go to HandleBadPeersRequest")
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

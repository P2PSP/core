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
  magic_flags_ = Common::kSTRPE;
  played_ = 0;
  losses_ = 0;
  ready_to_leave_the_team_ = false;
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

  char y[256];
  char g[256];
  char p[256];
  char q[40];

  std::string msg(message.begin(), message.end());

  //LOG("message: " + msg);
  // ERROR here: Check if this proccess is correct.

  LOG("**** DSA key *****");
  dsa_key = DSA_new();

  strcpy(y, msg.substr(0,256).c_str());
  BN_hex2bn(&dsa_key->pub_key,y);
  //LOG("pub_key: " << y);

  strcpy(g, msg.substr(256,256).c_str());
  BN_hex2bn(&dsa_key->g,g);
  //LOG("g: " << g);

  strcpy(p, msg.substr(512,256).c_str());
  BN_hex2bn(&dsa_key->p,p);
  //LOG("p: " << p);

  strcpy(q, msg.substr(768,40).c_str());
  BN_hex2bn(&dsa_key->q,q);
  //LOG("q: " << q);

  TRACE("DSA key received");
  message_size_=4+kChunkIndexSize+chunk_size_+40+40;

}

void PeerSTRPEDS::ProcessBadMessage(const std::vector<char> &message,
                                    const ip::udp::endpoint &sender) {
  LOG("bad peer: " << sender);
  bad_peers_.push_back(sender);
  peer_list_.erase(std::find(peer_list_.begin(), peer_list_.end(), sender));
}

bool PeerSTRPEDS::IsControlMessage(std::vector<char> message) {
	TRACE("Control message: " <<  message.size());
	return message.size() != (sizeof(uint32_t) + sizeof(uint16_t) + chunk_size_ + 40 + 40);
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
	  LOG("MESSAGE SIZE: " << message.size() << " from " << sender.port());
	  uint16_t chunk_number = ntohs(*(short *)message.data());
	  std::vector<char> chunk(chunk_size_);
	  std::copy(message.data() + sizeof(uint16_t), message.data() + sizeof(uint16_t) + chunk_size_, chunk.data());

	  char sigr[41]; sigr[40]=0;
	  std::copy(message.data() + sizeof(uint16_t) + chunk_size_, message.data() + sizeof(uint16_t) + chunk_size_ + 40, sigr);
	  char sigs[41]; sigs[40]=0;
	  std::copy(message.data() + sizeof(uint16_t) + chunk_size_ + 40, message.data() + sizeof(uint16_t) + chunk_size_ + 40 + 40, sigs);

	  std::vector<char> m(2 + chunk_size_ + 4 + 2);
	  boost::asio::ip::udp::endpoint dst = sender;//team_socket_.local_endpoint();

	  (*(uint16_t *)m.data()) = htons(chunk_number);

	  std::copy(chunk.data(), chunk.data() + chunk_size_, m.data() + sizeof(uint16_t));

	  in_addr addr;
	  inet_aton(dst.address().to_string().c_str(), &addr);

	  (*(in_addr *)(m.data() + chunk_size_ + sizeof(uint16_t))) = addr;
	  (*(uint16_t *)(m.data() + chunk_size_ + sizeof(uint16_t) + 4)) = htons(dst.port());

	  //LOG("chunk " + std::to_string(chunk_number) + "dst= " + dst.address().to_string() + ":" + std::to_string(dst.port()));
	  std::vector<char> h(32);
	  Common::sha256(m, h);

	  //LOG("TAMANO: "+ std::to_string(h.size()));

	  /*
	  std::string str(h.begin(), h.end());
	  LOG("HASH= " + str);


	  LOG(" ----- MESSAGE ----- ");
	  std::string b(m.begin(), m.end());
	  LOG(b);
	  LOG(" ---- FIN MESSAGE ----");


	  LOG(" ---- SIGNATURES ----");
	  LOG("->" << sigr << "<-");
	  LOG("->" << sigs << "<-");
	  LOG(" ---- FIN SIGNATURES ----");
	   */

	  DSA_SIG* sig = DSA_SIG_new();

	  BN_hex2bn(&sig->r, sigr);
	  BN_hex2bn(&sig->s, sigs);

	 LOG("Size r: " << *(sig->r->d));
	 LOG("Size s: " << *(sig->s->d));

	  if (DSA_do_verify((unsigned char*)h.data(), h.size(), sig, dsa_key)){
		  TRACE("Sender is clean: sign verified. CN: " + std::to_string(chunk_number));
		  return true;
	  }else{
		  TRACE("Sender is bad: sign doesn't match CN: " + std::to_string(chunk_number));
		  return false;
	  }

	  DSA_SIG_free(sig);

  }else{
	  TRACE("Sender sent a control message: " + std::to_string(message.size()));
  }
  return true;
}

int PeerSTRPEDS::HandleBadPeersRequest() {
  if (bad_peers_.size() > 0){
    std::string bad("B");
    std::vector<char> msg(bad.size() + sizeof(uint16_t) + (bad_peers_.size()*6) + 1);
    ip::udp::endpoint peer;

    std::copy(bad.begin(), bad.end(), msg.data());

    *((uint16_t *)(msg.data() + bad.size())) = htons((uint16_t)bad_peers_.size());

    TRACE("SIZE: " << ntohs(*((uint16_t *)(msg.data() + bad.size()))));
    for (unsigned int i = 0; i < bad_peers_.size(); i++){
      peer = bad_peers_.at(i);
      in_addr net_ip;
      inet_aton(peer.address().to_string().c_str(), &net_ip);
      (*(in_addr *) (msg.data() + bad.size() + sizeof(uint16_t) + (6*i))) = net_ip;
      uint16_t port = htons(peer.port());
      (*(uint16_t *)(msg.data() + bad.size() + sizeof(uint16_t) + (6*i) + sizeof(net_ip))) = port;
      uint16_t p = ntohs(*(uint16_t *)(msg.data() + 1 + sizeof(uint16_t) + (6*i) + sizeof(net_ip)));
      TRACE("P " << p);
    }

    msg.at(msg.size()-1) = 0;
    team_socket_.send_to(buffer(msg), splitter_);

    std::string s(msg.begin(), msg.end());
    LOG("Message List: " << s);
    TRACE("Bad Header sent to the splitter");

    bad_peers_.clear();
    player_alive_ = false;
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

  // --------------- For current round ---------------------
  if (!IsControlMessage(message) and IsCurrentMessageFromSplitter()){
	  current_round_ = ntohl(*(uint32_t *)(message.data() + sizeof(uint16_t) + chunk_size_ + 40 + 40));
  	  LOG("Current Round: " << current_round_);
	  if (logging_ and latest_chunk_number_ != 0) {
		LogMessage("buffer correctnes " + std::to_string(CalcBufferCorrectness()));
	    LogMessage("buffer filling " + std::to_string(CalcBufferFilling()));
	    if (played_ > 0 and played_ >= (int) peer_list_.size()){
	      TRACE("Losses in the previous round: " << losses_ << " played " << played_);
	      LogMessage("buffer fullness " + std::to_string((float)losses_ / (float)played_));
	      losses_ = 0;
	      played_ = 0;
	    }
	  }
  }
  //---------------------

  if (IsCurrentMessageFromSplitter() or CheckMessage(message, sender)) {
    if (IsControlMessage(message) and (message[0] == 'B')) {
      return HandleBadPeersRequest();
    } else {
      return PeerDBS::ProcessMessage(message, sender);
    }
  } else {
    ProcessBadMessage(message, sender);
    //Informing to the splitter ASAP. Only TP will be taking into account.
    //return HandleBadPeersRequest();
  }

  return -1;
}

void PeerSTRPEDS::PlayNextChunk(int chunk_number) {

  for (int i = 0; i < (chunk_number-latest_chunk_number_);i++) {
	    if (chunks_[played_chunk_ % buffer_size_].received){
	    	//PlayChunk(played_chunk_);
	    	chunks_[played_chunk_ % buffer_size_].received = false;
	    	received_counter_--;
	    	LOG("Chunk Consumed at: " << played_chunk_ % buffer_size_);	       
	    }else{
	    	Complain(played_chunk_);
	    	losses_++;
	    	/*
	    	 if (logging_) {
	    		  LogMessage("chunk lost at " + std::to_string(played_chunk_ % buffer_size_));
	    	}
	    	*/
	    	LOG("Chunk lost at: " << played_chunk_ % buffer_size_);
	    }
	    played_++;
	 played_chunk_++;
	}

	if ((latest_chunk_number_ % Common::kMaxChunkNumber) < chunk_number)
			latest_chunk_number_=chunk_number;
  }

void PeerSTRPEDS::Complain(int chunk_number) {
  std::vector<char> message(2);
  uint16_t chunk_number_network = htons(chunk_number);
  std::memcpy(message.data(), &chunk_number_network, sizeof(uint16_t));

  team_socket_.send_to(buffer(message), splitter_);

  TRACE("lost chunk:" << std::to_string(chunk_number));
};

std::string PeerSTRPEDS::BuildLogMessage(const std::string &message) {
  // return "{0}\t{1}".format(repr(time.time()), message)
	return std::to_string(current_round_) + "\t" + message;
}

void PeerSTRPEDS::WaitForThePlayer() {}

void PeerSTRPEDS::ReceiveTheHeader() {
    int header_size_in_bytes = header_size_in_chunks_ * chunk_size_;
    std::vector<char> header(header_size_in_bytes);

    boost::system::error_code ec;
    streambuf chunk;

    read(splitter_socket_, chunk, transfer_exactly(header_size_in_bytes), ec);

    if (ec) {
      ERROR(ec.message());
      splitter_socket_.close();
      ConnectToTheSplitter();
    }

    TRACE("Received " << std::to_string(header_size_in_bytes)
          << "bytes of header");
  }

void PeerSTRPEDS::SetLogFile(const std::string &filename) {
  log_file_.open(filename);
}

void PeerSTRPEDS::SetLogging(bool enabled) { logging_ = enabled; }

uint32_t PeerSTRPEDS::GetCurrentRound(){return current_round_;}
void PeerSTRPEDS::SetCurrentRound(uint32_t current_round){current_round_=current_round;}
void PeerSTRPEDS::SetPlayerAlive(bool status){player_alive_ = status;}
}


//
//  splitter_strpe.cc
//  P2PSP
//
//  This code is distributed under the GNU General Public License (see
//  THE_GENERAL_GNU_PUBLIC_LICENSE.txt for extending this information).
//  Copyright (C) 2016, the P2PSP team.
//  http://www.p2psp.org
//

#include "splitter_strpeds.h"

namespace p2psp {
using namespace std;
using namespace boost;

SplitterSTRPEDS::SplitterSTRPEDS() :
		SplitterDBS(), logging_(kLogging), current_round_(kCurrentRound) {
	magic_flags_ = Common::kSTRPE;
	LOG("STrPeDS");
	digest_size_ = kDigestSize;
	gather_bad_peers_sleep_ = kGatherBadPeersSleep;
}

SplitterSTRPEDS::~SplitterSTRPEDS() {
	TRACE("USING STRPEDS");
}

void SplitterSTRPEDS::SetMajorityRatio(int majority_ratio) {
	majority_ratio_ = majority_ratio;
}

void SplitterSTRPEDS::HandleAPeerArrival(
		std::shared_ptr<boost::asio::ip::tcp::socket> serve_socket) {
	asio::ip::tcp::endpoint incoming_peer = serve_socket->remote_endpoint();
	TRACE("STRPEDS: Accepted connection from peer " << incoming_peer);
	SendConfiguration(serve_socket);
	SendTheListOfPeers(serve_socket);
	SendDsaKey(serve_socket);
	serve_socket->close();

	InsertPeer(boost::asio::ip::udp::endpoint(incoming_peer.address(),incoming_peer.port()));

	//InsertPeer(
	//		boost::asio::ip::udp::endpoint(incoming_peer.address(),
	//				incoming_peer.port()));
}

void SplitterSTRPEDS::SendDsaKey(
		const std::shared_ptr<boost::asio::ip::tcp::socket> &sock) {
	// send Public key (y), Sub-group generator (g), Modulus, finite field order (p), Sub-group order (q)
	// in one message
	char* y = new char[256];
	y = BN_bn2hex(dsa_key->pub_key);
	char* g = new char[256];
	g = BN_bn2hex(dsa_key->g);
	char* p = new char[256];
	p = BN_bn2hex(dsa_key->p);
	char* q = new char[40];
	q = BN_bn2hex(dsa_key->q);

	LOG("**** DSA key *****");
	LOG("pub_key: " << y);
	LOG("g: " << g);
	LOG("p: " << p);
	LOG("q: " << q);

	std::stringstream message;
	message << y << g << p << q;

	/*
	TRACE(
			"Sending DSA Key => Size pub_key: " + to_string(strlen(y)) + " g "
					+ to_string(strlen(g)) + " p " + to_string(strlen(p)) + " q "
					+ to_string(strlen(q)) + " message: " + message.str());
	*/
	sock->send(asio::buffer(message.str()));

    delete[] y; delete[] g; delete[] p; delete[] q;
}

void SplitterSTRPEDS::GatherBadPeers() {
  for (unsigned int i=0; i<trusted_peers_.size(); i++) {
     boost::asio::ip::udp::endpoint tp = trusted_peers_[i];
     RequestBadPeers(tp);
  }
}

asio::ip::udp::endpoint SplitterSTRPEDS::GetPeerForGathering() {
	gathering_counter_ = (gathering_counter_ + 1) % peer_list_.size();
	asio::ip::udp::endpoint peer = peer_list_[gathering_counter_];
	return peer;
}

asio::ip::udp::endpoint SplitterSTRPEDS::GetTrustedPeerForGathering() {
	if (trusted_peers_.size() > 0) {
		trusted_gathering_counter_ = (trusted_gathering_counter_ + 1)
				% trusted_peers_.size();

		if (std::find(peer_list_.begin(), peer_list_.end(),
				trusted_peers_[trusted_gathering_counter_])
				!= peer_list_.end()) {
			return trusted_peers_[trusted_gathering_counter_];
		}
	}
	throw null();
}

void SplitterSTRPEDS::RequestBadPeers(const asio::ip::udp::endpoint &dest) {
	team_socket_.send_to(asio::buffer("B"), dest);
}

void SplitterSTRPEDS::Run() {
	ReceiveTheHeader();
	InitKey();

	/* A DBS splitter runs 4 threads. The main one and the
	 "handle_arrivals" thread are equivalent to the daemons used
	 by the IMS splitter. "moderate_the_team" and
	 "reset_counters_thread" are new.
	 */

	TRACE("STRPEDS: waiting for the monitor peers ...");

	std::shared_ptr<asio::ip::tcp::socket> connection = make_shared<
			asio::ip::tcp::socket>(boost::ref(io_service_));
	acceptor_.accept(*connection);
	HandleAPeerArrival(connection);

	// Threads
	thread t1(bind(&SplitterIMS::HandleArrivals, this));
	thread t2(bind(&SplitterSTRPEDS::ModerateTheTeam, this));
	thread t3(bind(&SplitterDBS::ResetCountersThread, this));
	//thread t4(bind(&SplitterSTRPEDS::GatherBadPeers, this));

	vector<char> message(2 + chunk_size_ + 40 + 40 + 4);
	asio::ip::udp::endpoint peer;

	while (alive_) {
		asio::streambuf chunk;

		size_t bytes_transferred = ReceiveChunk(chunk);

		try {
			peer = peer_list_.at(peer_number_);
			/*
			 (*(uint16_t *)message.data()) = htons(chunk_number_);

			 copy(asio::buffer_cast<const char *>(chunk.data()),
			 asio::buffer_cast<const char *>(chunk.data()) + chunk.size(),
			 message.data() + sizeof(uint16_t));
			 */

			message = GetMessage(chunk_number_, chunk, peer);

			TRACE("sending a message with size " << message.size());
			SendChunk(message, peer);

			TRACE("Chunk_Number= " << chunk_number_ << " Buffer size: " << buffer_size_ << " Peer: " << peer.address().to_string() << ":" << peer.port());
			destination_of_chunk_[chunk_number_ % buffer_size_] = peer;
			chunk_number_ = (chunk_number_ + 1) % Common::kMaxChunkNumber;

			if (logging_) {
			  TRACE("PEER_NUMBER_ = " << peer_number_);
				if (peer_number_ == 0) {
					current_round_++;
					std::string message = to_string(current_round_)
							+ " " + to_string(peer_list_.size());

					for (unsigned int i=0; i<peer_list_.size(); i++){
						message	= message + " " + peer_list_.at(i).address().to_string() + ":" + std::to_string(peer_list_.at(i).port());
					}
					TRACE("LOG: " << message);
					LogMessage(message);
				}

			}

			if (peer_number_ == ((int) peer_list_.size()) - 1){
				OnRoundBeginning();

				for (unsigned int i=0; i<outgoing_peer_list_.size(); i++){
					RemovePeer(outgoing_peer_list_[i]);
					SayGoodbye(outgoing_peer_list_[i]);
				}

				outgoing_peer_list_.clear();
			}

			//TODO: Here or before logging?
			ComputeNextPeerNumber(peer);

		} catch (const std::out_of_range &oor) {
			TRACE("The monitor peer has died!");
			exit(-1);
		}

		chunk.consume(bytes_transferred);

	}
}

void SplitterSTRPEDS::InitKey() {
	dsa_key = DSA_generate_parameters(1024, NULL, 0, NULL, NULL, NULL, 0);
	DSA_generate_key(dsa_key);
}

std::vector<char> SplitterSTRPEDS::GetMessage(int chunk_number,
		const asio::streambuf &chunk,
		const boost::asio::ip::udp::endpoint &dst) {

	std::vector<char> m(2 + chunk_size_ + 4 + 2);

	(*(uint16_t *) m.data()) = htons(chunk_number);

	copy(asio::buffer_cast<const char *>(chunk.data()),
			asio::buffer_cast<const char *>(chunk.data()) + chunk_size_,
			m.data() + sizeof(uint16_t));

	in_addr addr;
	inet_aton(dst.address().to_string().c_str(), &addr);
	(*(in_addr *) (m.data() + chunk.size() + sizeof(uint16_t))) = addr;
	(*(uint16_t *) (m.data() + chunk.size() + sizeof(uint16_t) + 4)) = htons(dst.port());

	std::vector<char> h(32);
	Common::sha256(m, h);

	//TRACE("HASH");


	//std::string str(h.begin(), h.end());
	//LOG("Chunk Number " + std::to_string(chunk_number) + " dest " + dst.address().to_string() + ":"+ std::to_string(dst.port()) +" HASH= " + str);

	/*
	LOG(" ----- MESSAGE ----- ");
	std::string b(m.begin(), m.end());
	LOG(b);
	LOG(" ---- FIN MESSAGE ----");
	*/

	DSA_SIG *sig = DSA_do_sign((unsigned char*) h.data(), h.size(), dsa_key);

	LOG("R: " << *(sig->r->d));
	LOG("S: " << *(sig->s->d));

	char* sigr = new char[40];
	//char sigr[40];
	char* sigs = new char[40];
	//char sigs[40];
	sigr = BN_bn2hex(sig->r);
	sigs = BN_bn2hex(sig->s);

	/*
    LOG(" ---- SIGNATURES ----");
    LOG(sigr);
    LOG(sigs);
    LOG(" ---- FIN SIGNATURES ----");
	*/

	//TRACE("SINGATURE");

	std::vector<char> message(sizeof(uint16_t) + chunk_size_ + 40 + 40 + sizeof(uint32_t));

	copy(m.data(), m.data() + chunk_size_ + sizeof(uint16_t), message.data());
	copy(sigr, sigr + 40,
			message.data() + chunk_size_ + sizeof(uint16_t));
	copy(sigs, sigs + 40,
			message.data() + chunk_size_ + sizeof(uint16_t) + 40);
	(*(uint32_t *) (message.data() + chunk_size_ + sizeof(uint16_t) + 40 + 40)) = htonl(current_round_);

	/*
	LOG(" ----- MESSAGE CON SIGNATURE ----- ");
		std::string c(message.begin(), message.end());
		LOG(c);
	LOG(" ---- FIN MESSAGE ----");
	 */
	delete[] sigr; delete[] sigs;

	return message;

}

void SplitterSTRPEDS::AddTrustedPeer(
		const boost::asio::ip::udp::endpoint &peer) {
	trusted_peers_.push_back(peer);
}

/*
 size_t SplitterDBS::ReceiveMessage(std::vector<char> &message, boost::asio::ip::udp::endpoint &endpoint) {
 system::error_code ec;

 size_t bytes_transferred =
 team_socket_.receive_from(asio::buffer(message), endpoint, 0, ec);

 if (ec) {
 ERROR("Unexepected error: " << ec.message());
 }

 return bytes_transferred;
 }
 */

void SplitterSTRPEDS::ModerateTheTeam() {
	// TODO: Check if something fails and a try catch statement has to be added

	// Max: 50 peer (6 bytes for each one) + 3bytes for header
	std::vector<char> message(303, 0);
	asio::ip::udp::endpoint sender;

	TRACE("ALIVE?" + alive_);

	while (alive_) {
		size_t bytes_transferred = ReceiveMessage(message, sender);

		if (bytes_transferred == 2) {
		  /*
		    The peer complains about a lost chunk.

		    In this situation, the splitter counts the number of
		    complains. If this number exceeds a threshold, the
		    unsupportive peer is expelled from the
		    team.
		  */
		  if (find(trusted_peers_.begin(), trusted_peers_.end(), sender) != trusted_peers_.end()) {
		    //uint16_t lost_chunk_number = GetLostChunkNumber(message);
		    //asio::ip::udp::endpoint bad_peer = GetLosser(lost_chunk_number);
		    //HandleBadPeerFromTrusted(bad_peer, sender);
		    //LOG("Complaint from TP (" << sender.port() <<") about lost chunk " << lost_chunk_number << " by " << bad_peer.port());
		    uint16_t lost_chunk_number = GetLostChunkNumber(message);
		    //trusted_peers_discovered_.push_back(sender);
		    ProcessLostChunk(lost_chunk_number, sender);
		  }

		} else {
			/*
			 The peer wants to leave the team.

			 A !2-length payload means that the peer wants to go
			 away.
			 */

			if (message.at(0) == 'B'){
				LOG("Bad complaint received");

				if (find(trusted_peers_.begin(), trusted_peers_.end(), sender) != trusted_peers_.end()) {
					LOG("Complaint about bad peer from " << sender.address().to_string() << ":" << sender.port());
					ProcessBadPeersMessage(message, sender);
				}
			}

			// 'G'oodbye
			if (message.at(0) == 'G') {
			  if (find(trusted_peers_.begin(), trusted_peers_.end(), sender) == trusted_peers_.end()) {
			     LOG("Goodbye from WIP: " << sender);
			     ProcessGoodbye(sender);
			  }else{
			     LOG("Goodbye from TP: " << sender); 
			  }
			}
		}
	}

	LOG("Exiting moderate the team");
}

void SplitterSTRPEDS::ProcessBadPeersMessage(const std::vector<char> &message,
		const boost::asio::ip::udp::endpoint &sender) {

	std::string bad("B");
	boost::asio::ip::udp::endpoint bad_peer;

	boost::asio::ip::address ip_addr;
    uint16_t port;

	uint16_t bad_number = ntohs(*(uint16_t *) (message.data() + bad.size()));

	 std::string s(message.begin(), message.end());
	  LOG("Message List: " << s);

	LOG("Number of BAD: "+ std::to_string(bad_number));

	for (int i = 0; i < bad_number; i++) {

		in_addr ip_raw = *(in_addr *)(message.data() + bad.size() + sizeof(uint16_t) + (6*i));
		ip_addr = boost::asio::ip::address::from_string(inet_ntoa(ip_raw));

		TRACE("IP BAD: " << ip_addr.to_string());

		port = ntohs(*(uint16_t *)(message.data() + bad.size() + sizeof(uint16_t) + (6*i) + sizeof(ip_raw)));

		TRACE("PORT BAD: " << port);

		bad_peer = boost::asio::ip::udp::endpoint(ip_addr, port);

		TRACE("BAD Peer: " + bad_peer.address().to_string() + ":" + to_string(bad_peer.port()));

		if (std::find(trusted_peers_.begin(), trusted_peers_.end(), sender) != trusted_peers_.end()) {
				HandleBadPeerFromTrusted(bad_peer, sender);
		} else {
				//HandleBadPeerFromRegular(bad_peer, sdr);
		}

	}
}

void SplitterSTRPEDS::HandleBadPeerFromTrusted(
		const boost::asio::ip::udp::endpoint &bad_peer,
		const boost::asio::ip::udp::endpoint &sender) {
  if (std::find(peer_list_.begin(), peer_list_.end(), bad_peer) != peer_list_.end()) {
	AddComplain(bad_peer, sender);
	if (std::find(bad_peers_.begin(), bad_peers_.end(), bad_peer) == bad_peers_.end()) {
		bad_peers_.push_back(bad_peer);
		trusted_peers_discovered_.push_back(sender);
		LOG("TP discovered " << sender);
	}
	//PunishPeer(bad_peer, "by trusted");
  }
}

void SplitterSTRPEDS::HandleBadPeerFromRegular(
		const boost::asio::ip::udp::endpoint &bad_peer,
		const boost::asio::ip::udp::endpoint &sender) {
	AddComplain(bad_peer, sender);
	int x = complains_[complains_map_[bad_peer]].size()
			/ std::max(1, (int) (peer_list_.size() - 1));
	if (x >= majority_ratio_) {
		PunishPeer(bad_peer, "by majority decision");
	}
}

void SplitterSTRPEDS::AddComplain(
		const boost::asio::ip::udp::endpoint &bad_peer,
		const boost::asio::ip::udp::endpoint &sender) {
	if (complains_map_.find(bad_peer) != complains_map_.end()) {
		if (complains_map_.find(sender) == complains_map_.end()) {
			complains_[complains_map_[bad_peer]].push_back(sender);
		}
	} else {
		std::vector<boost::asio::ip::udp::endpoint> bads;
		bads.push_back(sender);
		complains_.push_back(bads);
		complains_map_.insert(
				std::pair<boost::asio::ip::udp::endpoint, int>(bad_peer,
						complains_.size() - 1));

	}
}

void SplitterSTRPEDS::PunishPeer(const boost::asio::ip::udp::endpoint &peer,
		std::string message) {

	if (std::find(peer_list_.begin(), peer_list_.end(), peer)
					!= peer_list_.end()) {
		if (logging_) {
				LogMessage(
						"bad peer " + peer.address().to_string() + ":"
								+ to_string(peer.port()) + "(" + message + ")");
		}

		LOG("!!! bad peer " << peer);

		RemovePeer(peer);
		LOG("Peer: " << peer << " removed" << message);

	}
}

void SplitterSTRPEDS::OnRoundBeginning(){
	RefreshTPs();
	PunishPeers();
	PunishTPs();
	GatherBadPeers();
}

void SplitterSTRPEDS::RefreshTPs(){

	trusted_file_.open("trusted.txt");
	if(trusted_file_.is_open()){
		std::string str;
		int index = 0;
		while (std::getline(trusted_file_, str)){
		  if (index >= (int) trusted_peers_.size()){
		    boost::char_separator<char> sep{":"};
		    boost::tokenizer<boost::char_separator<char>> tok{str, sep};
		    boost::tokenizer< boost::char_separator<char> >::iterator t = tok.begin();
		    boost::asio::ip::address address = boost::asio::ip::address::from_string(*t);
		    t++;
		    uint16_t port = atoi((*t).c_str());
		    //LOG("IP: " + address.to_string() + ":" + std::to_string(port));
		    AddTrustedPeer(boost::asio::ip::udp::endpoint(address,port));
		  }
		  index++;
		}
		TRACE("TP list updated. Size: " << trusted_peers_.size());
		trusted_file_.close();
	}else{
			ERROR("trusted.txt doesn't exist");
	}

}

void SplitterSTRPEDS::PunishPeers(){
	int r;
	for (unsigned int i =0; i<bad_peers_.size(); i++) {
				r = rand() % 100 + 1;
				if (r <= p_mpl_){
					PunishPeer(bad_peers_[i], "by trusted");
					bad_peers_.erase(remove(bad_peers_.begin(), bad_peers_.end(), bad_peers_[i]),
												 bad_peers_.end());
				}
	}

}

void SplitterSTRPEDS::PunishTPs(){
	int r;
	for (unsigned int i = 0; i<trusted_peers_discovered_.size(); i++) {
				r = rand() % 100 + 1;
				if (r <= p_tpl_){
				  //PunishPeer(trusted_peers_discovered_[i], "by splitter");
				  //trusted_peers_discovered_.erase(remove(trusted_peers_discovered_.begin(), trusted_peers_discovered_.end(), trusted_peers_discovered_[i]),
				  //trusted_peers_discovered_.end());
				  ProcessGoodbye(trusted_peers_discovered_[i]);
				  if (logging_) {
				    LogMessage("bad peer " + trusted_peers_discovered_[i].address().to_string() + ":"+ to_string(trusted_peers_discovered_[i].port()) + "(by splitter)");
				  }
				  LOG("Peer: " << trusted_peers_discovered_[i] << " removed" << "(by splitter)");
				  trusted_peers_discovered_.erase(remove(trusted_peers_discovered_.begin(), trusted_peers_discovered_.end(), trusted_peers_discovered_[i]), trusted_peers_discovered_.end());
				}
	}

}

void SplitterSTRPEDS::IncrementUnsupportivityOfPeer(
                                                const boost::asio::ip::udp::endpoint &peer) {
  bool peerExists = true;

  try {
	  if (find(trusted_peers_.begin(), trusted_peers_.end(), peer)
	  								== trusted_peers_.end()) {
		  losses_[peer] += 1;
	  }
  } catch (std::exception e) {
    TRACE("The unsupportive peer " << peer << " does not exist!");
    peerExists = false;
  }

  if (peerExists) {
    TRACE("" << peer << " has lost " << to_string(losses_[peer]) << " chunks");

    if (losses_[peer] > max_number_of_chunk_loss_) {
    	if (std::find(bad_peers_.begin(), bad_peers_.end(), peer) ==
    		      bad_peers_.end()) {
    			bad_peers_.push_back(peer);
    		}
    }
  }
}

void SplitterSTRPEDS::SetPMPL(int probability){
	p_mpl_=probability;
}
int SplitterSTRPEDS::GetPMPL(){
	return p_mpl_;
}
void SplitterSTRPEDS::SetPTPL(int probability){
	p_tpl_=probability;
}
int SplitterSTRPEDS::GetPTPL(){
	return p_tpl_;
}
void SplitterSTRPEDS::SetLogFile(const std::string &filename) {
  filename_ = filename;
}

void SplitterSTRPEDS::SetLogging(bool enabled) { logging_ = enabled; }

void SplitterSTRPEDS::LogMessage(const std::string &message) {
  log_file_.open(filename_, ofstream::out | ofstream::app);
	log_file_ << BuildLogMessage(message+"\n");
	log_file_.flush();
	log_file_.close();
	// TODO: Where to close the ofstream?
}

string SplitterSTRPEDS::BuildLogMessage(const std::string &message) {
	return to_string(current_round_) + "\t" + message;
}

void SplitterSTRPEDS::Start() {
	LOG("Start");
	thread_.reset(new boost::thread(boost::bind(&SplitterSTRPEDS::Run, this)));
}
}

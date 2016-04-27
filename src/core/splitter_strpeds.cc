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

  SplitterSTRPEDS::SplitterSTRPEDS()
    : SplitterDBS(), logging_(kLogging), current_round_(kCurrentRound) {
    magic_flags_ = Common::kSTRPE;
    LOG("STrPeDS");
  }
  
  SplitterSTRPEDS::~SplitterSTRPEDS() {
    TRACE("USING STRPEDS");
  }
  
  void SplitterSTRPEDS::SetMajorityRatio(int majority_ratio){
    majority_ratio_ = majority_ratio;
  }

  void SplitterSTRPEDS::HandleAPeerArrival(std::shared_ptr<boost::asio::ip::tcp::socket> serve_socket) {
    asio::ip::tcp::endpoint incoming_peer = serve_socket->remote_endpoint();
    TRACE("Accepted connection from peer " << incoming_peer);
    SendConfiguration(serve_socket);
    SendTheListOfPeers(serve_socket);
    SendDsaKey(serve_socket);
    serve_socket->close();
    InsertPeer(boost::asio::ip::udp::endpoint(incoming_peer.address(), incoming_peer.port()));
  }

  void SplitterSTRPEDS::SendDsaKey(const std::shared_ptr<boost::asio::ip::tcp::socket> &sock){
    // send Public key (y), Sub-group generator (g), Modulus, finite field order (p), Sub-group order (q)
    // in one message  
    char* y = BN_bn2hex(dsa_key->pub_key);
    char* g = BN_bn2hex(dsa_key->g);
    char* p = BN_bn2hex(dsa_key->p);
    char* q = BN_bn2hex(dsa_key->q);

    std::stringstream message;
    message << y << g << p << q;
    /*
    (*(std::stringstream *)&message) = y;
    (*(std::stringstream *)(message + 256)) = g;
    (*(std::stringstream *)(message + 512)) = p;
    (*(std::stringstream *)(message + 768)) = q;
    */
    TRACE("Sending DSA Key => Size pub_key: " + to_string(strlen(y)) + "g" + to_string(strlen(g)) + "p" + to_string(strlen(p)) + "q"+ to_string(strlen(q)) + "message: " + message.str());
    sock->send(asio::buffer(message.str()));
  }

  void SplitterSTRPEDS::GatherBadPeers(){
	boost::asio::ip::udp::endpoint nopeer =  boost::asio::ip::udp::endpoint(boost::asio::ip::address::from_string("0.0.0.0"),0);
    while (alive_){
      if (peer_list_.size() > 0 ){
    	  boost::asio::ip::udp::endpoint peer = GetPeerForGathering();
    	  RequestBadPeers(peer);
    	  sleep(2);
    	  boost::asio::ip::udp::endpoint tp = GetTrustedPeerForGathering();
    	  if (tp != nopeer and tp != peer){
    		  RequestBadPeers(tp);
    	  }
      }
      sleep(gather_bad_peers_sleep_);
    }
  }
  
  asio::ip::udp::endpoint SplitterSTRPEDS::GetPeerForGathering(){
    gathering_counter_ = (gathering_counter_ + 1) % peer_list_.size();
    asio::ip::udp::endpoint peer = peer_list_[gathering_counter_];
    return peer;
  }

  asio::ip::udp::endpoint SplitterSTRPEDS::GetTrustedPeerForGathering(){
    trusted_gathering_counter_ = (trusted_gathering_counter_ + 1) % trusted_peers_.size();
    if (std::find(peer_list_.begin(), peer_list_.end(), trusted_peers_[trusted_gathering_counter_] ) != peer_list_.end() ){
      return trusted_peers_[trusted_gathering_counter_];
    }
    return boost::asio::ip::udp::endpoint(boost::asio::ip::address::from_string("0.0.0.0"),0);
  }

  void SplitterSTRPEDS::RequestBadPeers(const asio::ip::udp::endpoint &dest){
    team_socket_.send_to(asio::buffer("B"), dest);
  }
  
  void SplitterSTRPEDS::Run(){
     ReceiveTheHeader();
     InitKey();
     
    /* A DBS splitter runs 4 threads. The main one and the
       "handle_arrivals" thread are equivalent to the daemons used
       by the IMS splitter. "moderate_the_team" and
       "reset_counters_thread" are new.
    */

    TRACE("STRPEDS: waiting for the monitor peers ...");

    std::shared_ptr<asio::ip::tcp::socket> connection =
      make_shared<asio::ip::tcp::socket>(boost::ref(io_service_));
    acceptor_.accept(*connection);
    HandleAPeerArrival(connection);

    // Threads
    thread t1(bind(&SplitterIMS::HandleArrivals, this));
    thread t2(bind(&SplitterDBS::ModerateTheTeam, this));
    thread t3(bind(&SplitterDBS::ResetCountersThread, this));
    thread t4(bind(&SplitterSTRPEDS::GatherBadPeers, this));

    vector<char> message(2+1024+40+40);
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

	SendChunk(message, peer);

	destination_of_chunk_[chunk_number_ % buffer_size_] = peer;
	chunk_number_ = (chunk_number_ + 1) % Common::kMaxChunkNumber;

	if (logging_){
	  if (peer_number_ == 0){
	    current_round_ ++;
	    //TODO: Add the peers contained in peer_list_ to the message
	    std::string message = to_string(current_round_) + to_string(peer_list_.size());
	    LogMessage(message);
	  }
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
  
  void SplitterSTRPEDS::InitKey(){
    dsa_key = DSA_generate_parameters(1024, NULL, 0, NULL, NULL, NULL, 0);
    DSA_generate_key(dsa_key);
  }

  std::vector<char> SplitterSTRPEDS::GetMessage(int chunk_number,  const asio::streambuf &chunk, const boost::asio::ip::udp::endpoint &dst){

	std::vector<char> m(2+1024+4+2);

	(*(uint16_t *)m.data()) = htons(chunk_number);

	copy(asio::buffer_cast<const char *>(chunk.data()),
	  	     asio::buffer_cast<const char *>(chunk.data()) + chunk.size(),
	  	     m.data() + sizeof(uint16_t));

	in_addr addr;

	inet_aton(dst.address().to_string().c_str(), &addr);
	(*(in_addr *)(m.data() + chunk.size() + sizeof(uint16_t))) = addr;
	(*(uint16_t *)(m.data() + chunk.size() + sizeof(uint16_t) + 4)) = htons(dst.port());

    std::vector<char> h(256);
    Common::sha256(m, h);

    TRACE("HASH");

    DSA_SIG *sig = DSA_do_sign((unsigned char*)h.data(), 256, dsa_key);

    char * sigr = BN_bn2hex(sig->r);
    char * sigs = BN_bn2hex(sig->s);

    TRACE("SINGATURE");

    std::vector<char> message(2+1024+40+40);
    copy(m.data(), m.data() + chunk_size_ + sizeof(uint16_t), message.data());

    copy(sigr, sigr + strlen(sigr), message.data() + chunk.size() + sizeof(uint16_t));
    copy(sigs, sigs + strlen(sigs), message.data() + chunk.size() + sizeof(uint16_t) + 40);

    return message;

  }

  void SplitterSTRPEDS::AddTrustedPeer(const boost::asio::ip::udp::endpoint &peer) {
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

  std::vector<char> message(5);
  asio::ip::udp::endpoint sender;

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

      uint16_t lost_chunk_number = GetLostChunkNumber(message);
      ProcessLostChunk(lost_chunk_number, sender);

    } else if (bytes_transferred == 6) {
      /*
       Trusted peer sends hash of received chunk
       number of chunk, hash (sha256) of chunk
       */

      if (find(trusted_peers_.begin(), trusted_peers_.end(), sender) !=
          trusted_peers_.end()) {
    	  ProcessBadPeersMessage(message, sender);
      }
    }

    else {
      /*
       The peer wants to leave the team.

       A !2-length payload means that the peer wants to go
       away.
       */

      // 'G'oodbye
      if (message.at(0) == 'G') {
        ProcessGoodbye(sender);
      }
    }
  }

  LOG("Exiting moderate the team");
}

  void SplitterSTRPEDS::ProcessBadPeersMessage(const std::vector<char> &message, const boost::asio::ip::udp::endpoint &sender){
	  system::error_code ec;
	  std::vector<char> msg(5);
	  boost::asio::ip::udp::endpoint sdr;
	  boost::asio::ip::udp::endpoint bad_peer;

	  uint16_t bad_number = *(uint16_t *)(message.data()+3);
	  for (int i=0; i<bad_number; i++){
		  team_socket_.receive_from(asio::buffer(msg), sdr, 0, ec);
		  if (ec) ERROR("Unexepected error: " << ec.message());
		  bad_peer = *(boost::asio::ip::udp::endpoint *)msg.data();
		  TRACE("BAD Peer: " + bad_peer.address().to_string() + ":" + to_string(bad_peer.port()));

		  if (std::find(trusted_peers_.begin(), trusted_peers_.end(), sdr) != trusted_peers_.end() ){
			  HandleBadPeerFromTrusted(bad_peer, sdr);
		  }else{
			  HandleBadPeerFromRegular(bad_peer, sdr);
		  }

	  }
  }


  void SplitterSTRPEDS::HandleBadPeerFromTrusted(const boost::asio::ip::udp::endpoint &bad_peer, const boost::asio::ip::udp::endpoint &sender){
	  AddComplain(bad_peer, sender);
	  PunishPeer(bad_peer, "by trusted");
  }

  void SplitterSTRPEDS::HandleBadPeerFromRegular(const boost::asio::ip::udp::endpoint &bad_peer, const boost::asio::ip::udp::endpoint &sender){
	  AddComplain(bad_peer, sender);
	  int x = complains_[complains_map_[bad_peer]].size() / std::max(1, (int)(peer_list_.size()-1));
	  if (x >= majority_ratio_) {
		  PunishPeer(bad_peer, "by majority decision");
	  }
  }

 void SplitterSTRPEDS::AddComplain(const boost::asio::ip::udp::endpoint &bad_peer, const boost::asio::ip::udp::endpoint &sender){
	 if (complains_map_.find(bad_peer) != complains_map_.end()){
		 if (complains_map_.find(sender) == complains_map_.end()){
			 complains_[complains_map_[bad_peer]].push_back(sender);
		 }
	 }else{
		 std::vector<boost::asio::ip::udp::endpoint> bads;
		 bads.push_back(sender);
		 complains_.push_back(bads);
		 complains_map_.insert(std::pair<boost::asio::ip::udp::endpoint,int>(bad_peer, complains_.size()-1));

	 }
 }

void SplitterSTRPEDS::PunishPeer(const boost::asio::ip::udp::endpoint &peer, std::string message) {
  if (logging_) {
    LogMessage("!!! bad peer" + peer.address().to_string() + ":" +
               to_string(peer.port()) + "(" + message + ")");
  }

  LOG("!!! bad peer " << peer);

  RemovePeer(peer);
}



void SplitterSTRPEDS::LogMessage(const std::string &message) {
  log_file_ << BuildLogMessage(message);
  // TODO: Where to close the ofstream?
}

string SplitterSTRPEDS::BuildLogMessage(const std::string &message) {
  return to_string(time(NULL)) + "\t" + message;
}


void SplitterSTRPEDS::Start() {
  LOG("Start");
  thread_.reset(new boost::thread(boost::bind(&SplitterSTRPEDS::Run, this)));
}
}

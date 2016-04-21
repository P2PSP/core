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
    std::stringstream y = LongToHex(dsa_key->pub_key);
    std::stringstream g = LongToHex(dsa_key->g);
    std::stringstream p = LongToHex(dsa_key->p);
    std::stringstream q = LongToHex(dsa_key->q);

    char message[1024];
    
    (*(std::stringstream *)&message) = y;
    (*(std::stringstream *)(message + 256)) = g;
    (*(std::stringstream *)(message + 512)) = p;
    (*(std::stringstream *)(message + 768)) = q;
    sock->send(asio::buffer(message));
  }

  void SplitterSTRPEDS::GatherBadPeers(){
    while (alive_){
      if (peer_list_.size() > 0 ){
    	  boost::asio::ip::udp::endpoint peer = GetPeerForGathering();
    	  RequestBadPeers(peer);
    	  sleep(2);
    	  boost::asio::ip::udp::endpoint tp = GetTrustedPeerForGathering();
    	  if (tp != NULL and tp != peer){
    		  RequestBadPeers(tp);
    	  }
      }
      sleep(gather_bad_peers_sleep_);
    }
  }
  
  asio::ip::udp::endpoint SplitterSTRPEDS::GetPeerForGathering(){
    gathering_counter_ = (gathering_counter_ + 1) % peer_list_.size();
    asio::ip::tcp::endpoint peer = peer_list_[gathering_counter_];
    return peer;
  }

  asio::ip::udp::endpoint SplitterSTRPEDS::GetTrustedPeerForGathering(){
    trusted_gathering_counter_ = (trusted_gathering_counter_ + 1) % trusted_peers_.size();
    if (std::find(peers_list_.begin(), peer_list_.end(), trusted_peers_.[trusted_gathering_counter_] ) != peer_list_.end() ){
      return trusted_peers_[trusted_gathering_counter_];
    }
    return NULL;	
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

    vector<char> message(sizeof(uint16_t) + chunk_size_ + digest_size_ + digest_size_);
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

  std::vector<char> SplitterSTRPEDS::GetMessage(int chunk_number,  asio::streambuf chunk, const boost::asio::ip::udp::endpoint dst){

    std::vector<char> m = std::to_string(chunk_number_) + chunk + dst.address().to_string() + std::to_string(dst.port());
    
    std::vector<char> h;
    Common::sha256(m, h);

    /* initialize random seed: */
     srand (time(NULL));
     long k = rand() % (dsa_key->q-1) + 1;

     /* HEREEEEEEE */

    int Siglen; 

    unsigned char *sig = malloc(DSA_size(dsa_key));
    if((DSA_sign(0, h, h.size(), sig, &Siglen, dsa_key)) != 1) {
      printf("ERROR: Digital signature signing failed.\n"); 
      DSA_free(dsa); 
      exit(0); 
    } 
    
    char message[1024];
    
    (*(std::stringstream *)&message) = y;
    (*(std::stringstream *)(message + 256)) = g;
    (*(std::stringstream *)(message + 512)) = p;
    (*(std::stringstream *)(message + 768)) = q;
  }

  
  void SplitterSTRPEDS::ModerateTheTeam() {
  // TODO: Check if something fails and a try catch statement has to be added

  std::vector<char> message(34);
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

    } else if (bytes_transferred == 34) {
      /*
       Trusted peer sends hash of received chunk
       number of chunk, hash (sha256) of chunk
       */

      if (find(trusted_peers_.begin(), trusted_peers_.end(), sender) !=
          trusted_peers_.end()) {
        ProcessChunkHashMessage(message);
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

void SplitterSTRPE::AddTrustedPeer(const boost::asio::ip::udp::endpoint &peer) {
  trusted_peers_.push_back(peer);
}

void SplitterSTRPE::PunishMaliciousPeer(const boost::asio::ip::udp::endpoint &peer) {
  if (logging_) {
    LogMessage("!!! malicious peer" + peer.address().to_string() + ":" +
               to_string(peer.port()));
  }

  LOG("!!! malicious peer " << peer);

  RemovePeer(peer);
}

void SplitterSTRPE::ProcessChunkHashMessage(const std::vector<char> &message) {
  uint16_t chunk_number = *(uint16_t *)message.data();
  std::vector<char> hash(32);

  copy(message.data() + sizeof(uint16_t), message.data() + message.size(),
       hash.data());

  std::vector<char> chunk_message = buffer_[chunk_number % buffer_size_];

  uint16_t stored_chunk_number = *(uint16_t *)chunk_message.data();
  std::vector<char> chunk;
  copy(chunk_message.data() + sizeof(uint16_t),
       chunk_message.data() + chunk_size_, chunk.data());

  stored_chunk_number = ntohs(stored_chunk_number);

  std::vector<char> digest(32);
  Common::sha256(chunk, digest);
  if (stored_chunk_number == chunk_number && digest != hash) {
    asio::ip::udp::endpoint peer =
        destination_of_chunk_[chunk_number % buffer_size_];
    PunishMaliciousPeer(peer);
  }
}

void SplitterSTRPE::SetLogFile(const std::string &filename) {
  log_file_.open(filename);
}

void SplitterSTRPE::SetLogging(bool enabled) { logging_ = enabled; }

void SplitterSTRPE::LogMessage(const std::string &message) {
  log_file_ << BuildLogMessage(message);
  // TODO: Where to close the ofstream?
}

string SplitterSTRPE::BuildLogMessage(const std::string &message) {
  return to_string(time(NULL)) + "\t" + message;
}


void SplitterSTRPE::Start() {
  LOG("Start");
  thread_.reset(new boost::thread(boost::bind(&SplitterSTRPE::Run, this)));
}
}

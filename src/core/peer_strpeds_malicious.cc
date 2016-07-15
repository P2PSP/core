//
//  peer_strpeds_malicious.cc
//  P2PSP
//
//  This code is distributed under the GNU General Public License (see
//  THE_GENERAL_GNU_PUBLIC_LICENSE.txt for extending this information).
//  Copyright (C) 2016, the P2PSP team.
//  http://www.p2psp.org
//

#include "peer_strpeds_malicious.h"

namespace p2psp {
void PeerStrpeDsMalicious::Init() {
	TRACE("Initialized");
}

void PeerStrpeDsMalicious::FirstMainTarget(){
	main_target_ = ChooseMainTarget();
	LOG("MainTarget selected: " << main_target_);
}

boost::asio::ip::udp::endpoint PeerStrpeDsMalicious::ChooseMainTarget(){

	std::vector<boost::asio::ip::udp::endpoint> attacked_peers;
	std::ifstream attacked_file;
	attacked_peers.clear();
	attacked_file.open("attacked.txt");
	if(attacked_file.is_open()){
		std::string str;
		while (std::getline(attacked_file, str))
		{

			boost::char_separator<char> sep{":"};
			boost::tokenizer<boost::char_separator<char>> tok{str, sep};
			boost::tokenizer< boost::char_separator<char> >::iterator t = tok.begin();
			boost::asio::ip::address address = boost::asio::ip::address::from_string(*t);
			t++;
			uint16_t port = atoi((*t).c_str());
			//LOG("IP: " + address.to_string() + ":" + std::to_string(port));
			attacked_peers.push_back(boost::asio::ip::udp::endpoint(address,port));

		}
		attacked_file.close();
	}else{
		ERROR("attacked.txt doesn't exist");
	}

	std::vector<boost::asio::ip::udp::endpoint> malicious_peers;
	std::ifstream malicious_file;
	malicious_peers.clear();
	malicious_file.open("malicious.txt");
	if(malicious_file.is_open()){
		std::string str;
		while (std::getline(malicious_file, str))
		{

			boost::char_separator<char> sep{":"};
			boost::tokenizer<boost::char_separator<char>> tok{str, sep};
			boost::tokenizer< boost::char_separator<char> >::iterator t = tok.begin();
			boost::asio::ip::address address = boost::asio::ip::address::from_string(*t);
			t++;
			uint16_t port = atoi((*t).c_str());
			//LOG("IP: " + address.to_string() + ":" + std::to_string(port));
			malicious_peers.push_back(boost::asio::ip::udp::endpoint(address,port));

		}
		malicious_file.close();
	}else{
		ERROR("malicious.txt doesn't exist");
	}

	boost::asio::ip::udp::endpoint re;
	bool re_found = false;
	while (!re_found){
		int r = rand() % (int)peer_list_.size();
		if (std::find(attacked_peers.begin(), attacked_peers.end(), peer_list_[r])== attacked_peers.end() and std::find(malicious_peers.begin(), malicious_peers.end(), peer_list_[r]) == malicious_peers.end()) {
			re = peer_list_[r];
			re_found = true;
		}
	}

	std::ofstream attacked_ofile;
	attacked_ofile.open ("attacked.txt", std::ofstream::out | std::ofstream::app);
	attacked_ofile << re.address().to_string() << ":" << re.port() << "\n";
	attacked_ofile.flush();
	attacked_ofile.close();

	return re;

}


  void PeerStrpeDsMalicious::AllAttack(){
	TRACE("All Attack Mode");
	regular_peers_.clear();

	std::ofstream regular_ofile;
	regular_ofile.open ("regular.txt", std::ofstream::out | std::ofstream::app);
	regular_ofile << main_target_.address().to_string() << ":" << main_target_.port() << "\n";
	regular_ofile.flush();
	regular_ofile.close();

  }

  void PeerStrpeDsMalicious::RefreshRegularPeers(){
	std::ifstream regular_file;
	regular_file.open("regular.txt");
	if(regular_file.is_open()){
		std::string str;
		while (std::getline(regular_file, str))
		{

			boost::char_separator<char> sep{":"};
			boost::tokenizer<boost::char_separator<char>> tok{str, sep};
			boost::tokenizer< boost::char_separator<char> >::iterator t = tok.begin();
			boost::asio::ip::address address = boost::asio::ip::address::from_string(*t);
			t++;
			uint16_t port = atoi((*t).c_str());
			//LOG("IP: " + address.to_string() + ":" + std::to_string(port));

			if (std::find(peer_list_.begin(), peer_list_.end(), boost::asio::ip::udp::endpoint(address,port)) != peer_list_.end()){
				regular_peers_.push_back(boost::asio::ip::udp::endpoint(address,port));
			}

			if (regular_peers_.size() * 2 > peer_list_.size()){
				break;
			}
		}
		regular_file.close();
	}else{
		ERROR("regular.txt doesn't exist");
	}
  }

void PeerStrpeDsMalicious::SetBadMouthAttack(bool value, std::string selected) {
  bad_mouth_attack_ = value;

  if (value) {
    // TODO: Tokenize string input
    // bad_peers_.insert(bad_peers_.end(), selected.begin(), selected.end());
  } else {
    bad_peers_.clear();
  }
}

void PeerStrpeDsMalicious::SetSelectiveAttack(bool value,
                                              std::string selected) {
  selective_attack_ = true;

  // TODO: Tokenize string input
  // selected_peers_for_attack_.insert(selected_peers_for_attack_.end(),selected.begin(),
  // selected.end());
}

void PeerStrpeDsMalicious::SetOnOffAttack(bool value, int ratio) {
  on_off_ratio_ = value;
  on_off_ratio_ = ratio;
}

void PeerStrpeDsMalicious::SetPersistentAttack(bool value) {
  persistent_attack_ = value;
}

void PeerStrpeDsMalicious::GetPoisonedChunk(std::vector<char> &message) {
  if ((int)message.size() == (2 + chunk_size_ + 40 + 40 + 4)) {
    std::memset(message.data() + 2, 0, chunk_size_);
  }
}

void PeerStrpeDsMalicious::SendChunk(const ip::udp::endpoint &peer) {
  std::vector<char> chunk = receive_and_feed_previous_;
  GetPoisonedChunk(chunk);

  if (persistent_attack_) {

	  if ((peer == main_target_) and (number_chunks_send_to_main_target_ < MPTR)){
		  team_socket_.send_to(buffer(chunk), peer);
		  sendto_counter_++;
		  TRACE("MainTarget Attack: " << peer.address().to_string() << ":" << peer.port());
		  number_chunks_send_to_main_target_++;
	  } else if ((peer == main_target_) and (number_chunks_send_to_main_target_ >= MPTR) ) {
		  AllAttack();
		  team_socket_.send_to(buffer(chunk), peer);
		  sendto_counter_++;
		  main_target_ = ChooseMainTarget();
	  } else if (std::find(regular_peers_.begin(), regular_peers_.end(), peer) != regular_peers_.end()) {
		  team_socket_.send_to(buffer(chunk), peer);
		  sendto_counter_++;
		  TRACE("AllAttackC attack: " << peer.address().to_string() << ":" << peer.port());
	  }else{
		  team_socket_.send_to(buffer(receive_and_feed_previous_), peer);
		  sendto_counter_++;
		  TRACE("No attack");
	  }

    return;
  }

  if (on_off_attack_) {
    int x = std::rand() % 100 + 1;
    if (x <= on_off_ratio_) {
      team_socket_.send_to(buffer(chunk), peer);
    } else {
      team_socket_.send_to(buffer(receive_and_feed_previous_), peer);
    }
    sendto_counter_++;
    return;
  }

  if (selective_attack_) {
    if (std::find(selected_peers_for_selective_attack_.begin(),
    		selected_peers_for_selective_attack_.end(),
                  peer) != selected_peers_for_selective_attack_.end()) {
      team_socket_.send_to(buffer(chunk), peer);
    } else {
      team_socket_.send_to(buffer(receive_and_feed_previous_), peer);
    }
    sendto_counter_++;
    return;
  }

  team_socket_.send_to(buffer(receive_and_feed_previous_), peer);
  sendto_counter_++;
}

int PeerStrpeDsMalicious::DBSProcessMessage(const std::vector<char> &message,
                                            const ip::udp::endpoint &sender) {
  // Now, receive and send.

  TRACE("PROCESS MESSAGE Malicious");

  TRACE("Size: " << message.size() << " vs " << message_size_)
  	// TODO: remove hardcoded values
  	if (message.size() == message_size_) {
  		// A video chunk has been received
  		ip::udp::endpoint peer;

  		uint16_t chunk_number = ntohs(*(uint16_t *) message.data());

  		chunks_[chunk_number % buffer_size_] = {
  			std::vector<char>(message.data() + sizeof(uint16_t),
  					message.data() + sizeof(uint16_t) + chunk_size_),
  			true};

  		received_counter_++;

  		LOG("Chunk Inserted at: " << (chunk_number%buffer_size_));

  		if (sender == splitter_) {

  			// Send the previous chunk in burst sending
  			// mode if the chunk has not been sent to all
  			// the peers of the list of peers.

  			TRACE(
  					"(" << team_socket_.local_endpoint().address().to_string() << "," << std::to_string(team_socket_.local_endpoint().port()) << ")" << "<-" << std::to_string(chunk_number) << "-" << "(" << sender.address().to_string() << "," << std::to_string(sender.port()) << ")");

  			while (receive_and_feed_counter_ < (int) peer_list_.size()
  					&& (receive_and_feed_counter_ > 0 or modified_list_)) {
  				peer = peer_list_[receive_and_feed_counter_];

  				//team_socket_.send_to(buffer(receive_and_feed_previous_),peer);
  				//sendto_counter_++;

  				SendChunk(peer);

  				TRACE(
  				      "(" << team_socket_.local_endpoint().address().to_string() << "," << std::to_string(team_socket_.local_endpoint().port()) << ")" << "-" << std::to_string(ntohs(*(uint16_t *)receive_and_feed_previous_.data())) << "->" << "(" << peer.address().to_string() << "," << std::to_string(peer.port()) << ")");

  				debt_[peer]++;

  				if (debt_[peer] > max_chunk_debt_/*kMaxChunkDebt*/) {
  					TRACE(
  							"(" << peer.address().to_string() << "," << std::to_string(peer.port()) << ")" << " removed by unsupportive (" + std::to_string(debt_[peer]) + " lossess)");
  					debt_.erase(peer);
  					peer_list_.erase(
  							std::find(peer_list_.begin(), peer_list_.end(),
  									peer));
  					//receive_and_feed_counter_--;
  				}

  				receive_and_feed_counter_++;
  			}


  			// Start playback with the first chunk received from the splitter //
  			std::vector<char> empty(message_size_, 0);
  			if (receive_and_feed_previous_ == empty){
  				played_chunk_ = ntohs(*(uint16_t *)message.data());
  			    TRACE("First chunk to play modified " << std::to_string(played_chunk_));
  			}
  			// --------------------------------------------- //

  			modified_list_ = false;
  			TRACE("Sent " << receive_and_feed_counter_ << " of " << peer_list_.size() );
  			receive_and_feed_counter_ = 0;
  			TRACE("Last Chunk saved in receive and feed: " << ntohs(*(uint16_t *)message.data()));
  			receive_and_feed_previous_ = message;
  		} else {
  			TRACE(
  					"(" << team_socket_.local_endpoint().address().to_string() << "," << std::to_string(team_socket_.local_endpoint().port()) << ")" << "<-" << std::to_string(chunk_number) << "-" << "(" << sender.address().to_string() << "," << std::to_string(sender.port()) << ")");

  			if (peer_list_.end()
  					== std::find(peer_list_.begin(), peer_list_.end(),
  							sender)) {
  				peer_list_.push_back(sender);
  				debt_[sender] = 0;
  				TRACE(
  						"(" << sender.address().to_string() << "," << std::to_string(sender.port()) << ")" << " added by chunk " << std::to_string(chunk_number));
  			} else {
  				debt_[sender]--;
  			}
  		}

  		// A new chunk has arrived and the previous must be forwarded to next peer
  		// of
  		// the list of peers.

  		std::vector<char> empty(message_size_, 0);

  		if (receive_and_feed_counter_ < (int) peer_list_.size()
  				&& receive_and_feed_previous_!=empty) {
  			// Send the previous chunk in congestion avoiding mode.

  			peer = peer_list_[receive_and_feed_counter_];

  			TRACE("Sending in congestion avoiding mode to " << peer.address().to_string() << ":" << peer.port() << "/ counter " << receive_and_feed_counter_)
  			//team_socket_.send_to(buffer(receive_and_feed_previous_), peer);
  			//sendto_counter_++;

  			SendChunk(peer);

  			debt_[peer]++;

  			if (debt_[peer] > max_chunk_debt_/*kMaxChunkDebt*/) {
  				TRACE(
  						"(" << peer.address().to_string() << "," << std::to_string(peer.port()) << ")" << " removed by unsupportive (" + std::to_string(debt_[peer]) + " lossess)");
  				debt_.erase(peer);
  				peer_list_.erase(
  						std::find(peer_list_.begin(), peer_list_.end(), peer));
  				//receive_and_feed_counter_--;
  			}

  			TRACE(
  					"(" << team_socket_.local_endpoint().address().to_string() << "," << std::to_string(team_socket_.local_endpoint().port()) << ")" << "-" << std::to_string(ntohs(*(short *)receive_and_feed_previous_.data())) << "->" << "(" << peer.address().to_string() << "," << std::to_string(peer.port()) << ")");

  			receive_and_feed_counter_++;
  		}

  		return chunk_number;
  	} else {
  		// A control chunk has been received

  		TRACE("Control message received");

  		if (message[0] == 'H') {
  			if (peer_list_.end()
  					== std::find(peer_list_.begin(), peer_list_.end(),
  							sender)) {
  				// The peer is new
  				peer_list_.push_back(sender);
  				debt_[sender] = 0;
  				TRACE(
  						"(" << sender.address().to_string() << "," << std::to_string(sender.port()) << ")" << " added by [hello] ");
  			}
  		} else {
  				if (peer_list_.end()
  						!= std::find(peer_list_.begin(), peer_list_.end(),
  								sender)) {
  					// sys.stdout.write(Color.red)
  					TRACE(
  							"(" << team_socket_.local_endpoint().address().to_string() << "," << std::to_string(team_socket_.local_endpoint().port()) << ") \b: received \"goodbye\" from (" << sender.address().to_string() << "," << std::to_string(sender.port()) << ")");
  					// sys.stdout.write(Color.none)
  					peer_list_.erase(
  							std::find(peer_list_.begin(), peer_list_.end(),
  									sender));
  					debt_.erase(sender);
  					if (receive_and_feed_counter_ > 0){
  						modified_list_ = true;
  						receive_and_feed_counter_--;
  					}
  				}else{
  					if (sender == splitter_){
  						TRACE("Goodbye received from splitter");
  						waiting_for_goodbye_ = false;
  					}
  				}

  			}

  		return -1;
  	}

  	return -1;
}

int PeerStrpeDsMalicious::ProcessMessage(const std::vector<char> &message,
                                         const ip::udp::endpoint &sender) {
  if (std::find(bad_peers_.begin(), bad_peers_.end(), sender) !=
      bad_peers_.end()) {
	  return -1;
  }

  if (IsCurrentMessageFromSplitter() || CheckMessage(message, sender)) {

	  if (IsCurrentMessageFromSplitter() and all_attack_c_){
		  RefreshRegularPeers();
	  }

	  if (IsControlMessage(message) and (message[0] == 'B')) {
		  return HandleBadPeersRequest();
	  } else {
		  return DBSProcessMessage(message, sender);
	  }
  } else {
    ProcessBadMessage(message, sender);
  }

  return -1;
}

void PeerStrpeDsMalicious::SetMPTR(int mptr){
	MPTR = mptr;
}

void PeerStrpeDsMalicious::ReceiveTheListOfPeers(){
	PeerDBS::ReceiveTheListOfPeers();
	FirstMainTarget();
}


}

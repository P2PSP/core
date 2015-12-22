
#include "peer_strpeds_malicious.h"

namespace p2psp {
void PeerStrpeDsMalicious::Init() { LOG("Initialized"); }

void PeerStrpeDsMalicious::SetBadMouthAttack(
    bool value, std::vector<ip::udp::endpoint> selected) {
  bad_mouth_attack_ = value;

  if (value) {
    bad_peers_.insert(bad_peers_.end(), selected.begin(), selected.end());
  } else {
    bad_peers_.clear();
  }
}

void PeerStrpeDsMalicious::SetSelectiveAttack(
    bool value, std::vector<ip::udp::endpoint> selected) {
  selective_attack_ = true;

  selected_peers_for_attack_.insert(selected_peers_for_attack_.end(),
                                    selected.begin(), selected.end());
}

void PeerStrpeDsMalicious::SetOnOffAttack(bool value, int ratio) {
  on_off_ratio_ = value;
  on_off_ratio_ = ratio;
}

void PeerStrpeDsMalicious::SetPersistentAttack(bool value) {
  persistent_attack_ = value;
}

void PeerStrpeDsMalicious::GetPoisonedChunk(std::vector<char> *message) {
  if (message->size() == (2 + 1024 + 40 + 40)) {
    std::memset(message->data() + 2, 0, 1024);
  }
}

void PeerStrpeDsMalicious::SendChunk(ip::udp::endpoint peer) {
  std::vector<char> chunk = receive_and_feed_previous_;
  GetPoisonedChunk(&chunk);
  if (persistent_attack_) {
    team_socket_.send_to(buffer(chunk), peer);
    sendto_counter_++;
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
    if (std::find(selected_peers_for_attack_.begin(),
                  selected_peers_for_attack_.end(),
                  peer) != selected_peers_for_attack_.end()) {
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
}
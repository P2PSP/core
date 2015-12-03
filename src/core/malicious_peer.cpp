
#include "malicious_peer.h"

namespace p2psp {

MaliciousPeer::MaliciousPeer(){};
MaliciousPeer::~MaliciousPeer(){};

void MaliciousPeer::Init() { LOG("Initialized"); }

void MaliciousPeer::SendChunk(ip::udp::endpoint peer) {
  std::vector<char> chunk = receive_and_feed_previous_;
  GetPoisonedChunk(&chunk);
  if (persistent_attack_) {
    team_socket_.send_to(buffer(chunk), peer);
    sendto_counter_++;
    return;
  }

  if (on_off_attack_) {
    int r = std::rand() % 100 + 1;
    if (r <= on_off_ratio_) {
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

void MaliciousPeer::GetPoisonedChunk(std::vector<char>* chunk) {
  int offset = sizeof(uint16_t);
  memset(chunk->data() + offset, 0, chunk->size() - offset);
}

void MaliciousPeer::SetPersistentAttack(bool value) {
  persistent_attack_ = value;
}

void MaliciousPeer::SetOnOffAttack(bool value, int ratio) {
  on_off_ratio_ = value;
  on_off_ratio_ = ratio;
}

void MaliciousPeer::SetSelectiveAttack(
    bool value, const std::vector<ip::udp::endpoint> selected) {
  selective_attack_ = true;
  selected_peers_for_attack_.insert(selected_peers_for_attack_.end(),
                                    selected.begin(), selected.end());
}
}
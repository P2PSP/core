
#include "malicious_peer.h"

namespace p2psp {

MaliciousPeer::MaliciousPeer(){};
MaliciousPeer::~MaliciousPeer(){};

void MaliciousPeer::Init() { LOG("Initialized"); }

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
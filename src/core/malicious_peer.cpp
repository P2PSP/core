
#include "malicious_peer.h"

namespace p2psp {

MaliciousPeer::MaliciousPeer(){};
MaliciousPeer::~MaliciousPeer(){};

void MaliciousPeer::Init() { LOG("Initialized"); }

void MaliciousPeer::GetPoisonedChunk(std::vector<char>* chunk) {
  int offset = sizeof(uint16_t);
  memset(chunk->data() + offset, 0, chunk->size() - offset);
};
}

#include "monitor_dbs.h"

namespace p2psp {

MonitorDBS::MonitorDBS() { LOG("Initialized"); };

MonitorDBS::~MonitorDBS(){};

void MonitorDBS::Complain(uint16_t chunk_number) {
  std::vector<char> message(2);
  std::memcpy(message.data(), &chunk_number, sizeof(uint16_t));

  team_socket_.send_to(buffer(message), splitter_);

  LOG("lost chunk:" << std::to_string(chunk_number));
};
}
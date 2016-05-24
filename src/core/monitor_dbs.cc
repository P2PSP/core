//
//  monitor_dbs.cc
//  P2PSP
//
//  This code is distributed under the GNU General Public License (see
//  THE_GENERAL_GNU_PUBLIC_LICENSE.txt for extending this information).
//  Copyright (C) 2016, the P2PSP team.
//  http://www.p2psp.org
//
//  DBS: Data Broadcasting Set of rules
//

#include "monitor_dbs.h"

namespace p2psp {

MonitorDBS::MonitorDBS(){
    magic_flags_ = Common::kDBS;
};

MonitorDBS::~MonitorDBS(){};

void MonitorDBS::Init() { TRACE("Initialized"); }

// def print_the_module_name(self):
// {{{

// sys.stdout.write(Color.red)
//_print_("Monitor DBS")
// sys.stdout.write(Color.none)

// }}}

void MonitorDBS::Complain(uint16_t chunk_number) {
  std::vector<char> message(2);
  uint16_t chunk_number_network = htons(chunk_number);
  std::memcpy(message.data(), &chunk_number_network, sizeof(uint16_t));

  team_socket_.send_to(buffer(message), splitter_);

  TRACE("lost chunk:" << std::to_string(chunk_number));
};

int MonitorDBS::FindNextChunk() {
  uint16_t chunk_number = (played_chunk_ + 1) % Common::kMaxChunkNumber;

  while (!chunks_[chunk_number % buffer_size_].received) {
    Complain(chunk_number);
    chunk_number = (chunk_number + 1) % Common::kMaxChunkNumber;
  }
  return chunk_number;
}
}

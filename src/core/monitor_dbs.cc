//
//  monitor_dbs.cc -- DBS peer monitor
//
//  This code is distributed under the GNU General Public License (see
//  THE_GENERAL_GNU_PUBLIC_LICENSE.txt for extending this information).
//  Copyright (C) 2016, the P2PSP team.
//  http://www.p2psp.org
//

#include "monitor_dbs.h"

namespace p2psp {

  Monitor_DBS::Monitor_DBS() {
    //    magic_flags_ = Common::kDBS;
  };

  Monitor_DBS::~Monitor_DBS(){};

  void Monitor_DBS::Init() { TRACE("Initialized"); }

  void Monitor_DBS::Complain(uint16_t chunk_position) {
    std::vector<char> message(2);
    uint16_t chunk_number_network = htons(chunk_position);
    std::memcpy(message.data(), &chunk_number_network, sizeof(uint16_t));

    team_socket_.send_to(buffer(message), splitter_);

    TRACE("lost chunk:"
	  << std::to_string(chunk_position));
  };

#ifdef _1_
  
  /*int Monitor_DBS::FindNextChunk() {
    uint16_t chunk_number = (played_chunk_ + 1) % Common::kMaxChunkNumber;

    while (!chunks_[chunk_number % buffer_size_].received) {
      Complain(chunk_number);
      chunk_number = (chunk_number + 1) % Common::kMaxChunkNumber;
    }
    return chunk_number;
    }*/

  void Monitor_DBS::PlayNextChunk(int chunk_number) {
    for (int i = 0; i < (chunk_number-latest_chunk_number_);i++) {
      if (chunks_[chunk_number % buffer_size_].received) {
	//PlayChunk(played_chunk_);
	player_alive_ = PlayChunk(chunks_[played_chunk_ % buffer_size_].data);
	chunks_[played_chunk_ % buffer_size_].received = false;
	received_counter_--;
	LOG("Chunk Consumed at: "
	    << played_chunk_ % buffer_size_);
      } else {
	Complain(chunk_number); // <- Monitor specific 
	LOG("Chunk lost at: "
	    << played_chunk_ % buffer_size_);
      }

      played_chunk_++;
    }

    if ((latest_chunk_number_ % Common::kMaxChunkNumber) < chunk_number)
      latest_chunk_number_ = chunk_number;
  }

#endif
  
}

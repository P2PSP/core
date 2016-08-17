//
//  monitor_lrs.cc
//  P2PSP
//
//  This code is distributed under the GNU General Public License (see
//  THE_GENERAL_GNU_PUBLIC_LICENSE.txt for extending this information).
//  Copyright (C) 2016, the P2PSP team.
//  http://www.p2psp.org
//
//  LRS: Lost chunks Recovery Set of rules
//

#include "monitor_lrs.h"

namespace p2psp {

  void Monitor_LRS::Init() {
#if defined __DEBUG__ || defined __SORS__
    TRACE("Initialized");
#endif
  }
  
  void Monitor_LRS::ReceiveBufferSize() {
    boost::array<char, 2> buffer;
    read(splitter_socket_, ::buffer(buffer));
    
    buffer_size_ = ntohs(*(short *)(buffer.c_array()));
    
    // Monitor peers that implements the LRS use a smaller buffer
    // in order to complains before the rest of peers reach them in
    // their buffers.
    buffer_size_ /= 2;
    INFO("buffer_size_ = " << std::to_string(buffer_size_));
  }
}

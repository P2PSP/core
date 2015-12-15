
#include "monitor_lrs.h"

namespace p2psp {

void MonitorLRS::Init() {
  // TODO: if __debug__:
  LOG("Initialized");
}

void MonitorLRS::ReceiveTheBufferSize() {
  boost::array<char, 2> buffer;
  read(splitter_socket_, ::buffer(buffer));

  buffer_size_ = ntohs(*(short *)(buffer.c_array()));

  // Monitor peers that implements the LRS use a smaller buffer
  // in order to complains before the rest of peers reach them in
  // their buffers.
  buffer_size_ /= 2;
  LOG("buffer_size_ = " << std::to_string(buffer_size_));
}
}
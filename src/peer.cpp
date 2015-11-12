
// TODO: include all needed libraries
#include "core/peer_ims.h"
#include "util/trace.h"

int main(int argc, const char* argv[]) {
  // TODO: Argument parser. Decide how to implement it

  p2psp::PeerIMS peer;

  peer.WaitForThePlayer();
  peer.ConnectToTheSplitter();
  peer.ReceiveTheMcasteEndpoint();
  peer.ReceiveTheHeaderSize();
  peer.ReceiveTheChunkSize();
  peer.ReceiveTheHeader();
  peer.ReceiveTheBufferSize();
  LOG("Using IP Multicast address = " + peer.GetMcastAddr());

  // TODO: if(args.show_buffer){
  // peer.SetShowBuffer(true);
  //}

  // A multicast address is always received, even for DBS peers.
  if (peer.GetMcastAddr() == "0.0.0.0") {
    // TODO: IP multicast mode
    // TODO: DBS
  } else {
    // IP multicast mode
    peer.ListenToTheTeam();
  }

  // TODO: Decide type of peer to work with

  // TODO: Start the peer's main thread

  // TODO: Print information about the status of the peer

  return 0;
}

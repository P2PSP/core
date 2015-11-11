
// TODO: include all needed libraries
#include "core/peer_ims.h"

int main(int argc, const char* argv[]) {
  // TODO: Argument parser. Decide how to implement it

  p2psp::PeerIMS peer;

  peer.WaitForThePlayer();
  peer.ConnectToTheSplitter();
  peer.ReceiveTheMcasteEndpoint();
  peer.ReceiveTheHeaderSize();
  peer.ReceiveTheChunkSize();
  // TODO: peer.ReceiveTheHeader();
  // TODO: peer.ReceiveTheBufferSize();*/

  // TODO: Decide type of peer to work with

  // TODO: Start the peer's main thread

  // TODO: Print information about the status of the peer

  return 0;
}

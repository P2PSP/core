//
//  splitter.cpp
//  P2PSP
//
//  This code is distributed under the GNU General Public License (see
//  THE_GENERAL_GNU_PUBLIC_LICENSE.txt for extending this information).
//  Copyright (C) 2014, the P2PSP team.
//  http://www.p2psp.org
//

#include <iostream>
#include "core/splitter_ims.h"
#include "core/splitter_dbs.h"
#include "core/splitter_acs.h"
#include "core/splitter_lrs.h"
#include "core/splitter_strpe.h"

int main(int argc, const char *argv[]) {
  // TODO: Argument parser.

  // TODO: Configure splitter

  // TODO: Start the splitter's main thread

  // TODO: Print information about the status of the splitter

  p2psp::SplitterACS splitter;

  splitter.Start();

  LOG("         | Received  | Sent      | Number       losses/ losses");
  LOG("    Time | (kbps)    | (kbps)    | peers (peer) sents   threshold "
      "period kbps");
  LOG("---------+-----------+-----------+-----------------------------------.."
      ".");

  int last_sendto_counter = splitter.GetSendToCounter();
  int last_recvfrom_counter = splitter.GetRecvFromCounter();
  int chunks_sendto = 0;
  int kbps_sendto = 0;
  int kbps_recvfrom = 0;
  int chunks_recvfrom = 0;
  std::vector<boost::asio::ip::udp::endpoint> peer_list;

  int get_loss = 0;

  while (splitter.isAlive()) {
    boost::this_thread::sleep(boost::posix_time::milliseconds(1000));
    chunks_sendto = splitter.GetSendToCounter() - last_sendto_counter;
    kbps_sendto = (chunks_sendto * splitter.GetChunkSize() * 8) / 1000;
    chunks_recvfrom = splitter.GetRecvFromCounter() - last_recvfrom_counter;
    kbps_recvfrom = (chunks_recvfrom * splitter.GetChunkSize() * 8) / 1000;
    last_sendto_counter = splitter.GetSendToCounter();
    last_recvfrom_counter = splitter.GetRecvFromCounter();
    LOG("|" << kbps_recvfrom << "|" << kbps_sendto << "|");
    // LOG(_SET_COLOR(_CYAN));

    // TODO: GetPeerList is only in DBS and derivated classes
    peer_list = splitter.GetPeerList();
    LOG("Size peer list: " << peer_list.size());

    std::vector<boost::asio::ip::udp::endpoint>::iterator it;
    for (it = peer_list.begin(); it != peer_list.end(); ++it) {
      _SET_COLOR(_BLUE);
      LOG("Peer: " << *it);
      _SET_COLOR(_RED);

      // TODO: GetLoss and GetMaxChunkLoss are only in DBS and derivated classes
      LOG(splitter.GetLoss(*it) << "/" << chunks_sendto << " " << splitter.GetMaxChunkLoss());
      
      // TODO: If is ACS
      _SET_COLOR(_YELLOW);
      LOG(splitter.GetPeriod(*it));
      LOG((splitter.GetNumberOfSentChunksPerPeer(*it) * splitter.GetChunkSize() * 8) / 1000);
      splitter.SetNumberOfSentChunksPerPeer(*it, 0);
    }
  }

  return 0;
}
//
// This code is distributed under the GNU General Public License (see
// THE_GENERAL_GNU_PUBLIC_LICENSE.txt for extending this information).
// Copyright (C) 2014, the P2PSP team.
// http://www.p2psp.org
//
// DBS: Data Broadcasting Set of rules
//

#ifndef P2PSP_CORE_PEER_DBS_H
#define P2PSP_CORE_PEER_DBS_H

#include <vector>
#include <string>
#include <map>
#include <boost/asio.hpp>
#include <boost/array.hpp>
#include <boost/date_time/posix_time/posix_time.hpp>
#include <boost/thread/thread.hpp>
#include <arpa/inet.h>
#include <ctime>
#include "../util/trace.h"
#include "peer_ims.h"

using namespace boost::asio;

namespace p2psp {

class PeerDBS : PeerIMS {
 protected:
  int kMaxChunkDebt = 128;  // Peer's rejecting threshold

  bool kLogging = false;  // A IMS???
  std::string kLogFile;   // A IMS???

  int kAddr = 0;
  int kPort = 1;

  std::map<ip::udp::endpoint, int> debt_;

  int number_of_monitors_;
  int number_of_peers_;

  int receive_and_feed_counter_;
  std::vector<char> receive_and_feed_previous_;

  ip::udp::endpoint me_;

  int debt_memory_;

 public:
  PeerDBS();
  ~PeerDBS();
  void SayHello(ip::udp::endpoint);
  void SayGoodbye(ip::udp::endpoint);
  void ReceiveMagicFlags();
  void ReceiveTheNumberOfPeers();
  void ReceiveTheListOfPeers();
  void ReceiveMyEndpoint();
  void ListenToTheTeam();
  int ProcessMessage(std::vector<char>, ip::udp::endpoint);
  void LogMessage(std::string);
  void BuildLogMessage(std::string);
  float CalcBufferCorrectness();
  float CalcBufferFilling();
  void PoliteFarewell();
  void BufferData();
  void Run();
};
}

#endif  // P2PSP_CORE_PEER_DBS_H

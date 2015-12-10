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

class PeerDBS : public PeerIMS {
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
  virtual void Init();
  virtual void SayHello(ip::udp::endpoint);
  virtual void SayGoodbye(ip::udp::endpoint);
  virtual void ReceiveMagicFlags();
  virtual void ReceiveTheNumberOfPeers();
  virtual void ReceiveTheListOfPeers();
  virtual void ReceiveMyEndpoint();
  virtual void ListenToTheTeam();
  virtual int ProcessMessage(std::vector<char>, ip::udp::endpoint);
  virtual void LogMessage(std::string);
  virtual void BuildLogMessage(std::string);
  virtual float CalcBufferCorrectness();
  virtual float CalcBufferFilling();
  virtual void PoliteFarewell();
  virtual void BufferData();
  virtual void Start();
  virtual void Run();
  virtual bool AmIAMonitor();

  virtual int GetNumberOfPeers();
};
}

#endif  // P2PSP_CORE_PEER_DBS_H

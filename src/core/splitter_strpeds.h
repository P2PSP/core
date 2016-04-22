//
//  splitter_strpe.h
//  P2PSP
//
//  This code is distributed under the GNU General Public License (see
//  THE_GENERAL_GNU_PUBLIC_LICENSE.txt for extending this information).
//  Copyright (C) 2016, the P2PSP team.
//  http://www.p2psp.org
//

#ifndef P2PSP_CORE_SPLITTER_STRPEDS_H_
#define P2PSP_CORE_SPLITTER_STRPEDS_H_

#include <stdio.h>
#include <stdlib.h>
#include <boost/asio.hpp>
#include <boost/unordered_map.hpp>
#include <fstream>
#include "../util/trace.h"
#include "splitter_lrs.h"
#include "common.h"
#include "openssl/dsa.h"

namespace p2psp {
class SplitterSTRPEDS : public SplitterDBS {
 protected:
  
  const int kDigestSize = 40;
  const int kGatherBadPeersSleep = 5;
  const bool kLogging = false;
  const int kCurrentRound = 0;

  int digest_size_;
  int gather_bad_peers_sleep_;
  bool logging_;
  std::ofstream log_file_;
  int current_round_;
 
  std::vector<boost::asio::ip::udp::endpoint> trusted_peers_;
  int gathering_counter_;
  int trusted_gathering_counter_;
  std::vector<boost::asio::ip::udp::endpoint> gathered_bad_peers_;
  std::vector<std::vector<boost::asio::ip::udp::endpoint> > complains_;
  int majority_ratio_;

  DSA* dsa_key;
  
  // Thread management
  void Run() override;


 public:
  SplitterSTRPEDS();
  ~SplitterSTRPEDS();
  void SetMajorityRatio(int majority_ratio);
  void HandleAPeerArrival(
      std::shared_ptr<boost::asio::ip::tcp::socket> serve_socket) override;
  void SendDsaKey(const std::shared_ptr<boost::asio::ip::tcp::socket> &sock);
  void GatherBadPeers();
  boost::asio::ip::udp::endpoint GetPeerForGathering();
  boost::asio::ip::udp::endpoint GetTrustedPeerForGathering();
  void RequestBadPeers(const boost::asio::ip::udp::endpoint &dest);
  void InitKey();
  std::vector<char> GetMessage(int chunk_number,  boost::asio::streambuf chunk, const boost::asio::ip::udp::endpoint dst);
  std::stringstream LongToHex(BIGNUM value);
  void AddTrustedPeer(const boost::asio::ip::udp::endpoint &peer);
  //size_t SplitterDBS::ReceiveMessage(std::vector<char> &message, boost::asio::ip::udp::endpoint &endpoint) override;
  void ModerateTheTeam();
  void ProcessBadPeersMessage(const std::vector<char> &message, const boost::asio::ip::udp::endpoint &sender);
  void HandleBadPeerFromTrusted(const boost::asio::ip::udp::endpoint &bad_peer, const boost::asio::ip::udp::endpoint &sender);
  void HandleBadPeerFromRegular(const boost::asio::ip::udp::endpoint &bad_peer, const boost::asio::ip::udp::endpoint &sender);
  void AddComplain(const boost::asio::ip::udp::endpoint &bad_peer, const boost::asio::ip::udp::endpoint &sender);
  void PunishPeer(const boost::asio::ip::udp::endpoint &bad_peer, std::string message);
  
  void LogMessage(const std::string &message);
  std::string BuildLogMessage(const std::string &message);	   
  
  //void SetLogging(bool enabled);
  //void SetLogFile(const std::string &filename);

  // Thread management
  void Start();
};
}

#endif  // defined P2PSP_CORE_SPLITTER_STRPEDS_H_

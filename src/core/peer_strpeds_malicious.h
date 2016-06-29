//
//  peer_strpeds_malicious.h
//  P2PSP
//
//  This code is distributed under the GNU General Public License (see
//  THE_GENERAL_GNU_PUBLIC_LICENSE.txt for extending this information).
//  Copyright (C) 2016, the P2PSP team.
//  http://www.p2psp.org
//


#ifndef P2PSP_CORE_PEER_STRPEDS_MALICIOUS_H
#define P2PSP_CORE_PEER_STRPEDS_MALICIOUS_H

#include <vector>
#include <boost/asio.hpp>

#include "peer_strpeds.h"
#include "../util/trace.h"
#include <fstream>

namespace p2psp {

using namespace boost::asio;

class PeerStrpeDsMalicious : public PeerSTRPEDS {
 protected:
	bool persistent_attack_;
	bool on_off_attack_;
	int on_off_ratio_;
	bool selective_attack_;
	std::vector<boost::asio::ip::udp::endpoint> selected_peers_for_selective_attack_;
	std::vector<boost::asio::ip::udp::endpoint> regular_peers_;
	boost::asio::ip::udp::endpoint main_target_;
	int number_chunks_send_to_main_target_;
	bool all_attack_c_;
	bool bad_mouth_attack_;
	int MPTR;


 public:
  PeerStrpeDsMalicious(){
    magic_flags_ = Common::kSTRPE;
  };
  ~PeerStrpeDsMalicious(){};
  virtual void Init() override;
  virtual void FirstMainTarget();
  virtual boost::asio::ip::udp::endpoint ChooseMainTarget();
  virtual void AllAttack();
  virtual void RefreshRegularPeers();
  virtual void SetMPTR(int mptr);
  virtual void SetBadMouthAttack(bool, std::string);
  virtual void SetSelectiveAttack(bool, std::string);
  virtual void SetOnOffAttack(bool, int);
  virtual void SetPersistentAttack(bool);
  virtual void GetPoisonedChunk(std::vector<char>&);
  virtual void SendChunk(const ip::udp::endpoint&);
  virtual int DBSProcessMessage(const std::vector<char>&,
                                const ip::udp::endpoint&);
  virtual int ProcessMessage(const std::vector<char>&,
                             const ip::udp::endpoint&) override;
  virtual void ReceiveTheListOfPeers() override;
};
}

#endif  // P2PSP_CORE_PEER_STRPEDS_MALICIOUS_H

//
//  splitter_ems.h
//  P2PSP
//
//  This code is distributed under the GNU General Public License (see
//  THE_GENERAL_GNU_PUBLIC_LICENSE.txt for extending this information).
//  Copyright (C) 2016, the P2PSP team.
//  http://www.p2psp.org
//
//  EMS: Endpoint Masquerading Set of Rules
//

#ifndef P2PSP_CORE_SPLITTER_EMS_H_
#define P2PSP_CORE_SPLITTER_EMS_H_

#include <stdio.h>
#include <string>
#include <boost/asio.hpp>
#include <boost/unordered_map.hpp>
#include "splitter_dbs.h"
#include "common.h"
#include <boost/tuple/tuple.hpp>



namespace p2psp {
class SplitterEMS : public SplitterDBS {
 protected:

  // HashTable of public to private endpoints
  boost::unordered_map<boost::asio::ip::udp::endpoint, boost::asio::ip::udp::endpoint,
                       std::size_t (*)(const boost::asio::ip::udp::endpoint &)>
      peer_pairs_;



 public:
  SplitterEMS();
  ~SplitterEMS();
  virtual void SendTheListOfPeers(
      const std::shared_ptr<boost::asio::ip::tcp::socket> &peer_serve_socket);
  
  virtual void HandleAPeerArrival(
      std::shared_ptr<boost::asio::ip::tcp::socket> serve_socket) override;

  virtual void RemovePeer(const boost::asio::ip::udp::endpoint &peer) override;



};
}

#endif  // defined P2PSP_CORE_SPLITTER_EMS_H_

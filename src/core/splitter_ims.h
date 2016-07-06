//
//  splitter_ims.h -- IMS definition
//
//  This code is distributed under the GNU General Public License (see
//  THE_GENERAL_GNU_PUBLIC_LICENSE.txt for extending this information).
//  Copyright (C) 2016, the P2PSP team.
//  http://www.p2psp.org
//

#ifndef P2PSP_CORE_SPLITTER_IMS_H_
#define P2PSP_CORE_SPLITTER_IMS_H_

#include "splitter_core.h"

namespace p2psp {

  class Splitter_IMS : public Splitter_core {

  public:

    Splitter_IMS();
    ~Splitter_IMS();

    void SendMcastGroup(const std::shared_ptr<boost::asio::ip::tcp::socket> &peer_serve_socket);
    //int GetRecvFromCounter();
    //int GetSendToCounter();
    std::string GetMcastAddr();
    int GetTTL();
    static int GetDefaultTTL();
    static std::string GetDefaultMcastAddr();
    void SetupTeamSocket();
    virtual void SendConfiguration(const std::shared_ptr<boost::asio::ip::tcp::socket> &sock);
    virtual void HandleAPeerArrival(std::shared_ptr<boost::asio::ip::tcp::socket> serve_socket);
    virtual void Run();
    virtual void Start();
    
  protected:
    static const std::string kMCastAddr;   // All Systems on this subnet
    static const uint16_t kMcastPort;
    static const int kTTL;                 // Time To Live of multicast packets

    std::string mcast_addr_;
    int ttl_;

    boost::asio::ip::udp::endpoint mcast_channel_;

  };
}

#endif  // defined P2PSP_CORE_SPLITTER_IMS_H_

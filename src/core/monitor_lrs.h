//
//  monitor_lrs.h
//  P2PSP
//
//  This code is distributed under the GNU General Public License (see
//  THE_GENERAL_GNU_PUBLIC_LICENSE.txt for extending this information).
//  Copyright (C) 2016, the P2PSP team.
//  http://www.p2psp.org
//
//  LRS: Lost chunks Recovery Set of rules
//

#ifndef P2PSP_CORE_MONITOR_LRS_H
#define P2PSP_CORE_MONITOR_LRS_H

#include <vector>
#include <boost/asio.hpp>

#include "monitor_dbs.h"
#include "../util/trace.h"

namespace p2psp {

  using namespace boost::asio;
  
  class Monitor_LRS : public Monitor_DBS {
  protected:
  public:
    Monitor_LRS(){
      //magic_flags_ = Common::kLRS;
    };
  ~Monitor_LRS(){};
  virtual void Init() override;
  virtual void ReceiveBufferSize() override;
};
}

#endif  // P2PSP_CORE_MONITOR_LRS_H

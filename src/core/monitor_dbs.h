//
//  monitor_dbs.h -- DBS peer monitor
//
//  This code is distributed under the GNU General Public License (see
//  THE_GENERAL_GNU_PUBLIC_LICENSE.txt for extending this information).
//  Copyright (C) 2016, the P2PSP team.
//  http://www.p2psp.org
//

#ifndef P2PSP_CORE_MONITOR_DBS_H
#define P2PSP_CORE_MONITOR_DBS_H

#include "peer_dbs.h"
#include "../util/trace.h"

namespace p2psp {
  
  class Monitor_DBS : public Peer_DBS {
  public:
    Monitor_DBS();
    ~Monitor_DBS();
    virtual void Init() override;
    virtual void Complain(uint16_t);
    virtual int FindNextChunk() override;
    virtual void PlayNextChunk(int chunk_number) override;
  };
}

#endif  // P2PSP_CORE_MONITOR_DBS_H

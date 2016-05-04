//
//  trace.h
//  P2PSP
//
//  This code is distributed under the GNU General Public License (see
//  THE_GENERAL_GNU_PUBLIC_LICENSE.txt for extending this information).
//  Copyright (C) 2016, the P2PSP team.
//  http://www.p2psp.org
//

#ifndef P2PSP_UTIL_TRACE_H
#define P2PSP_UTIL_TRACE_H

#include <memory>
#include <boost/log/core.hpp>
#include <boost/log/trivial.hpp>

namespace p2psp
{

  /**
   * Wrapper used by the application to handle the log/trace
   * messages by means of the Boost Log library.
   */
  class TraceSystem
  {

  private:

    class Sink;
    typedef boost::log::sources::severity_logger<
      boost::log::trivial::severity_level> Logger;

    Logger logger_;
    std::unique_ptr<Sink> sink_ptr_;

    static TraceSystem trace_system_;

  public:

    TraceSystem();

    static Logger& logger()
    {
      return trace_system_.logger_;
    }

    static void Flush();

  };

}

#define _RED            "31m"
#define _GREEN          "32m"
#define _YELLOW         "33m"
#define _BLUE           "34m"

#ifndef TRACE_NO_COLORS

#define _SET_COLOR(a)   "\033[" a
#define _RESET_COLOR()  "\033[0m"

#else

#define _SET_COLOR(a)   ""
#define _RESET_COLOR()  ""

#endif // TRACE_NO_COLORS

#ifndef TRACE_SILENT_MODE

#ifndef NDEBUG

#define LOG(a)      \
  { BOOST_LOG_SEV(p2psp::TraceSystem::logger(), boost::log::trivial::info) \
    << a; }

#define LOGC(c, a)  \
  { BOOST_LOG_SEV(p2psp::TraceSystem::logger(), boost::log::trivial::info) \
    << _SET_COLOR(c) << a << _RESET_COLOR(); }

#define ERROR(a)    \
  { BOOST_LOG_SEV(p2psp::TraceSystem::logger(), boost::log::trivial::error)  \
    << _SET_COLOR(_RED) << __FILE__ << ":" << __LINE__ << ": ERROR: " \
    << a << _RESET_COLOR(); }

#define WARNING(a)    \
  { BOOST_LOG_SEV(p2psp::TraceSystem::logger(), boost::log::trivial::warning)  \
    << _SET_COLOR(_YELLOW) << __FILE__ << ":" << __LINE__ << ": WARNING: " \
    << a << _RESET_COLOR(); }

#define DEBUG(a)    \
  { BOOST_LOG_SEV(p2psp::TraceSystem::logger(), boost::log::trivial::debug)  \
    << __FILE__ << ":" << __LINE__ << ": DEBUG: " << a; }

#define TRACE(a)    \
  { BOOST_LOG_SEV(p2psp::TraceSystem::logger(), boost::log::trivial::trace)  \
    << _SET_COLOR(_YELLOW) << __FILE__ << ":" << __LINE__ << ": TRACE: " \
    << a << _RESET_COLOR(); }

#else

#define LOG(a)      {}
#define LOGC(c, a)  {}
#define WARNING(a)  {}
#define DEBUG(a)    {}

#define ERROR(a)    \
  { BOOST_LOG_SEV(p2psp::TraceSystem::logger(), boost::log::trivial::error)  \
    << _SET_COLOR(_RED) << __FILE__ << ":" << __LINE__ << ": ERROR: " \
    << a << _RESET_COLOR(); }

#define TRACE(a)    {}

#endif // NDEBUG

#else // TRACE_SILENT_MODE

#define LOG(a)      {}
#define LOGC(c, a)  {}
#define ERROR(a)    {}
#define WARNING(a)  {}
#define DEBUG(a)    {}
#define TRACE(a)    {}

#endif // TRACE_SILENT_MODE

#endif // P2PSP_UTIL_TRACE_H

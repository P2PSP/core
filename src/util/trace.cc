//
//  trace.cc
//  P2PSP
//
//  This code is distributed under the GNU General Public License (see
//  THE_GENERAL_GNU_PUBLIC_LICENSE.txt for extending this information).
//  Copyright (C) 2016, the P2PSP team.
//  http://www.p2psp.org
//

#include "trace.h"

#include <boost/date_time/posix_time/posix_time_types.hpp>
#include <boost/log/expressions.hpp>
#include <boost/log/sinks/sync_frontend.hpp>
#include <boost/log/sinks/text_file_backend.hpp>
#include <boost/log/sources/record_ostream.hpp>
#include <boost/log/sources/severity_logger.hpp>
#include <boost/log/support/date_time.hpp>
#include <boost/log/utility/setup/common_attributes.hpp>
#include <boost/log/utility/setup/console.hpp>
#include <boost/log/utility/setup/file.hpp>

#ifndef TRACE_THRESHOLD

#ifdef NDEBUG

#define TRACE_THRESHOLD info

#else

#define TRACE_THRESHOLD trace

#endif

#endif  // TRACE_THRESHOLD

namespace p2psp {

using namespace boost;

class TraceSystem::Sink {
 public:
  shared_ptr<boost::log::sinks::synchronous_sink<
      boost::log::sinks::text_file_backend> >
      log_sink_;
};

TraceSystem TraceSystem::trace_system_;

TraceSystem::TraceSystem() {
#ifdef TRACE_FILE_OUPUT

  sink_ptr_.reset(new TraceSystem::Sink());

  sink_ptr_->log_sink_ = log::add_file_log(
      log::keywords::file_name = "p2psp_%N.log",
      log::keywords::rotation_size = 10 * 1024 * 1024,
      log::keywords::time_based_rotation =
          log::sinks::file::rotation_at_time_point(0, 0, 0),
      log::keywords::format =
          (log::expressions::stream
           << log::expressions::format_date_time<posix_time::ptime>(
                  "TimeStamp", "%Y-%m-%d %H:%M:%S.%f")
           << " " << log::expressions::smessage));

#endif  // TRACE_FILE_OUTPUT

  log::add_console_log(
      std::cout, log::keywords::format =
                     (log::expressions::stream
                      << log::expressions::format_date_time<posix_time::ptime>(
                             "TimeStamp", "%Y-%m-%d %H:%M:%S.%f")
                      << " " << log::expressions::smessage));

  log::core::get()->set_filter(log::trivial::severity >=
                               log::trivial::TRACE_THRESHOLD);

  log::add_common_attributes();
}

void TraceSystem::Flush() {
  if (trace_system_.sink_ptr_) trace_system_.sink_ptr_->log_sink_->flush();
}
}
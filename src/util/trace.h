#ifndef _TRACE_H_
#define _TRACE_H_


#include <string>
#include <iostream>

#define LOG4CPP_FIX_ERROR_COLLISION 1
#include <log4cpp/Category.hh>
#include <log4cpp/FileAppender.hh>
#include <log4cpp/PatternLayout.hh>
#include <log4cpp/OstreamAppender.hh>


/**
 * Wrapper used by the application to handle the log/trace
 * messages by means of the log4cpp library.
 */
class TraceSystem
{
private:
  log4cpp::Category *category;
  log4cpp::Appender *appender;
  log4cpp::PatternLayout *layout;
  log4cpp::Appender *file_appender;
  log4cpp::PatternLayout *file_layout;

  static TraceSystem traceSystem;

  TraceSystem();
  virtual ~TraceSystem();

  bool AppendToFile_(const char *name);

public:
  static bool AppendToFile(const char *name)
  {
    return traceSystem.AppendToFile_(name);
  }

  static bool AppendToFile(const std::string& name)
  {
    return traceSystem.AppendToFile_(name.c_str());
  }

  static log4cpp::CategoryStream logStream()
  {
    return traceSystem.category->infoStream();
  }

  static log4cpp::CategoryStream errorStream()
  {
    return traceSystem.category->errorStream();
  }

  static log4cpp::CategoryStream traceStream()
  {
    return traceSystem.category->debugStream();
  }
};


#define _RED            "31m"
#define _GREEN          "32m"
#define _YELLOW         "33m"
#define _BLUE           "34m"

#ifndef NO_COLORS
#define _SET_COLOR(a)   "\033[" a
#define _RESET_COLOR()  "\033[0m"
#else
#define _SET_COLOR(a)   ""
#define _RESET_COLOR()  ""
#endif

#ifndef SILENT_MODE
#define LOG(a)      (TraceSystem::logStream() << a << log4cpp::eol)
#define LOGC(c, a)  (TraceSystem::logStream() << _SET_COLOR(c) << a << _RESET_COLOR() << log4cpp::eol)
#define ERROR(a)    (TraceSystem::errorStream() << _SET_COLOR(_RED) << __FILE__ << ":" << __LINE__ << ": ERROR: " << a << _RESET_COLOR() << log4cpp::eol)
#else
#define LOG(a)      {}
#define LOGC(c, a)  {}
#define ERROR(a)    {}
#endif

#if defined(SHOW_TRACES) && !defined(NDEBUG) && !defined(SILENT_MODE)
#define TRACE(a)    (TraceSystem::traceStream() << _SET_COLOR(_YELLOW) << __FILE__ << ":" << __LINE__ << ": TRACE: " << a << _RESET_COLOR() << log4cpp::eol)
#else
#define TRACE(a)    {}
#endif

#define CERR(a)     (cerr << _SET_COLOR(_RED) << a << "!" << _RESET_COLOR() << endl, -1)

#endif

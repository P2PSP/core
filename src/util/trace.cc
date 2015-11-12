#include "trace.h"


using namespace std;


TraceSystem TraceSystem::traceSystem;


TraceSystem::TraceSystem()
{
#ifndef SILENT_MODE
  layout = new log4cpp::PatternLayout();
  layout->setConversionPattern("%d: %m %n");

  appender = new log4cpp::OstreamAppender("OstreamAppender", &cout);
  appender->setLayout(layout);

  category = &(log4cpp::Category::getInstance("Category"));
  category->setPriority(log4cpp::Priority::DEBUG);
  category->setAppender(appender);

  file_appender = NULL;
#endif
}

bool TraceSystem::AppendToFile_(const char *name)
{
#ifdef SILENT_MODE
  return true;
#else
  if(file_appender) return false;
  else {
    char tm_cad[20] = "";
    char fn_cad[200] = "";

    time_t t;
    struct tm *tmp;

    t = time(NULL);
    tmp = localtime(&t);

    if(tmp == NULL) return false;
    else {
      if(!strftime(tm_cad, sizeof(tm_cad), "%Y%m%d.%H%M%S", tmp)) return false;
      else {
        snprintf(fn_cad, sizeof(fn_cad), "%s.%s.log", name, tm_cad);

        file_layout = new log4cpp::PatternLayout();
        file_layout->setConversionPattern("%d: %m %n");

        file_appender = new log4cpp::FileAppender("FileAppender", fn_cad);
        file_appender->setLayout(file_layout);

        category->setAppender(file_appender);

        return true;
      }
    }
  }
#endif
}

TraceSystem::~TraceSystem()
{
  log4cpp::Category::shutdown();
}

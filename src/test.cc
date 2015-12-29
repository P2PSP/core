#include "util/trace.h"


int main(int argc, const char* argv[]) 
{
    LOG("log 1");
    TRACE("trace");
    ERROR("error");
    LOG("log 2");
    
    p2psp::TraceSystem::Flush();
    
    return 0;
}

#include "util/trace.h"


int main(int argc, const char* argv[]) 
{
    INFO("info 1");
    TRACE("trace");
    ERROR("error");
    INFO("info 2");
    
    p2psp::TraceSystem::Flush();
    
    return 0;
}

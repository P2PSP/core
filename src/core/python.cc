#include <boost/python.hpp>

#include "peer_ims.h"
#include "peer_dbs.h"


using namespace p2psp;
using namespace boost::python;


BOOST_PYTHON_MODULE(libp2psp)
{
    class_<PeerIMS, boost::noncopyable>("PeerIMS")
        .def("Init", &PeerIMS::Init)
    ;
    
    class_<PeerDBS, boost::noncopyable>("PeerDBS")
        .def("Init", &PeerDBS::Init)
    ;
}
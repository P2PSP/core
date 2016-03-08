#include <boost/python.hpp>
#include <boost/python/suite/indexing/vector_indexing_suite.hpp>

#include "peer_ims.h"
#include "peer_dbs.h"


using namespace p2psp;
using namespace boost::python;

/*
std::vector<std::pair<ip::address, uint16_t> > GetList(){
	
	py::list peer_list_python;

	std::vector<std::pair<ip::address, uint16_t> > peer_list_aux_;
	peer_list_aux_.push_back(std::pair<ip::address, uint16_t>(ip::address::from_string("127.0.0.1"),4551));
	peer_list_aux_.push_back(std::pair<ip::address, uint16_t>(ip::address::from_string("127.0.0.2"),4552));
	return peer_list_aux_;
}

boost::python::list GetList()
{
  boost::python::list l;

  std::vector<std::pair<ip::address, uint16_t> > peer_list_aux_;
  peer_list_aux_.push_back(std::pair<ip::address, uint16_t>(ip::address::from_string("127.0.0.1"),4551));
  peer_list_aux_.push_back(std::pair<ip::address, uint16_t>(ip::address::from_string("127.0.0.2"),4552));

  typename std::vector<std::pair<ip::address, uint16_t> >::const_iterator it;
  for (it =  peer_list_aux_.begin(); it !=  peer_list_aux_.end(); ++it)
    l.append(*it);   
  return l;  
}
*/
BOOST_PYTHON_MODULE(libp2psp)
{
    //def("GetList",GetList);
    //class_<std::vector<std::pair<ip::address, uint16_t> > >("vecEP")
      //      .def(vector_indexing_suite<std::vector<std::pair<ip::address, uint16_t> > >());

    class_<PeerIMS, boost::noncopyable>("PeerIMS")
        .def("Init", &PeerIMS::Init)
        .def("WaitForThePlayer", &PeerIMS::WaitForThePlayer)
        .def("ConnectToTheSplitter", &PeerIMS::ConnectToTheSplitter)
        .def("DisconnectFromTheSplitter", &PeerIMS::DisconnectFromTheSplitter)
        .def("ReceiveTheMcasteEndpoint", &PeerIMS::ReceiveTheMcasteEndpoint)
        .def("ReceiveTheHeader", &PeerIMS::ReceiveTheHeader)
        .def("ReceiveTheChunkSize", &PeerIMS::ReceiveTheChunkSize)
        .def("ReceiveTheHeaderSize", &PeerIMS::ReceiveTheHeaderSize)
        .def("ReceiveTheBufferSize", &PeerIMS::ReceiveTheBufferSize)
        .def("ListenToTheTeam", &PeerIMS::ListenToTheTeam)
        .def("ReceiveTheNextMessage", &PeerIMS::ReceiveTheNextMessage)
        .def("ProcessMessage", &PeerIMS::ProcessMessage)
        .def("ProcessNextMessage", &PeerIMS::ProcessNextMessage)
        .def("BufferData", &PeerIMS::BufferData)
        .def("FindNextChunk", &PeerIMS::FindNextChunk)
        .def("PlayChunk", &PeerIMS::PlayChunk)
        .def("PlayNextChunk", &PeerIMS::PlayNextChunk)
        .def("KeepTheBufferFull", &PeerIMS::KeepTheBufferFull)
        .def("Run", &PeerIMS::Run)
        .def("Start", &PeerIMS::Start)
        .def("GetMcastAddr", &PeerIMS::GetMcastAddr)
        .def("IsPlayerAlive", &PeerIMS::IsPlayerAlive)
        .def("GetPlayedChunk", &PeerIMS::GetPlayedChunk)
        .def("GetChunkSize", &PeerIMS::GetChunkSize)
        .def("GetSendtoCounter", &PeerIMS::GetSendtoCounter)
        //.def("GetPeerList", &PeerIMS::GetPeerList)
        .def("GetRecvfromCounter", &PeerIMS::GetRecvfromCounter)
        .def("SetShowBuffer", &PeerIMS::SetShowBuffer)
        .def("SetSendtoCounter", &PeerIMS::SetSendtoCounter)
    ;
    
    class_<PeerDBS, bases<PeerIMS>, boost::noncopyable>("PeerDBS")
        .def("Init", &PeerDBS::Init)
	.def("SayHello", &PeerDBS::SayHello)
	.def("SayGoodbye", &PeerDBS::SayGoodbye)
	.def("ReceiveMagicFlags", &PeerDBS::ReceiveMagicFlags)
	.def("ReceiveTheNumberOfPeers", &PeerDBS::ReceiveTheNumberOfPeers)
	.def("ReceiveTheListOfPeers", &PeerDBS::ReceiveTheListOfPeers)
	.def("ReceiveMyEndpoint", &PeerDBS::ReceiveMyEndpoint)
	.def("ListenToTheTeam", &PeerDBS::ListenToTheTeam)
	.def("ProcessMessage", &PeerDBS::ProcessMessage)
	//.def("LogMessage", &PeerBDS::LogMessage)
	.def("BuildLogMessage", &PeerDBS::BuildLogMessage)
	.def("CalcBufferCorrectness", &PeerDBS::CalcBufferCorrectness)
	.def("CalcBufferFilling", &PeerDBS::CalcBufferFilling)
	.def("PoliteFarewell", &PeerDBS::PoliteFarewell)
	.def("BufferData", &PeerDBS::BufferData)
	.def("Start", &PeerDBS::Start)
	.def("Run", &PeerDBS::Run)	
	.def("AmIAMonitor", &PeerDBS::AmIAMonitor)
	.def("GetNumberOfPeers", &PeerDBS::GetNumberOfPeers)
	.def("SetMaxChunkDebt", &PeerDBS::SetMaxChunkDebt)
    ;
}

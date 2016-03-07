#include <boost/python.hpp>

#include "peer_ims.h"
#include "peer_dbs.h"


using namespace p2psp;
using namespace boost::python;


BOOST_PYTHON_MODULE(libp2psp)
{
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
    
    class_<PeerDBS, boost::noncopyable>("PeerDBS")
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

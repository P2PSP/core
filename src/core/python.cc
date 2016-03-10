#include <boost/python.hpp>
#include <boost/python/tuple.hpp>

#include "peer_ims.h"
#include "peer_dbs.h"
#include "splitter_ims.h"
#include "splitter_dbs.h"

#include <sstream>

using namespace p2psp;
using namespace boost::python;

//TODO Only the return methods have been converter to python compatible data types. I think that is necesary to do the same with parameters in the methods.

//Peer
class PyPeerDBS: public PeerDBS {
public:

	list GetPeerList_() {
		list l;
		std::string address;
		uint16_t port;
		for (unsigned int i = 0; i < peer_list_.size(); i++) {
			address = peer_list_[i].address().to_string();
			port = peer_list_[i].port();
			l.append(boost::python::make_tuple(address, port));
		}
		return l;
	}
};

//Splitter
class PySplitterDBS: public SplitterDBS {
public:

	list GetPeerList_() {
		list l;
		std::string address;
		uint16_t port;
		for (unsigned int i = 0; i < peer_list_.size(); i++) {
			address = peer_list_[i].address().to_string();
			port = peer_list_[i].port();
			l.append(boost::python::make_tuple(address, port));
		}
		return l;
	}
};

BOOST_PYTHON_MODULE(libp2psp)
{
	class_<PyPeerDBS, boost::noncopyable>("PeerDBS")
	//For variables
	//.add_property("var", &Class::get_var, &Class::set_var)

	//IMS
	.def("Init", &PyPeerDBS::Init)
	.def("WaitForThePlayer", &PyPeerDBS::WaitForThePlayer)
	.def("ConnectToTheSplitter", &PyPeerDBS::ConnectToTheSplitter)
	.def("DisconnectFromTheSplitter", &PyPeerDBS::DisconnectFromTheSplitter)
	.def("ReceiveTheMcasteEndpoint", &PyPeerDBS::ReceiveTheMcasteEndpoint)
	.def("ReceiveTheHeader", &PyPeerDBS::ReceiveTheHeader)
	.def("ReceiveTheChunkSize", &PyPeerDBS::ReceiveTheChunkSize)
	.def("ReceiveTheHeaderSize", &PyPeerDBS::ReceiveTheHeaderSize)
	.def("ReceiveTheBufferSize", &PyPeerDBS::ReceiveTheBufferSize)
	.def("ListenToTheTeam", &PyPeerDBS::ListenToTheTeam)
	.def("ReceiveTheNextMessage", &PyPeerDBS::ReceiveTheNextMessage)
	.def("ProcessMessage", &PyPeerDBS::ProcessMessage)
	.def("ProcessNextMessage", &PyPeerDBS::ProcessNextMessage)
	.def("BufferData", &PyPeerDBS::BufferData)
	.def("FindNextChunk", &PyPeerDBS::FindNextChunk)
	.def("PlayChunk", &PyPeerDBS::PlayChunk)
	.def("PlayNextChunk", &PyPeerDBS::PlayNextChunk)
	.def("KeepTheBufferFull", &PyPeerDBS::KeepTheBufferFull)
	.def("Run", &PyPeerDBS::Run)
	.def("Start", &PyPeerDBS::Start)
	.def("GetMcastAddr", &PyPeerDBS::GetMcastAddr)
	.def("IsPlayerAlive", &PyPeerDBS::IsPlayerAlive)
	.def("GetPlayedChunk", &PyPeerDBS::GetPlayedChunk)
	.def("GetChunkSize", &PyPeerDBS::GetChunkSize)
	.def("GetSendtoCounter", &PyPeerDBS::GetSendtoCounter)
	.def("GetRecvfromCounter", &PyPeerDBS::GetRecvfromCounter)
	.def("GetPeerList", &PyPeerDBS::GetPeerList_) //Modified here
	.def("SetShowBuffer", &PyPeerDBS::SetShowBuffer)
	.def("SetSendtoCounter", &PyPeerDBS::SetSendtoCounter)
	//DBS
	.def("SayHello", &PyPeerDBS::SayHello)
	.def("SayGoodbye", &PyPeerDBS::SayGoodbye)
	.def("ReceiveMagicFlags", &PyPeerDBS::ReceiveMagicFlags)
	.def("ReceiveTheNumberOfPeers", &PyPeerDBS::ReceiveTheNumberOfPeers)
	.def("ReceiveTheListOfPeers", &PyPeerDBS::ReceiveTheListOfPeers)
	.def("ReceiveMyEndpoint", &PyPeerDBS::ReceiveMyEndpoint)
	.def("ListenToTheTeam", &PyPeerDBS::ListenToTheTeam)
	.def("ProcessMessage", &PyPeerDBS::ProcessMessage)
	.def("LogMessage", &PyPeerDBS::LogMessage)
	.def("BuildLogMessage", &PyPeerDBS::BuildLogMessage)
	.def("CalcBufferCorrectness", &PyPeerDBS::CalcBufferCorrectness)
	.def("CalcBufferFilling", &PyPeerDBS::CalcBufferFilling)
	.def("PoliteFarewell", &PyPeerDBS::PoliteFarewell)
	.def("BufferData", &PyPeerDBS::BufferData)
	.def("Start", &PyPeerDBS::Start)
	.def("Run", &PyPeerDBS::Run)
	.def("AmIAMonitor", &PyPeerDBS::AmIAMonitor)
	.def("GetNumberOfPeers", &PyPeerDBS::GetNumberOfPeers)
	.def("SetMaxChunkDebt", &PyPeerDBS::SetMaxChunkDebt)
	;

	class_<PySplitterDBS, boost::noncopyable>("SplitterDBS")
	//IMS
	.def("SendTheHeader", &PySplitterDBS::SendTheHeader)
	.def("SendTheBufferSize", &PySplitterDBS::SendTheBufferSize)
	.def("SendTheChunkSize", &PySplitterDBS::SendTheChunkSize)
	.def("SendTheMcastChannel", &PySplitterDBS::SendTheMcastChannel)
	.def("SendTheHeaderSize", &PySplitterDBS::SendTheHeaderSize)
	.def("SendConfiguration", &PySplitterDBS::SendConfiguration)
	.def("HandleAPeerArrival", &PySplitterDBS::HandleAPeerArrival)
	.def("HandleArrivals", &PySplitterDBS::HandleArrivals)
	.def("SetupPeerConnectionSocket", &PySplitterDBS::SetupPeerConnectionSocket)
	.def("SetupTeamSocket", &PySplitterDBS::SetupTeamSocket)
	.def("RequestTheVideoFromTheSource", &PySplitterDBS::RequestTheVideoFromTheSource)
	.def("ConfigureSockets", &PySplitterDBS::ConfigureSockets)
	.def("LoadTheVideoHeader", &PySplitterDBS::LoadTheVideoHeader)
	.def("ReceiveNextChunk", &PySplitterDBS::ReceiveNextChunk)
	.def("ReceiveChunk", &PySplitterDBS::ReceiveChunk)
	.def("SendChunk", &PySplitterDBS::SendChunk)
	.def("ReceiveTheHeader", &PySplitterDBS::ReceiveTheHeader)
	.def("SayGoodbye", &PySplitterDBS::SayGoodbye)
	.def("Start", &PySplitterDBS::Start)
	.def("isAlive", &PySplitterDBS::isAlive)
	.def("GetRecvFromCounter", &PySplitterDBS::GetRecvFromCounter)
	.def("GetSendToCounter", &PySplitterDBS::GetSendToCounter)
	.def("GetChunkSize", &PySplitterDBS::GetChunkSize)
	.def("GetPort", &PySplitterDBS::GetPort)
	.def("SetAlive", &PySplitterDBS::SetAlive)
	.def("SetBufferSize", &PySplitterDBS::SetBufferSize)
	.def("SetChannel", &PySplitterDBS::SetChannel)
	.def("SetChunkSize", &PySplitterDBS::SetChunkSize)
	.def("SetHeaderSize", &PySplitterDBS::SetHeaderSize)
	.def("SetPort", &PySplitterDBS::SetPort)
	.def("SetSourceAddr", &PySplitterDBS::SetSourceAddr)
	.def("SetSourcePort", &PySplitterDBS::SetSourcePort)
	.def("SetGETMessage", &PySplitterDBS::SetGETMessage)
	//DBS
	.def("SendMagicFlags", &PySplitterDBS::SendMagicFlags)
	.def("SendTheListSize", &PySplitterDBS::SendTheListSize)
	.def("SendTheListOfPeers", &PySplitterDBS::SendTheListOfPeers)
	.def("SendThePeerEndpoint", &PySplitterDBS::SendThePeerEndpoint)
	.def("SendConfiguration", &PySplitterDBS::SendConfiguration)
	.def("InsertPeer", &PySplitterDBS::InsertPeer)
	.def("HandleAPeerArrival", &PySplitterDBS::HandleAPeerArrival)
	.def("ReceiveMessage", &PySplitterDBS::ReceiveMessage)
	.def("GetLostChunkNumber", &PySplitterDBS::GetLostChunkNumber)
	.def("RemovePeer", &PySplitterDBS::RemovePeer)
	.def("IncrementUnsupportivityOfPeer", &PySplitterDBS::IncrementUnsupportivityOfPeer)
	.def("ProcessLostChunk", &PySplitterDBS::ProcessLostChunk)
	.def("ProcessGoodbye", &PySplitterDBS::ProcessGoodbye)
	.def("ModerateTheTeam", &PySplitterDBS::ModerateTheTeam)
	.def("SetupTeamSocket", &PySplitterDBS::SetupTeamSocket)
	.def("ResetCounters", &PySplitterDBS::ResetCounters)
	.def("ResetCountersThread", &PySplitterDBS::ResetCountersThread)
	.def("ComputeNextPeerNumber", &PySplitterDBS::ComputeNextPeerNumber)
	.def("Start", &PySplitterDBS::Start)
	.def("GetPeerList", &PySplitterDBS::GetPeerList_) //Modified here
	.def("GetMaxChunkLoss", &PySplitterDBS::GetMaxChunkLoss)
	.def("GetLoss", &PySplitterDBS::GetLoss)
	.def("SetMaxChunkLoss", &PySplitterDBS::SetMaxChunkLoss)
	.def("SetMonitorNumber", &PySplitterDBS::SetMonitorNumber)
	;

}

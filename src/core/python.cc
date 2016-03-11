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

	void InsertPeer_(boost::python::tuple peer){
		ip::address address = boost::asio::ip::address::from_string(boost::python::extract<std::string>(peer[0]));
		uint16_t port = boost::python::extract<uint16_t>(peer[1]);
		peer_list_.push_back(boost::asio::ip::udp::endpoint(address,port));
	}

};

BOOST_PYTHON_MODULE(libp2psp)
{
	class_<PyPeerDBS, boost::noncopyable>("PeerDBS")
	//For variables
	//.add_property("var", &Class::get_var, &Class::set_var)

	//IMS
	.def("Init", &PyPeerDBS::Init) //used
	.def("WaitForThePlayer", &PyPeerDBS::WaitForThePlayer) //used
	.def("ConnectToTheSplitter", &PyPeerDBS::ConnectToTheSplitter) //used
	.def("DisconnectFromTheSplitter", &PyPeerDBS::DisconnectFromTheSplitter) //used
	.def("ReceiveTheMcasteEndpoint", &PyPeerDBS::ReceiveTheMcasteEndpoint) //used
	.def("ReceiveTheHeader", &PyPeerDBS::ReceiveTheHeader) //used
	.def("ReceiveTheChunkSize", &PyPeerDBS::ReceiveTheChunkSize) //used
	.def("ReceiveTheHeaderSize", &PyPeerDBS::ReceiveTheHeaderSize) //used
	.def("ReceiveTheBufferSize", &PyPeerDBS::ReceiveTheBufferSize) //used
	.def("ListenToTheTeam", &PyPeerDBS::ListenToTheTeam) //used
	.def("ReceiveTheNextMessage", &PyPeerDBS::ReceiveTheNextMessage)
	.def("ProcessMessage", &PyPeerDBS::ProcessMessage)
	.def("ProcessNextMessage", &PyPeerDBS::ProcessNextMessage)
	.def("BufferData", &PyPeerDBS::BufferData) //used
	.def("FindNextChunk", &PyPeerDBS::FindNextChunk)
	.def("PlayChunk", &PyPeerDBS::PlayChunk)
	.def("PlayNextChunk", &PyPeerDBS::PlayNextChunk)
	.def("KeepTheBufferFull", &PyPeerDBS::KeepTheBufferFull)
	.def("Run", &PyPeerDBS::Run)
	.def("Start", &PyPeerDBS::Start) //used
	.def("GetMcastAddr", &PyPeerDBS::GetMcastAddr) //used
	.def("IsPlayerAlive", &PyPeerDBS::IsPlayerAlive) //used
	.def("GetPlayedChunk", &PyPeerDBS::GetPlayedChunk) //used
	.def("GetChunkSize", &PyPeerDBS::GetChunkSize) //used
	.def("GetSendtoCounter", &PyPeerDBS::GetSendtoCounter) //used
	.def("GetRecvfromCounter", &PyPeerDBS::GetRecvfromCounter) //used
	.def("GetPeerList", &PyPeerDBS::GetPeerList_) //Modified here //used
	.def("SetShowBuffer", &PyPeerDBS::SetShowBuffer) //used
	.def("SetSendtoCounter", &PyPeerDBS::SetSendtoCounter) //used
	.def("SetPlayerPort", &PyPeerDBS::SetPlayerPort) //used
	.def("SetSplitterAddr", &PyPeerDBS::SetSplitterAddr) //used
	.def("SetSplitterPort", &PyPeerDBS::SetSplitterPort) //used
	.def("SetPort", &PyPeerDBS::SetPort) //used
	.def("SetUseLocalhost", &PyPeerDBS::SetUseLocalhost) //used

	//DBS
	.def("SayHello", &PyPeerDBS::SayHello)
	.def("SayGoodbye", &PyPeerDBS::SayGoodbye)
	.def("ReceiveMagicFlags", &PyPeerDBS::ReceiveMagicFlags) //used
	.def("ReceiveTheNumberOfPeers", &PyPeerDBS::ReceiveTheNumberOfPeers) //used
	.def("ReceiveTheListOfPeers", &PyPeerDBS::ReceiveTheListOfPeers) //used
	.def("ReceiveMyEndpoint", &PyPeerDBS::ReceiveMyEndpoint) //used
	.def("ListenToTheTeam", &PyPeerDBS::ListenToTheTeam) //used
	.def("ProcessMessage", &PyPeerDBS::ProcessMessage)
	.def("LogMessage", &PyPeerDBS::LogMessage)
	.def("BuildLogMessage", &PyPeerDBS::BuildLogMessage)
	.def("CalcBufferCorrectness", &PyPeerDBS::CalcBufferCorrectness)
	.def("CalcBufferFilling", &PyPeerDBS::CalcBufferFilling)
	.def("PoliteFarewell", &PyPeerDBS::PoliteFarewell)
	.def("BufferData", &PyPeerDBS::BufferData)
	.def("Start", &PyPeerDBS::Start)
	.def("Run", &PyPeerDBS::Run)
	.def("AmIAMonitor", &PyPeerDBS::AmIAMonitor) //used
	.def("GetNumberOfPeers", &PyPeerDBS::GetNumberOfPeers) //used
	.def("SetMaxChunkDebt", &PyPeerDBS::SetMaxChunkDebt) //used
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
	.def("SayGoodbye", &PySplitterDBS::SayGoodbye) //used
	.def("Start", &PySplitterDBS::Start)
	.def("isAlive", &PySplitterDBS::isAlive) //used
	.def("GetRecvFromCounter", &PySplitterDBS::GetRecvFromCounter) //used
	.def("GetSendToCounter", &PySplitterDBS::GetSendToCounter) //used
	.def("GetChunkSize", &PySplitterDBS::GetChunkSize) //used
	.def("GetPort", &PySplitterDBS::GetPort)
	.def("SetAlive", &PySplitterDBS::SetAlive) //used
	.def("SetBufferSize", &PySplitterDBS::SetBufferSize) //used
	.def("SetChannel", &PySplitterDBS::SetChannel) //used
	.def("SetChunkSize", &PySplitterDBS::SetChunkSize) //used
	.def("SetHeaderSize", &PySplitterDBS::SetHeaderSize) //used
	.def("SetPort", &PySplitterDBS::SetPort) //used
	.def("SetSourceAddr", &PySplitterDBS::SetSourceAddr) //used
	.def("SetSourcePort", &PySplitterDBS::SetSourcePort) //used
	.def("SetGETMessage", &PySplitterDBS::SetGETMessage)

	//DBS
	.def("SendMagicFlags", &PySplitterDBS::SendMagicFlags)
	.def("SendTheListSize", &PySplitterDBS::SendTheListSize)
	.def("SendTheListOfPeers", &PySplitterDBS::SendTheListOfPeers)
	.def("SendThePeerEndpoint", &PySplitterDBS::SendThePeerEndpoint)
	.def("SendConfiguration", &PySplitterDBS::SendConfiguration)
	.def("InsertPeer", &PySplitterDBS::InsertPeer_)
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
	.def("Start", &PySplitterDBS::Start) //used
	.def("GetPeerList", &PySplitterDBS::GetPeerList_) //Modified here //used
	.def("GetMaxChunkLoss", &PySplitterDBS::GetMaxChunkLoss) //used
	.def("GetLoss", &PySplitterDBS::GetLoss) //used
	.def("SetMaxChunkLoss", &PySplitterDBS::SetMaxChunkLoss) //used
	.def("SetMonitorNumber", &PySplitterDBS::SetMonitorNumber) //used
	;

}

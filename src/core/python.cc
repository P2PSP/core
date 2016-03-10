#include <boost/python.hpp>
#include <boost/python/tuple.hpp>

#include "peer_ims.h"
#include "peer_dbs.h"

#include <sstream>

using namespace p2psp;
using namespace boost::python;

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

BOOST_PYTHON_MODULE(libp2psp)
{
	class_<PyPeerDBS, boost::noncopyable>("PyPeerDBS")
	//For variables
	//.add_property("var", &Class::get_var, &Class::set_var)

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
	.def("GetPeerList", &PyPeerDBS::GetPeerList_)
	.def("SetShowBuffer", &PyPeerDBS::SetShowBuffer)
	.def("SetSendtoCounter", &PyPeerDBS::SetSendtoCounter)
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
}

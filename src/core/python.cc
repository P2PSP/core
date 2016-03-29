#include <boost/python.hpp>
#include <boost/python/tuple.hpp>

#include "peer_ims.h"
#include "peer_dbs.h"
#include "monitor_dbs.h"
#include "splitter_ims.h"
#include "splitter_dbs.h"

#include <sstream>

using namespace p2psp;
using namespace boost::python;

//Monitor
class PyMonitorDBS: public MonitorDBS {
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

  void SetMcastAddr(std::string address){
    mcast_addr_ = ip::address::from_string(address);
  }

  void SetChunkSize(int chunk_size){
    chunk_size_ = chunk_size;
  }

  void SetRecvfromCounter(int recvfrom_counter){
    recvfrom_counter_ = recvfrom_counter;
  }
  
  std::string GetSplitterAddr(){
    return splitter_addr_.to_string();
  }
  
  uint16_t GetSplitterPort(){
    return splitter_port_;
  }
  
  uint16_t GetPort(){
    return port_;
  }

  uint16_t GetPlayerPort(){
    return player_port_;
  }
  
  int GetMaxChunkDebt(){
	  return max_chunk_debt_;
  }
  
  bool GetUseLocalhost(){
    return use_localhost_;
  }
  
  bool GetShowBuffer(){
    return show_buffer_;
  }
};
  
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

  void SetMcastAddr(std::string address){
    mcast_addr_ = ip::address::from_string(address);
  }

  void SetChunkSize(int chunk_size){
    chunk_size_ = chunk_size;
  }

  void SetRecvfromCounter(int recvfrom_counter){
    recvfrom_counter_ = recvfrom_counter;
  }
  
  std::string GetSplitterAddr(){
    return splitter_addr_.to_string();
  }
  
  uint16_t GetSplitterPort(){
    return splitter_port_;
  }
  
  uint16_t GetPort(){
    return port_;
  }

  uint16_t GetPlayerPort(){
    return player_port_;
  }
  
  int GetMaxChunkDebt(){
	  return max_chunk_debt_;
  }
  
  bool GetUseLocalhost(){
    return use_localhost_;
  }
  
  bool GetShowBuffer(){
    return show_buffer_;
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
  
  int GetLoss_(boost::python::tuple peer){
    ip::address address = boost::asio::ip::address::from_string(boost::python::extract<std::string>(peer[0]));
    uint16_t port = boost::python::extract<uint16_t>(peer[1]);
    return losses_[boost::asio::ip::udp::endpoint(address,port)];
  }

  std::string GetChannel(){
    return channel_;
  }
  
  std::string GetSourceAddr(){
    return source_addr_;
  }
  
  int GetMonitorNumber(){
    return monitor_number_;
  }
  
  int GetBufferSize(){
    return buffer_size_;
  }
  
  int GetHeaderSize(){
    return header_size_;
  }

  int GetSourcePort(){
    return source_port_;
  }
  
  void SetRecvFromCounter(int recvfrom_counter){
    recvfrom_counter_ = recvfrom_counter;
  }

  void SetSendToCounter(int sendto_counter){
    sendto_counter_ = sendto_counter;
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
    //variables
    .add_property("splitter_addr", &PyPeerDBS::GetSplitterAddr, &PyPeerDBS::SetSplitterAddr)
    .add_property("splitter_port", &PyPeerDBS::GetSplitterPort, &PyPeerDBS::SetSplitterPort)
    .add_property("port", &PyPeerDBS::GetPort, &PyPeerDBS::SetPort)
    .add_property("player_port", &PyPeerDBS::GetPlayerPort, &PyPeerDBS::SetPlayerPort)
    .add_property("max_chunk_debt", &PyPeerDBS::GetMaxChunkDebt, &PyPeerDBS::SetMaxChunkDebt)
    .add_property("use_localhost", &PyPeerDBS::GetUseLocalhost, &PyPeerDBS::SetUseLocalhost)
    .add_property("mcast_addr", &PyPeerDBS::GetMcastAddr, &PyPeerDBS::SetMcastAddr)
    .add_property("show_buffer", &PyPeerDBS::GetShowBuffer, &PyPeerDBS::SetShowBuffer)
    .add_property("chunk_size", &PyPeerDBS::GetChunkSize, &PyPeerDBS::SetChunkSize)
    .add_property("sendto_counter", &PyPeerDBS::GetSendtoCounter, &PyPeerDBS::SetSendtoCounter)
    .add_property("recvfrom_counter", &PyPeerDBS::GetRecvfromCounter, &PyPeerDBS::SetRecvfromCounter)
	  
    //IMS
    .def("Init", &PyPeerDBS::Init) //used
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
    .def("IsPlayerAlive", &PyPeerDBS::IsPlayerAlive)
    .def("GetPlayedChunk", &PyPeerDBS::GetPlayedChunk)
    .def("GetPeerList", &PyPeerDBS::GetPeerList_) //Modified here

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
    .def("PoliteFarewell", &PyPeerDBS::PoliteFarewell)
    .def("BufferData", &PyPeerDBS::BufferData)
    .def("Start", &PyPeerDBS::Start)
    .def("Run", &PyPeerDBS::Run)
    .def("AmIAMonitor", &PyPeerDBS::AmIAMonitor)
    .def("GetNumberOfPeers", &PyPeerDBS::GetNumberOfPeers)
    .def("SetMaxChunkDebt", &PyPeerDBS::SetMaxChunkDebt) 
    ;

   class_<PyMonitorDBS, boost::noncopyable>("MonitorDBS")
    //variables
    .add_property("splitter_addr", &PyMonitorDBS::GetSplitterAddr, &PyMonitorDBS::SetSplitterAddr)
    .add_property("splitter_port", &PyMonitorDBS::GetSplitterPort, &PyMonitorDBS::SetSplitterPort)
    .add_property("port", &PyMonitorDBS::GetPort, &PyMonitorDBS::SetPort)
    .add_property("player_port", &PyMonitorDBS::GetPlayerPort, &PyMonitorDBS::SetPlayerPort)
    .add_property("max_chunk_debt", &PyMonitorDBS::GetMaxChunkDebt, &PyMonitorDBS::SetMaxChunkDebt)
    .add_property("use_localhost", &PyMonitorDBS::GetUseLocalhost, &PyMonitorDBS::SetUseLocalhost)
    .add_property("mcast_addr", &PyMonitorDBS::GetMcastAddr, &PyMonitorDBS::SetMcastAddr)
    .add_property("show_buffer", &PyMonitorDBS::GetShowBuffer, &PyMonitorDBS::SetShowBuffer)
    .add_property("chunk_size", &PyMonitorDBS::GetChunkSize, &PyMonitorDBS::SetChunkSize)
    .add_property("sendto_counter", &PyMonitorDBS::GetSendtoCounter, &PyMonitorDBS::SetSendtoCounter)
    .add_property("recvfrom_counter", &PyMonitorDBS::GetRecvfromCounter, &PyMonitorDBS::SetRecvfromCounter)
	  
    //IMS
    .def("Init", &PyMonitorDBS::Init) //used
    .def("WaitForThePlayer", &PyMonitorDBS::WaitForThePlayer)
    .def("ConnectToTheSplitter", &PyMonitorDBS::ConnectToTheSplitter)
    .def("DisconnectFromTheSplitter", &PyMonitorDBS::DisconnectFromTheSplitter)
    .def("ReceiveTheMcasteEndpoint", &PyMonitorDBS::ReceiveTheMcasteEndpoint) 
    .def("ReceiveTheHeader", &PyMonitorDBS::ReceiveTheHeader)
    .def("ReceiveTheChunkSize", &PyMonitorDBS::ReceiveTheChunkSize)
    .def("ReceiveTheHeaderSize", &PyMonitorDBS::ReceiveTheHeaderSize)
    .def("ReceiveTheBufferSize", &PyMonitorDBS::ReceiveTheBufferSize)
    .def("ListenToTheTeam", &PyMonitorDBS::ListenToTheTeam)
    .def("ReceiveTheNextMessage", &PyMonitorDBS::ReceiveTheNextMessage)
    .def("ProcessMessage", &PyMonitorDBS::ProcessMessage)
    .def("ProcessNextMessage", &PyMonitorDBS::ProcessNextMessage)
    .def("BufferData", &PyMonitorDBS::BufferData)
    .def("FindNextChunk", &PyMonitorDBS::FindNextChunk)
    .def("PlayChunk", &PyMonitorDBS::PlayChunk)
    .def("PlayNextChunk", &PyMonitorDBS::PlayNextChunk)
    .def("KeepTheBufferFull", &PyMonitorDBS::KeepTheBufferFull)
    .def("Run", &PyMonitorDBS::Run)
    .def("Start", &PyMonitorDBS::Start)
    .def("IsPlayerAlive", &PyMonitorDBS::IsPlayerAlive)
    .def("GetPlayedChunk", &PyMonitorDBS::GetPlayedChunk)
    .def("GetPeerList", &PyMonitorDBS::GetPeerList_) //Modified here

    //DBS
    .def("SayHello", &PyMonitorDBS::SayHello)
    .def("SayGoodbye", &PyMonitorDBS::SayGoodbye)
    .def("ReceiveMagicFlags", &PyMonitorDBS::ReceiveMagicFlags)
    .def("ReceiveTheNumberOfPeers", &PyMonitorDBS::ReceiveTheNumberOfPeers)
    .def("ReceiveTheListOfPeers", &PyMonitorDBS::ReceiveTheListOfPeers)
    .def("ReceiveMyEndpoint", &PyMonitorDBS::ReceiveMyEndpoint)
    .def("ListenToTheTeam", &PyMonitorDBS::ListenToTheTeam)
    .def("ProcessMessage", &PyMonitorDBS::ProcessMessage)
    .def("LogMessage", &PyMonitorDBS::LogMessage)
    .def("BuildLogMessage", &PyMonitorDBS::BuildLogMessage)
    .def("PoliteFarewell", &PyMonitorDBS::PoliteFarewell)
    .def("BufferData", &PyMonitorDBS::BufferData)
    .def("Start", &PyMonitorDBS::Start)
    .def("Run", &PyMonitorDBS::Run)
    .def("AmIAMonitor", &PyMonitorDBS::AmIAMonitor)
    .def("GetNumberOfPeers", &PyMonitorDBS::GetNumberOfPeers)
    .def("SetMaxChunkDebt", &PyMonitorDBS::SetMaxChunkDebt) 
    ;
  
  class_<PySplitterDBS, boost::noncopyable>("SplitterDBS")
    //Variables
    .add_property("buffer_size", &PySplitterDBS::GetBufferSize, &PySplitterDBS::SetBufferSize)
    .add_property("channel", &PySplitterDBS::GetChannel, &PySplitterDBS::SetChannel)
    .add_property("chunk_size", &PySplitterDBS::GetChunkSize, &PySplitterDBS::SetChunkSize)
    .add_property("header_size", &PySplitterDBS::GetHeaderSize, &PySplitterDBS::SetHeaderSize)
    .add_property("port", &PySplitterDBS::GetPort, &PySplitterDBS::SetPort)
    .add_property("source_addr", &PySplitterDBS::GetSourceAddr, &PySplitterDBS::SetSourceAddr)
    .add_property("source_port", &PySplitterDBS::GetSourcePort, &PySplitterDBS::SetSourcePort)
    .add_property("sendto_counter", &PySplitterDBS::GetSendToCounter, &PySplitterDBS::SetSendToCounter)
    .add_property("recvfrom_counter", &PySplitterDBS::GetRecvFromCounter, &PySplitterDBS::SetRecvFromCounter)
    .add_property("max_chunk_loss", &PySplitterDBS::GetMaxChunkLoss, &PySplitterDBS::SetMaxChunkLoss)
    .add_property("monitor_number", &PySplitterDBS::GetMonitorNumber, &PySplitterDBS::SetMonitorNumber)
    
    
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
    .def("SetAlive", &PySplitterDBS::SetAlive)
    .def("SetGETMessage", &PySplitterDBS::SetGETMessage)

    //DBS
    .def("SendMagicFlags", &PySplitterDBS::SendMagicFlags)
    .def("SendTheListSize", &PySplitterDBS::SendTheListSize)
    .def("SendTheListOfPeers", &PySplitterDBS::SendTheListOfPeers)
    .def("SendThePeerEndpoint", &PySplitterDBS::SendThePeerEndpoint)
    .def("SendConfiguration", &PySplitterDBS::SendConfiguration)
    .def("InsertPeer", &PySplitterDBS::InsertPeer_) //Modified here
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
    .def("GetLoss", &PySplitterDBS::GetLoss_) //Modified here
    ;
}

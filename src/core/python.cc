#include <boost/python.hpp>
#include <boost/python/tuple.hpp>
#include <boost/python/suite/indexing/vector_indexing_suite.hpp>
#include <boost/thread/thread.hpp>
#include <exception>

#include "peer_ims.h"
#include "peer_dbs.h"
#include "monitor_dbs.h"
#include "splitter_ims.h"
#include "splitter_dbs.h"

#include <sstream>

using namespace p2psp;
using namespace boost::python;

class acquireGIL 
{
public:
    inline acquireGIL(){
        state = PyGILState_Ensure();
    }

    inline ~acquireGIL(){
        PyGILState_Release(state);
    }
private:
    PyGILState_STATE state;
};

class releaseGIL{
public:
    inline releaseGIL(){
        save_state = PyEval_SaveThread();
    }

    inline ~releaseGIL(){
        PyEval_RestoreThread(save_state);
    }
private:
    PyThreadState *save_state;
};

//Monitor
class PyMonitorDBS: public MonitorDBS {
public:

  void Run(){
    TRACE("ENTRA EN RUN del WRAPPER");
    releaseGIL unlock;
    PeerDBS::Run();
  }
  
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
class PyPeerDBS: public PeerDBS, public wrapper<PeerDBS> {
public:
  PyPeerDBS () : PeerDBS(){}

  void Run(){
    TRACE("ENTRA EN RUN del WRAPPER");
    releaseGIL unlock;
    PeerDBS::Run();
  }
  
  int ProcessMessage(const std::vector<char> &message, const ip::udp::endpoint &sender) {
    TRACE("ENTRA EN PROCESS MESSAGE!!!");
     acquireGIL lock;
     if (override ProcessMessage = get_override("ProcessMessage")){
      TRACE("ENTRA EN PROCESS MESSAGE por PYTHON!!!");
      std::string address = sender.address().to_string();
      uint16_t port = sender.port();
      //This doesn't work properly. It seems a problem with message
      //data type. What is the corresponding one in python?
      //std::string message_(message.begin(),message.end());
      //boost::python::list l;
      //for (unsigned int i = 0; i < message.size(); i++) {
      //	l.append((unsigned char)message[i]);
      //}
      boost::python::object memoryView(boost::python::handle<>(PyMemoryView_FromMemory((char*)message.data(), message.size(), PyBUF_READ)));
      TRACE("SALE DE PROCESS MESSAGE por PYTHON!!!");
      return ProcessMessage(memoryView, boost::python::make_tuple(address, port));
      }
    TRACE("SALE DE PROCESS MESSAGE por C++!!!");
    return PeerDBS::ProcessMessage(message, sender);
  }

  int Default_ProcessMessage(const std::vector<char> &message, const ip::udp::endpoint &sender){
    return this->PeerDBS::ProcessMessage(message, sender);
  }

  int SendChunk(boost::python::list message, boost::python::tuple peer){
    ip::address address = boost::asio::ip::address::from_string(boost::python::extract<std::string>(peer[0]));
    uint16_t port = boost::python::extract<uint16_t>(peer[1]);
    
    std::vector<char> msg(len(message));
    for (int i = 0; i < len(message); ++i)
    {
      msg.push_back((char)boost::python::extract<unsigned char>(message[i]));
    }
    return team_socket_.send_to(::buffer(msg), boost::asio::ip::udp::endpoint(address,port));
  }

  void InsertChunk(int position, boost::python::object chunk){//boost::python::list chunk){
    /*
    std::vector<char> chunk_(len(chunk));
    for (int i = 0; i < len(chunk); ++i)
    {
      chunk_.push_back((char)boost::python::extract<unsigned char>(chunk[i]));
      }*/

    std::vector<char> chunk_ = boost::python::extract<std::vector<char> >(chunk);
    
    chunks_[position]= {chunk_, true};
  }
    /*
  void SendChunk(const ip::udp::endpoint &peer){
    if (override SendChunk = this->get_override("SendChunk")){
      std::string address = peer.address().to_string();
      uint16_t port = peer.port();
      SendChunk(boost::python::make_tuple(address, port));
    }
    PeerDBS::SendChunk(peer);
  }
*/
  list GetReceiveAndFeedPrevious(){
    boost::python::list l;
    for (unsigned int i = 0; i < receive_and_feed_previous_.size(); i++) {
      	l.append((unsigned char)receive_and_feed_previous_[i]);
    }
    return l; 
  }

  void SetReceiveAndFeedPrevious(boost::python::list l){
    for (int i = 0; i < len(l); ++i)
    {
        receive_and_feed_previous_.push_back(boost::python::extract<unsigned char>(l[i]));
    }
  }
    
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

  void RemovePeer_(boost::python::tuple peer){
    ip::address address = boost::asio::ip::address::from_string(boost::python::extract<std::string>(peer[0]));
    uint16_t port = boost::python::extract<uint16_t>(peer[1]);
    peer_list_.erase(std::find(peer_list_.begin(), peer_list_.end(), boost::asio::ip::udp::endpoint(address,port)));
  }

  void AddDebt(boost::python::tuple peer){
    ip::address address = boost::asio::ip::address::from_string(boost::python::extract<std::string>(peer[0]));
    uint16_t port = boost::python::extract<uint16_t>(peer[1]);
    debt_[boost::asio::ip::udp::endpoint(address,port)]++;
  }

  void SetDebt(boost::python::tuple peer, int value){
    ip::address address = boost::asio::ip::address::from_string(boost::python::extract<std::string>(peer[0]));
    uint16_t port = boost::python::extract<uint16_t>(peer[1]);
    debt_[boost::asio::ip::udp::endpoint(address,port)] = value;
  }

  int GetDebt(boost::python::tuple peer){
    ip::address address = boost::asio::ip::address::from_string(boost::python::extract<std::string>(peer[0]));
    uint16_t port = boost::python::extract<uint16_t>(peer[1]);
    return debt_[boost::asio::ip::udp::endpoint(address,port)];
  }

  void RemoveDebt(boost::python::tuple peer){
    ip::address address = boost::asio::ip::address::from_string(boost::python::extract<std::string>(peer[0]));
    uint16_t port = boost::python::extract<uint16_t>(peer[1]);
    debt_.erase(boost::asio::ip::udp::endpoint(address,port));
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

  int GetMessageSize(){
    return message_size_;
  }

  void SetMessageSize(int message_size){
    message_size_ = message_size;
  }

  int GetBufferSize(){
    return buffer_size_;
  }

  void SetBufferSize(int buffer_size){
    buffer_size_=buffer_size;
  }

  int GetReceivedCounter(){
    return received_counter_;
  }

  void SetReceivedCounter(int received_counter){
    received_counter_ = received_counter;
  }

  int GetRecAndFeedCounter(){
    return receive_and_feed_counter_;
  }

  void SetRecAndFeedCounter (int receive_and_feed_counter ){
    receive_and_feed_counter_ = receive_and_feed_counter;
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
  PyEval_InitThreads();
  class_<std::vector<char> >("CharVec")
            .def(vector_indexing_suite<std::vector<char> >());
  
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
    .add_property("message_size", &PyPeerDBS::GetMessageSize, &PyPeerDBS::SetMessageSize)
    .add_property("buffer_size", &PyPeerDBS::GetBufferSize, &PyPeerDBS::SetBufferSize)
    .add_property("received_counter", &PyPeerDBS::GetReceivedCounter, &PyPeerDBS::SetReceivedCounter)
    .add_property("receive_and_feed_counter", &PyPeerDBS::GetRecAndFeedCounter, &PyPeerDBS::SetRecAndFeedCounter)
    .add_property("receive_and_feed_previous_" , &PyPeerDBS::GetReceiveAndFeedPrevious, &PyPeerDBS::SetReceiveAndFeedPrevious)
    
    //IMS
    .def("Init", &PeerDBS::Init) //used
    .def("WaitForThePlayer", &PeerDBS::WaitForThePlayer)
    .def("ConnectToTheSplitter", &PeerDBS::ConnectToTheSplitter)
    .def("DisconnectFromTheSplitter", &PeerDBS::DisconnectFromTheSplitter)
    .def("ReceiveTheMcasteEndpoint", &PeerDBS::ReceiveTheMcasteEndpoint) 
    .def("ReceiveTheHeader", &PeerDBS::ReceiveTheHeader)
    .def("ReceiveTheChunkSize", &PeerDBS::ReceiveTheChunkSize)
    .def("ReceiveTheHeaderSize", &PeerDBS::ReceiveTheHeaderSize)
    .def("ReceiveTheBufferSize", &PeerDBS::ReceiveTheBufferSize)
    .def("ListenToTheTeam", &PeerDBS::ListenToTheTeam)
    .def("ReceiveTheNextMessage", &PeerDBS::ReceiveTheNextMessage)
    .def("ProcessNextMessage", &PeerDBS::ProcessNextMessage)
    .def("BufferData", &PeerDBS::BufferData)
    .def("FindNextChunk", &PeerDBS::FindNextChunk)
    .def("PlayChunk", &PeerDBS::PlayChunk)
    .def("PlayNextChunk", &PeerDBS::PlayNextChunk)
    .def("KeepTheBufferFull", &PeerDBS::KeepTheBufferFull)
    .def("Run", &PeerDBS::Run)
    .def("Start", &PeerDBS::Start)
    .def("IsPlayerAlive", &PeerDBS::IsPlayerAlive)
    .def("GetPlayedChunk", &PeerDBS::GetPlayedChunk)
    .def("GetPeerList", &PyPeerDBS::GetPeerList_) //Modified here
    
    //DBS
    .def("SayHello", &PyPeerDBS::SayHello)
    .def("SayGoodbye", &PyPeerDBS::SayGoodbye)
    .def("ReceiveMagicFlags", &PyPeerDBS::ReceiveMagicFlags)
    .def("ReceiveTheNumberOfPeers", &PyPeerDBS::ReceiveTheNumberOfPeers)
    .def("ReceiveTheListOfPeers", &PyPeerDBS::ReceiveTheListOfPeers)
    .def("ReceiveMyEndpoint", &PyPeerDBS::ReceiveMyEndpoint)
    .def("ListenToTheTeam", &PyPeerDBS::ListenToTheTeam)
    .def("LogMessage", &PyPeerDBS::LogMessage)
    .def("BuildLogMessage", &PyPeerDBS::BuildLogMessage)
    .def("PoliteFarewell", &PyPeerDBS::PoliteFarewell)
    .def("BufferData", &PyPeerDBS::BufferData)
    .def("Start", &PyPeerDBS::Start)
    .def("Run", &PyPeerDBS::Run)
    .def("AmIAMonitor", &PyPeerDBS::AmIAMonitor)
    .def("GetNumberOfPeers", &PyPeerDBS::GetNumberOfPeers)
    .def("SetMaxChunkDebt", &PyPeerDBS::SetMaxChunkDebt)
    .def("InsertPeer", &PyPeerDBS::InsertPeer_) //Modified here
    .def("RemovePeer", &PyPeerDBS::RemovePeer_) //Modified here
    .def("AddDebt", &PyPeerDBS::AddDebt)
    .def("GetDebt", &PyPeerDBS::GetDebt)
    .def("RemoveDebt", &PyPeerDBS::RemoveDebt)
    .def("SetDebt", &PyPeerDBS::SetDebt)
	 
    //Overrides
    .def("ProcessMessage", &PyPeerDBS::ProcessMessage, &PyPeerDBS::Default_ProcessMessage)
    .def("SendChunk", &PyPeerDBS::SendChunk)
    .def("InsertChunk", &PyPeerDBS::InsertChunk)
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

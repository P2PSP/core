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
#include "splitter_strpeds.h"
#include "peer_strpeds.h"

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

  std::string GetMcastAddr_(){
    return mcast_addr_.to_string();
  }

  void SetMcastAddr_(std::string address){
    mcast_addr_ = ip::address::from_string(address);
  }

  std::string GetSplitterAddr_(){
    return splitter_addr_.to_string();
  }

  void SetSplitterAddr_(std::string address){
    splitter_addr_ = ip::address::from_string(address);
  }

  void SetChunkSize(int chunk_size){
    chunk_size_ = chunk_size;
  }
  /*
  void SetRecvfromCounter(int recvfrom_counter){
    recvfrom_counter_ = recvfrom_counter;
  }
  */

  bool GetShowBuffer(){
    return show_buffer_;
  }

  bool GetUseLocalhost(){
    return use_localhost_;
  }
};

//Peer
class PyPeerDBS: public PeerDBS, public wrapper<PeerDBS> {
public:
  PyPeerDBS () : PeerDBS(){}

  void Run(){
    releaseGIL unlock;
    PeerDBS::Run();
  }

  int ProcessMessage(const std::vector<char> &message, const ip::udp::endpoint &sender) {
    acquireGIL lock;
    if (override ProcessMessage = get_override("ProcessMessage")){
      std::string address = sender.address().to_string();
      uint16_t port = sender.port();

      boost::python::object memoryView(boost::python::handle<>(PyMemoryView_FromMemory((char*)message.data(), message.size(), PyBUF_READ)));
      return ProcessMessage(memoryView, boost::python::make_tuple(address, port));
    }
    return PeerDBS::ProcessMessage(message, sender);
  }


  int SendChunk(boost::python::object message, boost::python::tuple peer){
    ip::address address = boost::asio::ip::address::from_string(boost::python::extract<std::string>(peer[0]));
    uint16_t port = boost::python::extract<uint16_t>(peer[1]);

    boost::python::object locals(boost::python::borrowed(PyEval_GetLocals()));
    boost::python::stl_input_iterator<unsigned char> begin(message), end;
    std::vector<char> msg(begin, end);

    return team_socket_.send_to(::buffer(msg), boost::asio::ip::udp::endpoint(address,port));
  }

  

  void InsertChunk(int position, boost::python::object chunk){//boost::python::list chunk){
    boost::python::object locals(boost::python::borrowed(PyEval_GetLocals()));
    boost::python::stl_input_iterator<unsigned char> begin(chunk), end;
    std::vector<char> chunk_(begin, end);
    chunks_[position] = {chunk_, true};
  }

  boost::python::object GetReceiveAndFeedPrevious(){
     boost::python::object receive_and_fedd_previous(boost::python::handle<>(PyMemoryView_FromMemory((char*)receive_and_feed_previous_.data(), receive_and_feed_previous_.size(), PyBUF_READ)));
    return receive_and_fedd_previous;
  }

  void SetReceiveAndFeedPrevious(boost::python::object receive_and_fedd_previous){
    boost::python::object locals(boost::python::borrowed(PyEval_GetLocals()));
    boost::python::stl_input_iterator<unsigned char> begin(receive_and_fedd_previous), end;
    std::vector<char> msg(begin, end);
    receive_and_feed_previous_ = msg;
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

  std::string GetMcastAddr_(){
    return mcast_addr_.to_string();
  }

  void SetMcastAddr_(std::string address){
    mcast_addr_ = ip::address::from_string(address);
  }

  void SetChunkSize(int chunk_size){
    chunk_size_ = chunk_size;
  }

  void SetRecvfromCounter(int recvfrom_counter){
    recvfrom_counter_ = recvfrom_counter;
  }

  std::string GetSplitterAddr_(){
    return splitter_addr_.to_string();
  }

  void SetSplitterAddr_(std::string address){
    splitter_addr_ = ip::address::from_string(address);
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

//PeerSTRPEDS
class PyPeerSTRPEDS: public PeerSTRPEDS, public wrapper<PeerSTRPEDS> {
public:
  PyPeerSTRPEDS () : PeerSTRPEDS(){}

  void Run(){
    releaseGIL unlock;
    PeerSTRPEDS::Run();
  }
  
  int ProcessMessage(const std::vector<char> &message, const ip::udp::endpoint &sender) {
    acquireGIL lock;
    if (override ProcessMessage = get_override("ProcessMessage")){     
      std::string address = sender.address().to_string();
      uint16_t port = sender.port();
      
      boost::python::object memoryView(boost::python::handle<>(PyMemoryView_FromMemory((char*)message.data(), message.size(), PyBUF_READ)));
      return ProcessMessage(memoryView, boost::python::make_tuple(address, port));
    }
    return PeerSTRPEDS::ProcessMessage(message, sender);
  }

  bool CheckMessage(boost::python::object message, boost::python::tuple peer) {
       ip::address address = boost::asio::ip::address::from_string(boost::python::extract<std::string>(peer[0]));
       uint16_t port = boost::python::extract<uint16_t>(peer[1]);
       
       boost::python::object locals(boost::python::borrowed(PyEval_GetLocals()));
       boost::python::stl_input_iterator<unsigned char> begin(message), end;
       std::vector<char> msg(begin, end);
      
     return PeerSTRPEDS::CheckMessage(msg, boost::asio::ip::udp::endpoint(address,port));
  }

   void ProcessBadMessage(boost::python::object message, boost::python::tuple peer){
    ip::address address = boost::asio::ip::address::from_string(boost::python::extract<std::string>(peer[0]));
    uint16_t port = boost::python::extract<uint16_t>(peer[1]);

    boost::python::object locals(boost::python::borrowed(PyEval_GetLocals()));
    boost::python::stl_input_iterator<unsigned char> begin(message), end;
    std::vector<char> msg(begin, end);
   
    PeerSTRPEDS::ProcessBadMessage(msg, boost::asio::ip::udp::endpoint(address,port));
  }
  
  bool IsControlMessage(boost::python::object message){
    boost::python::object locals(boost::python::borrowed(PyEval_GetLocals()));
    boost::python::stl_input_iterator<unsigned char> begin(message), end;
    std::vector<char> msg(begin, end);

    return PeerSTRPEDS::IsControlMessage(msg);
  }

  int SendChunk(boost::python::object message, boost::python::tuple peer){
    ip::address address = boost::asio::ip::address::from_string(boost::python::extract<std::string>(peer[0]));
    uint16_t port = boost::python::extract<uint16_t>(peer[1]);

    boost::python::object locals(boost::python::borrowed(PyEval_GetLocals()));
    boost::python::stl_input_iterator<unsigned char> begin(message), end;
    std::vector<char> msg(begin, end);
   
    return team_socket_.send_to(::buffer(msg), boost::asio::ip::udp::endpoint(address,port));
  }
  /*
  int SendFakeChunk(boost::python::tuple peer){
    ip::address address = boost::asio::ip::address::from_string(boost::python::extract<std::string>(peer[0]));
    uint16_t port = boost::python::extract<uint16_t>(peer[1]);
    std::vector<char> fake_chunk(1106);
    fake_chunk = receive_and_feed_previous_;
    fake_chunk[2] = 'F';
    return team_socket_.send_to(::buffer(fake_chunk), boost::asio::ip::udp::endpoint(address,port));
  }

  int SendRegularChunk(boost::python::tuple peer){
    ip::address address = boost::asio::ip::address::from_string(boost::python::extract<std::string>(peer[0]));
    uint16_t port = boost::python::extract<uint16_t>(peer[1]);
    return team_socket_.send_to(::buffer(receive_and_feed_previous_), boost::asio::ip::udp::endpoint(address,port));
  }
  */
  void InsertChunk(int position, boost::python::object chunk){//boost::python::list chunk){
    boost::python::object locals(boost::python::borrowed(PyEval_GetLocals()));
    boost::python::stl_input_iterator<unsigned char> begin(chunk), end;
    std::vector<char> chunk_(begin, end);
    chunks_[position] = {chunk_, true};
  }

  boost::python::object GetReceiveAndFeedPrevious(){
     boost::python::object receive_and_fedd_previous(boost::python::handle<>(PyMemoryView_FromMemory((char*)receive_and_feed_previous_.data(), receive_and_feed_previous_.size(), PyBUF_READ)));
    return receive_and_fedd_previous; 
  }

  void SetReceiveAndFeedPrevious(boost::python::object receive_and_fedd_previous){
    boost::python::object locals(boost::python::borrowed(PyEval_GetLocals()));
    boost::python::stl_input_iterator<unsigned char> begin(receive_and_fedd_previous), end;
    std::vector<char> msg(begin, end);
    receive_and_feed_previous_ = msg;
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

   list GetBadPeerList() {
    list l;
    std::string address;
    uint16_t port;
    for (unsigned int i = 0; i < bad_peers_.size(); i++) {
      address = bad_peers_[i].address().to_string();
      port = bad_peers_[i].port();
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

  std::string GetMcastAddr_(){
    return mcast_addr_.to_string();
  }
  
  void SetMcastAddr_(std::string address){
    mcast_addr_ = ip::address::from_string(address);
  }

  void SetChunkSize(int chunk_size){
    chunk_size_ = chunk_size;
  }

  void SetRecvfromCounter(int recvfrom_counter){
    recvfrom_counter_ = recvfrom_counter;
  }
  
  std::string GetSplitterAddr_(){
    return splitter_addr_.to_string();
  }

  void SetSplitterAddr_(std::string address){
    splitter_addr_ = ip::address::from_string(address);
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

  void KillThePlayer(){
    player_alive_ = false;
  }
};

  
//Splitter
class PySplitterDBS: public SplitterDBS  {
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

  int GetBufferSize(){
    return buffer_size_;
  }

  int GetHeaderSize(){
    return header_size_;
  }

  int GetSourcePort(){
    return source_port_;
  }

  void InsertPeer_(boost::python::tuple peer){
    ip::address address = boost::asio::ip::address::from_string(boost::python::extract<std::string>(peer[0]));
    uint16_t port = boost::python::extract<uint16_t>(peer[1]);
    peer_list_.push_back(boost::asio::ip::udp::endpoint(address,port));
  }


};

//Splitter STRPEDS
class PySplitterSTRPEDS: public SplitterSTRPEDS {
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
    
  int GetBufferSize(){
    return buffer_size_;
  }
  
  int GetHeaderSize(){
    return header_size_;
  }

  int GetSourcePort(){
    return source_port_;
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

  class_<PyPeerDBS, boost::noncopyable>("PeerDBS")

    //variables
    .add_property("splitter_addr", &PyPeerDBS::GetSplitterAddr_, &PyPeerDBS::SetSplitterAddr_)
    .add_property("splitter_port", &PyPeerDBS::GetSplitterPort, &PyPeerDBS::SetSplitterPort)
    .add_property("team_port", &PyPeerDBS::GetTeamPort, &PyPeerDBS::SetTeamPort)
    .add_property("player_port", &PyPeerDBS::GetPlayerPort, &PyPeerDBS::SetPlayerPort)
    .add_property("max_chunk_debt", &PyPeerDBS::GetMaxChunkDebt, &PyPeerDBS::SetMaxChunkDebt)
    .add_property("use_localhost", &PyPeerDBS::GetUseLocalhost, &PyPeerDBS::SetUseLocalhost)
    .add_property("mcast_addr", &PyPeerDBS::GetMcastAddr_, &PyPeerDBS::SetMcastAddr_)
    .add_property("show_buffer", &PyPeerDBS::GetShowBuffer, &PyPeerDBS::SetShowBuffer)
    .add_property("chunk_size", &PyPeerDBS::GetChunkSize, &PyPeerDBS::SetChunkSize)
    .add_property("message_size", &PyPeerDBS::GetMessageSize, &PyPeerDBS::SetMessageSize)
    .add_property("buffer_size", &PyPeerDBS::GetBufferSize, &PyPeerDBS::SetBufferSize)
    .add_property("received_counter", &PyPeerDBS::GetReceivedCounter, &PyPeerDBS::SetReceivedCounter)
    .add_property("receive_and_feed_counter", &PyPeerDBS::GetRecAndFeedCounter, &PyPeerDBS::SetRecAndFeedCounter)
    .add_property("receive_and_feed_previous" , &PyPeerDBS::GetReceiveAndFeedPrevious, &PyPeerDBS::SetReceiveAndFeedPrevious)
    .add_property("sendto_counter", &PyPeerDBS::GetSendtoCounter, &PyPeerDBS::SetSendtoCounter)


    //IMS
    .def("Init", &PeerDBS::Init) //used
    .def("WaitForThePlayer", &PeerDBS::WaitForThePlayer)
    .def("ConnectToTheSplitter", &PeerDBS::ConnectToTheSplitter)
    .def("DisconnectFromTheSplitter", &PeerDBS::DisconnectFromTheSplitter)
    .def("ReceiveTheMcastEndpoint", &PeerDBS::ReceiveTheMcastEndpoint)
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
    .def("ProcessMessage", &PyPeerDBS::ProcessMessage)
    .def("SendChunk", &PyPeerDBS::SendChunk)
    .def("InsertChunk", &PyPeerDBS::InsertChunk)
    ;


  class_<PyPeerSTRPEDS, boost::noncopyable>("PeerSTRPEDS")
    
    //variables
    .add_property("splitter_addr", &PyPeerSTRPEDS::GetSplitterAddr_, &PyPeerSTRPEDS::SetSplitterAddr_)
    .add_property("splitter_port", &PyPeerSTRPEDS::GetSplitterPort, &PyPeerSTRPEDS::SetSplitterPort)
    .add_property("team_port", &PyPeerSTRPEDS::GetTeamPort, &PyPeerSTRPEDS::SetTeamPort)
    .add_property("player_port", &PyPeerSTRPEDS::GetPlayerPort, &PyPeerSTRPEDS::SetPlayerPort)
    .add_property("max_chunk_debt", &PyPeerSTRPEDS::GetMaxChunkDebt, &PyPeerSTRPEDS::SetMaxChunkDebt)
    .add_property("use_localhost", &PyPeerSTRPEDS::GetUseLocalhost, &PyPeerSTRPEDS::SetUseLocalhost)
    .add_property("mcast_addr", &PyPeerSTRPEDS::GetMcastAddr_, &PyPeerSTRPEDS::SetMcastAddr_)
    .add_property("show_buffer", &PyPeerSTRPEDS::GetShowBuffer, &PyPeerSTRPEDS::SetShowBuffer)
    .add_property("chunk_size", &PyPeerSTRPEDS::GetChunkSize, &PyPeerSTRPEDS::SetChunkSize)
    .add_property("message_size", &PyPeerSTRPEDS::GetMessageSize, &PyPeerSTRPEDS::SetMessageSize)
    .add_property("buffer_size", &PyPeerSTRPEDS::GetBufferSize, &PyPeerSTRPEDS::SetBufferSize)
    .add_property("received_counter", &PyPeerSTRPEDS::GetReceivedCounter, &PyPeerSTRPEDS::SetReceivedCounter)
    .add_property("receive_and_feed_counter", &PyPeerSTRPEDS::GetRecAndFeedCounter, &PyPeerSTRPEDS::SetRecAndFeedCounter)
    .add_property("receive_and_feed_previous" , &PyPeerSTRPEDS::GetReceiveAndFeedPrevious, &PyPeerSTRPEDS::SetReceiveAndFeedPrevious)
    .add_property("sendto_counter", &PyPeerSTRPEDS::GetSendtoCounter, &PyPeerSTRPEDS::SetSendtoCounter)
    .add_property("recvfrom_counter", &PyPeerSTRPEDS::GetRecvfromCounter, &PyPeerSTRPEDS::SetRecvfromCounter)
	.add_property("current_round", &PyPeerSTRPEDS::GetCurrentRound, &PyPeerSTRPEDS::SetCurrentRound)
    
    //IMS
    .def("Init", &PeerSTRPEDS::Init) //used
    .def("WaitForThePlayer", &PeerSTRPEDS::WaitForThePlayer)
    .def("ConnectToTheSplitter", &PeerSTRPEDS::ConnectToTheSplitter)
    .def("DisconnectFromTheSplitter", &PeerSTRPEDS::DisconnectFromTheSplitter)
    .def("ReceiveTheMcastEndpoint", &PeerSTRPEDS::ReceiveTheMcastEndpoint) 
    .def("ReceiveTheHeader", &PeerSTRPEDS::ReceiveTheHeader)
    .def("ReceiveTheChunkSize", &PeerSTRPEDS::ReceiveTheChunkSize)
    .def("ReceiveTheHeaderSize", &PeerSTRPEDS::ReceiveTheHeaderSize)
    .def("ReceiveTheBufferSize", &PeerSTRPEDS::ReceiveTheBufferSize)
    .def("ListenToTheTeam", &PeerSTRPEDS::ListenToTheTeam)
    .def("ReceiveTheNextMessage", &PeerSTRPEDS::ReceiveTheNextMessage)
    .def("ProcessNextMessage", &PeerSTRPEDS::ProcessNextMessage)
    .def("BufferData", &PeerSTRPEDS::BufferData)
    .def("FindNextChunk", &PeerSTRPEDS::FindNextChunk)
    .def("PlayChunk", &PeerSTRPEDS::PlayChunk)
    .def("PlayNextChunk", &PeerSTRPEDS::PlayNextChunk)
    .def("KeepTheBufferFull", &PeerSTRPEDS::KeepTheBufferFull)
    .def("Run", &PeerSTRPEDS::Run)
    .def("Start", &PeerSTRPEDS::Start)
    .def("IsPlayerAlive", &PeerSTRPEDS::IsPlayerAlive)
    .def("GetPlayedChunk", &PeerSTRPEDS::GetPlayedChunk)
    .def("GetPeerList", &PyPeerSTRPEDS::GetPeerList_) //Modified here
    
    //DBS
    .def("SayHello", &PyPeerSTRPEDS::SayHello)
    .def("SayGoodbye", &PyPeerSTRPEDS::SayGoodbye)
    .def("ReceiveMagicFlags", &PyPeerSTRPEDS::ReceiveMagicFlags)
    .def("ReceiveTheNumberOfPeers", &PyPeerSTRPEDS::ReceiveTheNumberOfPeers)
    .def("ReceiveTheListOfPeers", &PyPeerSTRPEDS::ReceiveTheListOfPeers)
    .def("ReceiveMyEndpoint", &PyPeerSTRPEDS::ReceiveMyEndpoint)
    .def("ListenToTheTeam", &PyPeerSTRPEDS::ListenToTheTeam)
    .def("LogMessage", &PyPeerSTRPEDS::LogMessage)
    .def("BuildLogMessage", &PyPeerSTRPEDS::BuildLogMessage)
    .def("PoliteFarewell", &PyPeerSTRPEDS::PoliteFarewell)
    .def("BufferData", &PyPeerSTRPEDS::BufferData)
    .def("Start", &PyPeerSTRPEDS::Start)
    .def("Run", &PyPeerSTRPEDS::Run)
    .def("AmIAMonitor", &PyPeerSTRPEDS::AmIAMonitor)
    .def("GetNumberOfPeers", &PyPeerSTRPEDS::GetNumberOfPeers)
    .def("SetMaxChunkDebt", &PyPeerSTRPEDS::SetMaxChunkDebt)
    .def("InsertPeer", &PyPeerSTRPEDS::InsertPeer_) //Modified here
    .def("RemovePeer", &PyPeerSTRPEDS::RemovePeer_) //Modified here
    .def("AddDebt", &PyPeerSTRPEDS::AddDebt)
    .def("GetDebt", &PyPeerSTRPEDS::GetDebt)
    .def("RemoveDebt", &PyPeerSTRPEDS::RemoveDebt)
    .def("SetDebt", &PyPeerSTRPEDS::SetDebt)
	 
    //Overrides
    .def("ProcessMessage", &PyPeerSTRPEDS::ProcessMessage)
    .def("SendChunk", &PyPeerSTRPEDS::SendChunk)
    .def("InsertChunk", &PyPeerSTRPEDS::InsertChunk)    
    
    //STRPEDS
    .def("ReceiveDsaKey", &PyPeerSTRPEDS::ReceiveDsaKey)
    .def("GetBadPeerList", &PyPeerSTRPEDS::GetBadPeerList)
    .def("IsCurrentMessageFromSplitter", &PyPeerSTRPEDS::IsCurrentMessageFromSplitter)
    .def("CheckMessage", &PyPeerSTRPEDS::CheckMessage)
    .def("IsControlMessage", &PyPeerSTRPEDS::IsControlMessage)
    .def("ProcessBadMessage", &PyPeerSTRPEDS::ProcessBadMessage)
    .def("SetLogging", &PyPeerSTRPEDS::SetLogging)
    .def("SetLogFile", &PyPeerSTRPEDS::SetLogFile)
    .def("KillThePlayer", &PyPeerSTRPEDS::KillThePlayer)
    //.def("SendRegularChunk", &PyPeerSTRPEDS::SendRegularChunk)
    //.def("SendFakeChunk", &PyPeerSTRPEDS::SendFakeChunk)
    ;

   

  class_<PyMonitorDBS, boost::noncopyable>("MonitorDBS")
    //variables
    .add_property("splitter_addr", &PyMonitorDBS::GetSplitterAddr_, &PyMonitorDBS::SetSplitterAddr_)
    .add_property("splitter_port", &PyMonitorDBS::GetSplitterPort, &PyMonitorDBS::SetSplitterPort)
    .add_property("team_port", &PyMonitorDBS::GetTeamPort, &PyMonitorDBS::SetTeamPort)
    .add_property("player_port", &PyMonitorDBS::GetPlayerPort, &PyMonitorDBS::SetPlayerPort)
    .add_property("max_chunk_debt", &PyMonitorDBS::GetMaxChunkDebt, &PyMonitorDBS::SetMaxChunkDebt)
    .add_property("use_localhost", &PyMonitorDBS::GetUseLocalhost, &PyMonitorDBS::SetUseLocalhost)
    .add_property("mcast_addr", &PyMonitorDBS::GetMcastAddr_, &PyMonitorDBS::SetMcastAddr_)
    .add_property("show_buffer", &PyMonitorDBS::GetShowBuffer, &PyMonitorDBS::SetShowBuffer)
    .add_property("chunk_size", &PyMonitorDBS::GetChunkSize, &PyMonitorDBS::SetChunkSize)
    .add_property("sendto_counter", &PyMonitorDBS::GetSendtoCounter, &PyMonitorDBS::SetSendtoCounter)

    //IMS
    .def("Init", &PyMonitorDBS::Init) //used
    .def("WaitForThePlayer", &PyMonitorDBS::WaitForThePlayer)
    .def("ConnectToTheSplitter", &PyMonitorDBS::ConnectToTheSplitter)
    .def("DisconnectFromTheSplitter", &PyMonitorDBS::DisconnectFromTheSplitter)
    .def("ReceiveTheMcastEndpoint", &PyMonitorDBS::ReceiveTheMcastEndpoint)
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
    .add_property("team_port", &PySplitterDBS::GetTeamPort, &PySplitterDBS::SetTeamPort)
    .add_property("source_addr", &PySplitterDBS::GetSourceAddr, &PySplitterDBS::SetSourceAddr)
    .add_property("source_port", &PySplitterDBS::GetSourcePort, &PySplitterDBS::SetSourcePort)
    .add_property("max_number_of_chunk_loss", &PySplitterDBS::GetMaxNumberOfChunkLoss, &PySplitterDBS::SetMaxNumberOfChunkLoss)
    .add_property("max_number_of_monitors", &PySplitterDBS::GetMaxNumberOfMonitors, &PySplitterDBS::SetMaxNumberOfMonitors)


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
    .def("GetSendToCounter", &PySplitterDBS::GetSendToCounter)
    .def("GetRecvFromCounter", &PySplitterDBS::GetRecvFromCounter)
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

  class_<PySplitterSTRPEDS, boost::noncopyable>("SplitterSTRPEDS")
    //Variables
    .add_property("buffer_size", &PySplitterSTRPEDS::GetBufferSize, &PySplitterSTRPEDS::SetBufferSize)
    .add_property("channel", &PySplitterSTRPEDS::GetChannel, &PySplitterSTRPEDS::SetChannel)
    .add_property("chunk_size", &PySplitterSTRPEDS::GetChunkSize, &PySplitterSTRPEDS::SetChunkSize)
    .add_property("header_size", &PySplitterSTRPEDS::GetHeaderSize, &PySplitterSTRPEDS::SetHeaderSize)
    .add_property("team_port", &PySplitterSTRPEDS::GetTeamPort, &PySplitterSTRPEDS::SetTeamPort)
    .add_property("source_addr", &PySplitterSTRPEDS::GetSourceAddr, &PySplitterSTRPEDS::SetSourceAddr)
    .add_property("source_port", &PySplitterSTRPEDS::GetSourcePort, &PySplitterSTRPEDS::SetSourcePort)
    .add_property("max_number_of_chunk_loss", &PySplitterSTRPEDS::GetMaxNumberOfChunkLoss, &PySplitterSTRPEDS::SetMaxNumberOfChunkLoss)
    .add_property("max_number_of_monitors", &PySplitterSTRPEDS::GetMaxNumberOfMonitors, &PySplitterSTRPEDS::SetMaxNumberOfMonitors)
    .add_property("p_mpl", &PySplitterSTRPEDS::GetPMPL, &PySplitterSTRPEDS::SetPMPL)
	.add_property("p_tpl", &PySplitterSTRPEDS::GetPTPL, &PySplitterSTRPEDS::SetPTPL)

    //IMS
    .def("SendTheHeader", &PySplitterSTRPEDS::SendTheHeader)
    .def("SendTheBufferSize", &PySplitterSTRPEDS::SendTheBufferSize)
    .def("SendTheChunkSize", &PySplitterSTRPEDS::SendTheChunkSize)
    .def("SendTheMcastChannel", &PySplitterSTRPEDS::SendTheMcastChannel)
    .def("SendTheHeaderSize", &PySplitterSTRPEDS::SendTheHeaderSize)
    .def("SendConfiguration", &PySplitterSTRPEDS::SendConfiguration)
    .def("HandleAPeerArrival", &PySplitterSTRPEDS::HandleAPeerArrival)
    .def("HandleArrivals", &PySplitterSTRPEDS::HandleArrivals)
    .def("SetupPeerConnectionSocket", &PySplitterSTRPEDS::SetupPeerConnectionSocket)
    .def("SetupTeamSocket", &PySplitterSTRPEDS::SetupTeamSocket)
    .def("RequestTheVideoFromTheSource", &PySplitterSTRPEDS::RequestTheVideoFromTheSource)
    .def("ConfigureSockets", &PySplitterSTRPEDS::ConfigureSockets)
    .def("LoadTheVideoHeader", &PySplitterSTRPEDS::LoadTheVideoHeader)
    .def("ReceiveNextChunk", &PySplitterSTRPEDS::ReceiveNextChunk)
    .def("ReceiveChunk", &PySplitterSTRPEDS::ReceiveChunk)
    .def("SendChunk", &PySplitterSTRPEDS::SendChunk)
    .def("ReceiveTheHeader", &PySplitterSTRPEDS::ReceiveTheHeader)
    .def("SayGoodbye", &PySplitterSTRPEDS::SayGoodbye)
    .def("Start", &PySplitterSTRPEDS::Start)
    .def("isAlive", &PySplitterSTRPEDS::isAlive)
    .def("SetAlive", &PySplitterSTRPEDS::SetAlive)
    .def("SetGETMessage", &PySplitterSTRPEDS::SetGETMessage)
    .def("GetSendToCounter", &PySplitterSTRPEDS::GetSendToCounter)
    .def("GetRecvFromCounter", &PySplitterSTRPEDS::GetRecvFromCounter)

    //DBS
    .def("SendMagicFlags", &PySplitterSTRPEDS::SendMagicFlags)
    .def("SendTheListSize", &PySplitterSTRPEDS::SendTheListSize)
    .def("SendTheListOfPeers", &PySplitterSTRPEDS::SendTheListOfPeers)
    .def("SendThePeerEndpoint", &PySplitterSTRPEDS::SendThePeerEndpoint)
    .def("SendConfiguration", &PySplitterSTRPEDS::SendConfiguration)
    .def("InsertPeer", &PySplitterSTRPEDS::InsertPeer_) //Modified here
    .def("HandleAPeerArrival", &PySplitterSTRPEDS::HandleAPeerArrival)
    .def("ReceiveMessage", &PySplitterSTRPEDS::ReceiveMessage)
    .def("GetLostChunkNumber", &PySplitterSTRPEDS::GetLostChunkNumber)
    .def("RemovePeer", &PySplitterSTRPEDS::RemovePeer)
    .def("IncrementUnsupportivityOfPeer", &PySplitterSTRPEDS::IncrementUnsupportivityOfPeer)
    .def("ProcessLostChunk", &PySplitterSTRPEDS::ProcessLostChunk)
    .def("ProcessGoodbye", &PySplitterSTRPEDS::ProcessGoodbye)
    .def("ModerateTheTeam", &PySplitterSTRPEDS::ModerateTheTeam)
    .def("SetupTeamSocket", &PySplitterSTRPEDS::SetupTeamSocket)
    .def("ResetCounters", &PySplitterSTRPEDS::ResetCounters)
    .def("ResetCountersThread", &PySplitterSTRPEDS::ResetCountersThread)
    .def("ComputeNextPeerNumber", &PySplitterSTRPEDS::ComputeNextPeerNumber)
    .def("Start", &PySplitterSTRPEDS::Start)
    .def("GetPeerList", &PySplitterSTRPEDS::GetPeerList_) //Modified here
    .def("GetLoss", &PySplitterSTRPEDS::GetLoss_) //Modified here

    //STRPEDS
    .def("SetLogging", &PySplitterSTRPEDS::SetLogging)
    .def("SetLogFile", &PySplitterSTRPEDS::SetLogFile)
	;
}

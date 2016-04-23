//
//  splitter.cpp
//  P2PSP
//
//  This code is distributed under the GNU General Public License (see
//  THE_GENERAL_GNU_PUBLIC_LICENSE.txt for extending this information).
//  Copyright (C) 2016, the P2PSP team.
//  http://www.p2psp.org
//

#include <iostream>
#include <memory>
#include "core/common.h"
#include "core/splitter_ims.h"
#include "core/splitter_dbs.h"
#include "core/splitter_acs.h"
#include "core/splitter_lrs.h"
#include "core/splitter_strpe.h"
#include "core/splitter_nts.h"
#include <boost/program_options/parsers.hpp>
#include <boost/program_options/variables_map.hpp>
#include <signal.h>
#include "util/trace.h"

// TODO: LOG fails if splitter is defined outside the main
// p2psp::SplitterSTRPE splitter;
std::shared_ptr<p2psp::SplitterIMS> splitter_ptr;
// True if splitter_ptr is SplitterIMS and no subclass
bool is_IMS_only;

void HandlerCtrlC(int s) {
  LOG("Keyboard interrupt detected ... Exiting!");

  // Say to daemon threads that the work has been finished,
  splitter_ptr->SetAlive(false);
}

void HandlerEndOfExecution() {
  // Wake up the "moderate_the_team" daemon, which is waiting in a recvfrom().
  splitter_ptr->SayGoodbye();

  // Wake up the "handle_arrivals" daemon, which is waiting in an accept().
  boost::asio::io_service io_service_;
  boost::system::error_code ec;
  boost::asio::ip::tcp::socket socket(io_service_);
  boost::asio::ip::tcp::endpoint endpoint(
      boost::asio::ip::address::from_string("127.0.0.1"),
      splitter_ptr->GetPort());

  socket.connect(endpoint, ec);

  // TODO: If "broken pipe" errors have to be avoided, replace the close method
  // with multiple receive calls in order to read the configuration sent by the
  // splitter
  socket.close();
}

bool HasParameter(const boost::program_options::variables_map& vm,
    const std::string& param_name, char min_magic_flags) {
  if (!vm.count(param_name)) {
    return false;
  }
  if (is_IMS_only || std::static_pointer_cast<p2psp::SplitterDBS>(
      splitter_ptr)->GetMagicFlags() < min_magic_flags) {
    ERROR("The parameter --" << param_name
        << " is not available for this splitter mode.");
    return false;
  }
  return true;
}

int main(int argc, const char *argv[]) {
  // Argument Parser
  boost::program_options::options_description desc(
      "This is the splitter node of a P2PSP team.  The splitter is in charge "
      "of defining the Set or Rules (SoR) that will control the team. By "
      "default, DBS (unicast transmissions) will be used");

  // TODO: strpe option should expect a list of arguments, not bool
  desc.add_options()("help,h", "Produce help message")("splitter_addr",
                     boost::program_options::value<std::string>(),
                     "IP address to serve (TCP) the peers. (Default = '{}')")(
      "buffer_size", boost::program_options::value<int>(),
      "size of the video buffer in blocks. Default = {}.")(
      "channel", boost::program_options::value<std::string>(),
      "Name of the channel served by the streaming source. Default = '{}'.")(
      "chunk_size", boost::program_options::value<int>(),
      "Chunk size in bytes. Default = '{}'.")(
      "header_size", boost::program_options::value<int>(),
      "Size of the header of the stream in chunks. Default = '{}'.")(
      "max_chunk_loss", boost::program_options::value<int>(),
      "Maximum number of lost chunks for an unsupportive peer. Makes sense "
      "only in unicast mode. Default = '{}'.")(
      "max_number_of_monitor_peers", boost::program_options::value<int>(),
      "Maximum number of monitors in the team. The first connecting peers will "
      "automatically become monitors. Default = '{}'.")(
      "mcast_addr", boost::program_options::value<std::string>(),
      "IP multicast address used to serve the chunks. Makes sense only in "
      "multicast mode. Default = '{}'.")(
      "port", boost::program_options::value<int>(),
      "Port to serve the peers. Default = '{}'.")(
      "source_addr", boost::program_options::value<std::string>(),
      "IP address or hostname of the streaming server. Default = '{}'.")(
      "source_port", boost::program_options::value<int>(),
      "Port where the streaming server is listening. Default = '{}'.")(
      "IMS", "Uses the IP multicast infrastructure, if available. IMS mode is "
      "incompatible with ACS, LRS, DIS and NTS modes.")(
      "NTS", "Enables NAT traversal.")(
      "ACS", "Enables Adaptative Chunk-rate.")(
      "LRS", "Enables Lost chunk Recovery")(
      "DIS", "Enables Data Integrity check.")(
      "strpe", "Selects STrPe model for DIS.")("strpeds", "Selects STrPe-DS model for DIS.")(
      "strpeds_majority_decision",
      "Sets majority decision ratio for STrPe-DS model.")(
      "strpe_log", boost::program_options::value<std::string>(),
      "Loggin STrPe & STrPe-DS specific data to file.")(
      "TTL", boost::program_options::value<int>(),
      "Time To Live of the multicast messages. Default = '{}'.");

  boost::program_options::variables_map vm;
  try {
    boost::program_options::store(boost::program_options::parse_command_line(argc, argv, desc), vm);
  } catch (std::exception &e) {

    // If the argument passed is unknown, print the list of available arguments
    std::cout << desc << "\n";
    return 1;
  }

  boost::program_options::notify(vm);

  if (vm.count("help")) {
    std::cout << desc << "\n";
    return 1;
  }

  is_IMS_only = false;
  if (vm.count("strpe")) {
    splitter_ptr.reset(new p2psp::SplitterSTRPE());
  } else if (vm.count("LRS")) {
    splitter_ptr.reset(new p2psp::SplitterLRS());
  } else if (vm.count("ACS")) {
    splitter_ptr.reset(new p2psp::SplitterACS());
  } else if (vm.count("NTS")) {
    splitter_ptr.reset(new p2psp::SplitterNTS());
  } else if (vm.count("IMS")) {
    is_IMS_only = true;
    splitter_ptr.reset(new p2psp::SplitterIMS());
  } else {
    splitter_ptr.reset(new p2psp::SplitterDBS());
  }

  if (vm.count("buffer_size")) {
    splitter_ptr->SetBufferSize(vm["buffer_size"].as<int>());
  }

  if (vm.count("channel")) {
    splitter_ptr->SetChannel(vm["channel"].as<std::string>());
  }

  if (vm.count("chunk_size")) {
    splitter_ptr->SetBufferSize(vm["chunk_size"].as<int>());
  }

  if (vm.count("header_size")) {
    splitter_ptr->SetHeaderSize(vm["header_size"].as<int>());
  }

  if (vm.count("port")) {
    splitter_ptr->SetPort(vm["port"].as<int>());
  }

  if (vm.count("source_addr")) {
    splitter_ptr->SetSourceAddr(vm["source_addr"].as<std::string>());
  }

  if (vm.count("source_port")) {
    splitter_ptr->SetSourcePort(vm["source_port"].as<int>());
  }

  // Parameters if splitter is not IMS
  if (HasParameter(vm, "max_chunk_loss", p2psp::Common::kDBS)) {
    std::shared_ptr<p2psp::SplitterDBS> splitter_dbs =
        std::static_pointer_cast<p2psp::SplitterDBS>(splitter_ptr);
    splitter_dbs->SetMaxChunkLoss(vm["max_chunk_loss"].as<int>());
  }

  if (HasParameter(vm, "max_number_of_monitor_peers", p2psp::Common::kDBS)) {
    std::shared_ptr<p2psp::SplitterDBS> splitter_dbs =
        std::static_pointer_cast<p2psp::SplitterDBS>(splitter_ptr);
    splitter_dbs->SetMonitorNumber(vm["max_number_of_monitor_peers"].as<int>());
  }

  // Parameters if STRPE
  if (HasParameter(vm, "strpe_log", p2psp::Common::kSTRPE)) {
    std::shared_ptr<p2psp::SplitterSTRPE> splitter_strpe =
        std::static_pointer_cast<p2psp::SplitterSTRPE>(splitter_ptr);
    splitter_strpe->SetLogging(true);
    splitter_strpe->SetLogFile(vm["strpe_log"].as<std::string>());
  }

  splitter_ptr->Start();

  LOG("         | Received  | Sent      | Number       losses/ losses");
  LOG("    Time | (kbps)    | (kbps)    | peers (peer) sents   threshold "
      "period kbps");
  LOG("---------+-----------+-----------+-----------------------------------.."
      ".");

  int last_sendto_counter = splitter_ptr->GetSendToCounter();
  int last_recvfrom_counter = splitter_ptr->GetRecvFromCounter();

  int chunks_sendto = 0;
  int kbps_sendto = 0;
  int kbps_recvfrom = 0;
  int chunks_recvfrom = 0;
  std::vector<boost::asio::ip::udp::endpoint> peer_list;

  // Listen to Ctrl-C interruption
  struct sigaction sigIntHandler;
  sigIntHandler.sa_handler = HandlerCtrlC;
  sigemptyset(&sigIntHandler.sa_mask);
  sigIntHandler.sa_flags = 0;
  sigaction(SIGINT, &sigIntHandler, NULL);

  std::shared_ptr<p2psp::SplitterDBS> splitter_dbs;
  if (!is_IMS_only) { // GetPeerList is only in DBS and derivated classes
    splitter_dbs = std::static_pointer_cast<p2psp::SplitterDBS>(splitter_ptr);
  }
  std::shared_ptr<p2psp::SplitterACS> splitter_acs;
  if (!is_IMS_only && splitter_dbs->GetMagicFlags() >= p2psp::Common::kACS) {
    splitter_acs = std::static_pointer_cast<p2psp::SplitterACS>(splitter_ptr);
  }
  while (splitter_ptr->isAlive()) {
    boost::this_thread::sleep(boost::posix_time::milliseconds(1000));
    chunks_sendto = splitter_ptr->GetSendToCounter() - last_sendto_counter;
    kbps_sendto = (chunks_sendto * splitter_ptr->GetChunkSize() * 8) / 1000;
    chunks_recvfrom =
        splitter_ptr->GetRecvFromCounter() - last_recvfrom_counter;
    kbps_recvfrom = (chunks_recvfrom * splitter_ptr->GetChunkSize() * 8) / 1000;
    last_sendto_counter = splitter_ptr->GetSendToCounter();
    last_recvfrom_counter = splitter_ptr->GetRecvFromCounter();

    LOG("|" << kbps_recvfrom << "|" << kbps_sendto << "|");
    // LOG(_SET_COLOR(_CYAN));

    if (!is_IMS_only) { // GetPeerList is only in DBS and derivated classes
      peer_list = splitter_dbs->GetPeerList();
      LOG("Size peer list: " << peer_list.size());

      std::vector<boost::asio::ip::udp::endpoint>::iterator it;
      for (it = peer_list.begin(); it != peer_list.end(); ++it) {
        // _SET_COLOR(_BLUE);
        LOG("Peer: " << *it);
        // _SET_COLOR(_RED);

        LOG(splitter_dbs->GetLoss(*it) << "/" << chunks_sendto << " "
                                       << splitter_dbs->GetMaxChunkLoss());

        if (splitter_dbs->GetMagicFlags() >= p2psp::Common::kACS) { // If is ACS
          // _SET_COLOR(_YELLOW);
          LOG(splitter_acs->GetPeriod(*it));
          // _SET_COLOR(_PURPLE)
          LOG((splitter_acs->GetNumberOfSentChunksPerPeer(*it) *
               splitter_acs->GetChunkSize() * 8) /
              1000);
          splitter_acs->SetNumberOfSentChunksPerPeer(*it, 0);
        }
      }
    }
  }

  LOG("Ending");
  HandlerEndOfExecution();

  return 0;
}

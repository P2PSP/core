//
//  splitter.cpp
//  P2PSP
//
//  This code is distributed under the GNU General Public License (see
//  THE_GENERAL_GNU_PUBLIC_LICENSE.txt for extending this information).
//  Copyright (C) 2014, the P2PSP team.
//  http://www.p2psp.org
//

#include <iostream>
#include "core/splitter_ims.h"
#include "core/splitter_dbs.h"
#include "core/splitter_acs.h"
#include "core/splitter_lrs.h"
#include "core/splitter_strpe.h"
#include <boost/program_options/parsers.hpp>
#include <boost/program_options/variables_map.hpp>

int main(int argc, const char *argv[]) {
  // TODO: Configure splitter

  // TODO: Start the splitter's main thread

  // TODO: Print information about the status of the splitter

  // Argument Parser
  boost::program_options::options_description desc(
      "This is the splitter node of a P2PSP team.  The splitter is in charge "
      "of defining the Set or Rules (SoR) that will control the team. By "
      "default, DBS (unicast transmissions) will be used.");

  desc.add_options()("splitter_addr",
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
      "IMS", boost::program_options::value<bool>()->implicit_value(true),
      "Uses the IP multicast infrastructure, if available. IMS mode is "
      "incompatible with ACS, LRS, DIS and NTS modes.")(
      "NTS", boost::program_options::value<bool>()->implicit_value(true),
      "Enables NAT traversal.")(
      "ACS", boost::program_options::value<bool>()->implicit_value(true),
      "Enables Adaptative Chunk-rate.")(
      "LRS", boost::program_options::value<bool>()->implicit_value(true),
      "Enables Lost chunk Recovery")(
      "DIS", boost::program_options::value<bool>()->implicit_value(true),
      "Enables Data Integrity check.")(
      "strpe", boost::program_options::value<bool>()->implicit_value(true),
      "Selects STrPe model for DIS.")("strpeds",
                                      boost::program_options::value<bool>(),
                                      "Selects STrPe-DS model for DIS.")(
      "strpeds_majority_decision",
      boost::program_options::value<bool>()->implicit_value(true),
      "Sets majority decision ratio for STrPe-DS model.")(
      "strpe_log", boost::program_options::value<bool>()->implicit_value(true),
      "Loggin STrPe & STrPe-DS specific data to file.")(
      "TTL", boost::program_options::value<int>(),
      "Time To Live of the multicast messages. Default = '{}'.");

  boost::program_options::variables_map vm;
  boost::program_options::store(
      boost::program_options::parse_command_line(argc, argv, desc), vm);
  boost::program_options::notify(vm);

  p2psp::SplitterACS splitter;

  if (vm.count("buffer_size")) {
    splitter.SetBufferSize(vm["buffer_size"].as<int>());
  }

  if (vm.count("channel")) {
    splitter.SetChannel(vm["channel"].as<std::string>());
  }

  if (vm.count("chunk_size")) {
    splitter.SetBufferSize(vm["chunk_size"].as<int>());
  }

  if (vm.count("header_size")) {
    splitter.SetHeaderSize(vm["header_size"].as<int>());
  }

  if (vm.count("port")) {
    splitter.SetPort(vm["port"].as<int>());
  }

  if (vm.count("source_addr")) {
    splitter.SetSourceAddr(vm["source_addr"].as<std::string>());
  }

  if (vm.count("source_port")) {
    splitter.SetSourcePort(vm["source_port"].as<int>());
  }

  splitter.Start();

  LOG("         | Received  | Sent      | Number       losses/ losses");
  LOG("    Time | (kbps)    | (kbps)    | peers (peer) sents   threshold "
      "period kbps");
  LOG("---------+-----------+-----------+-----------------------------------.."
      ".");

  int last_sendto_counter = splitter.GetSendToCounter();
  int last_recvfrom_counter = splitter.GetRecvFromCounter();
  int chunks_sendto = 0;
  int kbps_sendto = 0;
  int kbps_recvfrom = 0;
  int chunks_recvfrom = 0;
  std::vector<boost::asio::ip::udp::endpoint> peer_list;

  int get_loss = 0;

  while (splitter.isAlive()) {
    boost::this_thread::sleep(boost::posix_time::milliseconds(1000));
    chunks_sendto = splitter.GetSendToCounter() - last_sendto_counter;
    kbps_sendto = (chunks_sendto * splitter.GetChunkSize() * 8) / 1000;
    chunks_recvfrom = splitter.GetRecvFromCounter() - last_recvfrom_counter;
    kbps_recvfrom = (chunks_recvfrom * splitter.GetChunkSize() * 8) / 1000;
    last_sendto_counter = splitter.GetSendToCounter();
    last_recvfrom_counter = splitter.GetRecvFromCounter();
    LOG("|" << kbps_recvfrom << "|" << kbps_sendto << "|");
    // LOG(_SET_COLOR(_CYAN));

    // TODO: GetPeerList is only in DBS and derivated classes
    peer_list = splitter.GetPeerList();
    LOG("Size peer list: " << peer_list.size());

    std::vector<boost::asio::ip::udp::endpoint>::iterator it;
    for (it = peer_list.begin(); it != peer_list.end(); ++it) {
      _SET_COLOR(_BLUE);
      LOG("Peer: " << *it);
      _SET_COLOR(_RED);

      // TODO: GetLoss and GetMaxChunkLoss are only in DBS and derivated classes
      LOG(splitter.GetLoss(*it) << "/" << chunks_sendto << " "
                                << splitter.GetMaxChunkLoss());

      // TODO: If is ACS
      _SET_COLOR(_YELLOW);
      LOG(splitter.GetPeriod(*it));
      LOG((splitter.GetNumberOfSentChunksPerPeer(*it) *
           splitter.GetChunkSize() * 8) /
          1000);
      splitter.SetNumberOfSentChunksPerPeer(*it, 0);
    }
  }

  return 0;
}
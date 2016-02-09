//
//  peer_core.cc
//  P2PSP
//
//  This code is distributed under the GNU General Public License (see
//  THE_GENERAL_GNU_PUBLIC_LICENSE.txt for extending this information).
//  Copyright (C) 2016, the P2PSP team.
//  http://www.p2psp.org
//

#include "peer_core.h"

namespace p2psp {

int run(int argc, const char* argv[]) throw(boost::system::system_error) {
  // TODO: Format default options
  boost::format format("Defaut = %5i");

  // Argument Parser
  boost::program_options::options_description desc(
      "This is the peer node of a P2PSP team.");

  // TODO: strpe option should expect a list of arguments, not bool
  desc.add_options()("help,h", "Produce help message")(
      "enable_chunk_loss", boost::program_options::value<std::string>(),
      "Forces a lost of chunks")(
      "max_chunk_debt", boost::program_options::value<int>(),
      "The maximun number of times that other peer "
      "can not send a chunk to "
      "this peer.")(  // TODO: (format % 10).str()).data())
                      // --
                      // format(Peer_DBS.MAX_CHUNK_DEBT)
      "player_port", boost::program_options::value<uint16_t>(),
      "Port to communicate with the player. "
      "Default = {}")(  //.format(Peer_IMS.PLAYER_PORT)"
      "port_step", boost::program_options::value<int>(),
      "Source port step forced when behind a sequentially port "
      "allocating NAT (conflicts with --chunk_loss_period). Default = "
      "{}")(  //.format(Symsp_Peer.PORT_STEP)

      "splitter_addr", boost::program_options::value<std::string>(),
      "IP address or hostname of the splitter. Default = {}.")(  //.format(Peer_IMS.SPLITTER_ADDR)

      "splitter_port", boost::program_options::value<uint16_t>(),
      "Listening port of the splitter. Default = {}.")(  //.format(Peer_IMS.SPLITTER_PORT)
      "port", boost::program_options::value<uint16_t>(),
      "Port to communicate with the peers. Default {} (the OS will chose "
      "it).")(  //.format(Peer_IMS.PORT)
      "use_localhost",
      "Forces the peer to use localhost instead of the IP of the adapter "
      "to connect to the splitter. Notice that in this case, peers that "
      "run outside of the host will not be able to communicate with this "
      "peer.")(
      //"malicious",
      // boost::program_options::value<bool>()->implicit_value(true),
      //"Enables the malicious activity for peer.")(
      "persistent", boost::program_options::value<std::string>(),
      "Forces the peer to send poisoned chunks to other peers.")(
      "on_off_ratio", boost::program_options::value<int>(),
      "Enables on-off attack and sets ratio for on off (from 1 to 100)")(
      "selective", boost::program_options::value<std::string>(),
      "Enables selective attack for given set of peers.")(
      "bad_mouth", boost::program_options::value<std::string>(),
      "Enables Bad Mouth attack for given set of peers.")(
      // "trusted", boost::program_options::value<bool>()->implicit_value(true),
      // "Forces the peer to send hashes of chunks to splitter")(
      "checkall",
      "Forces the peer to send hashes of every chunks to splitter (works only "
      "with trusted option)")(
      // "strpeds", boost::program_options::value<bool>()->implicit_value(true),
      // "Enables STrPe-DS")(
      "strpe_log", "Logging STrPe & STrPe-DS specific data to file.")(
      "monitor", "The peer is a monitor")(
      "show_buffer", "Shows the status of the buffer of chunks.");

  boost::program_options::variables_map vm;
  try {
    boost::program_options::store(
        boost::program_options::parse_command_line(argc, argv, desc), vm);
  } catch (std::exception& e) {
    // If the argument passed is unknown, print the list of available arguments
    std::cout << desc << "\n";
    return 1;
  }
  boost::program_options::notify(vm);

  if (vm.count("help")) {
    std::cout << desc << "\n";
    return 1;
  }

  std::unique_ptr<p2psp::PeerDBS> peer;

  if (vm.count("monitor")) {
    // Monitor enabled
    LOG("Monitor enabled.");
    peer.reset(new p2psp::MonitorLRS());
  } else {
    peer.reset(new p2psp::PeerDBS());
  }

  peer->Init();

  if (vm.count("show_buffer")) {
    peer->SetShowBuffer(true);
  }

  if (vm.count("max_chunk_debt")) {
    peer->SetMaxChunkDebt(vm["max_chunk_debt"].as<int>());
  }

  if (vm.count("player_port")) {
    peer->SetPlayerPort(vm["player_port"].as<uint16_t>());
  }

  if (vm.count("port_step")) {
    // Symsp_Peer peer->SetPortStep(vm["port_step"].as<int>());
  }

  if (vm.count("splitter_addr")) {
    peer->SetSplitterAddr(vm["splitter_addr"].as<std::string>());
  }

  if (vm.count("splitter_port")) {
    peer->SetSplitterPort(vm["splitter_port"].as<uint16_t>());
  }

  if (vm.count("port")) {
    peer->SetPort(vm["port"].as<uint16_t>());
  }

  if (vm.count("use_localhost")) {
    peer->SetUseLocalhost(true);
  }

  // TODO: To the future
  /*
  if (vm.count("persistent")) {
    peer->SetPersistentAttack(true);
  }

  if (vm.count("on_off_ratio")) {
    peer->SetOnOffAttack(true, vm["on_off_ratio"].as<int>());
  }

  if (vm.count("selective")) {
    peer->SetSelectiveAttack(true, vm["selective"].as<std::string>());
  }

  if (vm.count("bad_mouth")) {
    peer->SetBadMouthAttack(true, vm["bad_mouth"].as<std::string>());
  }

  if (vm.count("checkall")) {
    peer->SetCheckAll(true);
  }

  if (vm.count("strpe_log")) {
    // TODO: Handle logging
  }*/

  peer->WaitForThePlayer();
  peer->ConnectToTheSplitter();
  peer->ReceiveTheMcasteEndpoint();
  peer->ReceiveTheHeaderSize();
  peer->ReceiveTheChunkSize();
  peer->ReceiveTheHeader();
  peer->ReceiveTheBufferSize();
  LOG("Using IP Multicast address = " << peer->GetMcastAddr());

  // A multicast address is always received, even for DBS peers.
  if (peer->GetMcastAddr() == "0.0.0.0") {
    peer->ReceiveMyEndpoint();
    peer->ReceiveMagicFlags();
    // LOG("Magic flags =" << std::bitset<8>(peer->magic_flags));
    peer->ReceiveTheNumberOfPeers();
    LOG("Number of peers in the team (excluding me) ="
        << std::to_string(peer->GetNumberOfPeers()));
    LOG("Am I a monitor peer? =" << (peer->AmIAMonitor() ? "True" : "False"));
    peer->ListenToTheTeam();
    peer->ReceiveTheListOfPeers();
    LOG("List of peers received");

    // After receiving the list of peers, the peer can check whether is a
    // monitor peer or not (only the first arriving peers are monitors)

    if (peer->AmIAMonitor()) {
      LOG("Monitor DBS enabled");

      // The peer is a monitor. Now it's time to know the sets of rules that
      // control this team.
    } else {
      LOG("Peer DBS enabled");

      // The peer is a normal peer-> Let's know the sets of rules that control
      // this team.
    }

  } else {
    // IP multicast mode
    peer->ListenToTheTeam();
  }

  peer->DisconnectFromTheSplitter();
  peer->BufferData();
  peer->Start();

  LOG("+-----------------------------------------------------+");
  LOG("| Received = Received kbps, including retransmissions |");
  LOG("|     Sent = Sent kbps                                |");
  LOG("|       (Expected values are between parenthesis)     |");
  LOG("------------------------------------------------------+");
  LOG("");
  LOG("         |     Received (kbps) |          Sent (kbps) |");
  LOG(
      "    Time |      Real  Expected |       Real  Expected | Team "
      "description");
  LOG(
      "---------+---------------------+----------------------+-----------------"
      "------------------...");

  int last_chunk_number = peer->GetPlayedChunk();
  int last_sendto_counter = -1;
  if (peer->GetSendtoCounter() < 0) {
    last_sendto_counter = 0;
  } else {
    peer->SetSendtoCounter(0);
    last_sendto_counter = 0;
  }

  int last_recvfrom_counter = peer->GetRecvfromCounter();
  float kbps_expected_recv = 0.0f;
  float kbps_recvfrom = 0.0f;
  float team_ratio = 0.0f;
  float kbps_sendto = 0.0f;
  float kbps_expected_sent = 0.0f;
  // float nice = 0.0f;
  int counter = 0;

  while (peer->IsPlayerAlive()) {
    boost::this_thread::sleep(boost::posix_time::seconds(1));
    kbps_expected_recv = ((peer->GetPlayedChunk() - last_chunk_number) *
                          peer->GetChunkSize() * 8) /
                         1000.0f;
    last_chunk_number = peer->GetPlayedChunk();
    kbps_recvfrom = ((peer->GetRecvfromCounter() - last_recvfrom_counter) *
                     peer->GetChunkSize() * 8) /
                    1000.0f;
    last_recvfrom_counter = peer->GetRecvfromCounter();
    team_ratio =
        peer->GetPeerList()->size() / (peer->GetPeerList()->size() + 1.0f);
    kbps_expected_sent = (int)(kbps_expected_recv * team_ratio);
    kbps_sendto = ((peer->GetSendtoCounter() - last_sendto_counter) *
                   peer->GetChunkSize() * 8) /
                  1000.0f;
    last_sendto_counter = peer->GetSendtoCounter();

    // try:
    if (p2psp::Common::kConsoleMode == false) {
      /*from gi.repository import GObject
      try:
      from adapter import speed_adapter
      except ImportError as msg:
      pass
      GObject.idle_add(speed_adapter.update_widget,str(kbps_recvfrom) << ' kbps'
                       ,str(kbps_sendto) << ' kbps'
                       ,str(len(peer->peer_list)+1))
      except Exception as msg:
      pass*/
    }

    if (kbps_recvfrom > 0 and kbps_expected_recv > 0) {
      // nice = 100.0 / (kbps_expected_recv / kbps_recvfrom) *
      // (peer->GetPeerList()->size() + 1.0f);
    } else {
      // nice = 0.0f;
    }

    LOG("|");

    if (kbps_expected_recv < kbps_recvfrom) {
      LOG(_SET_COLOR(_RED));
    } else if (kbps_expected_recv > kbps_recvfrom) {
      LOG(_SET_COLOR(_GREEN));
    }

    // TODO: format
    LOG(kbps_expected_recv);
    LOG(kbps_recvfrom);
    //#print(("{:.1f}".format(nice)).rjust(6), end=' | ')
    //#sys.stdout.write(Color.none)

    if (kbps_expected_sent > kbps_sendto) {
      LOG(_SET_COLOR(_RED));
    } else if (kbps_expected_sent < kbps_sendto) {
      LOG(_SET_COLOR(_GREEN));
    }
    // TODO: format
    LOG(kbps_sendto);
    LOG(kbps_expected_sent);
    // sys.stdout.write(Color.none)
    // print(repr(nice).ljust(1)[:6], end=' ')
    LOG(peer->GetPeerList()->size());
    counter = 0;
    for (std::vector<boost::asio::ip::udp::endpoint>::iterator p =
             peer->GetPeerList()->begin();
         p != peer->GetPeerList()->end(); ++p) {
      if (counter < 5) {
        LOG("(" << p->address().to_string() << "," << std::to_string(p->port())
                << ")");
        counter++;
      } else {
        break;
        LOG("");
      }
    }

    // try:
    if (p2psp::Common::kConsoleMode == false) {
      /*GObject.idle_add(speed_adapter.update_widget,str(0)+'
       kbps',str(0)+' kbps',str(0))
       except  Exception as msg:
       pass
       }
       */
    }
  }

  return 0;
}
}
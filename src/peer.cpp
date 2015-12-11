
// TODO: include all needed libraries
#include "core/peer_ims.h"
#include "core/peer_dbs.h"
#include "core/monitor_dbs.h"
#include "core/malicious_peer.h"
#include "core/trusted_peer.h"
#include "core/peer_strpeds.h"
#include "core/common.h"
#include "util/trace.h"

int main(int argc, const char* argv[]) {
  // TODO: Argument parser. Decide how to implement it

  p2psp::PeerStrpeDs peer;
  peer.Init();

  peer.WaitForThePlayer();
  peer.ConnectToTheSplitter();
  peer.ReceiveTheMcasteEndpoint();
  peer.ReceiveTheHeaderSize();
  peer.ReceiveTheChunkSize();
  peer.ReceiveTheHeader();
  peer.ReceiveTheBufferSize();
  LOG("Using IP Multicast address = " << peer.GetMcastAddr());

  // TODO: if(args.show_buffer){
  // peer.SetShowBuffer(true);
  //}

  // A multicast address is always received, even for DBS peers.
  if (peer.GetMcastAddr() == "0.0.0.0") {
    // TODO: IP multicast mode
    // TODO: DBS

    peer.ReceiveMyEndpoint();
    peer.ReceiveMagicFlags();
    // LOG("Magic flags =" << std::bitset<8>(peer.magic_flags));
    peer.ReceiveTheNumberOfPeers();
    LOG("Number of peers in the team (excluding me) ="
        << std::to_string(peer.GetNumberOfPeers()));
    LOG("Am I a monitor peer? =" << (peer.AmIAMonitor() ? "True" : "False"));
    peer.ListenToTheTeam();
    peer.ReceiveTheListOfPeers();
    LOG("List of peers received");

    // After receiving the list of peers, the peer can check whether is a
    // monitor peer or not (only the first arriving peers are monitors)

    if (peer.AmIAMonitor()) {
      // TODO: peer = Monitor_DBS(peer)
      LOG("Monitor DBS enabled");

      // The peer is a monitor. Now it's time to know the sets of rules that
      // control this team.

      // TODO: Delete this
      // if (peer.magic_flags & Common.LRS):
      // peer = Monitor_LRS(peer)
      // _print_("Monitor LRS enabled")
      // if (peer.magic_flags & Common.NTS):
      //  peer = Monitor_NTS(peer)
      //  _print_("Monitor NTS enabled")
    } else {
      // peer = Peer_DBS(peer)
      LOG("Peer DBS enabled");

      // The peer is a normal peer. Let's know the sets of rules that control
      // this team.
    }

    // TODO: Decide type of peer to work with
  } else {
    // IP multicast mode
    peer.ListenToTheTeam();
  }

  peer.DisconnectFromTheSplitter();
  peer.BufferData();
  peer.Start();

  LOG("+-----------------------------------------------------+");
  LOG("| Received = Received kbps, including retransmissions |");
  LOG("|     Sent = Sent kbps                                |");
  LOG("|       (Expected values are between parenthesis)     |");
  LOG("------------------------------------------------------+");
  LOG("");
  LOG("         |     Received (kbps) |          Sent (kbps) |");
  LOG("    Time |      Real  Expected |       Real  Expected | Team "
      "description");
  LOG("---------+---------------------+----------------------+-----------------"
      "------------------...");

  int last_chunk_number = peer.GetPlayedChunk();
  int last_sendto_counter = -1;
  if (peer.GetSendtoCounter() < 0) {
    last_sendto_counter = 0;
  } else {
    peer.SetSendtoCounter(0);
    last_sendto_counter = 0;
  }

  int last_recvfrom_counter = peer.GetRecvfromCounter();
  float kbps_expected_recv = 0.0f;
  float kbps_recvfrom = 0.0f;
  float team_ratio = 0.0f;
  float kbps_sendto = 0.0f;
  float kbps_expected_sent = 0.0f;
  float nice = 0.0f;
  int counter = 0;

  while (peer.IsPlayerAlive()) {
    boost::this_thread::sleep(boost::posix_time::seconds(1));
    kbps_expected_recv = ((peer.GetPlayedChunk() - last_chunk_number) *
                          peer.GetChunkSize() * 8) /
                         1000.0f;
    last_chunk_number = peer.GetPlayedChunk();
    kbps_recvfrom = ((peer.GetRecvfromCounter() - last_recvfrom_counter) *
                     peer.GetChunkSize() * 8) /
                    1000.0f;
    last_recvfrom_counter = peer.GetRecvfromCounter();
    team_ratio =
        peer.GetPeerList()->size() / (peer.GetPeerList()->size() + 1.0f);
    kbps_expected_sent = (int)(kbps_expected_recv * team_ratio);
    kbps_sendto = ((peer.GetSendtoCounter() - last_sendto_counter) *
                   peer.GetChunkSize() * 8) /
                  1000.0f;
    last_sendto_counter = peer.GetSendtoCounter();

    // try:
    if (p2psp::Common::kConsoleMode == false) {
      /*from gi.repository import GObject
      try:
      from adapter import speed_adapter
      except ImportError as msg:
      pass
      GObject.idle_add(speed_adapter.update_widget,str(kbps_recvfrom) << ' kbps'
                       ,str(kbps_sendto) << ' kbps'
                       ,str(len(peer.peer_list)+1))
      except Exception as msg:
      pass*/
    }

    if (kbps_recvfrom > 0 and kbps_expected_recv > 0) {
      nice = 100.0 / (kbps_expected_recv / kbps_recvfrom) *
             (peer.GetPeerList()->size() + 1.0f);
    } else {
      nice = 0.0f;
      LOG("|");
      if (kbps_expected_recv < kbps_recvfrom) {
        LOG(_SET_COLOR(_RED));
      } else if (kbps_expected_recv > kbps_recvfrom) {
        LOG(_SET_COLOR(_GREEN));
        // TODO: format
        // print(repr(int(kbps_expected_recv)).rjust(10), end=Color.none)
        // print(repr(int(kbps_recvfrom)).rjust(10), end=' | ')
      }
    }

    if (kbps_expected_sent > kbps_sendto) {
      LOG(_SET_COLOR(_RED));
    } else if (kbps_expected_sent < kbps_sendto) {
      LOG(_SET_COLOR(_GREEN));
      // TODO: format
      // print(repr(int(kbps_sendto)).rjust(10), end=Color.none)
      // print(repr(int(kbps_expected_sent)).rjust(10), end=' | ')
      // sys.stdout.write(Color.none)
      // print(repr(nice).ljust(1)[:6], end=' ')
      LOG(peer.GetPeerList()->size());
      counter = 0;
      for (std::vector<boost::asio::ip::udp::endpoint>::iterator p =
               peer.GetPeerList()->begin();
           p != peer.GetPeerList()->end(); ++p) {
        if (counter < 5) {
          LOG("(" << p->address().to_string() << ","
                  << std::to_string(p->port()) << ")");
          counter++;
        } else {
          break;
          LOG("");

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
      }
    }
  }

  return 0;
}

//
//  This code is distributed under the GNU General Public License (see
//  THE_GENERAL_GNU_PUBLIC_LICENSE.txt for extending this information).
//  Copyright (C) 2016, the P2PSP team.
//  http://www.p2psp.org
//

#ifndef P2PSP_CORE_COMMON_NTS_H
#define P2PSP_CORE_COMMON_NTS_H

#include <string>
#include <sstream>
#include <boost/asio.hpp>
#include <chrono>

namespace std {
template <class Key, class Value>
bool operator==(const std::pair<const Key, Value> iter_pair,
    const Key key) {
  return iter_pair.first == key;
}
}

namespace p2psp {

typedef std::pair<std::string, boost::asio::ip::udp::endpoint> message_t;
typedef std::chrono::steady_clock::time_point timepoint_t;

class CommonNTS {
 public:
  // Size of the IDs used in NTS for incorporating peers
  static const int kPeerIdLength = 7;

  // Time between continuously sent packets
  static const std::chrono::seconds kHelloPacketTiming;

  // Maximum time after peer retries incorporation
  static const std::chrono::seconds kMaxPeerArrivingTime;

  // Peers needing longer to incorporate are removed from team
  static const std::chrono::seconds kMaxTotalIncorporationTime;

  // Number of probable source ports that will be tried
  static const int kMaxPredictedPorts = 20;

  // TODO: Provide a similar method with maximal search length
  template <class Container, typename Item>
  static bool Contains(const Container& container, const Item& item) {
    return std::find(container.begin(), container.end(), item)
        != container.end();
  }

  template <class Container, typename Item>
  static unsigned int Index(const Container& container, const Item& item) {
    return std::find(container.begin(), container.end(), item)
        - container.begin();
  }

  template <class Container>
  static std::string Join(const Container& container, std::string delimiter) {
    if (container.size() == 0) {
      return std::string();
    }
    std::ostringstream str;
    auto iter = container.begin();
    str << *iter;
    while (++iter != container.end()) {
      str << delimiter;
      str << *iter;
    }
    return str.str();
  }

  template <class Socket>
  static std::string ReceiveString(Socket& socket, size_t length) {
    std::vector<char> message(length);
    read(socket, boost::asio::buffer(message));
    return std::string(message.data(), length);
  }

  static std::string ReceiveString(std::istringstream& str, size_t length) {
    std::vector<char> message(length);
    str.read(message.data(), length);
    return std::string(message.data(), length);
  }

  static uint16_t NetworkToHost(uint16_t t) {
    return ntohs(t);
  }
  static uint32_t NetworkToHost(uint32_t t) {
    return ntohl(t);
  }
  static uint16_t HostToNetwork(uint16_t t) {
    return htons(t);
  }
  static uint32_t HostToNetwork(uint32_t t) {
    return htonl(t);
  }

  template <typename T, class Socket>
  static T Receive(Socket& socket) {
    T t[1];
    read(socket, boost::asio::buffer(t, sizeof(T)));
    return NetworkToHost(t[0]);
  }

  template <typename T>
  static T Receive(std::istringstream& str) {
    T t[1];
    str.read((char*)t, sizeof(T));
    return NetworkToHost(t[0]);
  }

  template <typename T>
  static void Write(std::ostringstream& str, const T& t) {
    T t2 = HostToNetwork(t);
    str << std::string((const char*) &t2, sizeof(T));
  }
};
}

#endif  // P2PSP_CORE_COMMON_NTS_H

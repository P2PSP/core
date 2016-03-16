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
  static std::string&& ReceiveString(Socket& socket, size_t length) {
    std::vector<char> message(length);
    read(socket, boost::asio::buffer(message));
    return std::move(std::string(message.data(), length));
  }

  static std::string&& ReceiveString(std::istringstream& str, size_t length) {
    std::vector<char> message(length);
    str.read(message.data(), length);
    return std::move(std::string(message.data(), length));
  }

  template <typename T, class Socket>
  static T Receive(Socket& socket) {
    std::array<char, sizeof(T)> message;
    read(socket, boost::asio::buffer(message));
    return *(T *)(message.data());
  }

  template <typename T>
  static T Receive(std::istringstream& str) {
    std::array<char, sizeof(T)> message;
    str.read(message.data(), sizeof(T));
    return *(T *)(message.data());
  }

  template <typename T>
  static void Write(std::ostringstream& str, const T& t) {
    str << std::string((const char*) &t, sizeof(T));
  }
};
}

#endif  // P2PSP_CORE_COMMON_NTS_H

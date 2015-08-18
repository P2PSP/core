NAT traversal testing
=====================

This document shows detailed information about the test network setup used to
test NAT traversal between two P2PSP peers, each behind a NAT. General
information about the test can be found [here](NAT_traversal_testing.md).

## Network setup
The setup with network interfaces and IP addresses as used in the tests is shown
in the following diagram:

![network setup details](images/network_setup_details.png)

## NAT types
To test the behaviour of peers behind different kinds of NAT devices (i.e.
routers), different NAT types are simulated. The characteristics of each type is
described in [this document](NAT_traversal.md).

The different NAT types are configured by the following iptables rules:

### NAT 1

#### Full Cone NAT

    ```
    *filter
    :INPUT ACCEPT [0:0]
    :FORWARD ACCEPT [0:0]
    :OUTPUT ACCEPT [0:0]
    COMMIT
    *nat
    :PREROUTING ACCEPT [0:0]
    :INPUT ACCEPT [0:0]
    :OUTPUT ACCEPT [0:0]
    :POSTROUTING ACCEPT [0:0]
    -A PREROUTING -i enp0s8 -j DNAT --to-destination 192.168.56.4
    -A POSTROUTING -o enp0s8 -j SNAT --to-source 192.168.57.4
    COMMIT
    ```

#### Restricted Cone NAT

    ```
    *filter
    :INPUT ACCEPT [0:0]
    :FORWARD ACCEPT [0:0]
    :OUTPUT ACCEPT [0:0]
    -A INPUT -i enp0s3 -j ACCEPT
    -A INPUT -i enp0s8 -p tcp -m state --state RELATED,ESTABLISHED -j ACCEPT
    -A INPUT -i enp0s8 -p udp -m state --state RELATED,ESTABLISHED -j ACCEPT
    -A INPUT -i enp0s8 -p tcp -m state --state NEW -j DROP
    -A INPUT -i enp0s8 -p udp -m state --state NEW -j DROP
    COMMIT
    *nat
    :PREROUTING ACCEPT [0:0]
    :INPUT ACCEPT [0:0]
    :OUTPUT ACCEPT [0:0]
    :POSTROUTING ACCEPT [0:0]
    -A PREROUTING -i enp0s8 -p tcp -j DNAT --to-destination 192.168.56.4
    -A PREROUTING -i enp0s8 -p udp -j DNAT --to-destination 192.168.56.4
    -A POSTROUTING -o enp0s8 -p tcp -j SNAT --to-source 192.168.57.4
    -A POSTROUTING -o enp0s8 -p udp -j SNAT --to-source 192.168.57.4
    COMMIT
    ```

#### Port-Restricted Cone NAT

    ```
    *filter
    :INPUT DROP [0:0]
    :FORWARD ACCEPT [0:0]
    :OUTPUT ACCEPT [0:0]
    -A INPUT -i enp0s8 -m state --state ESTABLISHED,RELATED -j ACCEPT
    -A INPUT -i enp0s3 -j ACCEPT
    COMMIT
    *nat
    :PREROUTING ACCEPT [0:0]
    :INPUT ACCEPT [0:0]
    :OUTPUT ACCEPT [0:0]
    :POSTROUTING ACCEPT [0:0]
    -A POSTROUTING -o enp0s8 -j SNAT --to-source 192.168.57.4
    COMMIT
    ```

#### Symmetric NAT: Port preservation

    ```
    *filter
    :INPUT ACCEPT [0:0]
    :FORWARD ACCEPT [0:0]
    :OUTPUT ACCEPT [0:0]
    -A FORWARD -i enp0s8 -o enp0s3 -m state --state RELATED,ESTABLISHED -j ACCEPT
    -A FORWARD -i enp0s8 -o enp0s3 -m state --state NEW -j DROP
    -A FORWARD -i enp0s3 -o enp0s8 -j ACCEPT
    COMMIT
    *nat
    :PREROUTING ACCEPT [0:0]
    :INPUT ACCEPT [0:0]
    :OUTPUT ACCEPT [0:0]
    :POSTROUTING ACCEPT [0:0]
    -A POSTROUTING -o enp0s8 -j MASQUERADE
    COMMIT
    ```

#### Symmetric NAT: Sequential port

    ```
    *filter
    :INPUT ACCEPT [0:0]
    :FORWARD ACCEPT [0:0]
    :OUTPUT ACCEPT [0:0]
    -A FORWARD -i enp0s8 -o enp0s3 -m state --state RELATED,ESTABLISHED -j ACCEPT
    -A FORWARD -i enp0s8 -o enp0s3 -m state --state NEW -j DROP
    -A FORWARD -i enp0s3 -o enp0s8 -j ACCEPT
    COMMIT
    *nat
    :PREROUTING ACCEPT [0:0]
    :INPUT ACCEPT [0:0]
    :OUTPUT ACCEPT [0:0]
    :POSTROUTING ACCEPT [0:0]
    -A POSTROUTING -p udp -o enp0s8 -j MASQUERADE --to-ports 2000-6000
    -A POSTROUTING -p tcp -o enp0s8 -j MASQUERADE --to-ports 2000-6000
    COMMIT
    ```

#### Symmetric NAT: Random port

    ```
    *filter
    :INPUT ACCEPT [0:0]
    :FORWARD ACCEPT [0:0]
    :OUTPUT ACCEPT [0:0]
    -A FORWARD -i enp0s8 -o enp0s3 -m state --state RELATED,ESTABLISHED -j ACCEPT
    -A FORWARD -i enp0s8 -o enp0s3 -m state --state NEW -j DROP
    -A FORWARD -i enp0s3 -o enp0s8 -j ACCEPT
    COMMIT
    *nat
    :PREROUTING ACCEPT [0:0]
    :INPUT ACCEPT [0:0]
    :OUTPUT ACCEPT [0:0]
    :POSTROUTING ACCEPT [0:0]
    -A POSTROUTING -o enp0s8 -j MASQUERADE --random
    COMMIT
    ```

### NAT 2

#### Full Cone NAT

    ```
    *filter
    :INPUT ACCEPT [0:0]
    :FORWARD ACCEPT [0:0]
    :OUTPUT ACCEPT [0:0]
    COMMIT
    *nat
    :PREROUTING ACCEPT [0:0]
    :INPUT ACCEPT [0:0]
    :OUTPUT ACCEPT [0:0]
    :POSTROUTING ACCEPT [0:0]
    -A PREROUTING -i enp0s3 -j DNAT --to-destination 192.168.58.5
    -A POSTROUTING -o enp0s3 -j SNAT --to-source 192.168.57.5
    COMMIT
    ```

#### Restricted Cone NAT

    ```
    *filter
    :INPUT ACCEPT [0:0]
    :FORWARD ACCEPT [0:0]
    :OUTPUT ACCEPT [0:0]
    -A INPUT -i enp0s8 -j ACCEPT
    -A INPUT -i enp0s3 -p tcp -m state --state RELATED,ESTABLISHED -j ACCEPT
    -A INPUT -i enp0s3 -p udp -m state --state RELATED,ESTABLISHED -j ACCEPT
    -A INPUT -i enp0s3 -p tcp -m state --state NEW -j DROP
    -A INPUT -i enp0s3 -p udp -m state --state NEW -j DROP
    COMMIT
    *nat
    :PREROUTING ACCEPT [0:0]
    :INPUT ACCEPT [0:0]
    :OUTPUT ACCEPT [0:0]
    :POSTROUTING ACCEPT [0:0]
    -A PREROUTING -i enp0s3 -p tcp -j DNAT --to-destination 192.168.58.5
    -A PREROUTING -i enp0s3 -p udp -j DNAT --to-destination 192.168.58.5
    -A POSTROUTING -o enp0s3 -p tcp -j SNAT --to-source 192.168.57.5
    -A POSTROUTING -o enp0s3 -p udp -j SNAT --to-source 192.168.57.5
    COMMIT
    ```

#### Port-Restricted Cone NAT

    ```
    *filter
    :INPUT DROP [0:0]
    :FORWARD ACCEPT [0:0]
    :OUTPUT ACCEPT [0:0]
    -A INPUT -i enp0s3 -m state --state RELATED,ESTABLISHED -j ACCEPT
    -A INPUT -i enp0s9 -m state --state RELATED,ESTABLISHED -j ACCEPT
    -A INPUT -i enp0s8 -j ACCEPT
    COMMIT
    *nat
    :PREROUTING ACCEPT [0:0]
    :INPUT ACCEPT [0:0]
    :OUTPUT ACCEPT [0:0]
    :POSTROUTING ACCEPT [0:0]
    -A POSTROUTING -o enp0s3 -j SNAT --to-source 192.168.57.5
    COMMIT
    ```

#### Symmetric NAT: Port preservation

    ```
    *filter
    :INPUT ACCEPT [0:0]
    :FORWARD ACCEPT [0:0]
    :OUTPUT ACCEPT [0:0]
    -A FORWARD -i enp0s3 -o enp0s8 -m state --state RELATED,ESTABLISHED -j ACCEPT
    -A FORWARD -i enp0s3 -o enp0s8 -m state --state NEW -j DROP
    -A FORWARD -i enp0s8 -o enp0s3 -j ACCEPT
    COMMIT
    *nat
    :PREROUTING ACCEPT [0:0]
    :INPUT ACCEPT [0:0]
    :OUTPUT ACCEPT [0:0]
    :POSTROUTING ACCEPT [0:0]
    -A POSTROUTING -o enp0s3 -j MASQUERADE
    COMMIT
    ```

#### Symmetric NAT: Sequential port

    ```
    *filter
    :INPUT ACCEPT [0:0]
    :FORWARD ACCEPT [0:0]
    :OUTPUT ACCEPT [0:0]
    -A FORWARD -i enp0s3 -o enp0s8 -m state --state RELATED,ESTABLISHED -j ACCEPT
    -A FORWARD -i enp0s3 -o enp0s8 -m state --state NEW -j DROP
    -A FORWARD -i enp0s8 -o enp0s3 -j ACCEPT
    COMMIT
    *nat
    :PREROUTING ACCEPT [0:0]
    :INPUT ACCEPT [0:0]
    :OUTPUT ACCEPT [0:0]
    :POSTROUTING ACCEPT [0:0]
    -A POSTROUTING -p udp -o enp0s3 -j MASQUERADE --to-ports 2000-6000
    -A POSTROUTING -p tcp -o enp0s3 -j MASQUERADE --to-ports 2000-6000
    COMMIT
    ```

#### Symmetric NAT: Random port

    ```
    *filter
    :INPUT ACCEPT [0:0]
    :FORWARD ACCEPT [0:0]
    :OUTPUT ACCEPT [0:0]
    -A FORWARD -i enp0s3 -o enp0s8 -m state --state RELATED,ESTABLISHED -j ACCEPT
    -A FORWARD -i enp0s3 -o enp0s8 -m state --state NEW -j DROP
    -A FORWARD -i enp0s8 -o enp0s3 -j ACCEPT
    COMMIT
    *nat
    :PREROUTING ACCEPT [0:0]
    :INPUT ACCEPT [0:0]
    :OUTPUT ACCEPT [0:0]
    :POSTROUTING ACCEPT [0:0]
    -A POSTROUTING -o enp0s3 -j MASQUERADE --random
    COMMIT
    ```

## Network interfaces
The network interfaces are set up using the netctl configuration files listed
below:

### PC 1

#### enp0s3

    ```
    Interface=enp0s3
    Connection=ethernet
    IP=static
    Address=('192.168.56.4/24')
    Gateway='192.168.56.5'
    DNS=('192.168.56.5')
    ```

### NAT 1

#### enp0s3

    ```
    Interface=enp0s3
    Connection=ethernet
    IP=static
    Address=('192.168.56.5/24')
    ```

#### enp0s8

    ```
    Interface=enp0s8
    Connection=ethernet
    IP=static
    Address=('192.168.57.4/24')
    ```

#### enp0s9

    ```
    Interface=enp0s9
    Connection=ethernet
    IP=dhcp
    ```

### Splitter

#### enp0s3

    ```
    Interface=enp0s3
    Connection=ethernet
    IP=static
    Address=('192.168.57.6/24')
    ```

#### enp0s8

    ```
    Interface=enp0s8
    Connection=ethernet
    IP=dhcp
    ```

### NAT 2

#### enp0s3

    ```
    Interface=enp0s3
    Connection=ethernet
    IP=static
    Address=('192.168.57.5/24')
    ```

#### enp0s8

    ```
    Interface=enp0s8
    Connection=ethernet
    IP=static
    Address=('192.168.58.4/24')
    ```

#### enp0s9

    ```
    Interface=enp0s9
    Connection=ethernet
    IP=dhcp
    ```

### PC 2

#### enp0s3

    ```
    Interface=enp0s3
    Connection=ethernet
    IP=static
    Address=('192.168.58.5/24')
    Gateway='192.168.58.4'
    DNS=('192.168.58.4')
    ```

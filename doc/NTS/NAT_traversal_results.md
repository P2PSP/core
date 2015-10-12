NAT traversal results
=====================

This document shows detailed information about the test
results. General information about the tests can be found
[here](NAT_traversal_testing.md).

## Results

[This test script](../tools/setup_NAT_network.sh) was run with the
network setup in network namespaces. A realistic network condition was
configured:

    ```
    ssh root@$nat1 tc qdisc add dev ifnat12 root netem delay 30ms 5ms loss 1%
    ssh root@$nat2 tc qdisc add dev ifnat21 root netem delay 30ms 5ms loss 1%
    ```

The script took about 11 hours for 250 test runs per NAT type
combination. The result table:

    ```
    Splitter_NTS, Monitor_NTS, Peer_NTS (branch nts, commit 5c7ad00):
    Results in % (250 test runs):

    Peer1\2 | fcn   | rcn   | prcn  | sympp | symsp | symrp
    ========================================================
    fcn     | 100   | 100   | 100   | 100   | 100   | 99
    rcn     | 100   | 100   | 100   | 100   | 99    | 100
    prcn    | 99    | 100   | 100   | 28    | 70    | 0
    sympp   | 100   | 100   | 99    | 27    | 70    | 0
    symsp   | 100   | 100   | 100   | 31    | 68    | 0
    symrp   | 99    | 100   | 0     | 0     | 0     | 0
    ```

As a comparison, another test was run with harder network
conditions (less delay between the peers is more difficult
for SYMPP NAT traversal):

    ```
    ssh root@$nat1 tc qdisc add dev ifnat12 root netem delay 10ms 5ms loss 10%
    ssh root@$nat2 tc qdisc add dev ifnat21 root netem delay 10ms 5ms loss 10%
    ```

The script was executed with 50 test runs per NAT type combination:

    ```
    Splitter_NTS, Monitor_NTS, Peer_NTS (branch nts, commit 5c7ad00):
    Results in % (50 test runs):

    Peer1\2 | fcn   | rcn   | prcn  | sympp | symsp | symrp
    ========================================================
    fcn     | 100   | 100   | 100   | 100   | 100   | 100
    rcn     | 100   | 100   | 100   | 100   | 100   | 100
    prcn    | 100   | 100   | 100   | 42    | 68    | 0
    sympp   | 100   | 100   | 84    | 54    | 48    | 0
    symsp   | 100   | 100   | 90    | 48    | 30    | 0
    symrp   | 100   | 100   | 0     | 0     | 0     | 0
    ```

## Discussion

Regarding the results above and comparing them to the theoretically
possible combinations listed [here](NAT_traversal.md), the following
can be noted:

* All theoretically possible combinations also work practically,
  although not always, and all theoretically impossible combinations
  never work in the test (none of the randomly generated source ports
  could be guessed even in over 1000 test runs when trying about 20
  probable ports per run).

* The packet loss does have little impact on the results, so the
  reliable packet sending over UDP works as expected.

* The SYMPP NAT as configured by the iptables rules shows odd
  behaviour as discussed [here](NAT_traversal_testing.md), and
  therefore combinations involving the SYMPP type sometimes do not
  work even though the source port is predictable (in the second
  scenario above it worked even better than in the first).

* Combinations involving FCN and RCN NATs do nearly always work, and
  the port allocated by a SYMSP NAT can be predicted correctly most of
  the time.

Data Privacy Set of rules
=========================

The following set of rules deals with privacy-related issues. Many
content providers offer pay-per-view channels as part of their
services. From a technical point of view, this implies having a Key
Server that ciphers the stream with a symmetric encryption key and
delivers such key to authorized members only. However, this is not
enough: it is crucial that the Key Server renews the encryption key
after the expiration of a peer's authorization period so the stream
can not be decrypted any more by the peer (this feature is called
\textit{forward secrecy}). In addition, if we want to play on the safe
side then the Key Server should renew the encryption key after a peer
purchases an authorization period (if the key remained the same then
the peer might decrypt previously captured stream packets for a later
viewing). This renewal process is not trivial and is carried out by a
\textit{secure multicast protocol}. In order to alleviate the overhead
incurred by avalanches of peers entering and leaving the authorized
group (for example, at the beginning of a high interest event such as
The Olympics) key renewal can be performed on a batch manner,
i.e. renewing the key at a given fixed frequency rather than on a per
arrival/exit basis. Finally, key renewal messages should be
authenticated by means of a digital signature or other alternative
methods [SPINS](#SPINS)

Many secure multicast protocols protocols exist in the literature, for
example \cite{Xu:2008,LinSKD,ZhouHuangEGK,Yoon2011620}. Here we
suggest the implementation of a protocol by Naranjo et al
\cite{NaranjoJISE}. On it, every authorized peer receives a large
prime number from the Key Server at the beginning of its authorization
period (this communication is done under a secure channel, for example
SSL/TLS). For every renewal, the Key Server generates a message
containing the new key to be used by means of algebraic operations:
all the authorized primes are involved in this message generation
process, and the key can only be extracted from the message by a peer
with a valid prime. This protocol is efficient and suits P2PSP
architecture in a natural way: every splitter can act as a Key Server
for its own team. Hence, the stream would be first transmitted
among splitters (possible encrypted by a different key, shared by the
splitters). Within each team, its corresponding splitter would
control the encryption and key renewal process.

# References

<a name="SPINS"></a>
```
@article{SPINS,
 author = {Perrig, A. and Szewczyk, R. and Tygar, J. D. and Wen, V. and Culler, David E.},
 title = {{SPINS}: security protocols for sensor networks},
 journal = {Wirel. Netw.},
 volume = {8},
 issue = {5},
 year = {2002},
 issn = {1022-0038},
 pages = {521--534},
 numpages = {14},
 url = {http://dx.doi.org/10.1023/A:1016598314198},
 doi = {http://dx.doi.org/10.1023/A:1016598314198},
 acmid = {582464},
 publisher = {Kluwer Academic Publishers},
 address = {Hingham, MA, USA},
}
```


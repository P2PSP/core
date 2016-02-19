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
methods [[Perrig]](#Perrig).

Many secure multicast protocols protocols exist in the literature, for
example [[Xu]](#Xu),[[Lin]](#Lin),[[Zhou]](#Zhou),[[Yoon]](#Yoon). Here we
suggest the implementation of a protocol by Naranjo et al
[[Naranjo]](#Naranjo). On it, every authorized peer receives a large
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

<a name="Perrig"></a>
```
@article{Perrig,
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

<a name="Xu"></a>
```
@article{Xu,
 author = {Xu, Lihao and Huang, Cheng},
 title = {Computation-Efficient Multicast Key Distribution},
 journal = {IEEE Trans. Parallel Distrib. Syst.},
 issue_date = {May 2008},
 volume = {19},
 number = {5},
 month = may,
 year = {2008},
 issn = {1045-9219},
 pages = {577--587},
 numpages = {11},
 url = {http://dx.doi.org/10.1109/TPDS.2007.70759},
 doi = {10.1109/TPDS.2007.70759},
 acmid = {1399352},
 publisher = {IEEE Press},
 address = {Piscataway, NJ, USA},
}
```

<a name="Lin"></a>
```
@article{Lin,
title = "Secure and efficient group key management with shared key derivation",
journal = "Comput. Stand. Inter.",
volume = "31",
number = "1",
pages = "192 - 208",
year = "2009",
note = "",
issn = "0920-5489",
doi = "DOI: 10.1016/j.csi.2007.11.005",
url = "http://www.sciencedirect.com/science/article/B6TYV-4R8H1TR-6/2/fb531f2c68f8b92beebf1608a5a82746",
author = "J. Lin and K. Huang and F. Lai and H. Lee",
keywords = "Secure group communication",
keywords = "Group key management",
keywords = "Key tree",
keywords = "Shared key derivation"
}
```

<a name="Zhou"></a>
```
@inproceedings{Zhou,
 author = {Zhou, Z. and Huang, D.},
 title = {An optimal key distribution scheme for secure multicast group communication},
 booktitle = {INFOCOM'10},
 year = {2010},
 isbn = {978-1-4244-5836-3},
 location = {San Diego, California, USA},
 pages = {331--335},
 numpages = {5},
 url = {http://portal.acm.org/citation.cfm?id=1833515.1833582},
 acmid = {1833582},
 keywords = {group key management, multicast, security},
} 
```

<a name="Yoon"></a>
```
@article{Yoon,
title = "A secure broadcasting cryptosystem and its application to grid computing",
journal = "Future Generation Computer Systems",
volume = "27",
number = "5",
pages = "620 - 626",
year = "2011",
note = "",
issn = "0167-739X",
doi = "10.1016/j.future.2010.09.012",
url = "http://www.sciencedirect.com/science/article/pii/S0167739X10001913",
author = "Eun-Jun Yoon and Kee-Young Yoo",
}
```

<a name="Naranjo"></a>
```
@article{Naranjo,
author = {Naranjo, J. A. M. and Casado, L. G. and L\'opez-Ramos, J. A.},
title = {Group Oriented Renewal of Secrets and Its Application to Secure Multicast},
journal = {\href{http://www.iis.sinica.edu.tw/page/jise/Introduction.html}{Journal of Information Science and Engineering}},
volume = {27},
number = {4},
pages = {1303--1313},
month = {july},
year = {2011}
}
```


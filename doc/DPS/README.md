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
methods <cite>[][1]</cite>

[1]:http://www.quotedb.com/quotes/2112

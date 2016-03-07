End-point Masquerading Set of rules
===================================

It is expected that most of the peers are running behind NAT (Network
Address Translation) devices which connect private address networks to
the public Internet. When a packet crosses the NAT from a private
network towards the public one, the source (private) end-point is
replaced (masqueraded) by a public end-point of the NAT and an
translation entry is created in the NAT table. NAT translation entries
are needed to relate the NAT public end-point with the source
(private) end-point.

Basically, there are three types of NATs: (1) full-cone NATs, (2)
restricted-cone NATs and (3) symmetric NATs. Depending on the type of
the NAT, the number of fields in the NAT entry and the NAT behaviour
is different. A Full-Cone NAT Entry (FCNE) has three fields:

	FCNE = (public NAT port $\cal{X}$, private IP address $\cal{Y}$, private port $\cal{Z}$)


and whatever the origin of the incoming packet (incomming
  packets go from the Internet towards the private network), if that
packet is received by the NAT at the end-point (public NAT IP address,
public NAT port $\cal{X}$), the packet will cross the NAT and it will
be delivered to the proccess that is listening at the end-point
(private IP address $\cal{Y}$, private port $\cal{Z}$).

This procedure is fully compatible with the DBS module because a
full-cone NAT-ed peer (a peer that is behind a full-cone NAT) behaves
like a public peer except that the NAT masks its actual private IP
address. Nevertheless, a problem arises when two or more peers are
behind the same NAT (are in the same private network). Although an
efficient (but also complex) solution for this case is proposed in
Section\ref{sec:dealing-symmetric-NAT}, it could happen that this
solution can not be applied. Therefore, if two (or more) peers $A$ and
$B$ are in the same NAT-ed network and no NAT loopback (this feature
allows a peer $A$ to connect to other peer $B$ in the same NAT-ed
network using a the public end-point of $B$ in the NAT) is avaiable,
the DBS module does not provide enough functionality because the
neigbouring peers does not know the private end-point of each other:
$A$ only knowns the public-end point of $B$ and viceversa.

For providing the extra functionality to solve this situation peers
must implement the EMS. At the beginning of the joining stage, each
EMS-powered peer sends to the splitter its local end-point and the
splitter checks if the source end-point of the received packet (which
figures in the packet header) matches the local end-point. If these
values are the same then the peer is public; otherwise, the peer is
running in a private host. When this is true, it holds that

	\begin{equation}
		X \neq (X),
	\end{equation}


where $X$ denotes the local (private) end-point of peer $X$ and $(X)$
the global (public) end-point of peer $X$ in $X$'s NAT. In general, we
have also that

	\begin{equation}
		{\cal N}(T)\subset T,
	\end{equation}

where $T$ represents all the elements of a team (including the
splitter) and ${\cal N}(T)$ those peers that behind a NAT. In other
words,

```
\begin{equation}
{\cal N}(T) = \{P\in T \mid P \neq (P)\}.
\end{equation}
```

Notice also that the splitter can find out if a peer $A$ has a
neightbour $B$ because in this case, the public IP address of the
end-point that the splitter see of $A$ and $B$ matches.

Accordingly, when the splitter is sending the list of peers to a
EMS-graded peer $A$ and this peer is hosted by a private machine, the
splitter also checks whether $A$ has neighbours, and if this is true, the
splitter sends to $A$ the private end-point of $B$ instead of its
public end-point, and viceversa. Hence, $A$ will use the private
end-point of $B$ to communicate with it and viceversa.

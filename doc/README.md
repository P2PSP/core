---
mathml-script: |
    /*
    March 19, 2004 MathHTML (c) Peter Jipsen http://www.chapman.edu/~jipsen
    Released under the GNU General Public License version 2 or later.
    See the GNU General Public License (at http://www.gnu.org/copyleft/gpl.html)
    for more details.
    */

    function convertMath(node) {// for Gecko
      if (node.nodeType==1) {
        var newnode =
          document.createElementNS("http://www.w3.org/1998/Math/MathML",
            node.nodeName.toLowerCase());
        for(var i=0; i < node.attributes.length; i++)
          newnode.setAttribute(node.attributes[i].nodeName,
            node.attributes[i].value);
        for (var i=0; i<node.childNodes.length; i++) {
          var st = node.childNodes[i].nodeValue;
          if (st==null || st.slice(0,1)!=" " && st.slice(0,1)!="\n")
            newnode.appendChild(convertMath(node.childNodes[i]));
        }
        return newnode;
      }
      else return node;
    }

    function convert() {
      var mmlnode = document.getElementsByTagName("math");
      var st,str,node,newnode;
      for (var i=0; i<mmlnode.length; i++)
        if (document.createElementNS!=null)
          mmlnode[i].parentNode.replaceChild(convertMath(mmlnode[i]),mmlnode[i]);
        else { // convert for IE
          str = "";
          node = mmlnode[i];
          while (node.nodeName!="/MATH") {
            st = node.nodeName.toLowerCase();
            if (st=="#text") str += node.nodeValue;
            else {
              str += (st.slice(0,1)=="/" ? "</m:"+st.slice(1) : "<m:"+st);
              if (st.slice(0,1)!="/")
                 for(var j=0; j < node.attributes.length; j++)
                   if (node.attributes[j].value!="italic" &&
                     node.attributes[j].value!="" &&
                     node.attributes[j].value!="inherit" &&
                     node.attributes[j].value!=undefined)
                     str += " "+node.attributes[j].nodeName+"="+
                         "\""+node.attributes[j].value+"\"";
              str += ">";
            }
            node = node.nextSibling;
            node.parentNode.removeChild(node.previousSibling);
          }
          str += "</m:math>";
          newnode = document.createElement("span");
          node.parentNode.replaceChild(newnode,node);
          newnode.innerHTML = str;
        }
    }

    if (document.createElementNS==null) {
      document.write("<object id=\"mathplayer\"\
      classid=\"clsid:32F66A20-7614-11D4-BD11-00104BD3F987\"></object>");
      document.write("<?import namespace=\"m\" implementation=\"#mathplayer\"?>");
    }
    if(typeof window.addEventListener != 'undefined'){
      window.addEventListener('load', convert, false);
    }
    if(typeof window.attachEvent != 'undefined') {
      window.attachEvent('onload', convert);
    }
title: 'Peer-to-Peer Straightforward Protocol (P2PSP)'
...

P2PSP is an application-layer protocol designed for real-time
broadcasting of data on a P2P overlay network. P2PSP mimics the IP
multicast behaviour, where a source sends only a copy of the stream to a
collection of peers which interchange between them those chunks of data
that are needed for the rest of the peers.

Motivation
==========

Efficient large scale distribution of media (real-time video, for
example) is one of the big challenges of the Internet. To achieve this,
IETF designed IP multicast. In this transmission model, a source sends
only one copy of the stream which is delivered to a set of receivers
thanks to the automatic replication of data in the IP multicast routers.
Unfortunately, IP multicast does not fit the bussines model of most
Internet Service Providers (ISP) which disables this functionality to
end-users.

Related work
============

There are plenty of P2P straeming protocols. Depending on the overhaly
topology, they can be clasified in chains, trees or meshes. A chain
overlay is quite rare because churn can degrade significatively the
Quality of Service (QoS) of the overlay, however, it has interesting
characteristics such as peers does not need to interchange buffer maps
and peers only send a copy of the stream regardless of the size of the
overlay (we will refeer to this characteristics as “replication
factor”). Tree overlays impose that peers must send so many copies of
the stream (replication factor) as the degree of the tree, but like
chains, the protocol is also push-based. Mesh-based protocols are more
flexible regarding the overlay topology (which can be any) but peers
must known the state of the buffer of their neighbours (the protocol is
pull-based), and also are more flexible about the replication factor,
which can be any. Obviously, push-based protocols are more efficient
than pull-based one in terms of bandwidth.

P2PSP is a fully-connected mesh-structured push-based protocol. Being
$N$ the number of peers in the overlay (a “team” in the P2PSP jargon),
$N$ is degree of the mesh. The replication factor in P2PSP is 1 by
default, although as in mesh-based protocolos, it can be any other
depending on the solidarity between the peers.

[IMS (Ip Multicast Set of rules)](IMS/README.md)
================================================

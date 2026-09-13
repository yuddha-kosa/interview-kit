------------------------------
## 📌 System Design Study Notes: DNS Infrastructure & Distributed Coordination (ZooKeeper)## 🌐 Part 1: Core Internet Architecture & DNS Resolution## 1. DNS Lookup Sequence (shop.in Example)

1. Browser cache          → check if IP already cached locally
2. OS cache               → check /etc/hosts and OS DNS cache
3. Router/ISP DNS cache   → check local network resolver
4. Recursive DNS resolver → ISP's resolver, checks its cache
5. Root nameserver        → knows TLD nameservers (.com, .ly, .io)
6. TLD nameserver         → knows authoritative nameserver for domain
7. Authoritative nameserver → returns actual IP for the domain
8. IP returned to browser → browser connects to that IP

When a browser makes a request, a Recursive Resolver orchestrates a hierarchical search across 3 major layers:

* Root Name Servers: Reads the right-most part of the domain (the Top-Level Domain or TLD, like .in or .com). It doesn't know the website's IP; it only responds with the address of the specific TLD server registry.
* TLD Name Servers: Manages data for a specific domain extension (e.g., country code extensions like .in or generic ones like .org). It responds with the address of the domain's Authoritative Name Server.
* Authoritative Name Servers: The ultimate source of truth managed by the website owner or host. It holds the final master DNS records and returns the destination IP address.

## 2. Low-Latency Optimization: DNS Caching & RTT

* RTT (Round-Trip Time): The total duration (in milliseconds) for a data packet to travel from a client to a server and back.
* Caching Strategy: To minimize cumulative RTT from hopping through multiple servers, DNS caching heavily short-circuits the system:
* Browser/OS Cache: Looks locally first. If the record's TTL (Time to Live) hasn't expired, it fetches the IP instantly (0ms RTT).
   * Resolver Cache: Public resolvers (like Cloudflare 1.1.1.1 or Google 8.8.8.8) aggressively cache TLD registry locations so they almost never have to query the Root Servers.
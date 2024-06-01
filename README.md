this project is for network applications class. it involves socket programming, some distributed systems concepts, and operating Docker, along with some system design.

here's a little story on how it goes:

this is Timmy.
```
    ____________________
    \   Hi, I'm Timmy!  \
     \___________________\
  O __/
 /|\   
 / \  
```
Timmy lives on planet Batata, where EVERYTHING is a service (even calculators!).

Timmy attends a respectable university, where advanced classes of math and arithmetic are taught. one day he's assigned a task by one of the professors, in which, given any two **4 byte integers**, he must find their **sum** and **product**.

there's no chatGPT in Timmy's world so he decides to use the *Interplanetary Calculator Service* (IPCS)!

the deadline is closing in, so he rushes to his computer to grab the latest version of `calc.py`, the client program to the IPCS.

and before we delve into the flow of how Timmy uses this system, a word must be said about the architecture.

## Architecture
this legacy of the IPCS was meshed by many developers spanning generations, as it was constructed to service the need to have a highly available, super fast, and resilient system to perform math complex math operations (as complex as a Timmy brain can handle).

at heart the IPCS is a distributed service that runs on a system of a number of **servers** as its backbone, and, due to the *interplanetary* nature of this system ,  a **load balancer** must sit in the front, spreading load across them. a discovery service **registry** is responsible for providing the load balancer with information on live servers.

![simple](./img/Pasted%20image%2020240601113713.png)

to the outside world, the cluster of servers appears as only one (big, giant calculator), thanks to having a load balancer that directs the flow of requests to appropriate servers according to its built-in Round-robin algorithm.

having multiple servers up ensures *availability*. some scientist somewhere might need to perform some time-critical math, and so we can't afford having the service down because some server is offline!. and should that happen, the system can handle it gracefully, directing traffic away from it until it comes back up. so in terms of *fault tolerance*, we're set.

## Initialization
this enigmatic system has been there for centuries, but stories of how developers stood it up have been passed down through generations.

for the back-end infrastructure, the developers chose **Docker** to streamline the development and deployment process, and further enhancing scalability, for having a new server added to the cluster, is just a couple lines of work.

when the `bootstrap.sh` script ran, it created the network that servers live on, and an interface, which serves as the communication point with the load balancer when it runs later. and with a swift `docker compose up` all containers are up and running, the discovery service, and whatever number of servers were defined in the original compose.yaml file.

the discovery service was the first to run, lurking, ready for heartbeats from servers. and whenever a server container is up, it starts the heartbeat routine, where it sends the discovery registry its own address. this is done over a **TCP** socket. and as long as the server is alive, it's sending its heartbeat on an interval on that connection.

finally, the load balancer was launched, and as soon as it did, it initialized its own address list by querying the registry. it will also continue to query the registry on a set interval for any updates to that list, as servers can be added, or some can go offline, and it needs to keep a valid list of live servers to direct traffic to.

With all in place, the system stood prepared to serve those in pursuit of computational might, a beacon of reliability that endures to this very day, offering its services to all who seek its power.

## Flow

![flow](./img/Pasted%20image%2020240601152538.png)

all Timmy has to do is launch the client program and provide the hostname and port of the service he wishes to use, which in our case is `calc.batata:8080`, and a prompt in his terminal appears to input whatever problem he needs solved (as long as it conforms to the protocol, which we'll get to later); the client then sends the packet over to the IPCS system, where the load balancer catches it, and forwards it to an appropriate server. the server does the computation and returns an 8-byte result (and its ID, in the experimental version).

however, some conversions to the packet are made along the way:

the client program speaks a protocol with the servers tailored for speed, performance, and small size. it's called the Highly Sophisticated Math and Arithmetic Protocol (**HSMAP**), the packets of which are ironically smaller in size than its name. but it's Batata, things are weird here.

HSMAP packets are carried over **UDP** datagrams to the load balancer, which upon arrival of said datagrams, crafts an Ethernet frame with a destination address of the previously picked server. it loads the HSMAP packet into the Ethernet frame and pushes it to the server over a raw socket connection with the docker network interface. **raw sockets** were used to prevent the network stack from interfering and dropping packets deemed invalid by the kernel, because HSMAP is a custom protocol created by the forefathers.

the load balancer addresss was hardcoded into each server's configuration, so they all know where to send their results packets to. once this whole exchange is done, the load balancer encapsulates the result in a UDP datagram and tosses it back to the user (Timmy), wrapping up the entire process.

### Protocol
Given that the forefathers crafted the protocol for an interplanetary system where countless users rely on it daily (obviously!), a swift and lightweight mode of communication is imperative; IPCS cannot afford the luxury of establishing connections with its vast user base, prioritizing **speed** over reliability. Hence, the developers naturally opted for **UDP** as the clear choice to communicate with the system, however, internally they ditched the UDP for a custom protocl, that's even lighter and more suitable for the job. thus the HSMAP emerged.

the request packet consists of two 4 byte fields for the unsigned integers, and a single byte denoting the operation (`1` for adddition, `2` for multiplication):

![request](img/Pasted%20image%2020240601165943.png)

the response is a single 8 byte field for the result, and an optional id field that was put there for experimental purposes, and to check whether load balancing was being done correctly:

![response](img/Pasted%20image%2020240601170021.png)

## Conclusion
And just like that, Timmy's wild ride with the IPCS, peak of innovation on planet Batata, has come to a close. Fear not, fellow math geeks, for the IPCS will keep on serving up those who dare to tackle the enigmatic realm of higher mathematics, braving the challenges of complex equations with unwavering dedication and boundless knowledge.

a final diagram for u:

![final](img/Pasted%20image%2020240601181007.png)
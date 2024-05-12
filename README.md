timmy is my first attempt at explaining my project with a story, it's allowed to be shitty, but the next works will definetly be better.


this is Timmy.
```
    ____________________
    \   Hi, I'm Timmy!  \
     \___________________\
  O __/
 /|\   
 / \  
```
Timmy lives on planet Cyberia, where EVERYTHING is a service (even calculators!).

Timmy attends a respectable university, where advanced classes of math and arithmetic are taught.
one day he's assigned a task by one of the professors, in which, given any two **4 byte integers**, he must find their **sum** and **product**.

there's no chatGPT in Timmy's world so he decides to use the _interplanetary calculator service_(ICS)!

the deadline is closing in, so he rushes to his computer to grab the latest version of `calc.py`, the client program to the ICS.

since the system is interplanetary a lot of users use it on a daily basis, it needs a low overhead, quick way of communcation. it can't afford establishing connections with its users, it needs 

so it employs a load balancer to do the job

UDP does come at the cose of reliability, but this is a world where you need to be FAST.

the backend system is crude and so, so _legacy_, so it only communicates using MAC addresses, there's no concept of IPs there.
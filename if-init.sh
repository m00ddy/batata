sudo ip link add link enp0s8 address 00:11:11:11:11:11 virtual0 type macvlan
sudo ifconfig virtual0 up 
sudo ifconfig enp0s8 promisc 
sudo ip addr add 192.168.1.201/24 dev virtual0
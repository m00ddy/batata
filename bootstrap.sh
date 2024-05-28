IF_NAME="br-backend"

# docker network up
create_docker_network() {
  docker network create \
    --subnet=172.16.238.0/24 \
    --internal \
    --driver=bridge \
    --opt com.docker.network.bridge.name=br-backend \
    --ipam-driver=default \
    --ipam-opt subnet=172.16.238.0/24 \
    "$1"
}
# extract interface interface MAC address
get_if_hwaddr(){
    ip link | awk '$1~/^[0-9]*:/{printf "%s ", $2} /^ /{print $2}' | grep $1 | cut -d ":" -f 2- | xargs
}

cleanup(){
    docker compose -f ./infra/compose.yaml down
    docker network rm backend
}
# gpt magic
add_discovery_dns_record(){
    # extract discovery IP from compose file
    ip_address=$(awk '/discovery:/, /ipv4_address/ {if ($1 == "ipv4_address:") print $2}' ./infra/compose.yaml)
    # add entry to /etc/hosts only if it doesn't exist
    sudo grep -qxF "$ip_address    discovery.batata" /etc/hosts || echo "$ip_address    discovery.batata" | sudo tee -a /etc/hosts
}


create_docker_network backend

add_discovery_dns_record

hwaddr=$(get_if_hwaddr $IF_NAME)
export BR_BACKEND="$hwaddr"
echo "br-backend MAC: $BR_BACKEND"


# get docker containers up
docker compose -f ./infra/compose.yaml up --force-recreate -d --remove-orphans
if [ $? -eq 0 ]; then
    echo "running load balancer"
    (sudo python3 load-balancer.py)
else
    echo "won't launch balancer, docker compose failed"
fi

read -p "Do you want to cleanup? (y/n): " choice

if [ "$choice" = "y" ]; then
    cleanup
    echo "cleanup executed successfully."
else
    echo "cleanup execution skipped."
fi
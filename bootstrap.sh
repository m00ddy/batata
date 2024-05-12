IF_NAME="br-backend"

# docker network up
create_docker_network() {
  docker network create \
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
}


create_docker_network backend

hwaddr=$(get_if_hwaddr $IF_NAME)
export LB_MAC="$hwaddr"
echo "br-backend MAC: $LB_MAC"

# get docker containers up
docker compose -f ./infra/compose.yaml up -d
if [ $? -eq 0 ]; then
    (sudo python3 load-balancer.py)
else
    echo "won't launch balancer, docker compose failed"
fi

cleanup
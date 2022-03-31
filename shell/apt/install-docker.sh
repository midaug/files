#!/bin/sh
export DIR="$( cd "$( dirname "$0"  )" && pwd )"
cd "${DIR}"


export C_USER=${SUDO_USER}

su - root -s /bin/sh <<EOF
    ## 安装docker
    if [ -f "$(command -v docker)" ];then
      echo "docker 已存在 ~~~"
      docker -v
    else
      curl -fsSL https://p.midaug.workers.dev/https://get.docker.com -o /tmp/get-docker.sh
      sh /tmp/get-docker.sh --mirror AzureChinaCloud
      rm -f /tmp/get-docker.sh
    fi

    #添加docker用户组
    echo "add ${C_USER} to docker group ~~~~~~"
    sudo groupadd docker  
    sudo gpasswd -a $C_USER docker 
    sudo usermod -a -G docker $C_USER
    newgrp docker

    ## 安装docker-compose
    if [ -f "$(command -v docker-compose)" ];then
      echo "docker-compose 已存在 ~~~"
      docker-compose -v
    else
      curl -L "https://gh.midaug.workers.dev/https://github.com/docker/compose/releases/download/1.29.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
      chmod +x /usr/local/bin/docker-compose
    fi
EOF
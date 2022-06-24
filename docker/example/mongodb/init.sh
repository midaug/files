#!/bin/bash
DIR="$( cd "$( dirname "$0"  )" && pwd )"
cd "${DIR}"

#清理容器和数据开始重新初始化
docker-compose stop && docker-compose rm -f
rm -rf ./data
rm -f ./tools/mongodb.key

docker-compose up

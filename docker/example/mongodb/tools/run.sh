#!/bin/bash
DIR="$( cd "$( dirname "$0"  )" && pwd )"
cd "${DIR}"

export RS_KEY_FILE=/tools/mongodb.key
export username=${MONGO_INITDB_ROOT_USERNAME:-"root"}
export password=${MONGO_INITDB_ROOT_PASSWORD:-"root"}
export host=${MONGO_RS_HOST:-"127.0.0.1"}
export port=${MONGO_RS_PORT:-"27017"}
export rs_name=${MONGO_RS_NAME:-"rs001"}

#判断没有副本集的key时开始初始化
if [ ! -f "$RS_KEY_FILE" ]; then
    #生成副本集key文件
    openssl rand -base64 512 > /tools/mongodb.key
    bash /tools/init.sh
fi

echo "run mongod =========================================================="
echo "mongod --replSet ${rs_name} --keyFile ${RS_KEY_FILE} --bind_ip_all --auth"

chmod 400 $RS_KEY_FILE
chown 999:999 $RS_KEY_FILE
mongod --replSet ${rs_name} --keyFile ${RS_KEY_FILE} --bind_ip_all --auth
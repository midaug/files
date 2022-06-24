#!/bin/bash

echo "rs init -> MONGO_RS_HOST=${host}"
echo "rs init -> MONGO_RS_PORT=${port}"
echo "rs init -> MONGO_RS_NAME=${rs_name}"

#初始化root用户
nohup mongod --bind_ip_all > /dev/null 2>&1 &
sleep 3s
mongo --port ${port} <<EOF
use admin 
db.createUser({user:"${username}",pwd:"${password}",roles:[{role:'root',db:'admin'}]})
exit
EOF
sleep 2s
ps aux | grep mongod | grep -v grep |  awk '{print $2}' | xargs kill -9 
sleep 2s

#初始化设置副本集模式
nohup mongod --replSet ${rs_name} --bind_ip_all > /dev/null 2>&1 &
sleep 3s
mongo --port ${port} <<EOF
use admin 
rs.initiate( { _id : "${rs_name}",members: [{ _id: 0,host: "${host}:${port}" }]})
exit
EOF
sleep 2s
ps aux | grep mongod | grep -v grep |  awk '{print $2}' | xargs kill -9 
sleep 2s
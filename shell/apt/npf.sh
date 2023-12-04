#!/bin/sh

FP_CODE=""

while IFS= read -r line; do
    cleaned_line=$(echo "$line" | tr -d '\n' | tr -d '[:space:]')
    if [ -n "$cleaned_line" ]; then
        p=$(echo "$cleaned_line" | cut -d'/' -f1) #端口
        f=$(echo "$cleaned_line" | cut -d'/' -f2) #转发地址
        t=$(echo "$cleaned_line" | cut -d'/' -f3) #协议,只能写udp,不为udp时必须为空
        if [ "$t" != "udp" ]; then
            t=""
        fi
        FP_CODE="${FP_CODE}
            server {
                listen       ${p} ${t};
                proxy_pass   ${f};
            }
            "
    fi
done < <(echo "$STREAM_CONF" | tr ';' '\n')

echo "===========================Splicing preparation"
echo -e "$FP_CODE"

DEFAULT_CONF="
user  nginx;   
worker_processes  auto;   
error_log  /dev/stdout notice;   
pid        /var/run/nginx.pid;   
events {   
    worker_connections  1024;   
}  
http {   
    include       /etc/nginx/mime.types;  
    default_type  application/octet-stream;     
    sendfile        on;
    keepalive_timeout  65;
}   
stream {
    log_format stream '\$remote_addr [\$time_local] '
           '\$protocol \$status br="\${bytes_received}" bs="\${bytes_sent}" '
           'st="\$session_time" "\$upstream_addr" '
          '"\$upstream_connect_time"';
    access_log /dev/stdout stream;
    ${FP_CODE}  
}
"

echo "===========================Final nginx.conf content"
echo -e "$DEFAULT_CONF"
echo -e "$DEFAULT_CONF" > /etc/nginx/nginx.conf

/bin/sh /docker-entrypoint.sh nginx -g 'daemon off;'

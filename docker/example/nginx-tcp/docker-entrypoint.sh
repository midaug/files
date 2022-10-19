#!/bin/sh
# vim:sw=4:ts=4:et

set -e
if [ -n "$NGINX_CONF" ]; then
    NGINX_CONF_PATH=/etc/nginx/nginx.conf
    echo "$NGINX_CONF" > $NGINX_CONF_PATH
    sed -i 's/@@/\$/g' $NGINX_CONF_PATH
    echo "cat $NGINX_CONF_PATH" && cat $NGINX_CONF_PATH
fi


source ./docker-entrypoint.sh
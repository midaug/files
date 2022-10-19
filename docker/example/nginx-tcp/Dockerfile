ARG NGINX_VERSION=1.23.0-alpine
FROM nginx:${NGINX_VERSION}
#FROM nginx:1.23.0-alpine

COPY docker-entrypoint.sh /new-docker-entrypoint.sh 
ENTRYPOINT ["/new-docker-entrypoint.sh"]
CMD ["nginx", "-g", "daemon off;"]
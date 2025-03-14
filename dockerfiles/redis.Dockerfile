FROM redis:7.2-alpine

WORKDIR /redis

EXPOSE 6379

COPY ./redis/redis.conf.example /usr/local/etc/redis/redis.conf

COPY ./src/scripts/entrypoint-redis.sh ./entrypoint.sh

RUN chmod +x ./entrypoint.sh

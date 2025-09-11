FROM nginx:latest

WORKDIR /app/www

COPY ./nginx/default.conf.template /etc/nginx/templates/

EXPOSE 80

CMD [ "nginx", "-g", "daemon off;" ]

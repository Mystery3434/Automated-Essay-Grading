FROM nginx:1.11.3
# RUN ls
RUN rm /etc/nginx/nginx.conf
COPY nginx.conf /etc/nginx/
RUN rm /etc/nginx/conf.d/default.conf
COPY kpep.conf /etc/nginx/conf.d/


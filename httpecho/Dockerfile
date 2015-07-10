# rhcarvalho/httpecho
FROM gliderlabs/alpine
RUN apk-install curl
COPY httpecho /
EXPOSE 8080
ENTRYPOINT ["/httpecho"]

# rhcarvalho/httphostname
FROM gliderlabs/alpine
RUN apk-install curl
COPY httphostname /
EXPOSE 8080
ENTRYPOINT ["/httphostname"]

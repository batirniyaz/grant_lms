FROM ubuntu:latest
LABEL authors="murat"

ENTRYPOINT ["top", "-b"]
#!/bin/sh
podman run --rm  -it \
 -v /home/l30/.centralizer/config/:/root/.centralizer/config/ \
 -p 8080:80 \
 --security-opt label=disable \
 centralizer

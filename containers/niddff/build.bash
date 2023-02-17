#!/bin/bash 

tag_version=$1
shift

# Build docker container
docker build --tag niddff:${tag_version} $* .

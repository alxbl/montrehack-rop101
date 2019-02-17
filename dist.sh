#!/bin/bash
docker build -t rop-final .
docker run -p3001:3001 -p3002:3002 -p3003:3003 \
    --name rop-final \
    --security-opt seccomp=unconfined \
    rop-final

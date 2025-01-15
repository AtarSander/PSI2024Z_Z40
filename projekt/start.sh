#!/bin/bash

if [ -z "$1" ]; then
  SERVER_BACKLOG=5
else
  SERVER_BACKLOG=$1
fi

export SERVER_BACKLOG

docker compose up --build
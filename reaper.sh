#!/bin/bash

# Clean up stalled processes.

while :; do
 echo "click."
 kill -9 $(ps -eo comm,pid,etimes | grep motd_v | awk '{ if ($3 > 60) { print $2 }}') &>/dev/null
 sleep 10
done;

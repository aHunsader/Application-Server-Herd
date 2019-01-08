#!/bin/bash

servers="Goloman Hands Holiday Wilkes Welsh"

for server in $servers; do
	python3 server.py $server &
	PID=$!
	echo $PID
done
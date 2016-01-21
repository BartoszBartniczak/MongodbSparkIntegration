#!/bin/bash


SPARK_DIR=/usr/local/spark
MASTER_HOST=master
MASTER_PORT=7077
CMD=${1:-"exit 0"}
if [[ "$CMD" == "-dm" ]];
then
	$SPARK_DIR/sbin/start-master.sh
	tail -f $SPARK_DIR/logs/*
elif [[ "$CMD" == "-ds" ]];
then
	$SPARK_DIR/sbin/start-slave.sh spark://$MASTER_HOST:$MASTER_PORT
	tail -f $SPARK_DIR/logs/*
else
	/bin/bash -c "$*"
fi

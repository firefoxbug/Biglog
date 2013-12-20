#!/bin/bash

# Author : firefoxbug
# E-Mail : wanghuafire@gmail.com
# Blog   : www.firefoxbug.net
# Function : biglog 启动脚本


cur_dir=$(pwd)

sleep 1

function stop_biglog()
{
	kill `ps axu | grep "BigLogDomain" | awk '{print $2}'` > /dev/null 2>&1 &
	kill `ps axu | grep "BigLogGeo" | awk '{print $2}'` > /dev/null 2>&1 &
	kill `ps axu | grep "biglog_recv" | awk '{print $2}'` > /dev/null 2>&1 &
	kill `ps axu | grep "biglog_collect" | awk '{print $2}'` > /dev/null 2>&1 &
	kill `ps axu | grep "BigLogMysql" | awk '{print $2}'` > /dev/null 2>&1 &
	kill `ps axu | grep "biglog_time" | awk '{print $2}'` > /dev/null 2>&1 &
}

function start_redis()
{
	#启动redis
	lines=`ps axu | grep redis | wc -l | awk '{print $1}'`
	if [ "$lines" != "1" ];then
		#redis already running
		return
	fi

	if [ ! -f "/etc/redis.conf" ];then
		cat  >/etc/redis.conf <<EOF
daemonize yes
pidfile /var/run/redis_6379.pid
port 6379
timeout 0
tcp-keepalive 0
loglevel notice
logfile /var/log/redis_6379.log
databases 16
save 900 1
save 300 10
save 60 10000
stop-writes-on-bgsave-error yes
rdbcompression yes
rdbchecksum yes
dbfilename dump.rdb
dir /var/lib/redis/
slave-serve-stale-data yes
slave-read-only yes
repl-disable-tcp-nodelay no
slave-priority 100
appendonly no
appendfsync everysec
no-appendfsync-on-rewrite no
auto-aof-rewrite-percentage 100
auto-aof-rewrite-min-size 64mb
lua-time-limit 5000
slowlog-log-slower-than 10000
slowlog-max-len 128
hash-max-ziplist-entries 512
hash-max-ziplist-value 64
list-max-ziplist-entries 512
list-max-ziplist-value 64
set-max-intset-entries 512
zset-max-ziplist-entries 128
zset-max-ziplist-value 64
activerehashing yes
client-output-buffer-limit normal 0 0 0
client-output-buffer-limit slave 256mb 64mb 60
client-output-buffer-limit pubsub 32mb 8mb 60
hz 10
EOF
	fi
	redis-server /etc/redis.conf
}

function start_gearmand()
{
	#启动gearmand
	lines=`ps axu | grep gearman | wc -l | awk '{print $1}'`
	if [ "$lines" == "1" ];then
		echo "starting gearmand ..."
		gearmand -d
	fi
}

function start_biglog()
{
	start_redis
	start_gearmand

	pushd ${cur_dir}/daemon
	nohup python2.6 -u BigLogDomain.py > ${cur_dir}/logs/BigLogDomain.log 2>&1 &
	nohup python2.6 -u BigLogMysql.py > ${cur_dir}/logs/BigLogMysql.log 2>&1 &
	nohup python2.6 -u BigLogMysql.py > ${cur_dir}/logs/BigLogMysql.log 2>&1 &
	popd

	pushd ${cur_dir}/daemon
	pushd geoip
	nohup python2.6 -u BigLogGeo.py > ${cur_dir}/logs/BigLogGeo.log 2>&1 &
	popd
	popd

	pushd ${cur_dir}/recv
	nohup python2.6 -u biglog_recv.py > ${cur_dir}/logs/biglog_recv.log 2>&1 &
	popd

	pushd ${cur_dir}/collect
	#nohup python2.6 biglog_collect.py > ${cur_dir}/logs/biglog_collect.log 2>&1 &
	nohup python2.6 -u biglog_timer.py > ${cur_dir}/logs/biglog_timer.log 2>&1 &
	popd
}

function main()
{
	stop_biglog
	start_biglog
}

main
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
	kill `ps axu | grep "BigLogGeoIP" | awk '{print $2}'` > /dev/null 2>&1 &
	kill `ps axu | grep "BigLogRecv" | awk '{print $2}'` > /dev/null 2>&1 &
	kill `ps axu | grep "BigLogTimer" | awk '{print $2}'` > /dev/null 2>&1 &
	kill `ps axu | grep "BigLogMysql" | awk '{print $2}'` > /dev/null 2>&1 &
}

function start_redis()
{
	#启动redis
	lines=`ps axu | grep redis | wc -l | awk '{print $1}'`
	if [ "$lines" != "1" ];then
		#redis already running
		return
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

function stop_gearmand()
{
	#停止gearmand
	kill `ps axu | grep gearman | awk '{print $2}'`
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
	nohup python2.6 -u BigLogGeoIP.py > ${cur_dir}/logs/BigLogGeo.log 2>&1 &
	popd
	popd

	pushd ${cur_dir}/recv
	nohup python2.6 -u BigLogRecv.py > ${cur_dir}/logs/BigLogRecv.log 2>&1 &
	popd

	pushd ${cur_dir}/collect
	#nohup python2.6 biglog_collect.py > ${cur_dir}/logs/biglog_collect.log 2>&1 &
	nohup python2.6 -u BigLogTimer.py > ${cur_dir}/logs/BigLogTimer.log 2>&1 &
	popd
}

function main()
{
	stop_biglog
	start_biglog
}

main
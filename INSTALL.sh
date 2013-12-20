#!/bin/bash

## Check user permissions ##
if [ $(id -u) != "0" ]; then
	echo "Error: NO PERMISSION! Please login as root to install Volcano."
	exit 1
fi

function yum_update()
{
	IS_64=`uname -a | grep "x86_64"`
	if [ -z "${IS_64}" ]
	then
		CPU_ARC="i386"
	else
		CPU_ARC="x86_64"
	fi

	IS_5=`cat /etc/redhat-release | grep "5.[0-9]"`
	if [ -z "${IS_5}" ]
	then
		VER="6"
		rpm_ver="epel-release-6-8.noarch.rpm"
	else
		VER="5"
		rpm_ver="epel-release-5-4.noarch.rpm"
	fi
	setenforce 0
	rpm -ivh "http://dl.fedoraproject.org/pub/epel/${VER}/${CPU_ARC}/${rpm_ver}"
	rm -rf /etc/localtime
	ln -s /usr/share/zoneinfo/Asia/Shanghai /etc/localtime

	yum -y install yum-fastestmirror ntpdate ntp git
	ntpdate -u pool.ntp.org
	/sbin/hwclock -w
}

function install_python26()
{
	echo "Checking python version...."
	py_version=$(python -V)
	echo "$py_version"
	py_version=$(echo "$py_version" | awk -F '[ .]' '{printf("%s.%s",$2,$3)}')
	if [ "$py_version" != "2.6" ];then
		echo "Now install python 2.6...."
		yum -y install python26 python26-mysqldb MySQL-python
	fi
}

function install_gearman()
{
	wget http://dagobah.ftphosting.net/yum/smartfile.repo -O /etc/yum.repos.d/smartfile.repo
	yum install -y python26-setuptools
	yum -y install gearmand libgearman
	wget -c ftp://182.255.0.82/FreeBSD/ports/distfiles/gearman-2.0.1.tar.gz
	tar xvzf  gearman-2.0.1.tar.gz
	cd gearman-2.0.1
	python2.6 setup.py install
	gearmand -d
}

function install_redis()
{
	yum install -y redis python26-redis
	git clone https://github.com/andymccurdy/redis-py.git
	cd redis-py
	python2.6 setup.py install	
	mv /etc/redis.conf /etc/redis.conf.bak
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
	redis-server /etc/redis.conf
}

function main()
{
	yum_update
	install_python26
	install_gearman
	install_redis
}

main

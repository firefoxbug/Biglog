#!/usr/bin/env python2.6
#-*- coding: utf-8 -*-

# Author : firefoxbug
# E-Mail : wanghuafire@gmail.com
# Blog   : www.firefoxbug.net
''' COLLECT Moudle : receive decoded logs from RECV Moudle and analysis every certain time . And send sql commands to TOSQL Module'''
import sys
sys.path.append("../")
sys.path.append("../daemon")
from data_trans import RecvLog
from biglog_mysql import mysql_init
#from BigLogCollect import collect_log
from biglog_redis import connect2redis
import biglog_gearman import connect2gearman

def main():
	mysql_init()
	connect2gearman()
	connect2redis(host="127.0.0.1")
	RecvLog.recv_redis_log()
#	collect_log()
	pass

if __name__ == '__main__':
	main()
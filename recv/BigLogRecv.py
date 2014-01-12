#!/usr/bin/env python2.6
#-*- coding: utf-8 -*-

# Author : firefoxbug
# E-Mail : wanghuafire@gmail.com
# Blog   : www.firefoxbug.net
''' RECV Moudle : parse received logs and send decoded logs to COLLECT Module'''
import sys
sys.path.append("../")

from log_trans import RecvLog
from biglog_redis import connect2redis

def main():
	connect2redis(host='127.0.0.1')
	biglog_rv = RecvLog.recv_udp_log()

if __name__ == '__main__':
	main()
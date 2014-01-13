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

	"""conf debug"""
	try:
		from biglog_conf import parse_biglog_conf
		input_info = parse_biglog_conf()
		udp_input_port = input_info['udp_port']
	except :
		udp_input_port = 515

	biglog_recv_input_log(udp_input_port)

def biglog_recv_input_log(PORT=515):
	connect2redis(host='127.0.0.1')
	biglog_rv = RecvLog.recv_udp_log(PORT)

if __name__ == '__main__':
	main()
#!/usr/bin/env python2.6
#-*- coding: utf-8 -*-

# Author : firefoxbug
# E-Mail : wanghuafire@gmail.com
# Blog   : www.firefoxbug.net

import os
import sys
sys.path.append("../")
import json
import socket

from data_record import RecordLogInfo
#from BigLogCollect import collect_log
import myredis

class RecvLog(object):
	@classmethod
	def recv_udp_log(self,PORT=514):
		"""receive logs from udp socket chosen port.default udp 515"""
		HOST = ''   # use '' to expose to all networks
	#	PORT = 515
		# Datagram (udp) socket
		try :
			s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
			print 'Socket created'
		except socket.error, msg :
			print 'Failed to create socket. Error Code : ' + str(msg[0]) + ' Message ' + msg[1]
			sys.exit()

		# Bind socket to local host and port
		try:
			s.bind((HOST, PORT))
		except socket.error , msg:
			print 'Bind failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1]
			sys.exit()

		biglog_rl = RecordLogInfo()

		try:
			while True:
				data, addr = s.recvfrom(4096)
				if not data:
					continue
				log_info = json.loads(data)
				biglog_rl.record_log_info(log_info)
		except KeyboardInterrupt:
			print()
			s.close()

	@classmethod
	def recv_redis_log(self):
		"""receive logs from redis key is biglog """
		biglog_rl = RecordLogInfo()
		try:
			while True:
				data = myredis.redis_q.get('BiglogDict')
				log_info = json.loads(data)
#				print log_info
				biglog_rl.record_log_info(log_info)
		except KeyboardInterrupt:
			print()	

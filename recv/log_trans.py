#!/usr/bin/env python2.6
#-*- coding: utf-8 -*-

# Author : firefoxbug
# E-Mail : wanghuafire@gmail.com
# Blog   : www.firefoxbug.net

import os
import sys
import json
import socket
'''receive logs '''

from log_parse import ParseLog
import log_parse
#from biglog_addjob import add_gearman_job
import myredis

class RecvLog(object):
	@classmethod
	def parse_input_log_type(self,biglog):
		

	@classmethod
	def recv_udp_log(self,PORT=515):
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
		
		biglog_plog = ParseLog()
#		biglog_slog = SendLog()

		try:
			while True:
				data, addr = s.recvfrom(4096)
				if not data:
					continue

				try :
					if biglog_plog.parse(data):
		#				print log_parse.log_info
#						biglog_slog.send_udp_log(log_parse.log_info)
						myredis.redis_q.put('BiglogDict',json.dumps(log_parse.log_info))
#						add_gearman_job("BigLogCollect",log_parse.log_info)
				except Exception,e:
					print "[ERROR] : %s"%str(e)		
		except KeyboardInterrupt:
			print()
			s.close()

	@classmethod
	def read_log_file(self,access_log):
		"""read logs from access log file"""
		if not os.path.isfile(access_log):
			print "[ERROR ] : %s is not a file"%access_log
			sys.exit(1)
		try :
			fd = open(access_log)
		except Exception,e:
			print "[ERROR ] : %s open failed"%access_log
			print str(e)
			sys.exit(1)
		biglog_plog = ParseLog()
#		biglog_slog = SendLog()

		while True:
			log_line = fd.readline()
			if not log_line :
					break
			try :
				if biglog_plog.parse(log_line):
					pass
#				print log_parse.log_info
#					biglog_slog.send_udp_log(log_parse.log_info)
			except Exception,e:
				print "[ERROR ] : Parse Log"
				print "[INFO ] : %s"%str(e)
		fd.close()

class SendLog(object):
	
	@classmethod
	def _init_socket(self,ip='127.0.0.1',port=514):
		"""send logs by udp socket in chosen port.default udp 514"""
		# addressing information of target
		self.addr = (ip,port)
		# initialize a socket, think of it as a cable
		try :
			self.s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, 0)
		except socket.error, msg :
			print '[ERROR ] : Failed to send log '
			print str(msg)

	def json_decode(self,data):
		return json.dumps(data)

	def send_udp_log(self,data):
		data2send = self.json_decode(data)
		self.s.sendto(data2send,self.addr)
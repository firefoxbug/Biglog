#!/usr/bin/env python2.6
#-*- coding: utf-8 -*-

# Author : firefoxbug
# E-Mail : wanghuafire@gmail.com
# Blog   : www.firefoxbug.net

import os
import sys
import time
from data_display import DisplayLogs
import signal

class RecordLogInfo(object):
	"""docstring for RecordLogInfo"""
	def __init__(self):
		self.log = {}

		self.insert_log_time = {}

		self.request_bandwidth = {}
		self.request_bandwidth['req_count'] = 0
		self.request_bandwidth['bandwidth'] = 0 

		self.INTERVAL = 60
		self.BASE_TIME_FORMAT = '%Y-%m-%d %H:%M:00'
		self.MYSQL_TIME_FORMAT = "%Y-%m-%d:%H:%M:00"
		self.UNIT = "minute"

		self.log_key = {}
		self.log_key['KEY_IP'] = "visitor_ip"					# request flow
		self.log_key['KEY_TIME_LOCAL'] = "time"					# request flow
		self.log_key['KEY_REQUEST'] = "request"					# request flow
		self.log_key['KEY_STATIC_FILE'] = "request_static"		# request flow
		self.log_key['KEY_STATUS_CODE'] = "status_code"
		self.log_key['KEY_REQUEST_NOT_FOUND'] = "request_not_found"
		self.log_key['KEY_REFERER'] = "referer"
		self.log_key['KEY_BROWSER'] = "browser"
		self.log_key['KEY_OS_TYPE'] = "os"
		self.log_key['KEY_BANDWIDTH'] = "bandwidth"

		time_local = time.strftime(self.BASE_TIME_FORMAT,time.localtime(time.time()))
		self.base_time = time.mktime(time.strptime(time_local,'%Y-%m-%d %H:%M:%S'))	

	def record_log_info(self,log_info):
		domain = log_info['domain']
		if domain == "-":
			return 
		time_key = log_info['time_key']
#		self.expired(log_info)

		self.domain_exists(domain)
		self.process_request_bw(domain,self.log_key['KEY_IP'],log_info['visitor_ip'],log_info['req_size'])
		self.process_request_bw(domain,self.log_key['KEY_TIME_LOCAL'],time_key,log_info['req_size'])
		if self.verify_static_content(log_info['uri']):
			# request uri is static file
			self.process_request_bw(domain,self.log_key['KEY_STATIC_FILE'],log_info['uri'],log_info['req_size'])
		else :
			# request uri is not static file
			self.process_domain_bw(domain,self.log_key['KEY_REQUEST'],log_info['uri'],log_info['req_size'])

		if log_info['status_code'] == "404":
			# request code is 404
			self.process_request_data(domain,self.log_key['KEY_REQUEST_NOT_FOUND'],log_info['uri'])
			
		self.process_request_data(domain,self.log_key['KEY_STATUS_CODE'],log_info['status_code'])
		self.process_request_data(domain,self.log_key['KEY_REFERER'],log_info['referer'])
		self.process_request_data(domain,self.log_key['KEY_BROWSER'],log_info['browser_type'])
		self.process_request_data(domain,self.log_key['KEY_OS_TYPE'],log_info['os_type'])

	def expired(self,log_info):
		if log_info['time_unix_all'] - self.base_time < self.INTERVAL:
			# log time in specified time interval
			# count all dictionaries
			return 
		else:
#			print log_info['time_unix_all'],self.base_time
			x = time.localtime(self.base_time)
			time_key = time.strftime(self.MYSQL_TIME_FORMAT,x)
			self.insert_log_time['time_str'] = time_key
			self.insert_log_time['time_num'] = self.base_time
			self.insert_log_time['UNIT'] = self.UNIT
			# save time_key in global values
			signal.signal(signal.SIGCHLD,signal.SIG_IGN)
			pid = os.fork()
			if pid == 0:
				DisplayLogs.display_log_summary(self.log,self.log_key,self.insert_log_time)
				sys.exit(1)
			else :
				x = time.localtime(log_info['time_unix_all'])
				time_minute = time.strftime(self.BASE_TIME_FORMAT,x)
				self.base_time = time.mktime(time.strptime(time_minute,'%Y-%m-%d %H:%M:%S'))
				# clear all dictionaries
				self.log.clear()

	def domain_exists(self,domain):
		if not self.log.has_key(domain):
			self.insert_domain(domain)

	def insert_domain(self,domain):
		self.log[domain] = {}
		self.log[domain][self.log_key['KEY_IP']] = {}
		self.log[domain][self.log_key['KEY_TIME_LOCAL']] = {}
		self.log[domain][self.log_key['KEY_REQUEST']] = {}
		self.log[domain][self.log_key['KEY_STATUS_CODE']] = {}
		self.log[domain][self.log_key['KEY_STATIC_FILE']] = {}
		self.log[domain][self.log_key['KEY_REQUEST_NOT_FOUND']] = {}
		self.log[domain][self.log_key['KEY_REFERER']] = {}
		self.log[domain][self.log_key['KEY_BROWSER']] = {}
		self.log[domain][self.log_key['KEY_OS_TYPE']] = {}
		self.log[domain][self.log_key['KEY_BANDWIDTH']] = 0

	# record request count and bandwidth of chosen domain,update dictionary
	def process_request_bw(self,domain,key_log_type,key_log_value,bandwidth):
		if not self.log[domain][key_log_type].has_key(key_log_value):
			self.log[domain][key_log_type][key_log_value] = self.request_bandwidth
			self.log[domain][key_log_type][key_log_value]['req_count']  = 1
			self.log[domain][key_log_type][key_log_value]['bandwidth'] = bandwidth
			return 

		self.log[domain][key_log_type][key_log_value]['req_count']  += 1
		self.log[domain][key_log_type][key_log_value]['bandwidth'] += bandwidth

	def process_domain_bw(self,domain,key_log_type,key_log_value,bandwidth):
		if not self.log[domain][key_log_type].has_key(key_log_value):
			self.log[domain][key_log_type][key_log_value] = self.request_bandwidth
			self.log[domain][key_log_type][key_log_value]['req_count']  = 1
			self.log[domain][key_log_type][key_log_value]['bandwidth'] = bandwidth
			self.log[domain][self.log_key['KEY_BANDWIDTH']] = bandwidth
			return

		self.log[domain][key_log_type][key_log_value]['req_count'] += 1
		self.log[domain][key_log_type][key_log_value]['bandwidth'] += bandwidth
		self.log[domain][self.log_key['KEY_BANDWIDTH']] += bandwidth

	# record request count
	def process_request_data(self,domain,key_log_type,key_log_value):
		if not self.log[domain][key_log_type].has_key(key_log_value):
			self.log[domain][key_log_type][key_log_value] = 1 
			return 1
		self.log[domain][key_log_type][key_log_value] += 1

	# check static uri
	def verify_static_content(self,request_uri):
		static_file_type = [".jpg",".JPG",".png",".PNG",".js",".JS",".gif",".GIF",".css",".CSS",".ico",".ICO",".swf",".SWF",".jpeg",".JPEG",]
		for item in static_file_type:
			if item in request_uri:
				return True
		return False

	def _clear(self):
		self.log.clear()

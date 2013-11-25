#!/usr/bin/env python2.6
#-*- coding: utf-8 -*-

# Author : firefoxbug
# E-Mail : wanghuafire@gmail.com
# Blog   : www.firefoxbug.net

import os
import sys
sys.path.append("../")
import time
import re
import datetime

log_info = {}

#from log_mysql import DomainDB
from biglog_addjob import add_gearman_job
import myredis

class ParseLog(object):
	"""docstring for ParseLog"""
	def __init__(self):
		self.BASE_TIME_FORMAT = '%Y-%m-%d %H:%M:00'
		pass;

	def parse(self,log_line):
		self.log_line = log_line
		self.get_domain()

		if not log_info['db_name']:
			return False

#		if not DomainDB.db_exists(log_info['db_name']):
#			return False

		if not self.get_remote_ip():
			return False

		myredis.redis_q.put('BiglogDomainDB',log_info['db_name'])
#		add_gearman_job("BigLogDomain",log_info['db_name'],wait_until_complete=False,background=True)
#		add_gearman_job("BigLogDomain",log_info['db_name'])
		
#		self.write_into_domain_file(self.log_line,log_info['db_name'])
		self.write_into_file(self.log_line,log_info['db_name'])

		time_index = self.get_time_now()
		log_info['time_key'] = log_info['time_minute']

		# split line into two parts
		former_line = self.log_line[:time_index]

		# len("[02/May/2013:17:42:31 +0800]") = 28
		later_line = self.log_line[time_index+29:]

		# get remote user
		log_info['remote_user'] = self.get_remote_user(former_line)

		# get request line
		code_index = self.get_request_line(later_line)

		referer_index = self.get_code_bw(later_line,code_index)
		referer_index = referer_index + code_index + 1

		agent_index = self.get_referer(later_line,referer_index)
		agent_index  = agent_index + referer_index + 3

		self.get_user_agent_extend(later_line,agent_index)

		return True
#		self.display_log_info()

	def get_domain(self):
		try:
			log_info['domain'] = self.log_line.split('&@&')[1].rstrip('\n')
			self.log_line = self.log_line.split('&@&')[0]
			log_info['db_name'] = log_info['domain'].replace(".","_").replace("-","_")
		except:
			print "[INFO ] : Domain invalid \n\'%s\'"%self.log_line
			log_info['domain'] = "-"
			log_info['db_name'] = ""

	def get_remote_ip(self):
		log_info['visitor_ip'] = re.findall(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', self.log_line)[0]

		ip_index = self.log_line.find(log_info['visitor_ip'])
		if ip_index < 0:
			return False
		self.log_line = self.log_line[ip_index:]
		return True

	def get_time_now(self):
		start = self.log_line.find("[")
		time_str = time.strftime(self.BASE_TIME_FORMAT,time.localtime(time.time()))
		log_info['time_minute'] = time_str
		log_info['time_unix_all'] = time.mktime(datetime.datetime.now().timetuple())
		log_info['time_record'] = log_info['time_unix_all']
		return start

	def get_remote_user(self,copy_line):
	#	return copy_line.split()[2]
		return "-"

	def get_request_line(self,copy_line):
		start = -1
		end = -1
		if "\"GET" in copy_line:
			start = copy_line.find("\"GET")
		elif "\"POST" in copy_line:
			start = copy_line.find("\"POST")
		elif "\"HEAD" in copy_line:
			start = copy_line.find("\"HEAD")

		if "HTTP/1.1\"" in copy_line:
			end = copy_line.find("HTTP/1.1\"")
		elif "HTTP/1.0\"" in copy_line:
			end = copy_line.find("HTTP/1.0\"")
		if start == -1 or end == -1:
			return -1
		# get request line
		request_line = copy_line[start+1:end+8]
		method,uri,version = request_line.split()[0],request_line.split()[1],request_line.split()[2]
		log_info['req_line'],log_info['method'],log_info['uri'],log_info['version'] = request_line,method,uri,version
		return end+10

	# get status code and body_bytes_sent
	def get_code_bw(self,copy_line,code_index):
		line_tmp = copy_line[code_index:]
		code_status = line_tmp.split()[0]
		req_size = int(line_tmp.split()[1])
		end = line_tmp.find("\"")
		log_info['status_code'],log_info['req_size'] = code_status,req_size
		return end

	def get_referer(self,copy_line,referer_index):
		referer = copy_line[referer_index:].split('\"')[0]
		end = len(referer)
		log_info['referer'] = referer
		return end

	def get_user_agent_extend(self,copy_line,agent_index):
		line_tmp = copy_line[agent_index:]
		user_agent = line_tmp.split('\"')[0]

		try :
			forwarded_for = line_tmp.split('\"')[2]
		except :
			forwarded_for = "-"

		try :
			hits = line_tmp.split('\"')[4]
		except :
			hits = "-"

		if "Windows" in user_agent or "windows" in user_agent:
			os_type = "Windows"
		elif "Macintosh" in user_agent or "macintosh" in user_agent:
			os_type = "Macintosh"
		elif "Linux" in user_agent or "linux" in user_agent:
			os_type = "Linux"
		elif "BSD" in user_agent:
			os_type = "BSD"
		elif "AIX" in user_agent:
			os_type = "AIX"
		else:
			os_type = "Others"

		if "MSIE" in user_agent :
			browser_type = "MSIE"
		elif "Firefox" in user_agent or "firefox" in user_agent:
			browser_type = "Firefox"
		elif "Chrome" in user_agent or "chrome" in user_agent:
			browser_type = "Chrome"
		elif "Camino" in user_agent or "camino" in user_agent:
			browser_type = "Camino"
		elif "Safari" in user_agent or "safari" in user_agent:
			browser_type = "Safari"
		elif "Opera" in user_agent or "opera" in user_agent:
			browser_type = "Opera"
		else:
			browser_type = "Others"

		log_info['user_agent'],log_info['os_type'],log_info['browser_type'],log_info['forwarded_for'],log_info['hits'] = user_agent,os_type,browser_type,forwarded_for,hits

	def display_log_info(self):
		print "time_local : %s"%log_info['time_key']
		print "visitor_ip : %s"%log_info['visitor_ip']
		print "remote_user : %s"%log_info['remote_user']
		print "request_line : %s"%log_info['req_line']
		print "status : %s"%log_info['status_code']
		print "body_bytes_sent : %d"%log_info['req_size']
		print "referer : %s"%log_info['referer']
		print "OS : %s"%log_info['os_type']
		print "browser : %s"%log_info['browser_type']
		print "forwarded_for : %s"%log_info['forwarded_for']
		print "hits : %s"%log_info['hits']
		print "domain : %s"%log_info['domain']
		print ""

	def write_into_domain_file(self,line,domain):
		log_name = "/home/logs/%s_access.log"%domain
		fd = open(log_name,'a')
		fd.write("%s\n"%line)
		fd.close()

	def write_into_file(self,line,domain):
		log_name = "/var/log/nginx_access.log"
		fd = open(log_name,'a')
		fd.write("%s &@&%s\n"%(line,domain))
		fd.close()

	def __clear__(self):
		log_info = {}
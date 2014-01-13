#!/usr/bin/env python2.6
#-*- coding: utf-8 -*-

# Author : firefoxbug
# E-Mail : wanghuafire@gmail.com
# Blog   : www.firefoxbug.net
# Function : biglog main start

import os
import sys
"""
sys.path.append("./recv")
from BigLogRecv import biglog_recv_input_log
sys.path.append("./daemon")
from BigLogDomain import domain_worker
sys.path.append("./daemon/geoip")
from BigLogGeoIP import geoip_worker
from BigLogMysql import mysql_worker
"""
'''
biglog结构体定义了biglog的日志输入端和输出端，输入端只能选择一个选项，输出端也只能选择一个选项
默认输入是udp 515端口

biglog {
#biglog输入端，udp和tcp只能选择一个，输入的类型也只能是一个
	input : {
		file : /var/log/nginx_access.log
		pipe : /tmp/cdn.pipe
		syslog : {
			udp : 515
			tcp : 515
		}
	}

#biglog输出端，如果是输出到mysql，那么需要配置mysql相关信息
	output : {
		mysql : {
			host = "127.0.0.1"
			username = "root"
			password = "biglog"
			port = 3306			
		}
		file {
			file = "/home/biglog_access.html"
		}
	}
}
'''	

class BigLog():
	"""biglog 主类"""
	def __init__(self	):
		self.child_process_pid = {"RECV":-1,"COLLECT":-1,"GeoIP":-1,"DOMAIN":-1,"MYSQL":[]}

		self.biglog = {}
		self.biglog["input"] = {}
		self.biglog["output"] = {}	
		self.biglog["input"]["syslog"] = {}
		self.biglog["input"]["syslog"]["udp"] = 515
		self.biglog["output"]["mysql"] = {}
		self.biglog["output"]["mysql"]["host"] = "127.0.0.1"
		self.biglog["output"]["mysql"]["port"] = 3306
		self.biglog["output"]["mysql"]["username"] = "root"
		self.biglog["output"]["mysql"]["password"] = "biglog"

	"""启动所有进程"""
	def start_work(self):
		"""启动IP地理位置查询进程"""
		self.start_GeoIP()
		self.parse_log_type()
		
		print "PID 			PorcessNmae"
		for key in self.child_process_pid:
			print self.child_process_pid[key],"			",key

	"""IP地理位置查询守护"""
	def start_GeoIP(self):
		pid = os.fork()
		if pid == 0:
			print "Starting GeoIP worker..."
			geoip_worker()
		else:
			self.child_process_pid["GeoIP"] = pid

	"""域名数据库建立守护"""
	def start_Domain(self,mysql_info):
		pid = os.fork()
		if pid == 0:
			print "Starting Domain worker..."
			domain_worker(mysql_info)
		else:
			self.child_process_pid["DOMAIN"] = pid		
	
	"""Mysql语句插入守护"""
	def start_Mysqlist(self,mysql_info):
		pid = os.fork()
		if pid == 0:
			print "Starting Mysqlist worker..."
			mysql_worker(mysql_info)
		else:
			self.child_process_pid["MYSQL"].append(pid)		

	"""日志接收模块守护"""
	def start_Recv(self,PORT):
		pid = os.fork()
		if pid == 0:
			print "Starting Mysqlist worker..."
			biglog_recv_input_log(PORT)
		else:
			self.child_process_pid["RECV"] = pid		

	"""解析输入和输出类型并且启动进程"""
	def parse_log_type(self):
		input_udp_port = 515
		if self.biglog["input"] == "file":
			print "Biglog input log type ==>> file"
		elif self.biglog["input"] == "pipe":
			print "Biglog input log type ==>> pipe"
		elif self.biglog["input"] == "syslog":
			print "Biglog input log type ==>> syslog"
			if self.biglog["input"]["syslog"]["udp"]:
				input_udp_port = self.biglog["input"]["syslog"]["udp"]
				"""启动日志接收模块"""
				self.start_Recv(input_udp_port)

		if self.biglog["output"] == "mysql":
			print "Biglog output log ==>> mysql"
			mysql_info = {"host":"127.0.0.1","port":3306,"username":"root","password":"biglogg"}
			for key in mysql_info.keys():
				mysql_info[key] = self.biglog["output"]["mysql"][key]
			
			"""启动域名查询进程"""
			self.start_Domain(mysql_info)

			"""启动Mysql插入进程"""
			self.start_Mysqlist(mysql_info)
		elif self.biglog["output"] == "file":
			print "Biglog output log ==>> file"

"""解析biglog配置文件"""
def parse_biglog_conf():
#	self.work_dir = "/usr/local/biglog/conf/"
	#不是在本文件中调用
	work_dir = "../conf/"
	conf_dir = work_dir + "biglog.conf"
	conf_tmp = work_dir + ".biglog.conf.bak"
	#定义一个栈
	stack = []
	#去除#开头的注释和空行
	grep_cmd = "grep -v -E '^$|^#' %s > %s"%(conf_dir,conf_tmp)
#		print grep_cmd
	os.system(grep_cmd)

	fd = open(conf_tmp)
	line = "biglog"
	input_info = {}
	while line:
		line = fd.readline()
		if "input" in line:
			while True:
				if "udp" not in line:
					line = fd.readline()
					continue
				try:
					udp_input_port = int(line.split('=')[1])
					input_info["udp_port"] = udp_input_port
				except Exception, e:
					raise e
				break
		elif "mysql" in line :
			while True:
				line = fd.readline()
				if "}" in line:
					break 
				try:
					key = line.split('=')[0].strip()
					value = line.split('=')[1].strip()
					input_info[key] = value
				except Exception, e:
					raise e
	return input_info

def main():
	parse_biglog_conf()	
#	biglog_i = BigLog()
#	biglog_i.parse_biglog_conf()
#	biglog_i.start_work()
#	print biglog

def read_biglog_conf():

	pass

if __name__ == '__main__':
	main()
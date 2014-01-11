#!/usr/bin/env python2.6
#-*- coding: utf-8 -*-

# Author : firefoxbug
# E-Mail : wanghuafire@gmail.com
# Blog   : www.firefoxbug.net
# Function : biglog main start

import os


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

class ParseConf(object):
	def __init__(self):
	#	self.work_dir = "/usr/local/biglog/conf/"
		self.work_dir = "./conf/"
		self.conf_dir = self.work_dir + "biglog.conf"
		self.conf_tmp = self.work_dir + ".biglog.conf.bak"
		self.biglog = {}
		self.biglog["input"] = {}
		self.biglog["output"] = {}

	def parse_conf(self):
		#定义一个栈
		stack = []
		
		#去除#开头的注释和空行
		grep_cmd = "grep -v -E '^$|^#' %s > %s"%(self.conf_dir,self.conf_tmp)
#		print grep_cmd
		os.system(grep_cmd)

		fd = open(self.conf_tmp)
		while True:
			line = fd.readline()
			break					

		self.biglog["input"]["syslog"] = {}
		self.biglog["input"]["syslog"]["udp"] = 515
		self.biglog["output"]["mysql"] = {}
		self.biglog["output"]["mysql"]["host"] = "127.0.0.1"
		self.biglog["output"]["mysql"]["port"] = 3306
		self.biglog["output"]["mysql"]["username"] = "root"
		self.biglog["output"]["mysql"]["password"] = "biglog"

		return self.biglog

	def get_mysql_info(self):
		self.biglog["output"]["mysql"] = {}

'''解析日志输入和输出方式'''
def parse_input_log_type(biglog):


def main():
	parse_conf_i = ParseConf()
	biglog = parse_conf_i.parse_conf()
	parse_input_log_type(biglog)
#	print biglog


if __name__ == '__main__':
	main()
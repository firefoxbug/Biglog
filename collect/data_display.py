#!/usr/bin/env python2.6
#-*- coding: utf-8 -*-

# Author : firefoxbug
# E-Mail : wanghuafire@gmail.com
# Blog   : www.firefoxbug.net

#from data_record import RecordLogInfo

import time
import operator
import uuid
import MySQLdb
import json
import socket
import operator
import sys
import gearman
sys.path.append("../")
import biglog_mysql
import myredis

import biglog_addjob
unit_summary = {}
unit_summary['unique_ip'] = 0
unit_summary['referer'] = 0

insert_time = ""
gearman_client = ""
biglog_sql = ""

class SendSQLCMD(object):
	def __init__(self,ip='127.0.0.1',port=513):
		"""send logs by tcp socket in chosen port.default tcp 513"""
		# addressing information of target
		self.addr = (ip,port)
		# initialize a socket, think of it as a cable
		try :
			self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
		except socket.error, msg :
			print '[ERROR ] : Failed to send log '
			print str(msg)

		try :
			self.s.connect(self.addr)
		except socket.error, msg :
			print 'Failed to Connect . Error Code : ' + str(msg[0]) + ' Message ' + msg[1]

	def send_sqlcmd(self,data2send):
		data2send = self.json_decode(data2send)
		self.s.send(data2send)

	def json_decode(self,data):
		return json.dumps(data)

	def disconnect(self):
		self.s.close()

class DisplayLogs():
	@classmethod
	def display_log_summary(self,log,log_key,insert_log_time):
		if not log:
			return
		global insert_time
		insert_time = insert_log_time
#		self.join_gearman()
#		global biglog_sql
#		biglog_sql = SendSQLCMD()

		print "\n-----------------",insert_time['time_str'],"-----------------\n"

		for domain in log.keys():
			print "\n%-20s %-10s"%("DOMAIN","BW")
			print "%-20s %-10s"%(domain,self.sizeof_fmt(log[domain][log_key['KEY_BANDWIDTH']]))

			uniq_ip = len(log[domain][log_key['KEY_IP']].keys())
			unit_summary['unique_ip'] += uniq_ip
			
			# count referer numbers
			refer_cnt = len(log[domain][log_key['KEY_REFERER']].keys())
			unit_summary['referer'] += refer_cnt

			self.display_unit_detail(log,domain,log_key)

#		biglog_sql.disconnect()

	@classmethod
	def display_unit_detail(self,log,domain,log_key):

		self.display_ip_info(log,domain,log_key['KEY_IP'])
#		self.display_request_bw(log,domain,log_key['KEY_IP'])
		self.display_request_bw(log,domain,log_key['KEY_REQUEST'])
		self.display_request_bw(log,domain,log_key['KEY_STATIC_FILE'])
		self.display_request_bw(log,domain,log_key['KEY_STATUS_CODE'],False)
		self.display_request_bw(log,domain,log_key['KEY_REQUEST_NOT_FOUND'],False)
		self.display_request_bw(log,domain,log_key['KEY_REFERER'],False)	
		self.display_request_bw(log,domain,log_key['KEY_BROWSER'],False)
		self.display_request_bw(log,domain,log_key['KEY_OS_TYPE'],False)
	
	'''display ip and location'''
	@classmethod
	def display_ip_info(self,log,domain,log_type):
#		self.join_gearman()
		global geo_ip_search_ins
#		global biglog_sql

		db_name = domain.replace(".","_").replace("-","_")
		request_dic = {}
		bw_dic = {}
		for item in log[domain][log_type].keys():
			req_count = log[domain][log_type][item]['req_count']
			bandwidth = log[domain][log_type][item]['bandwidth']
			request_dic[item] = req_count
			bw_dic[item] = bandwidth
		request_list = sorted(request_dic.iteritems(), key=operator.itemgetter(1), reverse=True)
		bw_list = sorted(bw_dic.iteritems(), key=operator.itemgetter(1), reverse=True)
		request_all = self.get_all_requests(request_list)
		ip_values_list = []
		for item in request_list:
			ip_key = item[0]
			request_count = item[1]
			percent = self.get_percent(request_all,request_count)
			req_size = log[domain][log_type][ip_key]['bandwidth']
#			ip_location = self.search_ip(str(ip_key))
			ip_location = biglog_addjob.search_ip(str(ip_key))
			values = self.summary_log_visitor_ip_sql(db_name,log_type,ip_key,percent,request_count,req_size,ip_location)
			ip_values_list.append(values)

		insert_log_cmd = "insert into %s.%s (_date,_time,unit,%s,percent,request_count,bandwidth,unix_time,country_code,country_desc,region,city,net) values "%(db_name,log_type,log_type)
		insert_log_cmd = insert_log_cmd + "(%s, %s, 'second', %s,%s,%s,%s,%s,%s,%s,%s,%s,%s);"
		sql_dic = {}
		sql_dic['sql'] = insert_log_cmd
		sql_dic['args'] = ip_values_list
		myredis.redis_q.put('BiglogSqlList',json.dumps(sql_dic))
#		biglog_mysql.mysql_instance.insert_many_log(insert_log_cmd,ip_values_list)
#			biglog_mysql.mysql_instance.insert_log(sql_cmd)
#			biglog_sql.send_sqlcmd(sql_cmd)

	@classmethod 
	def join_gearman(self):
		global gearman_client
		try :
			gearman_client = gearman.GearmanClient(['127.0.0.1'])
		except Exception,e:
			print "[ERROR GEARMAN]: %s"% (time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time())))
			print "%s\n"%(str(e))

	@classmethod
	def search_ip(self,ip):
		global gearman_client
		try :
			res = gearman_client.submit_job('BigLogGeo',ip)
			return json.loads(res.result)
		except Exception,e:
			print "[ERROR SEARCH_IP %s]: ERROR IP:%s [INFO %s]"% (time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time())),ip,str(e))
			return ["","","","","","",""]

	@classmethod
	def add_sqls_job(self,sql_cmd):
		global gearman_client
		try :
			gearman_client.submit_job('BigLogMysql',json.dumps(sql_cmd),background=True)
			return True
		except Exception,e:
			print "[ERROR TOMYSQL %s]: [INFO %s] %s"% (time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time())),str(e),sql_cmd)
			return False

	@classmethod		
	def display_request_bw(self,log,domain,log_type,bw_flag = True):
		global biglog_sql

		db_name = domain.replace(".","_").replace("-","_")
		values_list = []

		if bw_flag:
			# include bandwidth
			request_dic = {}
			bw_dic = {}
			for item in log[domain][log_type].keys():
				req_count = log[domain][log_type][item]['req_count']
				bandwidth = log[domain][log_type][item]['bandwidth']
				request_dic[item] = req_count
				bw_dic[item] = bandwidth
			request_list = sorted(request_dic.iteritems(), key=operator.itemgetter(1), reverse=True)
			bw_list = sorted(bw_dic.iteritems(), key=operator.itemgetter(1), reverse=True)

			request_all = self.get_all_requests(request_list)
#			print "\n[%-9s %-10s %-10s %s]"%("Request","Percent","bandwidth",log_type.upper())
			
			for item in request_list[:20]:
				key_log_type = item[0]
				request_count = item[1]
				percent = self.get_percent(request_all,request_count)
				req_size = log[domain][log_type][key_log_type]['bandwidth']
			
#				print "%-10s %-10s %-10s %s"%(request_count,percent,self.sizeof_fmt(req_size),key_log_type)
				values = self.summary_log_bw_sql(db_name,log_type,key_log_type,percent,request_count,req_size)
				values_list.append(values)
#				biglog_sql.send_sqlcmd(sql_cmd)
#				biglog_mysql.mysql_instance.insert_log(sql_cmd)
			insert_log_cmd = '''insert into %s.%s (_date,_time,unit,%s,percent,request_count,bandwidth,unix_time) values '''%(db_name,log_type,log_type)
			insert_log_cmd = insert_log_cmd + "(%s,%s,%s,%s,%s,%s,%s,%s);"

		else:
			request_list = sorted(log[domain][log_type].iteritems(), key=operator.itemgetter(1), reverse=True)
		
			request_all = self.get_all_requests(request_list)

#			print "\n[%-9s %-10s %s]"%("Request","Percent",log_type.upper())
			for item in request_list[:20]:
				key_log_type = item[0]
				request_count = item[1]
				percent = self.get_percent(request_all,request_count)

				# composite sql statement
				values = self.summary_log_sql(db_name,log_type,key_log_type,percent,request_count)
				values_list.append(values)
#				biglog_sql.send_sqlcmd(sql_cmd)
#				biglog_mysql.mysql_instance.insert_log(sql_cmd)
#				print "%-10s %-10s %s"%(request_count,self.get_percent(request_all,request_count),key_log_type)
			insert_log_cmd = '''insert into %s.%s (_date,_time,unit,%s,percent,request_count,unix_time) values '''%(db_name,log_type,log_type)
			insert_log_cmd = insert_log_cmd + "(%s,%s,%s,%s,%s,%s,%s);"

		sql_dic = {}
		sql_dic['sql'] = insert_log_cmd
		sql_dic['args'] = values_list
	#	biglog_mysql.mysql_instance.insert_many_log(insert_log_cmd,values_list)
		myredis.redis_q.put('BiglogSqlList',json.dumps(sql_dic))

	# count all request numbers
	@classmethod
	def get_all_requests(self,req_list):
		req_count = 0
		for item in req_list:
			request_count = item[1]
			req_count += request_count
		return req_count

	@classmethod
	def sizeof_fmt(self,num):
		for x in ['Byte','kByte','MByte', 'GByte', 'TByte', 'PByte', 'EByte', 'ZByte', 'YByte']:
			if num < 1024.0:
				return "%3.2f %s" % (num, x)
			num /= 1024.0

	@classmethod
	def get_percent(self,request_all,request_count):
		return "%2.2f%%"%(float(request_count)/request_all * 100)

	@classmethod
	def summary_log_bw_sql(self,db_name,log_type,log_type_value,percent,req_cnt,bw):
		global insert_time
		time_str = insert_time['time_str']
		date,time_str = time_str.split(':')[0],time_str[11:]
		unix_time = str(int(insert_time['time_num']))

#		insert_log_cmd = "insert into %s.%s (_date,_time,unit,%s,percent,request_count,bandwidth,unix_time)values('%s', '%s', '%s', '%s','%s','%s','%s','%s');"%(db_name,log_type,log_type,date,time_str,insert_time['UNIT'],MySQLdb.escape_string(log_type_value),percent,req_cnt,bw,unix_time)
#		print insert_log_cmd
#		self.add_sqls_job(insert_log_cmd)
#		myredis.redis_q.put('BiglogSql',insert_log_cmd)
		return (date,time_str,insert_time['UNIT'],MySQLdb.escape_string(log_type_value),percent,req_cnt,bw,unix_time)

	@classmethod
	def summary_log_sql(self,db_name,log_type,log_type_value,percent,req_cnt):
		global insert_time
		time_str = insert_time['time_str']
		date,time_str = time_str.split(':')[0],time_str[11:]
		unix_time = str(int(insert_time['time_num']))
#		insert_log_cmd = "insert into %s.%s (_date,_time,unit,%s,percent,request_count,unix_time) values ('%s', '%s', '%s', '%s','%s','%s','%s');"%(db_name,log_type,log_type,date,time_str,insert_time['UNIT'],MySQLdb.escape_string(log_type_value),percent,req_cnt,unix_time)
#		print insert_log_cmd
#		self.add_sqls_job(insert_log_cmd)
#		myredis.redis_q.put('BiglogSql',insert_log_cmd)
		return (date,time_str,insert_time['UNIT'],MySQLdb.escape_string(log_type_value),percent,req_cnt,unix_time)
		
	@classmethod
	def summary_log_visitor_ip_sql(self,db_name,log_type,log_type_value,percent,req_cnt,bw,ip_location):
		global insert_time
		time_str = insert_time['time_str']
		date,time_str = time_str.split(':')[0],time_str[11:]
		unix_time = str(int(insert_time['time_num']))
#		insert_log_cmd = "insert into %s.%s (_date,_time,unit,%s,percent,request_count,bandwidth,unix_time,country_code,country_desc,region,city,net) values ('%s', '%s', 'monitue', '%s','%s','%s','%s','%s','%s','%s','%s','%s','%s');"%(db_name,log_type,log_type,date,time_str,MySQLdb.escape_string(log_type_value),percent,req_cnt,bw,unix_time,ip_location['country_code'],ip_location['country_desc'],ip_location['region'],ip_location['city'],ip_location['net'])
#		print insert_log_cmd
#		self.add_sqls_job(insert_log_cmd)
#		myredis.redis_q.put('BiglogSql',insert_log_cmd)
		return (date,time_str,MySQLdb.escape_string(log_type_value),percent,req_cnt,bw,unix_time,ip_location['country_code'],ip_location['country_desc'],ip_location['region'],ip_location['city'],ip_location['net'])
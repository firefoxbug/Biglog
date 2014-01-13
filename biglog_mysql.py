#!/usr/bin/env python2.6
#-*- coding: utf-8 -*-

import os
import sys
import MySQLdb

mysql_instance = ""

class MySQLHelper:
	def __init__(self,host,user,password,charset="utf8"):
		self.host = host
		self.user = user
		self.password = password
#		self.db_name = db_name
		self.charset = charset
		try:
			self.conn = MySQLdb.connect(host=self.host,user=self.user,passwd=self.password, charset=self.charset)
			self.conn.ping(True)
		except:
			print("Mysql Connect Error ")
			sys.exit(0)

	def insert_log(self,sql_cmd):
		self.cur = self.conn.cursor()
		try :
			self.conn.autocommit(False)
			self.cur.execute(sql_cmd)
			self.conn.commit()
			self.cur.close()
			return True
		except Exception,e:
			print "[MYSQL ERROR] : %s"%sql_cmd
			print "[INFO] : %s\n"%(str(e))
			self.cur.close()
			return False

	def insert_many_log(self,sql,values):
		self.cur = self.conn.cursor()
		try :
#			self.conn.autocommit(False)
			self.cur.executemany(sql,values)
			self.conn.commit()
			self.cur.close()
			return True
		except Exception,e:
			print "[MYSQL ERROR] : %s"%sql
			print "[INFO] : %s\n"%(str(e))
			self.cur.close()
			return False

	def db_exists(self,sql_cmd):
		try :
			self.cur = self.conn.cursor()
			self.cur.execute(sql_cmd)
			sql_results = self.cur.fetchone()
			#print sql_results[0]
			self.cur.close()
		 	if 1==sql_results[0]:
		 		return True
		 	else:
		 		return False
		except :
			print "[MYSQL ERROR] : %s"%sql_cmd
			self.cur.close()
			return True

	def run_sql_cmd(self,sql_cmd):
		try :
			self.cur = self.conn.cursor()
			self.cur.execute(sql_cmd)
			self.cur.close()
		except Exception, e:
			print "[MYSQL ERROR] : %s"%sql_cmd
			self.cur.close()

	def close(self):
		self.conn.close()

def mysql_init(mysql_host='127.0.0.1',mysql_username='root',mysql_password='zooboa'):
	try:
		from biglog_conf import parse_biglog_conf
		input_info = parse_biglog_conf()
		mysql_host = input_info['host']
		mysql_username = input_info['username']
		mysql_password = input_info['password']
	except Exception, e:
		raise e

	try:
		global mysql_instance
		mysql_instance = MySQLHelper(mysql_host,mysql_username,mysql_password)		
	except Exception, e:
		print("Mysql Error %d: %s" % (e.args[0], e.args[1]))
		sys.exit(1)

if __name__ == '__main__':
	mysql_init(mysql_host='127.0.0.1',mysql_username='root',mysql_password='zooboa.com')
	fd = open("10000.txt")
	while True:
		sql_cmd = fd.readline()
		mysql_instance.insert_log(sql_cmd)
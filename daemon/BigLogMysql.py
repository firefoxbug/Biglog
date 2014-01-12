#!/usr/bin/env python2.6
#-*- coding: utf-8 -*-

# Author : firefoxbug
# E-Mail : wanghuafire@gmail.com
# Blog   : www.firefoxbug.net
# Function : read mysql statements from gearman and parse 

import sys
sys.path.append("../")
import time
import json
import gearman
import biglog_mysql
from biglog_mysql import mysql_init
import biglog_redis

class CustomGearmanWorker(gearman.GearmanWorker):
	def on_job_execute(self, current_job):
#		print "Job started"
		return super(CustomGearmanWorker, self).on_job_execute(current_job)

	def on_job_exception(self, current_job, exc_info):
		print "[ERROR] : %s mysql=%s"%(current_job.task,current_job.data)
		for item in exc_info[1]:
			print str(item)+'\n'
		return super(CustomGearmanWorker, self).on_job_exception(current_job, exc_info)

	def on_job_complete(self, current_job, job_result):
#		print "[OK] : %s site_id=%s"%(current_job.task,current_job.data)
		return super(CustomGearmanWorker, self).send_job_complete(current_job, job_result)

	def after_poll(self, any_activity):
		# Return True if you want to continue polling, replaces callback_fxn
		return True

def toSql(gearman_worker, job):
	sql_cmd = json.loads(job.data)
	biglog_mysql.mysql_instance.insert_log(sql_cmd)
	return "True"

def gearman_logs2sql():
	try :
		new_worker = CustomGearmanWorker(['127.0.0.1'])
	except Exception,e:
		print "[ERROR GEARMAN]: %s"% (time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time())))
		print "%s\n"%(str(e))
		sys.exit(1)
	mysql_init()
	new_worker.register_task("BigLogMysql",toSql)
	new_worker.work()

def redis_logs2sql():
	mysql_init()
	biglog_redis.connect2redis(host='127.0.0.1')
	while True:
		sql_cmd = biglog_redis.redis_q.get('BiglogSql')
		biglog_mysql.mysql_instance.insert_log(sql_cmd)

def mysql_worker(mysql_info):
	mysql_init(mysql_info['host'],mysql_info['username'],mysql_info['password'])
	biglog_redis.connect2redis(host='127.0.0.1')
	while True:
		sql_str = biglog_redis.redis_q.get('BiglogSqlList')
		sql_dic = json.loads(sql_str)
		sql = sql_dic['sql']
		args = sql_dic['args']
		biglog_mysql.mysql_instance.insert_many_log(sql,args)

if __name__ == '__main__':
#	gearman_logs2sql()
#	redis_logs2sql
	mysql_worker(mysql_info)

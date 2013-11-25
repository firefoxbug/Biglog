#!/usr/bin/env python2.6
#-*- coding: utf-8 -*-

# Author : firefoxbug
# E-Mail : wanghuafire@gmail.com
# Blog   : www.firefoxbug.net
# Function : read from gearman and create database

import sys
sys.path.append("../")
sys.path.append("../recv")
import time
import json
import gearman

from biglog_mysql import mysql_init
from log_mysql import DomainDB

import myredis

class CustomGearmanWorker(gearman.GearmanWorker):
	def on_job_execute(self, current_job):
#		print "Job started"
		return super(CustomGearmanWorker, self).on_job_execute(current_job)

	def on_job_exception(self, current_job, exc_info):
		print "[ERROR] : %s db_name=%s"%(current_job.task,current_job.data)
		for item in exc_info[1]:
			print str(item)+'\n'
		return super(CustomGearmanWorker, self).on_job_exception(current_job, exc_info)

	def on_job_complete(self, current_job, job_result):
#		print "[OK] : %s site_id=%s"%(current_job.task,current_job.data)
		return super(CustomGearmanWorker, self).send_job_complete(current_job, job_result)

	def after_poll(self, any_activity):
		# Return True if you want to continue polling, replaces callback_fxn
		return True

def create_db(gearman_worker, job):
	db_name = json.loads(job.data)
#	print db_name['db_name']
	if not DomainDB.db_exists(db_name):
#		print "[ERROR GEARMAN %s]: [moudle:log_db] [create %s failured]"% (time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time())),db_name)
		return "False"
	return "True"

"""read from gearman and create database"""
def gearman_worker():
	try :
		new_worker = CustomGearmanWorker(['127.0.0.1'])
	except Exception,e:
		print "[ERROR GEARMAN]: %s"% (time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time())))
		print "%s\n"%(str(e))
		sys.exit(1)

	mysql_init()
	new_worker.register_task("BigLogDomain",create_db)
	new_worker.work()

def redis_worker():
	myredis.connect2redis(host='127.0.0.1')
	mysql_init()
	while True:
		db_name = myredis.redis_q.get('BiglogDomainDB')
		DomainDB.db_exists(db_name)

if __name__ == '__main__':
	redis_worker()
#	gearman_worker()

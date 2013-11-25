#!/usr/bin/env python2.6
#-*- coding: utf-8 -*-

# Author : firefoxbug
# E-Mail : wanghuafire@gmail.com
# Blog   : www.firefoxbug.net
# Function : read log dic from gearman and parse 

import sys
sys.path.append("../")
sys.path.append("../collect")
import time
import json
import gearman

from data_record import RecordLogInfo
biglog_rl = ""

class CustomGearmanWorker(gearman.GearmanWorker):
	def on_job_execute(self, current_job):
#		print "Job started"
		return super(CustomGearmanWorker, self).on_job_execute(current_job)

	def on_job_exception(self, current_job, exc_info):
		print "[ERROR] : %s log_info=%s"%(current_job.task,current_job.data)
		for item in exc_info[1]:
			print str(item)+'\n'
		return super(CustomGearmanWorker, self).on_job_exception(current_job, exc_info)

	def on_job_complete(self, current_job, job_result):
#		print "[OK] : %s site_id=%s"%(current_job.task,current_job.data)
		return super(CustomGearmanWorker, self).send_job_complete(current_job, job_result)

	def after_poll(self, any_activity):
		# Return True if you want to continue polling, replaces callback_fxn
		return True

def collect(gearman_worker, job):
	global biglog_rl
	log_info = json.loads(job.data)
	biglog_rl.record_log_info(log_info)
	return "True"

def collect_log():
	try :
		new_worker = CustomGearmanWorker(['127.0.0.1'])
	except Exception,e:
		print "[ERROR GEARMAN]: %s"% (time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time())))
		print "%s\n"%(str(e))
		sys.exit(1)
	global biglog_rl

	biglog_rl = RecordLogInfo()
	new_worker.register_task("BigLogCollect",collect)
	new_worker.work()

if __name__ == '__main__':
	collect_log()

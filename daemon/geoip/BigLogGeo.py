#!/usr/bin/python
# -*- coding: UTF-8 -*-

# author : firefoxbug
# E-Mail : wanghuafire@gmail.com
# Blog   : www.firefoxbug.net

import gearman
import time

import math
import json

from geo_man import init_geoip
import geo_man

class CustomGearmanWorker(gearman.GearmanWorker):
	def on_job_execute(self, current_job):
#		print "Job started"
		return super(CustomGearmanWorker, self).on_job_execute(current_job)

	def on_job_exception(self, current_job, exc_info):
		print "[ERROR] : %s site_id=%s"%(current_job.task,current_job.data)
		for item in exc_info[1]:
			print str(item)+'\n'
		return super(CustomGearmanWorker, self).on_job_exception(current_job, exc_info)

	def on_job_complete(self, current_job, job_result):
#		print "[OK] : %s site_id=%s"%(current_job.task,current_job.data)
		return super(CustomGearmanWorker, self).send_job_complete(current_job, job_result)

	def after_poll(self, any_activity):
		# Return True if you want to continue polling, replaces callback_fxn
		return True

def geo_search(gearman_worker, job):
#	ip = json.loads(job.data)
	try :
		ip = job.data
		location = geo_man.geo_ip_search_ins.search_ip_country_city(ip)
		ip_location = geo_man.geo_ip_search_ins.get_summary_ip(location)
		results = json.dumps(ip_location)
		return results
	except :
		return json.dumps(dict(country_code="",country_desc="",region="",city="",net=""))
#	print results
	

def main():
	try :
		new_worker = CustomGearmanWorker(['127.0.0.1'])
	except Exception,e:
		print "[ERROR GEARMAN]: %s"% (time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time())))
		print "%s\n"%(str(e))
		sys.exit(1)
	init_geoip()

	new_worker.register_task("BigLogGeo", geo_search)
	new_worker.work()

if __name__ == '__main__':
	main()
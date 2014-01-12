#!/usr/bin/env python2.6
#-*- coding: utf-8 -*-

# Author : firefoxbug
# E-Mail : wanghuafire@gmail.com
# Blog   : www.firefoxbug.net
# Function : add one job to gearmand

import sys
import time
import json
import gearman

gearman_client = ""

def connect2gearman():
	try :
		global gearman_client
		gearman_client = gearman.GearmanClient(['127.0.0.1'])
	except Exception,e:
		print "[ERROR GEARMAN]: %s"% (time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time())))
		print "%s\n"%(str(e))
		sys.exit(1)

def add_gearman_job(module,data,background_flag=True):
	global gearman_client
	try :
		gearman_client.submit_job(module,json.dumps(data),background=background_flag)
	except Exception, e:
		print "[ERROR GEARMAN %s]: [module:%s] [data:%s]"% (time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time())),module,data)
		print "%s\n"%(str(e))		

def search_ip(ip):
	global gearman_client
	try :
		res = gearman_client.submit_job('BigLogGeo',ip,poll_timeout=2)
		return json.loads(res.result)
	except Exception,e:
		print "[ERROR SEARCH_IP %s]: ERROR IP:%s [INFO %s]"% (time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time())),ip,str(e))
		return ["","","","","","",""]	
	

if __name__ == '__main__':
	connect2gearman()
	

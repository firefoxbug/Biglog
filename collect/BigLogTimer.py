#!/usr/bin/env python2.6
#-*- coding: utf-8 -*-

# Author : firefoxbug
# E-Mail : wanghuafire@gmail.com
# Blog   : www.firefoxbug.net

import os
import sys
import threading
import signal
import json
import time
import datetime
sys.path.append("../")
import biglog_redis
from data_record import RecordLogInfo
from data_display import DisplayLogs
from biglog_addjob import connect2gearman

biglog_rl = ""
time_str = ""
time_unix = ""

class Watcher:
	def __init__(self):
		""" Creates a child thread, which returns.  The parent
			thread waits for a KeyboardInterrupt and then kills
			the child thread.
		"""
		self.child = os.fork()
		if self.child == 0:
			return
		else:
			self.watch()
 
	def watch(self):
		try:
			os.wait()
		except KeyboardInterrupt:
			print ' exit...'
			self.kill()
		sys.exit()
 
	def kill(self):
		try:
			os.kill(self.child, signal.SIGKILL)
		except OSError:
			pass

class BiglogTimer(threading.Thread): #The BiglogTimer class is derived from the class threading.Thread
	def __init__(self):
		threading.Thread.__init__(self)
		self.thread_stop = False
  
	def run(self): #Overwrite run() method, put what you want the thread do here
		global biglog_rl
		while not self.thread_stop:
			data = biglog_redis.redis_q.get('BiglogDict')
			log_info = json.loads(data)
#			print log_info
			biglog_rl.record_log_info(log_info)
#		print "exit..."

	def _stop(self):
		global time_str 
		global time_unix
		self.thread_stop = True
#		print biglog_rl.log
		insert_log_time = {}
		insert_log_time['time_str'] = time_str
		insert_log_time['time_num'] = time_unix
		insert_log_time['UNIT'] = 'second'

		#时间一到，就进行统计，对这段时间内的日志统计进行呈现或者把sql语句导入redis
		DisplayLogs.display_log_summary(biglog_rl.log,biglog_rl.log_key,insert_log_time)
		biglog_rl._clear()

if __name__ == '__main__':
	Watcher()
	connect2gearman()
	biglog_redis.connect2redis(host='127.0.0.1')
	biglog_rl = RecordLogInfo()
	while True:
		time_str = time.strftime('%Y-%m-%d:%H:%M:%S',time.localtime(time.time()))
		time_unix = int(time.mktime(datetime.datetime.now().timetuple()))
		thread1 = BiglogTimer()
		thread1.start()
		time.sleep(10)
		thread1._stop()

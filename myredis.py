#!/usr/bin/env python2.6
#-*- coding: utf-8 -*-

# Author : firefoxbug
# E-Mail : wanghuafire@gmail.com
# Blog   : www.firefoxbug.net
# Function : put or get log dictionary from redis-server

import redis  

global redis_q

class RedisQueue(object):  
	"""Simple Queue with Redis Backend"""  
	def __init__(self,**redis_kwargs):  
		"""The default connection parameters are: host='localhost', port=6379, db=0"""  
		self.__db= redis.Redis(**redis_kwargs)  
#		self.key = '%s:%s' %(namespace, name)  

	def qsize(self,key):
		"""Return the approximate size of the queue."""  
		return self.__db.llen(key)

	def empty(self):  
		"""Return True if the queue is empty, False otherwise."""  
		return self.qsize() == 0  
  
	def put(self,key,item):  
		"""Put item into the queue."""  
		self.__db.rpush(key, item)  

	def get(self,key,block=True, timeout=None):  
		"""Remove and return an item from the queue.  
 
		If optional args block is true and timeout is None (the default), block 
		if necessary until an item is available."""  
		if block:  
			item = self.__db.blpop(key, timeout=timeout)  
		else:  
			item = self.__db.lpop(key)  

		if item:  
			item = item[1]  
		return item  
  
	def get_nowait(self):  
		"""Equivalent to get(False)."""  
		return self.get(False) 

def connect2redis(host='127.0.0.1'):
	global redis_q
	redis_q = RedisQueue()

if __name__ == '__main__':
	redis_q = RedisQueue(host='127.0.0.1')
	i = 0
	while True:
		print redis_q.get('test2')

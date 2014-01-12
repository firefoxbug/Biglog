#!/usr/bin/python
# -*- coding: UTF-8 -*-

# author : firefoxbug
# E-Mail : wanghuafire@gmail.com
# Blog   : www.firefoxbug.net

import gearman
import time

import math
import json

import sys
import socket
import struct
import linecache
import operator

geo_ip_search_ins = ""

class BigLog_GeoIP(object):
	"""search ip geography"""
	def __init__(self):
		self.work_dir = "./"
		self.ip_to_city = self.work_dir + "geoip/ip_to_city.txt"
		self.ip_to_country = self.work_dir + "geoip/ip_to_country.txt"

		self.ip_city_map = {}
		self.ip_city_list =[]

		self.ip_country_map = {}
		self.ip_country_list=[]
		
		self.read_city_database()
		self.read_country_database()

	'''read geo city database'''
	def read_city_database(self):
		'''read city database and country database into memory'''
		try:
			fd_city = open(self.ip_to_city)
		except IOError:
			print "ERROR : Open geography city database file failured!"
			return
		line = fd_city.readline()
		while line:
			start_ip_str = line.split('|')[0]
			end_ip_str = line.split('|')[1].split(':')[0]
			start_ip = struct.unpack("!L",socket.inet_aton(start_ip_str))[0]
			end_ip = struct.unpack("!L",socket.inet_aton(end_ip_str))[0]
			self.ip_city_map[start_ip] = end_ip
			line = fd_city.readline()
		fd_city.close()
		self.ip_city_list = sorted(self.ip_city_map.keys())

	'''read geo country database'''	
	def read_country_database(self):
		try:
			fd_conutry = open(self.ip_to_country)
		except IOError:
			print "[ERROR] : Open geography country database file failured !"
			return
		'''read ip-to-country.txt into list'''
		line = fd_conutry.readline()
		while line:
			start_ip = long(line.split('|')[0])
			end_ip = long(line.split('|')[1])
			self.ip_country_map[start_ip] = end_ip
			line = fd_conutry.readline()
		fd_conutry.close()
		self.ip_country_list = sorted(self.ip_country_map.keys())

	def BinarySearch(self,keyTime,List):
		low = 0
		high = len(List) - 1
		middle = 0

		while(low <= high):
			middle = int((low + high) / 2)
			listTime = List[middle]
			if listTime == keyTime:
				return middle
				break
			elif listTime < keyTime:
				low = middle + 1
			elif listTime > keyTime:
				high = middle - 1

			if high < 0:
	#           print 'not in list'
				return -1
			elif low > len(List) - 1:
	#           print 'over list'
				return -1
		return high

	'''search ip's city '''	
	def search_ip_city(self,ip_to_search):
		'''args : list of ip to search'''
		ip_geo_line = ["","","","","","",""]
		ip_to_search = struct.unpack("!L",socket.inet_aton(ip_to_search))[0]
		index_city = self.BinarySearch(ip_to_search,self.ip_city_list)
		if index_city == -1:
			return ip_geo_line
		if ip_to_search <= self.ip_city_map[self.ip_city_list[index_city]]:
			ip_city_line = linecache.getline(self.ip_to_city,index_city+1)
			country = ip_city_line.split('|')[1].split(':')[1]
			region = ip_city_line.split('|')[2]
			city = ip_city_line.split('|')[3]
			net = ip_city_line.split('|')[5]
			ip_geo_line = ['','','',country,region,city,net]
			return ip_geo_line
		return ip_geo_line

	'''search ip's country and city '''	
	def search_ip_country_city(self,ip_to_search):
		'''args : list of ip to search'''

		ip_geo_line = ["","","","","","",""]
		ip_to_search = struct.unpack("!L",socket.inet_aton(ip_to_search))[0]
		index_city =  self.BinarySearch(ip_to_search,self.ip_city_list)
		if index_city == -1:
			return ip_geo_line
		if ip_to_search <= self.ip_city_map[self.ip_city_list[index_city]]:
			ip_city_line = linecache.getline(self.ip_to_city,index_city+1)
	#		print ip_city_line
			country = ip_city_line.split('|')[1].split(':')[1]
			region = ip_city_line.split('|')[2]
			city = ip_city_line.split('|')[3]
			net = ip_city_line.split('|')[5]
			ip_geo_line = ['','','',country,region,city,net]
			return ip_geo_line
		else :
			index_country = self.BinarySearch(ip_to_search,self.ip_country_list)
			if index_country == -1:
				return ip_geo_line
			if ip_to_search <= self.ip_country_map[self.ip_country_list[index_country]]:
				ip_country_line = linecache.getline(self.ip_to_country,index_country+1)
	#			print ip_country_line
				geo_country_en = ip_country_line.split('|')[2]
				geo_country_ens = ip_country_line.split('|')[3]
				geo_country_cn = ip_country_line.split('|')[4]
				ip_geo_line = [geo_country_en,geo_country_ens,geo_country_cn,'','','','']
				return ip_geo_line
		return ip_geo_line

		'''Get summary ip geography'''
	def get_summary_ip(self,location):
		merge = {}
		merge['country_code'] = ""
		merge['country_desc'] = ""
		merge['region'] =""
		merge['city'] = ""
		merge['net'] = ""

		if location[3] :
			# 百度库内能找到
			merge['country_code'] = location[3]
			merge['country_desc'] = "中国"
			merge['region'] = location[4]
			merge['city'] = location[5]
			merge['net'] = location[6]
		else:
			merge['country_code'] = location[0]
		return merge

def init_geoip():
	'''initial geo ip database'''
	global geo_ip_search_ins
	try :
		geo_ip_search_ins = BigLog_GeoIP()
	except Exception,e :
		print "[ERROR] : Initial geography IP database failured"
		print str(e)
		sys.exit(1)

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
		location = geo_ip_search_ins.search_ip_country_city(ip)
		ip_location = geo_ip_search_ins.get_summary_ip(location)
		results = json.dumps(ip_location)
		return results
	except :
		return json.dumps(dict(country_code="",country_desc="",region="",city="",net=""))
#	print results
	
def geoip_worker():
	try :
		new_worker = CustomGearmanWorker(['127.0.0.1'])
	except Exception,e:
		print "[ERROR GEARMAN]: %s"% (time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time())))
		print "%s\n"%(str(e))
		sys.exit(1)
	init_geoip()

	new_worker.register_task("BigLogGeo", geo_search)
	new_worker.work()

def main():
	geoip_worker()

if __name__ == '__main__':
	main()
#!/usr/bin/env python2.6
#-*- coding: utf-8 -*-

import os
import sys
sys.path.append("../")
import biglog_mysql

import MySQLdb

class DomainDB(object):
	
	@classmethod
	def db_exists(self,domain):

		query = "SELECT COUNT(1) FROM `information_schema`.`SCHEMATA` WHERE `SCHEMA_NAME`='%s';"%(domain)

		if not biglog_mysql.mysql_instance.db_exists(query):
			# if database does not exists
			self.create_domain_db(domain)
			print "[INFO]:create database %s successfully."%domain
			return False
		else:
			return True

	@classmethod
	def create_domain_db(self,domain):
		db_create = "CREATE DATABASE IF NOT EXISTS %s DEFAULT CHARSET utf8 COLLATE utf8_general_ci"%(domain)

		#Table structure for table `original log`
		log_original_create = '''
		CREATE TABLE %s.`log_original` (
		`uuid` char(36) NOT NULL,
		`remote_addr` varchar(15) NOT NULL,
		`remote_user` varchar(1024) DEFAULT NULL,
		`time_local` bigint(20) NOT NULL,
		`request` varchar(1024) NOT NULL,
		`status` int(11) NOT NULL,
		`body_bytes_sent` bigint(20) NOT NULL DEFAULT '0',
		`http_referer` varchar(1024) DEFAULT NULL,
		`http_user_agent` text,
		`http_x_forwarded_for` varchar(512) DEFAULT NULL,
		`upstream_cache_status` enum('MISS','HIT','EXPIRED','UPDATING','STALE','DEF') NOT NULL DEFAULT 'DEF',
		`host` varchar(512) NOT NULL
		) ENGINE=ARCHIVE DEFAULT CHARSET=utf8;
		'''%domain

		#Table structure for table `browser`
		browser_create = '''
		CREATE TABLE %s.`browser` (
		`id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
		`_date` date NOT NULL,
		`_time` varchar(10) NOT NULL,
		`unit` enum('year','month','date','hour','minute','second') NOT NULL DEFAULT 'hour',
		`browser` varchar(1024) NOT NULL,
		`percent` decimal(10,2) DEFAULT NULL,
		`request_count` bigint(20) DEFAULT NULL,
		`unix_time` bigint(20) DEFAULT NULL, KEY(`id`) 
		) ENGINE=ARCHIVE DEFAULT CHARSET=utf8;
		'''%domain

		#Table structure for table `os`
		os_create = '''
		CREATE TABLE %s.`os` (
		`id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
		`_date` date NOT NULL,
		`_time` varchar(10) NOT NULL,
		`unit` enum('year','month','date','hour','minute','second') NOT NULL DEFAULT 'hour',
		`os` varchar(1024) NOT NULL,
		`percent` decimal(10,2) DEFAULT NULL,
		`request_count` bigint(20) DEFAULT NULL,
		`unix_time` bigint(20) DEFAULT NULL, KEY(`id`) 
		) ENGINE=ARCHIVE DEFAULT CHARSET=utf8;
		'''%domain

		#Table structure for table `referer`
		referer_create = '''
		CREATE TABLE %s.`referer` (
		`id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
		`_date` date NOT NULL,
		`_time` varchar(10) NOT NULL,
		`unit` enum('year','month','date','hour','minute','second') NOT NULL DEFAULT 'hour',
		`referer` varchar(4096) NOT NULL,
		`percent` decimal(10,2) DEFAULT NULL,
		`request_count` bigint(20) DEFAULT NULL,
		`unix_time` bigint(20) DEFAULT NULL, KEY(`id`) 
		) ENGINE=ARCHIVE DEFAULT CHARSET=utf8;
		'''%domain

		#Table structure for table `request`
		request_create = '''
		CREATE TABLE %s.`request` (
		`id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
		`_date` date NOT NULL,
		`_time` varchar(10) NOT NULL,
		`unit` enum('year','month','date','hour','minute','second') NOT NULL DEFAULT 'hour',
		`request` varchar(4096) NOT NULL,
		`percent` decimal(10,2) DEFAULT NULL,
		`request_count` bigint(20) DEFAULT NULL,
		`bandwidth` bigint(20) DEFAULT NULL,
		`unix_time` bigint(20) DEFAULT NULL, KEY(`id`) 
		) ENGINE=InnoDB DEFAULT CHARSET=utf8;
		'''%domain

		#Table structure for table `request_not_found`
		request_not_found_create = '''
		CREATE TABLE %s.`request_not_found` (
		`id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
		`_date` date NOT NULL,
		`_time` varchar(10) NOT NULL,
		`unit` enum('year','month','date','hour','minute','second') NOT NULL DEFAULT 'hour',
		`request_not_found` varchar(4096) NOT NULL,
		`percent` decimal(10,2) DEFAULT NULL,
		`request_count` bigint(20) DEFAULT NULL,
		`unix_time` bigint(20) DEFAULT NULL, KEY(`id`) 
		) ENGINE=ARCHIVE DEFAULT CHARSET=utf8;
		'''%domain

		#Table structure for table `request_static`
		request_static_create = '''
		CREATE TABLE %s.`request_static` (
		`id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
		`_date` date NOT NULL,
		`_time` varchar(10) NOT NULL,
		`unit` enum('year','month','date','hour','minute','second') NOT NULL DEFAULT 'hour',
		`request_static` varchar(4096) NOT NULL,
		`percent` decimal(10,2) DEFAULT NULL,
		`request_count` bigint(20) DEFAULT NULL,
		`bandwidth` bigint(20) DEFAULT NULL,
		`unix_time` bigint(20) DEFAULT NULL, KEY(`id`) 
		) ENGINE=ARCHIVE DEFAULT CHARSET=utf8;
		'''%domain

		#Table structure for table `status_code`
		status_code_create = '''
		CREATE TABLE %s.`status_code` (
		`id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
		`_date` date NOT NULL,
		`_time` varchar(10) NOT NULL,
		`unit` enum('year','month','date','hour','minute','second') NOT NULL DEFAULT 'hour',
		`status_code` varchar(10) NOT NULL,
		`percent` decimal(10,2) DEFAULT NULL,
		`request_count` bigint(20) DEFAULT NULL,
		`unix_time` bigint(20) DEFAULT NULL, KEY(`id`) 
		) ENGINE=ARCHIVE DEFAULT CHARSET=utf8;
		'''%domain

		#Table structure for table `visitor_ip` 
		visitor_ip_create = '''
		CREATE TABLE %s.`visitor_ip` (
		`id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
		`_date` date NOT NULL,
		`_time` varchar(10) NOT NULL,
		`unit` enum('year','month','date','hour','minute','second') NOT NULL DEFAULT 'hour',
		`visitor_ip` varchar(20) NOT NULL,
		`percent` decimal(10,2) DEFAULT NULL,
		`request_count` bigint(20) DEFAULT NULL,
		`bandwidth` bigint(20) DEFAULT NULL,
		`unix_time` bigint(20) DEFAULT NULL,
		`country_code` varchar(255) DEFAULT NULL,
		`country_desc` varchar(255) DEFAULT NULL,
		`region` varchar(255) DEFAULT NULL,
		`city` varchar(255) DEFAULT NULL,
		`net` varchar(255) DEFAULT NULL, KEY(`id`) 
		) ENGINE=ARCHIVE DEFAULT CHARSET=utf8;
		'''%domain

		#Table structure for table `attack_log` 
		attack_log_create = '''
		CREATE TABLE %s.`attack_log` (
			`id` char(40) NOT NULL,
			`client_ip` varchar(30) NOT NULL,
			`client_port` int(10) unsigned NOT NULL,
			`server_ip` varchar(30) NOT NULL,
			`server_port` int(10) unsigned NOT NULL,
			`attack_type` varchar(255) NOT NULL,
			`severity` varchar(30) NOT NULL,
			`status` int(10) unsigned NOT NULL,
			`action` varchar(500) NOT NULL,
			`payload` varchar(500) NOT NULL,
			`protocol` decimal(9,2) NOT NULL,
			`referer` varchar(500) NOT NULL,
			`url` varchar(255) NOT NULL,
			`method` enum('GET','POST','PUT','DELETE') NOT NULL DEFAULT 'GET',
			`user_agent` varchar(255) NOT NULL,
			`post_body` varchar(500) NOT NULL,
			`insert_time` int(10) unsigned NOT NULL,
			`unix_time` bigint(20) DEFAULT NULL,
			`country_code` varchar(255) DEFAULT NULL,
			`country_desc` varchar(255) DEFAULT NULL,
			`region` varchar(255) DEFAULT NULL,
			`city` varchar(255) DEFAULT NULL,
			`net` varchar(255) DEFAULT NULL
		) ENGINE=ARCHIVE DEFAULT CHARSET=utf8 COMMENT='sh_attack'
		'''%domain

		biglog_mysql.mysql_instance.run_sql_cmd(db_create)
#		biglog_mysql.mysql_instance.run_sql_cmd(log_original_create)
		biglog_mysql.mysql_instance.run_sql_cmd(browser_create)
		biglog_mysql.mysql_instance.run_sql_cmd(os_create)
		biglog_mysql.mysql_instance.run_sql_cmd(referer_create)
		biglog_mysql.mysql_instance.run_sql_cmd(request_create)
		biglog_mysql.mysql_instance.run_sql_cmd(request_not_found_create)
		biglog_mysql.mysql_instance.run_sql_cmd(request_static_create)
		biglog_mysql.mysql_instance.run_sql_cmd(status_code_create)
		biglog_mysql.mysql_instance.run_sql_cmd(visitor_ip_create)
		biglog_mysql.mysql_instance.run_sql_cmd(attack_log_create)

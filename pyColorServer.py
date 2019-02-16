#!/usr/bin/python
# -*- coding: utf-8 -*-

# // http://91.212.177.22:8888/js/vrTestEPI_0.9.apk
# // сделать страницу авторизации по емайл и захода по user_id
# // https
# // сделать возможность выбора отображаемых полей  SELECT `COLUMN_NAME` FROM `INFORMATION_SCHEMA`.`COLUMNS` WHERE `TABLE_NAME`='user_data';
# // сделать выборку по
# //   указанным в запросе полям slect v1,v2 from table;
# //   количество записей в таблице =  select count(*) from test_data;
# //   дату последнего допбавления = SELECT id,date FROM user_data ORDER BY id DESC LIMIT 1;
# //   указанное в запросе количество по id =  WHERE id BETWEEN 100 AND 200;

import signal
import logging
import random
from datetime import date

import tornado.escape
import tornado.ioloop
import tornado.web
import tornado.options

import pymysql
import json

import os
import time

# Global parameters
serverPort = 8888

# DB connection  parameters
dbServerName  = "127.0.0.1"
dbUser = "os"
dbPassword = "11"
dbName = "colors"
tableData = "user_data"
tableTest = "test_data"
version = "0.8"
root_dir = os.path.dirname(__file__)

class Application(tornado.web.Application):
	is_closing = False
	db = None

	def checkDB(self):
		try:
			self.db = pymysql.connect(host=dbServerName, user=dbUser, password=dbPassword, db=dbName,autocommit=True)
			logApp.info("DB exist")
		except Exception as e:
			logErr.error(time.strftime('%Y-%m-%d %H:%M:%S ')+"Exeception DB occured:{}".format(e))
			pass
		checkUserDataTable = "SELECT COUNT(*) FROM "+tableData+";"
		try:
			self.db.cursor().execute(checkUserDataTable)
			logApp.info("UserData table exist")
		except Exception as e:
			logApp.info("UserData table does not exist. Creating...")
			# userID for corresponde between tables
			self.db.cursor().execute("CREATE TABLE "+tableData+
			"""(id int NOT NULL AUTO_INCREMENT,
			user VARCHAR(40),
			ip VARCHAR(25),
			deviceID VARCHAR(70),
			email VARCHAR(70),
			userID VARCHAR(40),
			ipInfo TEXT,
			lang VARCHAR(10),
			userDate VARCHAR(30),
			userZone VARCHAR(200),
			date DATETIME,
			rightObjectsList TEXT,
			selectedObjectsList TEXT,
			snenasMotionData MEDIUMTEXT,
			PRIMARY KEY (id));""")
			logApp.info("UserData table is created")
			pass
		checkUserTestTable = "SELECT COUNT(*)  FROM "+tableTest+";"
		try:
			self.db.cursor().execute(checkUserTestTable)
			logApp.info("testData table exist")
		except Exception as e:
			logApp.info("TestData table does not exist. Creating...")
			# userID from datatable for corresponding between tables
			self.db.cursor().execute("CREATE TABLE "+tableTest+
			""" (id int NOT NULL AUTO_INCREMENT,
			user VARCHAR(40),
			userID VARCHAR(40),
			ip VARCHAR(25),
			ipInfo TEXT,
			lang VARCHAR(10),
			data TEXT,
			testTime INT,
			email VARCHAR(70),
			date DATETIME,
			birthDate DATE,
			extra TINYINT,
			stabil TINYINT,
			lying TINYINT,
			PRIMARY KEY (id));""")
			logApp.info("testData table is created")
			pass
	def signal_handler(self, signum, frame):
		logApp.info("exiting...")
		self.is_closing = True

	def try_exit(self):
		if self.is_closing:
			# clean up here
			self.db.close()
			tornado.ioloop.IOLoop.instance().stop()
			logApp.info(time.strftime('%Y-%m-%d %H:%M:%S ')+"exit success")

class MainHandler(tornado.web.RequestHandler):
	def get(self):
		# logging.info('start main='+self.request.remote_ip)
		logApp.info(time.strftime('%Y-%m-%d %H:%M:%S ')+'get index')
		self.render(os.path.join("static","index.html"))

class ResultHandler(tornado.web.RequestHandler):
	def get(self):
		logApp.info(time.strftime('%Y-%m-%d %H:%M:%S ')+'get main')
		self.render(os.path.join("static","main.html"))

class VersionHandler(tornado.web.RequestHandler):
	def get(self):
		response = { 'version': version }
		response["id"] = "".join(random.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890") for _ in range(24))
		self.write(response)

class GetByIdHandler(tornado.web.RequestHandler):
	def get(self,req):
		# logging.info(self.request.query_arguments)
		logging.info(req)
		# logging.info(self.request.remote_ip)
		# json.dumps({ k: self.get_argument(k) for k in self.request.arguments })
		# http://localhost:8888/getID/re?ff=230&id=33
		entry = {}
		if id:
			# logging.info(self.request)
			# entry = self.queryone("SELECT * FROM "+tableData+" WHERE id = %s", int(id))
			self.write("dd")

class GetLastDataHandler(tornado.web.RequestHandler):
	def get(self):
		try:
			# logging.info(self.request)
			answer={}
			with self.application.db.cursor() as cursor:
				cursor.execute("SELECT id,date FROM "+tableData+" ORDER BY id DESC LIMIT 1;")
				res = cursor.fetchone()
				answer['vr id'] = res[0]
				answer['vr date'] = str(res[1])
				print(res[1])
				cursor.execute("select count(*) from "+tableData)
				res2 = cursor.fetchone()
				answer['vr count'] = res2[0]
				cursor.execute("SELECT id,date FROM "+tableData+" ORDER BY id DESC LIMIT 1;")
				res3 = cursor.fetchone()
				answer['text id'] = res3[0]
				answer['text date'] = str(res3[1])
				cursor.execute("select count(*) from "+tableTest)
				res4 = cursor.fetchone()
				answer['text count'] = res4[0]
				# print(answer)
				# print(json.dumps(answer))
			self.write(json.dumps(answer))
		except Exception as e:
			logErr.error(time.strftime('%Y-%m-%d %H:%M:%S ')+"GetAll Exeception occured:{}".format(e))
			self.write( "Error GetAll")

class PutTest(tornado.web.RequestHandler):
	#wget --post-data="{\"user\":\"user645\",\"data\":\"data445\"}"  "http://localhost:8888/putRecord"
	def prepare(self):
		json_data = None
		self.post_result = "Json test post OK"
		if self.request.body:
			try:
				# logging.info(self.request.body)
				json_data = tornado.escape.json_decode(self.request.body)
			except Exception as e:
				self.post_result = "Error parse JSON body"
				logErr.error(time.strftime('%Y-%m-%d %H:%M:%S')+"PutTest JSON Decode Exeception body occured:{}".format(e))
				pass
		if json_data:
			try:
				strData = tornado.escape.json_encode(json_data["answers"])
				# logging.info(strData)
				insertStatement = "INSERT INTO "+tableTest+" (user,ip,ipInfo,lang,data,testTime,date,birthDate,extra,stabil,lying) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);"
				logApp.info(time.strftime('%Y-%m-%d %H:%M:%S ')+insertStatement)
				strUser = str(json_data["user"])
				ipInfo = tornado.escape.json_encode(json_data["ipInfo"])
				Extra = json_data["result"]["extra"]
				ip = json_data["ip"]
				Stabil = json_data["result"]["stabil"]
				Lying = json_data["result"]["lying"]
				strLang = str(json_data["lang"])
				strDate = str(json_data["date"])
				strTestTime = json_data["testTime"]
				strTime = time.strftime('%Y-%m-%d %H:%M:%S')
				# print(tableTest+strUser+strData+strDate+strTime)
				self.application.db.cursor().execute(insertStatement,(strUser,ip,ipInfo,strLang,strData,strTestTime,strTime,strDate,Extra,Stabil,Lying))
			except Exception as e:
				logErr.error(time.strftime('%Y-%m-%d %H:%M:%S ')+"PutTest JSON Parse Exeception occured:{}".format(e))
				self.post_result = "Error parse JSON"
				pass
	def post(self):
		logApp.info(time.strftime('%Y-%m-%d %H:%M:%S ')+self.post_result)
		# logging.info(self.post_result)
		self.write(self.post_result)
	def get(self):
		logApp.info(time.strftime('%Y-%m-%d %H:%M:%S ')+'user try use get method')
		# logging.info('user try use get method')
		self.write("Error!")

class PutVrData(tornado.web.RequestHandler):
	def prepare(self):
		logging.info(PutVrData)
		json_data = None
		self.post_result = "Json test post OK"
		if self.request.body:
			try:
				json_data = tornado.escape.json_decode(self.request.body)
				# logging.info(json_data)
				#json_data = {"user":"user333","data":"dddddddd fff"}
			except Exception as e:
				self.post_result = "Error parse JSON body"
				logErr.error(time.strftime('%Y-%m-%d %H:%M:%S')+"PutTest JSON Decode Exeception body occured:{}".format(e))
				pass
		if json_data:
			try:
				logging.info("json_data ok")
				ip = json_data["ip"]
				ipInfo = tornado.escape.json_encode(json_data["ipInfo"])
				deviceID = json_data["deviceID"]
				email = json_data["userEmail"]
				lang = json_data["lang"]
				userDate = json_data["startDateTime"]
				userZone = json_data["userZone"]
				date = time.strftime('%Y-%m-%d %H:%M:%S')
				userID = "".join(random.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890") for _ in range(24))
				rightObjectsList = tornado.escape.json_encode(json_data["rightObjectsList"])
				selectedObjectsList = tornado.escape.json_encode(json_data["selectedObjectsList"])
				snenasMotionData = tornado.escape.json_encode(json_data["snenasMotionData"])
				insertStatement = "INSERT INTO "+tableData+" (ip,ipInfo,deviceID,userID,email,lang,userDate,userZone,date,rightObjectsList,selectedObjectsList,snenasMotionData) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);"
				self.application.db.cursor().execute(
				insertStatement,(ip,ipInfo,deviceID,userID,email,lang,userDate,userZone,date,rightObjectsList,selectedObjectsList,snenasMotionData))
				logging.info("json_data ok")
			except Exception as e:
				logErr.error(time.strftime('%Y-%m-%d %H:%M:%S ')+"PutTest JSON Parse Exeception occured:{}".format(e))
				self.post_result = "Error parse JSON"
				pass
	def post(self):
		logApp.info(time.strftime('%Y-%m-%d %H:%M:%S ')+self.post_result)
		# logging.info(self.post_result)
		self.write(self.post_result)
	def get(self):
		logApp.info(time.strftime('%Y-%m-%d %H:%M:%S ')+'user try use get method')
		# logging.info('user try use get method')
		self.write("Error!")

application = Application([
	(r"/", MainHandler),
	(r"/results", ResultHandler),
	(r"/getLastData", GetLastDataHandler),
	(r"/getID/([^/]+)", GetByIdHandler),
	(r'/(favicon.ico)', tornado.web.StaticFileHandler, {"path": ""}),
	(r"/images/(.*)",tornado.web.StaticFileHandler, {"path": "./static/images"},),
	(r"/js/(.*)",tornado.web.StaticFileHandler, {"path": "./static/js"},),
	# (r"/putRecord", PutRecord),
	(r"/putTest", PutTest),
	(r"/putVrData", PutVrData),
	(r"/ver", VersionHandler)
	],
	debug=True,
	static_hash_cache=False
	)

if __name__ == "__main__":
	tornado.options.parse_command_line()
	try:
		tornado.log.enable_pretty_logging()

		handler = logging.FileHandler(os.path.join(root_dir,"server.log"))
		logger = logging.getLogger()
		logger.setLevel(logging.DEBUG)
		logApp = logging.getLogger("tornado.application")
		logApp.addHandler(handler)

		handlerErr = logging.FileHandler(os.path.join(root_dir,"serverErr.log"))
		loggerErr = logging.getLogger()
		loggerErr.setLevel(logging.DEBUG)
		logErr = logging.getLogger("tornado.general")
		logErr.addHandler(handlerErr)

		handlerAcc = logging.FileHandler(os.path.join(root_dir,"serverAcc.log"))
		loggerAcc = logging.getLogger()
		loggerAcc.setLevel(logging.DEBUG)
		logAcc = logging.getLogger("tornado.access")
		logAcc.addHandler(handlerAcc)

		logging.info("Log is enable")
	except Exception as e:
		logging.error(time.strftime('%Y-%m-%d %H:%M:%S ')+"Log Exeception occured:{}".format(e))
	logApp.info(time.strftime('%Y-%m-%d %H:%M:%S ')+"starting server ")
	application.checkDB()
	signal.signal(signal.SIGINT, application.signal_handler)
	application.listen(serverPort)
	tornado.ioloop.PeriodicCallback(application.try_exit, 100).start()
	print("Press Ctrl-C for stop the server.")
	for dir, _, files in os.walk('static'):
		[tornado.autoreload.watch(dir + '/' + f) for f in files if not f.startswith('.')]
	tornado.ioloop.IOLoop.instance().start()

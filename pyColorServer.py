#!/usr/bin/python
# -*- coding: utf-8 -*-

import signal
import logging
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
root_dir = os.path.dirname(__file__)

#root = os.path.dirname(__file__)
#static_path=os.path.join(root, 'static')
# добавить
# вход с помощью соц сетей
# девайс пользователя и есть ли установленный софт

class SQLHandler(tornado.web.RequestHandler):
	def row_to_obj(self, row, cur):
		#Convert a SQL row to an object supporting dict and attribute access.
		obj = tornado.util.ObjectDict()
		for val, desc in zip(row, cur.description):
			#print("val="+str(val)+" desc="+ str(desc[0]))
			obj[desc[0]] = val
		return obj

	def execute(self, stmt, *args):
		#Execute a SQL statement.
		with (self.application.db.cursor()) as cur:
			cur.execute(stmt, args)

	def query(self, stmt, *args):
		with (self.application.db.cursor()) as cur:
			cur.execute(stmt, args)
		return [self.row_to_obj(row, cur) for row in cur.fetchall()]

	def queryone(self, stmt, *args):
		#Query for exactly one result.
		results = self.query(stmt, *args)
		if len(results) == 0:
			raise NoResultError()
		elif len(results) > 1:
			raise ValueError("Expected 1 result, got %d" % len(results))
		return results[0]

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
			self.db.cursor().execute("CREATE TABLE "+tableData+
			"""(id int NOT NULL AUTO_INCREMENT,
			user VARCHAR(40),
			ip VARCHAR(25),
			deviceID VARCHAR(70),
			email VARCHAR(70),
			userID VARCHAR(40),
			ipInfo TEXT,
			lang VARCHAR(10),
			userDate VARCHAR(250),
			date datetime,
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
			# CREATE TABLE test_data (id int NOT NULL AUTO_INCREMENT, user VARCHAR(40), ip VARCHAR(30), data VARCHAR(255), date datetime, birthDate datetime, PRIMARY KEY (id));
			self.db.cursor().execute("CREATE TABLE "+tableTest+
			""" (id int NOT NULL AUTO_INCREMENT,
			user VARCHAR(40),
			userID VARCHAR(40),
			ip VARCHAR(25),
			ipInfo TEXT,
			lang VARCHAR(10),
			data TEXT,
			testTime int,
			email VARCHAR(70),
			date datetime,
			birthDate date,
			extra tinyint,
			stabil tinyint,
			lying tinyint,
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
		response = { 'version': '0.0.1', 'last_build':  date.today().isoformat() }
		self.write(response)

class GetByIdHandler(SQLHandler):
	async  def get(self):
		id = self.get_argument("id", None)
		entry = {}
		if id:
			entry = self.queryone("SELECT * FROM "+tableData+" WHERE id = %s", int(id))
			self.write(json.dumps(entry))

class GetAllDataHandler(SQLHandler):
	async  def get(self):
		recNumber = str(self.get_argument("limit", 10))
		entries= {}
		#logging.info("recNumber="+recNumber)
		if id:
			entries = self.query("SELECT * FROM "+tableData+" ORDER BY id DESC limit "+recNumber)
			#logging.info(entries)
		self.write(json.dumps(entries))

class PutRecord(tornado.web.RequestHandler):
	#wget --post-data="{\"user\":\"user645\",\"data\":\"data445\"}"  "http://localhost:8888/putRecord"
	def prepare(self):
		json_data = None
		self.post_result = "Json post OK"
		if self.request.body:
			try:
				logApp.info(time.strftime('%Y-%m-%d %H:%M:%S ')+self.request.body)
				json_data = tornado.escape.json_decode(self.request.body)
				#json_data = {"user":"user333","data":"dddddddd fff"}
			except Exception as e:
				self.post_result = "Error decode JSON"
				logErr.error(time.strftime('%Y-%m-%d %H:%M:%S ')+"PutRecord Json decode Exeception body occured:{}".format(e))
				pass
		if json_data:
			try:
				#logging.info('start put data to DB')
				cursorObject = self.application.db.cursor()
				insertStatement = "INSERT INTO "+tableData+" (user, date, data) VALUES (\""+str(json_data["user"])+"\",\""+time.strftime('%Y-%m-%d %H:%M:%S')+"\",\""+str(json_data["data"])+"\");"
				logApp.info(insertStatement)
				cursorObject.execute(insertStatement)
			except Exception as e:
				logErr.error(time.strftime('%Y-%m-%d %H:%M:%S ')+"PutRecord Jsom parse Exeception occured:{}".format(e))
				self.post_result = "Error parse JSON"

class PutTest(tornado.web.RequestHandler):
	#wget --post-data="{\"user\":\"user645\",\"data\":\"data445\"}"  "http://localhost:8888/putRecord"
	def prepare(self):
		json_data = None
		self.post_result = "Json test post OK"
		if self.request.body:
			try:
				# logging.info(self.request.body)
				json_data = tornado.escape.json_decode(self.request.body)
				#json_data = {"user":"user333","data":"dddddddd fff"}
			except Exception as e:
				self.post_result = "Error parse JSON body"
				logErr.error(time.strftime('%Y-%m-%d %H:%M:%S')+"PutTest JSON Decode Exeception body occured:{}".format(e))
				pass
		if json_data:
			try:
				strData = tornado.escape.json_encode(json_data["answers"])
				# strResult = tornado.escape.json_encode(json_data["result"])
				# strData = "test"
				# logging.info(strData)
				#time.strftime('%Y-%m-%d %H:%M:%S')
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
	#wget --post-data="{\"user\":\"user645\",\"data\":\"data445\"}"  "http://localhost:8888/putRecord"
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
				date = time.strftime('%Y-%m-%d %H:%M:%S')
				rightObjectsList = tornado.escape.json_encode(json_data["rightObjectsList"])
				selectedObjectsList = tornado.escape.json_encode(json_data["selectedObjectsList"])
				snenasMotionData = tornado.escape.json_encode(json_data["snenasMotionData"])
				insertStatement = "INSERT INTO "+tableData+" (user,ip,ipInfo,lang,data,testTime,date,birthDate,extra,stabil,lying) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);"
				self.application.db.cursor().execute(insertStatement,(strUser,ip,ipInfo,strLang,strData,strTestTime,strTime,strDate,Extra,Stabil,Lying))
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
	(r"/getAllData", GetAllDataHandler),
	(r"/getRecordid/([0-9]+)", GetByIdHandler),
	(r'/(favicon.ico)', tornado.web.StaticFileHandler, {"path": ""}),
	(r"/images/(.*)",tornado.web.StaticFileHandler, {"path": "./static/images"},),
	(r"/js/(.*)",tornado.web.StaticFileHandler, {"path": "./static/js"},),
	(r"/putRecord", PutRecord),
	(r"/putTest", PutTest),
	(r"/putVrData", PutVrData),
	(r"/version", VersionHandler)
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
	# handler = grapy.GELFHandler('host_to_graylog_node', port, localname="name_of_your_app_identifier")
	application.checkDB()
	signal.signal(signal.SIGINT, application.signal_handler)
	application.listen(serverPort)
	tornado.ioloop.PeriodicCallback(application.try_exit, 100).start()
	print("Press Ctrl-C for stop the server.")
	for dir, _, files in os.walk('static'):
		[tornado.autoreload.watch(dir + '/' + f) for f in files if not f.startswith('.')]
	tornado.ioloop.IOLoop.instance().start()

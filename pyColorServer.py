#!/usr/bin/python
# -*- coding: utf-8 -*-


# Добавить генерацию письма на почтовый адрес
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
version = "0.9"
root_dir = os.path.dirname(__file__)

class Object(object):
    pass

class Application(tornado.web.Application):
	is_closing = False
	db = None

	def checkDB(self):

		try:
			self.db = pymysql.connect(host=dbServerName, user=dbUser, password=dbPassword, db=dbName,autocommit=True)
			logApp.info("DB exist")
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
				deviceInfo VARCHAR(250),
				gyro VARCHAR(1),
				userID VARCHAR(40),
				ipInfo TEXT,
				lang VARCHAR(10),
				userStartTime VARCHAR(30),
				zone VARCHAR(200),
				date DATETIME,
				txtVersion VARCHAR(6),
				input VARCHAR(6),
				birth VARCHAR(30),
				gender VARCHAR(6),
				extra VARCHAR(2),
				stabil VARCHAR(2),
				rightObjectsList TEXT,
				selectedObjectsList TEXT,
				snenasMotionData MEDIUMTEXT,
				colorTestResult TEXT,
				textTestResult TEXT,
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
				user VARCHAR(80),
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
		except Exception as e:
			logErr.error(time.strftime('%Y-%m-%d %H:%M:%S ')+"Can not connect to DB server")
			logErr.error("Exeception DB occured:{}".format(e))
			logApp.info(time.strftime('%Y-%m-%d %H:%M:%S ')+"exit success")
			tornado.ioloop.IOLoop.instance().stop()

	def signal_handler(self, signum, frame):
		logApp.info("exiting...")
		self.is_closing = True

	def try_exit(self):
		if self.is_closing:
			# clean up here
			self.db.close()
			logApp.info(time.strftime('%Y-%m-%d %H:%M:%S ')+"exit success")
			tornado.ioloop.IOLoop.instance().stop()


class MainHandler(tornado.web.RequestHandler):
	def get(self):
		# logging.info('start main='+self.request.remote_ip)
		logApp.info(time.strftime('%Y-%m-%d %H:%M:%S ')+'get index')
		self.render(os.path.join("static","index.html"))

class ResultHandler(tornado.web.RequestHandler):
	def get(self):
		logApp.info(time.strftime('%Y-%m-%d %H:%M:%S ')+'get main')
		self.render(os.path.join("static","main.html"))

class ShowResultHandler(tornado.web.RequestHandler):
	def get(self):
		logApp.info(time.strftime('%Y-%m-%d %H:%M:%S ')+'get main')
		self.render(os.path.join("static","showResults.html"))

class VersionHandler(tornado.web.RequestHandler):
	def get(self):
		response = { 'version': version }
		x_real_ip = self.request.headers.get("X-Real-IP")
		# remote_ip = x_real_ip or self.request.remote_ip
		# remote_ip = self.request.headers.get('X-Forwarded-For', self.request.headers.get('X-Real-Ip', self.request.remote_ip))
		# logging.info(remote_ip)
		remote_ip = str(self.request.headers)
		response["ip"] = remote_ip
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
				if(res):
					answer['vr id'] = res[0]
					answer['vr date'] = str(res[1])
				else:
					answer['vr id'] = 0
					answer['vr date'] = 0
				cursor.execute("select count(*) from "+tableData)
				res2 = cursor.fetchone()
				answer['vr count'] = res2[0]
				cursor.execute("SELECT id,date FROM "+tableTest+" ORDER BY id DESC LIMIT 1;")
				res3 = cursor.fetchone()
				if(res3):
					answer['text id'] = res3[0]
					answer['text date'] = str(res3[1])
				else:
					answer['text id'] = 0
					answer['text date'] = 0
				cursor.execute("select count(*) from "+tableTest)
				res4 = cursor.fetchone()
				answer['text count'] = res4[0]
				# print(answer)
				# print(json.dumps(answer))
			self.write(json.dumps(answer))
		except Exception as e:
			logErr.error(time.strftime('%Y-%m-%d %H:%M:%S ')+"GetAll Exeception occured:{}".format(e))
			self.write( '{"error":'+"GetAll Exeception occured:{}".format(e)+'}')

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
				self.post_result = '{"error":"Error parse json!"}'
				pass
	def post(self):
		logApp.info(time.strftime('%Y-%m-%d %H:%M:%S ')+self.post_result)
		# logging.info(self.post_result)
		self.write(self.post_result)
	def get(self):
		logApp.info(time.strftime('%Y-%m-%d %H:%M:%S ')+'user try use get method')
		# logging.info('user try use get method')
		self.write('{"error":"Error!"}')

class PutVrData(tornado.web.RequestHandler):
	def prepare(self):
		logging.info("PutVrData")
		json_data = None
		self.post_result = "Json test post OK"
		if self.request.body:
			try:
				json_data = tornado.escape.json_decode(self.request.body)
				# logging.info(json_data)
				#json_data = {"user":"user333","data":"dddddddd fff"}
				# ALTER TABLE user_data ADD deviceInfo VARCHAR(250) AFTER deviceID;
			except Exception as e:
				self.post_result = "Error parse JSON body"
				logErr.error(time.strftime('%Y-%m-%d %H:%M:%S')+"PutTest JSON Decode Exeception body occured:{}".format(e))
		if json_data:
				#logging.info("json_data start")
				dataListStr = ["ip","deviceID","deviceInfo","gyro","email","lang","zone","txtVersion","input","gender","birth"]
				dataListObj = ["ipInfo","textTestResult","colorTestResult","rightObjectsList","selectedObjectsList","snenasMotionData"]
				data = {}
				for i in range(len(dataListStr)):
					try:
						data[dataListStr[i]] = str(json_data["userData"][dataListStr[i]])
					except  Exception as e:
						data[dataListStr[i]] = ""
						logging.error("can not parse "+dataListStr[i])
				# print(json.dumps(data))
				for i in range(len(dataListObj)):
					try:
						data[dataListObj[i]] = tornado.escape.json_encode(json_data[dataListObj[i]])
					except Exception as e:
						data[dataListStr[i]] = ""
						logging.error("can not parse "+dataListObj[i])
				data["date"] = time.strftime('%Y-%m-%d %H:%M:%S')
				try:
					data["userStartTime"] = str(json_data["userStartTime"])
				except Exception as e:
					data["userStartTime"] = str(data["date"])
				data["userID"] = "".join(random.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890") for _ in range(24))
				#print(json.dumps(data))
				placeholders = ', '.join(['%s'] * len(data))
				columns = ', '.join(data.keys())
				values = list(data.values())
				sql = "INSERT INTO %s ( %s ) VALUES ( %s )" % (tableData, columns, placeholders)
				self.application.db.cursor().execute( sql, values)
				#insertStatement,(ip,ipInfo,deviceID,userID,deviceInfo,gyro,email,lang,userDate,userZone,date,txtVersion,Input,Gender,Birth,rightObjectsList,selectedObjectsList,snenasMotionData))
				#logging.info("json_data ok")
				self.post_result = "Parsed ok"
	def post(self):
		logApp.info(time.strftime('%Y-%m-%d %H:%M:%S ')+self.post_result)
		# logging.info(self.post_result)
		self.write(self.post_result)
	def get(self):
		logApp.info(time.strftime('%Y-%m-%d %H:%M:%S ')+'user try use get method')
		# logging.info('user try use get method')
		self.write("Error!!!")


class NotFoundHandler(tornado.web.RequestHandler):
	def get(self):
		logging.info(self.request.body)
		self.write('{"error":"404"}')

application = Application([
	(r"/", MainHandler),
	(r"/results", ResultHandler),
	(r"/showResults", ShowResultHandler),
	(r"/getLastData", GetLastDataHandler),
	(r"/getID/([^/]+)", GetByIdHandler),
	(r'/(favicon.ico)', tornado.web.StaticFileHandler, {"path": ""}),
	(r"/images/(.*)",tornado.web.StaticFileHandler, {"path": "static/images"},),
	(r"/js/(.*)",tornado.web.StaticFileHandler, {"path": "static/js"},),
	# (r"/putRecord", PutRecord),
	(r"/putTest", PutTest),
	(r"/putVrData", PutVrData),
	(r"/ver", VersionHandler),
	(r"/.*", NotFoundHandler),
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
	logApp.info(time.strftime('%Y-%m-%d %H:%M:%S ')+"starting server on port "+str(serverPort))
	application.checkDB()
	signal.signal(signal.SIGINT, application.signal_handler)
	application.listen(serverPort)
	tornado.ioloop.PeriodicCallback(application.try_exit, 100).start()
	print("Press Ctrl-C for stop the server.")
	for dir, _, files in os.walk('static'):
		[tornado.autoreload.watch(dir + '/' + f) for f in files if not f.startswith('.')]
	tornado.ioloop.IOLoop.instance().start()

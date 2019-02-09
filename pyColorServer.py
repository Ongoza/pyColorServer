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

#root = os.path.dirname(__file__)
#static_path=os.path.join(root, 'static')

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
			logging.info("DB OK")
		except Exception as e:
			logging.info("Exeception DB occured:{}".format(e))

		checkUserDataTable = "SELECT COUNT(*) FROM "+tableData+";"
		try:
			self.db.cursor().execute(checkUserDataTable)
			logging.info("DB UserDATA OK")
		except Exception as e:
			logging.info("UserDATA Table not exist. Creating...")
			self.db.cursor().execute("CREATE TABLE "+tableData+" (id int NOT NULL AUTO_INCREMENT, user VARCHAR(40), ip VARCHAR(30), data MEDIUMTEXT, date datetime, PRIMARY KEY (id));")
			logging.info("UserDATA Table created")
		checkUserTestTable = "SELECT COUNT(*)  FROM "+tableTest+";"
		try:
			self.db.cursor().execute(checkUserTestTable)
			logging.info("DB testDATA OK")
		except Exception as e:
			logging.info("TestDATA Table not exist. Creating...")
			# CREATE TABLE test_data (id int NOT NULL AUTO_INCREMENT, user VARCHAR(40), ip VARCHAR(30), data VARCHAR(255), date datetime, birthDate datetime, PRIMARY KEY (id));
			self.db.cursor().execute("CREATE TABLE "+tableTest+" (id int NOT NULL AUTO_INCREMENT, user VARCHAR(40), ip VARCHAR(30), data TEXT, date datetime, birthDate date, PRIMARY KEY (id));")
			logging.info("testDATA Table created")
	def signal_handler(self, signum, frame):
		logging.info("exiting...")
		self.is_closing = True

	def try_exit(self):
		if self.is_closing:
			# clean up here
			self.db.close()
			tornado.ioloop.IOLoop.instance().stop()
			logging.info("exit success")

class MainHandler(tornado.web.RequestHandler):
	def get(self):
		logging.info('start main=')
		self.render("static\index.html")

class ResultHandler(tornado.web.RequestHandler):
	def get(self):
		logging.info('start main=')
		self.render("static\main.html")

class VersionHandler(tornado.web.RequestHandler):
	def get(self):
		response = { 'version': '0.0.1',
			'last_build':  date.today().isoformat() }
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
				logging.info(self.request.body)
				json_data = tornado.escape.json_decode(self.request.body)
				#json_data = {"user":"user333","data":"dddddddd fff"}
			except Exception as e:
				self.post_result = "Error parse JSON body"
				logging.info("Exeception body occured:{}".format(e))
				pass
		if json_data:
			try:
				#logging.info('start put data to DB')
				cursorObject = self.application.db.cursor()
				insertStatement = "INSERT INTO "+tableData+" (user, date, data) VALUES (\""+str(json_data["user"])+"\",\""+time.strftime('%Y-%m-%d %H:%M:%S')+"\",\""+str(json_data["data"])+"\");"
				logging.info(insertStatement)
				cursorObject.execute(insertStatement)
			except Exception as e:
				logging.info("Exeception occured:{}".format(e))
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
				logging.info("Exeception body occured:{}".format(e))
				pass
		if json_data:
			try:
				strData = tornado.escape.json_encode(json_data["answers"])
				# strData = "test"
				# logging.info(strData)
				#time.strftime('%Y-%m-%d %H:%M:%S')
				insertStatement = "INSERT INTO "+tableTest+" (user,data,date,birthDate) VALUES (%s,%s,%s,%s);"
				logging.info(insertStatement)
				strUser = str(json_data["user"])
				strDate = str(json_data["date"])
				strTime = time.strftime('%Y-%m-%d %H:%M:%S')
				print(tableTest+strUser+strData+strDate+strTime)
				self.application.db.cursor().execute(insertStatement,(strUser,strData,strTime,strDate))
			except Exception as e:
				logging.info("Exeception occured:{}".format(e))
				self.post_result = "Error parse JSON"
				pass
	def post(self):
		logging.info(self.post_result)
		self.write(self.post_result)
	def get(self):
		logging.info('user try use get method')
		self.write("You should use a post method!")

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
	(r"/version", VersionHandler)
	],
	debug=True,
	static_hash_cache=False
	)

if __name__ == "__main__":
	tornado.options.parse_command_line()
	application.checkDB()
	signal.signal(signal.SIGINT, application.signal_handler)
	application.listen(serverPort)
	tornado.ioloop.PeriodicCallback(application.try_exit, 100).start()
	print("Press Ctrl-C for stop the server.")
	for dir, _, files in os.walk('static'):
		[tornado.autoreload.watch(dir + '/' + f) for f in files if not f.startswith('.')]
	tornado.ioloop.IOLoop.instance().start()

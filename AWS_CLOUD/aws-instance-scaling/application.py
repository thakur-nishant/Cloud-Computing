from flask import Flask, render_template, redirect, request, json, jsonify, url_for
from werkzeug import secure_filename
import csv
from flaskext.mysql import MySQL
import time
import hashlib
import datetime

application = Flask(__name__)

mysql = MySQL()
 
# MySQL configurations
application.config['MYSQL_DATABASE_USER'] = 'root'
application.config['MYSQL_DATABASE_PASSWORD'] = 'N!shant22'
application.config['MYSQL_DATABASE_DB'] = 'mydb'
application.config['MYSQL_DATABASE_HOST'] = 'myclouddb.cdiq0jfmc5nn.us-east-2.rds.amazonaws.com'
# application.config['MYSQL_DATABASE_HOST'] = 'myclouddb.cdiq0jfmc5nn.us-east-2.rds.amazonaws.com'
mysql.init_app(application)

conn = mysql.connect()

cursor = conn.cursor()

@application.route('/')
def home():
	return render_template('index.html', script_root = request.script_root)


@application.route('/searchMagnitude', methods=['POST','GET'])
def searchMagnitude():
	if request.method == 'POST':
		data = request.form
		cursor.execute("SELECT * FROM earthquake WHERE mag > " + data['searchWord']+ ";") 
		row = cursor.fetchone()
		result = []
		while row:
			row1 = [str(i) for i in row]
			result.append(row1)
			row = cursor.fetchone()
		return jsonify(result)


@application.route('/searchMagnitudeRange', methods=['POST','GET'])
def searchMagnitudeRange():
	if request.method == 'POST':
		data = request.form
		sql = "SELECT * FROM earthquake WHERE mag between " + data['range1'] + " and " + data['range2'] + " and CONVERT(datetime,LEFT(time,10),126) BETWEEN '"+ data['startDate'] +"' AND '"+ data['endDate'] +"'";

		cursor.execute(sql)
		row = cursor.fetchone()
		result = []
		while row:
			row1 = [str(i) for i in row]
			result.append(row1)
			row = cursor.fetchone()
		return jsonify(result)

@application.route('/searchMagnitudeIntervals', methods=['POST','GET'])
def searchMagnitudeIntervals():
	if request.method == 'POST':
		data = request.form
		pointer1 = int(data['range1'])
		endPoint = int(data['range2'])
		rows = []
		start_time = time.time()
		now = datetime.datetime.now()
		while pointer1 < endPoint :
			pointer2 = pointer1 + 0.1
			sql = "SELECT * FROM earthquake WHERE mag between " + str(pointer1+0.001)  + " and " + str(pointer2) +";"
			
			print(sql)
			cursor.execute(sql)
			row = cursor.fetchone()
			result = []
			while row:
				row1 = [str(i) for i in row]
				result.append(row1)
				row = cursor.fetchone()

			rows.append([[pointer1, pointer2],result])

			pointer1 = pointer2
		total_time = time.time() - start_time
		# print(rows)
		return jsonify(["first select time: " + str(now)]+["total_time: " + str(total_time)] + rows)


@application.route('/searchLocation', methods=['POST','GET'])
def searchLocation():
	if request.method == 'POST':
		data = request.form
		sql = "SELECT * FROM(SELECT *,(((acos(sin((" + data['latitude'] + "*(22/7)/180)) * sin((latitude*(22/7)/180))+cos((" + data['latitude'] + "*(22/7)/180)) * cos((latitude*(22/7)/180)) * cos(((" + data['longitude'] + " - longitude)*(22/7)/180))))*180/(22/7))*60*1.1515*1.609344) as distance FROM earthquake) t WHERE distance <= "+  data['distance']
		print(sql)
		cursor.execute(sql)
		row = cursor.fetchone()
		result = []
		while row:
			row1 = [str(i) for i in row]
			result.append(row1)
			row = cursor.fetchone()
		return jsonify(result)

@application.route('/searchLocationDistance', methods=['POST','GET'])
def searchLocationDistance():
	if request.method == 'POST':
		data = request.form
		res = []
		start_time = time.time()
		for i in range(1,101,5):
			sql = "SELECT * FROM(SELECT *,(((acos(sin((" + data['latitude'] + "*(22/7)/180)) * sin((latitude*(22/7)/180))+cos((" + data['latitude'] + "*(22/7)/180)) * cos((latitude*(22/7)/180)) * cos(((" + data['longitude'] + " - longitude)*(22/7)/180))))*180/(22/7))*60*1.1515*1.609344) as distance FROM earthquake) t WHERE distance <= "+  str(i)
			print(sql)
			
			cursor.execute(sql)
			row = cursor.fetchone()
			result = []
			while row:
				row1 = [str(i) for i in row]
				result.append(row1)
				row = cursor.fetchone()
				
			res.append({'range': str(i) + " km", 'results': result})
		total_time = time.time() - start_time
	return jsonify(["total_time: " + str(total_time)] + res)
		

@application.route('/searchLocationName', methods=['POST','GET'])
def searchLocationName():
	if request.method == 'POST':
		data = request.form
		sql = "SELECT * FROM earthquake WHERE locationSource = '" + data['name'] + "' and mag between " + data['range1'] + " and " + data['range2'] + ";"
		print(sql)
		cursor.execute(sql)
		row = cursor.fetchone()
		result = []
		while row:
			row1 = [str(i) for i in row]
			result.append(row1)
			row = cursor.fetchone()
		return jsonify(result)
		

@application.route('/searchLocationRange', methods=['POST','GET'])
def searchLocationRange():
	if request.method == 'POST':
		data = request.form
		sql = "SELECT * FROM earthquake WHERE latitude between " + data['latitude1'] + " and " + data['latitude2'] + " and longitude between " + data['longitude1'] + " and " + data['longitude2'] + ";"
		cursor.execute(sql)
		row = cursor.fetchone()
		result = []
		while row:
			row1 = [str(i) for i in row]
			result.append(row1)
			row = cursor.fetchone()
		return jsonify(result)


if __name__ == '__main__':
	application.run()

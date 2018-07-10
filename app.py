import matplotlib
matplotlib.use('Agg')
import sys
from flask import Flask,render_template,request
import time   #query time-
import cStringIO
import pymysql
from azure.storage.blob import PublicAccess
from flask import Flask
from azure.storage.blob import BlockBlobService
from azure.storage.blob import ContentSettings
from flask import render_template
from flask import request
import glob
import os
import datetime
import hashlib
import pickle as cPickle
import csv
import pylab
from werkzeug.utils import secure_filename

hostname = ''
username = ''
password = ''
database = ''

#myConnection = pymysql.connect( host=hostname, user=username, passwd=password, db=database, cursorclass=pymysql.cursors.DictCursor, local_infile=True)
myConnection = pymysql.connect( host=hostname, user=username, passwd=password, db=database, cursorclass=pymysql.cursors.DictCursor, local_infile=True)
print 'DB connected'

#blob
block_csv = BlockBlobService(account_name='', account_key='')
print ('Blob connected')


application = Flask(__name__)
app=application

APP_ROOT = os.path.dirname(os.path.abspath(__file__))
BASE_ROOT = os.path.dirname(APP_ROOT)
print APP_ROOT

@app.route('/')
def main():
	return render_template("index.html")

@app.route("/upload", methods = ['POST'])
def csv_upload():
	user_act=request.form['shilpa']
	username_be=request.form['username']
	password_be=request.form['password']
	query="select * from students where Username='"+username_be+"' and Password='"+password_be+"'"
	print (query)
	with myConnection.cursor() as cursor:
		cursor.execute(query)
		row_count = cursor.rowcount
		if row_count==0:
			return "Invalid Credentials"
		else:	
			print (user_act)
			if user_act=="1":
				return render_template("Upload.html")
			elif user_act=="2":
				query_course="select distinct CourseNo from classes"
				cursor.execute(query_course)
				result=cursor.fetchall()					
				return render_template("CourseList.html", res=result, studentid=username_be)
			elif user_act=="3":
				return render_template("filehandle.html")
	cursor.close()
	return "failure"


@app.route("/uploadCsv", methods = ['POST'])
def csv_uploadCsv():
	global file_name
	f=request.files['upload_files']
	file_name=f.filename	
	print (file_name)
	titlename=request.form['file']
	global newfile
	newfile=os.path.abspath(file_name)
	print "new file down"
	print newfile
	block_csv.create_blob_from_path('shilpashreesvp',file_name,newfile,content_settings=ContentSettings(content_type='text/csv'))
	return "done"

@app.route("/load_db", methods = ['POST'])
def load_db():#For uploading the file
	#global file_name'
	UPLOAD_FOLDER="/home/shilpashree/cdassign/"
	csv_file = request.files['file_upload']	
	file_name=csv_file.filename
	#session['file_name']=file_name
	print "file recieved"
	#filename = secure_filename(csv_file.filename)
	#csv_file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
	drop_query="drop table IF EXISTS "+ file_name[:-4]
	with myConnection.cursor() as cursor:
		#self.cursor.execute(drop_query)
		myConnection.commit()
	print "dropped"
	column_name="("
	abs_filename=UPLOAD_FOLDER+file_name
	with open(abs_filename, 'r') as f:
		reader = csv.reader(f)
		for row in reader:
			line=row
			break
	for i in line:
		column_name+=i+" VARCHAR(50),"
	query="Create table if not exists " + file_name[:-4]+column_name+" sr_no INT NOT NULL AUTO_INCREMENT, PRIMARY KEY(sr_no));"
	print query
	starttime = time.time()
	with myConnection.cursor() as cursor:
		cursor.execute(query)
		myConnection.commit()
	cursor.close()
	print "successfully created"
	#insert_str = r"LOAD DATA LOCAL INFILE + abs_filename + INTO TABLE + file_name[:-4]+  FIELDS TERMINATED BY ',' ENCLOSED BY '"' LINES TERMINATED BY '\n' IGNORE 1 lines"
   	#newline="\\\n"
	#new_char=newline[1:3]
	#print new_char
	insert_str="""LOAD DATA LOCAL INFILE '"""+abs_filename+ """' INTO TABLE """+ file_name[:-4] +""" FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '"' LINES TERMINATED BY '\n' IGNORE 1 ROWS;"""
	print (insert_str)
	with myConnection.cursor() as cursor:
		cursor.execute(insert_str)
		myConnection.commit()
	endtime = time.time()
	count_str="SELECT count(*) FROM "+ file_name[:-4]
	with myConnection.cursor() as cursor:
		cursor.execute(count_str)
		result=cursor.fetchall()
	print "successfully loaded"
	totalsqltime = endtime - starttime 
	return render_template("index.html")

@app.route("/instruct", methods = ['POST'])
def instruct():#For uploading the file
	username_be=request.form['inst']
	query="select * from classes where Instructor='"+username_be+"'"
	print (query)
	with myConnection.cursor() as cursor:
		cursor.execute(query)
		result=cursor.fetchall()
	print "successfully executed"
	return render_template("filehandle.html",res=result)

@app.route("/courseslist", methods=['POST'])
def courseslist():
	course_name=request.form['coursename']
	studentid=request.form['sid']
	print (course_name)
	print (studentid)
	query="insert into enroll values('"+course_name+"','"+studentid+"')"
	print (query)
	with myConnection.cursor() as cursor:
		cursor.execute(query)
		myConnection.commit()
	cursor.close()
	print "successful"
	return render_template("filehandle.html")

if __name__ == "__main__":
	app.run(debug=True,host='0.0.0.0')


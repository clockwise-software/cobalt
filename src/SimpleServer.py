## CLOCKWISE-BOOTCAMP SimpleServer.py 
## Based on Server from Dr. Ian Cooper @ Cardiff
## Updated by Dr. Mike Borowczak @ UWyo March 2021

import os
from flask import Flask, redirect, request, render_template, jsonify, make_response
import sqlite3
import DBUtils

DATABASE = 'employee.db'

app = Flask(__name__)

@app.route("/")
def basic():
    return render_template('Employee.html')

@app.route("/Filter")
def filter():
    filter1 = request.args.getlist('filter1')
    print("Filter 1: " + str(filter1))
    conn = sqlite3.connect(DATABASE)
    cur = conn.cursor()
    cur.execute("SELECT * FROM 'license'")
    licenseData = cur.fetchall()
    cur.execute("SELECT * FROM 'skill' ORDER BY Skill")
    skillData = cur.fetchall()
    cur.execute("SELECT DISTINCT SkillLevel FROM 'EmployeeList' WHERE SkillLevel <> ''")
    skillLevelData = cur.fetchall()
    cur.execute("SELECT DISTINCT StateProvince from 'EmployeeList' ORDER BY StateProvince")
    locationData = cur.fetchall()
    return render_template('EmployeeFilter.html', filter1=filter1, licenseData=licenseData, skillData=skillData, skillLevelData=skillLevelData, locationData = locationData)

@app.route("/FilterSearch")
def filterFind():
    filter1 = request.args.getlist('filter1')
    filter2 = request.args.getlist('filter2')
    filter3 = request.args.getlist('filter3')
    filter4 = request.args.getlist('filter4')
    if (len(filter1) == 0 and len(filter2) == 0 and len(filter3) == 0 and len(filter4) == 0):
        html = render_template('EmployeeFilterResults.html', employeeList=[])
        return make_response(jsonify({"html": html}))
    conn = sqlite3.connect(DATABASE)
    cur = conn.cursor()
    sql = ''
    params = []
    for filter in filter1:
        if (sql != ''):
            sql += " or "
        sql += "RegisteredLicenses like ?"
        params.append("%" + filter + "%")
    for filter in filter2:
        if (sql != ''):
            sql += " or "
        sql += "skill like ?"
        params.append("%" + filter + "%")
    for filter in filter3:
        if (sql != ''):
            sql += " or "
        sql += "skillLevel like ?"
        params.append("%" + filter + "%")
    for filter in filter4:
        if (sql != ''):
            sql += " or "
        sql += "StateProvince like ?"
        params.append("%" + filter + "%")
    sql = "select * from EmployeeList where " + sql
    print(sql)
    print(params)
    cur.execute(sql,params)
    employeeList = cur.fetchall()
    employeeList = DBUtils.convertToDictionary(cur,employeeList)
    print(employeeList)
    html = render_template('EmployeeFilterResults.html', employeeList=employeeList)
    return make_response(jsonify({"html": html}))
    ## return render_template('EmployeeFilterResults.html', employeeList=employeeList)

@app.route("/Employee/AddEmployee", methods = ['POST','GET'])
def studentAddDetails():
	if request.method =='GET':
		return render_template('EmployeeData.html')
	if request.method =='POST':
		firstName = request.form.get('firstName', default="Error") 
		lastName = request.form.get('lastName', default="Error")
		businessunit = request.form.get('bu', default="Error")
		state = request.form.get('state', default="Error")
		print("inserting employee"+firstName)
		try:
			conn = sqlite3.connect(DATABASE)
			cur = conn.cursor()
			cur.execute("INSERT INTO EmployeeList ('FirstName', 'LastName', 'Business Unit', 'State/Province')\
						VALUES (?,?,?,?)",(firstName, lastName, businessunit, state ) )

			conn.commit()
			msg = "Record successfully added"
		except:
			conn.rollback()
			msg = "error in insert operation"
		finally:
			conn.close()
			return msg

@app.route("/Employee/Search", methods = ['GET','POST'])
def surnameSearch():
	if request.method =='GET':
		return render_template('EmployeeSearch.html')
	if request.method =='POST':
		try:
			lastName = request.form.get('lastName', default="Error") #rem: args for get form for post
			conn = sqlite3.connect(DATABASE)
			cur = conn.cursor()
			cur.execute("SELECT * FROM 'EmployeeList' WHERE LastName=?", [lastName])
			data = cur.fetchall()
			print(data)
		except:
			print('there was an error', data)
			conn.close()
		finally:
			conn.close()
			#return str(data)
			return render_template('Employee.html', data = data)



# The name says it...
@app.route("/Employee/VulnerableSearch", methods = ['GET','POST'])
def surnameInjectionSearch():
	if request.method =='GET':
		return render_template('EmployeeSQLInjection.html')
	if request.method =='POST':
		lastName = request.form.get('lastName', default="Error") #rem: args for get form for post
		conn = sqlite3.connect(DATABASE)
		cur = conn.cursor()
		
		# VERY BAD VERY BAD VERY BAD VERY BAD VERY BAD VERY BAD VERY BAD VERY BAD VERY BAD VERY BAD
		query = "SELECT * FROM EmployeeList WHERE lastname= '%s' " % (lastName,)
		print (query)
		cur.execute(query)
		# VERY BAD VERY BAD VERY BAD VERY BAD VERY BAD VERY BAD VERY BAD VERY BAD VERY BAD VERY BAD
		
		data = cur.fetchall()
		print (data)
		print (lastName)
		conn.close()
		return render_template('Employee.html', data = data)


if __name__ == "__main__":
	app.run(debug=True)
	app.run(host='0.0.0.0', port=5000)

# CLOCKWISE-BOOTCAMP SimpleServer.py
# Based on Server from Dr. Ian Cooper @ Cardiff
# Updated by Dr. Mike Borowczak @ UWyo March 2021

import os
from flask import Flask, redirect, request, render_template
import sqlite3

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
    cur.execute("SELECT * FROM 'skill'")
    skillData = cur.fetchall()
    cur.execute("SELECT DISTINCT SkillLevel FROM 'EmployeeList'")
    skillLevelData = cur.fetchall()
    return render_template('EmployeeFilter.html', filter1=filter1, licenseData=licenseData, skillData=skillData, skillLevelData=skillLevelData)

@app.route("/Employee/AddEmployee", methods = ['POST','GET'])
def studentAddDetails():
    if request.method == 'GET':
        return render_template('EmployeeData.html')
    if request.method == 'POST':
        firstName = request.form.get('firstName', default="Error")
        lastName = request.form.get('lastName', default="Error")
        businessunit = request.form.get('bu', default="Error")
        state = request.form.get('state', default="Error")
        print("inserting employee"+firstName)
        try:
            conn = sqlite3.connect(DATABASE)
            cur = conn.cursor()
            cur.execute("INSERT INTO EmployeeList ('FirstName', 'LastName', 'BusinessUnit', 'StateProvince')\
						VALUES (?,?,?,?)", (firstName, lastName, businessunit, state))

            conn.commit()
            msg = "Record successfully added"
        except:
            conn.rollback()
            msg = "error in insert operation"
        finally:
            conn.close()
            return msg


@app.route("/Employee/Search", methods=['GET', 'POST'])
def surnameSearch():
    if request.method == 'GET':
        return render_template('EmployeeSearch.html')
    if request.method == 'POST':
        try:
            # rem: args for get form for post
            lastName = request.form.get('lastName', default="Error")
            conn = sqlite3.connect(DATABASE)
            cur = conn.cursor()
            cur.execute(
                "SELECT * FROM 'EmployeeList' WHERE LastName=?", [lastName])
            data = cur.fetchall()
            print(data)
        except:
            print('there was an error', data)
            conn.close()
        finally:
            conn.close()
            # return str(data)
            return render_template('Employee.html', data=data)


@app.route("/Employee/UpdateEmployee", methods=['POST', 'GET'])
def studentUpdateDetails():
    xid = request.args.get('xid', default="12") #default value so webpage loads for now, as it must be given an xid value. later xid value will be sent via which emp has their "edit" button clicked on on another webpage
    if request.method == 'GET':
        print("label"+xid)
        try:
            # rem: args for get form for post
            conn = sqlite3.connect(DATABASE)
            cur = conn.cursor()
            cur.execute("SELECT * FROM 'EmployeeList' WHERE Id=?", [xid])
            data = cur.fetchall()
            print(data)
        except:
            print('there was an error', data)
            conn.close()
        finally:
            conn.close()
            if data==[]:
                for i in range(len(data)):
                    data[i]=None
            employee = data[0]
            return render_template('EmployeeUpdate.html',data=employee)
    if request.method == 'POST':
        firstName = request.form.get('firstName', default="Error")
        lastName = request.form.get('lastName', default="Error")
        jobStatus = request.form.get('jobStatus', default="Error")
        businessUnit = request.form.get('businessUnit', default="Error")
        city = request.form.get('city', default="Error")
        state = request.form.get('state', default="Error")
        careerTitle = request.form.get('careerTitle', default="Error")
        totalYears = request.form.get('totalYears', default="Error")
        licenses = request.form.get('licenses', default="Error")
        skills = request.form.get('skills', default="Error")
        skillLevel = request.form.get('skillLevel', default="Error")
        lat = request.form.get('lat', default="Error")
        longi = request.form.get('longi', default="Error")
        isAvailable = request.form.get('isAvailable', default="Error")
        print("updating employee"+firstName)
        try:
            conn = sqlite3.connect(DATABASE)
            cur = conn.cursor()
            cur.execute("UPDATE 'EmployeeList' SET 'FirstName'=?, 'LastName'=?, 'JobStatus'=?, 'BusinessUnit'=?,\
                'City'=?, 'StateProvince'=?, 'CareerMatrixTitle'=?, 'TotalYears'=?, 'RegisteredLicenses'=?,\
                    'Skill'=?, 'SkillLevel'=?, 'Lat'=?, 'Long'=?, 'IsAvailable'=? WHERE Id=?\
                        ", (firstName, lastName, jobStatus, businessUnit, city, state, careerTitle, totalYears, licenses, skills, skillLevel, lat, longi, isAvailable, xid))

            conn.commit()
            msg = "Record successfully updated"
        except:
            conn.rollback()
            msg = "error in update operation"
        finally:
            conn.close()
            return msg

@app.route("/Employee/DeleteEmployee", methods = ['POST','GET'])
def studentDeleteDetails():
    if request.method == 'GET':
        return render_template('EmployeeDelete.html')
    if request.method == 'POST':
        firstName = request.form.get('firstName', default="Error")
        lastName = request.form.get('lastName', default="Error")
        print("deleting employee"+firstName)
        try:
            conn = sqlite3.connect(DATABASE)
            cur = conn.cursor()
            cur.execute("DELETE FROM 'EmployeeList' WHERE FirstName=? AND LastName=?", (firstName, lastName))

            conn.commit()
            msg = "Record successfully deleted" #the deletion works but this doesn't print on the webpage, not sure why
        except:
            conn.rollback()
            msg = "error in delete operation"
        finally:
            conn.close()
            return msg


# The name says it...
# @app.route("/Employee/VulnerableSearch", methods = ['GET','POST'])
# def surnameInjectionSearch():
#	if request.method =='GET':
#		return render_template('EmployeeSQLInjection.html')
#	if request.method =='POST':
#		lastName = request.form.get('lastName', default="Error") #rem: args for get form for post
#		conn = sqlite3.connect(DATABASE)
#		cur = conn.cursor()

        # VERY BAD VERY BAD VERY BAD VERY BAD VERY BAD VERY BAD VERY BAD VERY BAD VERY BAD VERY BAD
#		query = "SELECT * FROM EmployeeList WHERE lastname= '%s' " % (lastName,)
#		print (query)
#		cur.execute(query)
        # VERY BAD VERY BAD VERY BAD VERY BAD VERY BAD VERY BAD VERY BAD VERY BAD VERY BAD VERY BAD

#		data = cur.fetchall()
#		print (data)
#		print (lastName)
#		conn.close()
#		return render_template('Employee.html', data = data)

if __name__ == "__main__":
    app.run(debug=True)
    app.run(host='0.0.0.0', port=5000)

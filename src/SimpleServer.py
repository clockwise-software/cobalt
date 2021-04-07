# CLOCKWISE-BOOTCAMP SimpleServer.py
# Based on Server from Dr. Ian Cooper @ Cardiff
# Updated by Dr. Mike Borowczak @ UWyo March 2021

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

@app.route("/AdminView")
def test():
    conn = sqlite3.connect(DATABASE)
    cur = conn.cursor()
    cur.execute("SELECT * FROM 'EmployeeList'")
    employeeList = cur.fetchall()
    conn.close()
    employeeList = DBUtils.convertToDictionary(cur,employeeList)
    return render_template('EmployeeData2.html', employeeList=employeeList)


@app.route("/Employee/AddEmployee", methods = ['POST','GET'])
def studentAddDetails():
    if request.method == 'GET':
        return render_template('EmployeeData.html')
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
        isAvailable = request.form.get('isAvailable', default="Error")
        print("inserting employee"+firstName)
        try:
            conn = sqlite3.connect(DATABASE)
            cur = conn.cursor()
            cur.execute("INSERT INTO EmployeeList ('FirstName', 'LastName', 'JobStatus', 'BusinessUnit', 'City', 'StateProvince', 'CareerMatrixTitle', \
						'TotalYears', 'RegisteredLicenses', 'Skill', 'SkillLevel', 'IsAvailable') VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)\
                        ", (firstName, lastName, jobStatus, businessUnit, city, state, careerTitle, totalYears, licenses, skills, skillLevel, isAvailable))

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
        isAvailable = request.form.get('isAvailable', default="Error")
        print("updating employee"+firstName)
        try:
            conn = sqlite3.connect(DATABASE)
            cur = conn.cursor()
            cur.execute("UPDATE 'EmployeeList' SET 'FirstName'=?, 'LastName'=?, 'JobStatus'=?, 'BusinessUnit'=?,\
                'City'=?, 'StateProvince'=?, 'CareerMatrixTitle'=?, 'TotalYears'=?, 'RegisteredLicenses'=?,\
                    'Skill'=?, 'SkillLevel'=?, 'IsAvailable'=? WHERE Id=?\
                        ", (firstName, lastName, jobStatus, businessUnit, city, state, careerTitle, totalYears, licenses, skills, skillLevel, isAvailable, xid))

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

if __name__ == "__main__":
    app.run(debug=True)
    app.run(host='0.0.0.0', port=5000)

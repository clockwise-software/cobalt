# CLOCKWISE-BOOTCAMP SimpleServer.py
# Based on Server from Dr. Ian Cooper @ Cardiff
# Updated by Dr. Mike Borowczak @ UWyo March 2021

import os
from flask import Flask, redirect, request, render_template, jsonify, make_response
import sqlite3
import DBUtils
import csv
import io
import json

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
    # Get Filters from args
    filter1 = request.args.getlist('filter1')
    filter2 = request.args.getlist('filter2')
    filter3 = request.args.getlist('filter3')
    filter4 = request.args.getlist('filter4')

    # Check that not all filters are empty
    if (len(filter1) == 0 and len(filter2) == 0 and len(filter3) == 0 and len(filter4) == 0):
        html = render_template('EmployeeFilterResults.html', employeeList=[], mapList=[])
        return make_response(jsonify({"html": html}))
    
    # Build search string for each filter
    f1 = "(" + (" or ").join([f"a.RegisteredLicenses like '%{f}%'" for f in filter1]) + ")"
    f2 = "(" + (" or ").join([f"a.skill like '%{f}%'" for f in filter2]) + ")"
    f3 = "(" + (" or ").join([f"a.skillLevel like '%{f}%'" for f in filter3]) + ")"
    f4 = "(" + (" or ").join([f"a.StateProvince like '%{f}%'" for f in filter4]) + ")"

    # Combine filters and build sql string
    f_strings = []
    if len(f1) > 2: f_strings.append(f1)
    if len(f2) > 2: f_strings.append(f2)
    if len(f3) > 2: f_strings.append(f3)
    if len(f4) > 2: f_strings.append(f4)
    sql = (" and ").join(f_strings)
    #sql = "select * from EmployeeList where " + sql 
    sql = "select a.*, b.lat as lat2, b.lng as lng2 from EmployeeList as a left join cities as b on b.city = a.City and b.stateName = a.StateProvince where " + sql
    print("SQL:", sql)

    # Connect to database, query, and print results
    conn = sqlite3.connect(DATABASE)
    cur = conn.cursor()
    cur.execute(sql)
    employeeList = cur.fetchall()
    employeeList = DBUtils.convertToDictionary(cur,employeeList)

    # Provide a second list for just the mapping function
    params = []
    for filter in filter1 + filter2 + filter3 + filter4:
        params.append("%" + filter + "%")
    sql = sql + " order by a.StateProvince, a.City"
    cur.execute(sql,params)
    employeeList2 = cur.fetchall()
    employeeList2 = DBUtils.convertToDictionary(cur,employeeList2)
    html = render_template('EmployeeFilterResults.html', employeeList=employeeList, mapList=json.dumps(employeeList2))
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
        conn = sqlite3.connect(DATABASE)
        cur = conn.cursor()
        cur.execute("SELECT city FROM cities")
        cities = cur.fetchall()
        cur.execute("SELECT Title FROM license")
        licenses = cur.fetchall()
        cur.execute("SELECT Skill FROM skill")
        skill = cur.fetchall()
        return render_template('EmployeeData.html',cities=cities,licenses=licenses,skill=skill)
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
						'TotalYears', 'RegisteredLicenses', 'Skill', 'SkillLevel', 'IsAvailable') VALUES (?,?,?,?,?,?,?,?,?,?,?,?)\
                        ", (firstName, lastName, jobStatus, businessUnit, city, state, careerTitle, totalYears, licenses, skills, skillLevel, isAvailable))

            conn.commit()
            msg = "Record successfully added"
        except:
            conn.rollback()
            msg = "error in insert operation"
        finally:
            conn.close()
            return msg


@app.route("/ImportEmployees", methods=['POST'])
def importEmployees():
    #fileitem = request.form['filename']
    fileitem = request.files['filename']
    if fileitem.filename:
        # strip the leading path from the file name
        csv_bytes = fileitem.read()
        csv_string = csv_bytes.decode("utf-8")
        new_entries = csv.reader(csv_string.splitlines()[1:])
        print(new_entries)
        try:
            conn = sqlite3.connect(DATABASE)
            cur = conn.cursor()
            cur.executemany("INSERT INTO EmployeeList ('FirstName','LastName','JobStatus','BusinessUnit','City','StateProvince','CareerMatrixTitle','TotalYears','RegisteredLicenses','Skill','SkillLevel','Lat','Long','IsAvailable') VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)", new_entries)
            conn.commit()
            print("Records successfully added")
        except:
            conn.rollback()
            print("error in import operation")
        finally:
            conn.close()
            return render_template('EmployeeFilter.html')
    else:
        print("No File given")
        return render_template('EmployeeData.html')
        

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
    xid = request.args.get('xid', default="2")
    if request.method == 'GET':
        print("label"+xid)
        conn = sqlite3.connect(DATABASE)
        cur = conn.cursor()
        cur.execute("SELECT city FROM cities")
        cities = cur.fetchall()
        cur.execute("SELECT Title FROM license")
        licenses = cur.fetchall()
        cur.execute("SELECT Skill FROM skill")
        skill = cur.fetchall()
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
            return render_template('EmployeeUpdate.html',data=employee,cities=cities,licenses=licenses,skill=skill)
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

@app.route("/Employee/DeleteEmployee", methods = ['POST', 'GET'])
def studentDeleteDetails():
    if request.method == 'POST':
        xid = request.form.get('dxid', default="1")
        print("deleting employee"+xid)
        try:
            conn = sqlite3.connect(DATABASE)
            cur = conn.cursor()
            cur.execute("DELETE FROM 'EmployeeList' WHERE ID=?", [xid])

            conn.commit()
            msg = "Record successfully deleted" 
        except:
            conn.rollback()
            msg = "error in delete operation"
        finally:
            conn.close()
            return msg

if __name__ == "__main__":
    app.run(debug=True)
    app.run(host='0.0.0.0', port=5000)

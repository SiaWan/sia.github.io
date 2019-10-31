from flask import Flask, render_template, request, jsonify, redirect, url_for
import requests
import bcrypt

app = Flask(__name__)

@app.route("/")
def home():
    return render_template('home.html', message="Welcome to Gift4You", user="")

@app.route("/giftCollection")
def table():
    headers = {
        'Authorization': 'Bearer keyZvXD7UzKgvfgi1',
    }
    r = requests.get('https://api.airtable.com/v0/appfbBjdbuy7p94lH/Sneaks?maxRecords=5&view=Gallery', headers=headers)
    dict = r.json()
    dataset = []
    for i in dict['records']:
         dataset.append(i['fields'])
    return render_template('table.html', entries=dataset)


@app.route("/user")
def user():
    return render_template('userform.html')

@app.route("/adduser",methods=['POST', 'GET'])
def adduser():
    fname = request.form['fname']
    lname = request.form['lname']
    date_of_birth = request.form['date_of_birth']
    pwd = request.form['pwd']
    pwd = pwd.encode('UTF-8')
    mydict = {
        "firstName": fname,
        "lastName": lname,
        "birthday": date_of_birth,
        'password': pwd
    }
    data = {"fields": mydict }
    headers = {'Authorization': 'Bearer keyZvXD7UzKgvfgi1', 'Content-Type': 'application/json; charset=utf-8'}
    r = requests.post('https://api.airtable.com/v0/appfbBjdbuy7p94lH/Users',json=data,headers=headers)
    return render_template('home.html',message="Thanks for signing up!")

@app.route("/updateuser",methods=['POST','PUT'])
def updateuser():
    record_id = request.form['record_id']
    headers = {
        'Authorization': 'Bearer keyZvXD7UzKgvfgi1',
    }
    r = requests.get('https://api.airtable.com/v0/appfbBjdbuy7p94lH/Users/' + record_id, headers=headers)

    if not r.json:
        return render_template('home.html', message="User not exist!")

    dict = r.json()
    dict_list = dict['fields']
    for i in dict_list:
        if (i == 'password'):
            pwd = dict_list[i]

    fname = request.form['fname']
    lname = request.form['lname']
    date_of_birth = request.form['date_of_birth']

    fields = {
    "firstName": fname,
    "lastName": lname,
    "birthday": date_of_birth,
    "password": pwd
    }

    data = {
      "records": [
          {
          "id": record_id,
          "fields": fields
          }
      ]
    }

    headers = {'Authorization': 'Bearer keyZvXD7UzKgvfgi1', 'Content-Type': 'application/json; charset=utf-8'}
    r = requests.put('https://api.airtable.com/v0/appfbBjdbuy7p94lH/Users',json=data,headers=headers)
    return render_template('home.html',message="Successfully updated")

@app.route("/deleteuser",methods=['POST','DELETE'])
def deleteuser():
    record_id = request.form['record_id']
    headers = {
        'Authorization': 'Bearer keyZvXD7UzKgvfgi1',
    }
    r = requests.get('https://api.airtable.com/v0/appfbBjdbuy7p94lH/Users/' + record_id, headers=headers)
    if not r.json:
        message="User not exist!"
    else:
        message="Time to say goodbye!"

    url = "https://api.airtable.com/v0/appfbBjdbuy7p94lH/Users/"
    headers = {'Authorization': 'Bearer keyZvXD7UzKgvfgi1', 'Content-Type': 'application/x-www-form-urlencoded'}
    r = requests.delete(url + record_id, headers=headers)

    return render_template('home.html', message=message)

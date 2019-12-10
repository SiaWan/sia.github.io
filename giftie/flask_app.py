from flask import Flask, render_template, request, flash, redirect, url_for, session
from flask_login import LoginManager, login_user, logout_user, login_required, UserMixin
from datetime import timedelta
import requests
import bcrypt
import random

app = Flask(__name__)

# config
app.secret_key = b"\xa8\xe6\xfa\xf3/\xc2\xe4r\x804\x83\xd2\xeb!\x8a'\\\x12\xdd\x1e!\xec\x90\xfd"

# flask-login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "signin"  # unauthenticated redirect


@login_manager.user_loader  # reload user object
def load_user(user_id):
    # if all data in session
    if user_id and ("email" in session) and ("username" in session) and ("subscribe" in session):
        # user data from session
        email = session["email"]
        username = session["username"]
        subscribe = session["subscribe"]

        return User(user_id, username, email, subscribe)

    return None


# user
class User(UserMixin):
    def __init__(self, user_id, username, email, subscribe):
        self.id = user_id
        self.username = username
        self.email = email
        self.subscribe = subscribe


@app.route("/")
@app.route("/home")
def home():
    return render_template('home.html')


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/gifts")
@app.route("/gifts/<personality>")
def gifts(personality=1):
    # gifts data page 1
    headers = {
        'Authorization': 'Bearer keyZvXD7UzKgvfgi1',
    }
    r = requests.get(
        'https://api.airtable.com/v0/appfnMQGqRHw0PWOl/gifts?sort%5B0%5D%5Bfield%5D=personality' + str(personality)
        + '&sort%5B0%5D%5Bdirection%5D=desc',
        headers=headers)
    js = r.json()
    data = []
    for i in js['records']:
        data.append(i['fields'])

    # gift data next pages
    while "offset" in js:
        offset = js["offset"]
        r = requests.get(
            'https://api.airtable.com/v0/appfnMQGqRHw0PWOl/gifts?sort%5B0%5D%5Bfield%5D=personality' + str(personality)
            + '&sort%5B0%5D%5Bdirection%5D=desc&offset=' + offset,
            headers=headers)
        js = r.json()
        for i in js['records']:
            data.append(i['fields'])

    return render_template("gifts.html", entries=data, p=str(personality))


@app.route("/updateGifts", methods=["POST", "PUT"])
def update_gifts():
    # form body
    product_id = request.form["product"]
    tag = request.form["tag"]

    # find product
    headers = {
        'Authorization': 'Bearer keyZvXD7UzKgvfgi1',
    }

    filter_formula = "IF({product_id}='" + product_id + "', 1, 0)"

    params = (
        ('view', 'Grid view'),
        ('filterByFormula', filter_formula),
    )

    r = requests.get(
        "https://api.airtable.com/v0/appfnMQGqRHw0PWOl/gifts",
        headers=headers, params=params)
    js = r.json()
    data = {}

    for i in js['records']:
        data = i["fields"]
    personality = "personality" + tag
    old = data[personality]

    data[personality] = old + 1

    data = {
        "records": [
            {
                "id": product_id,
                "fields": {
                    "product_url": data["product_url"],
                    "product_price": data["product_price"],
                    "image_url": data["image_url"],
                    "product_name": data["product_name"],
                    "personality1": data["personality1"],
                    "personality4": data["personality4"],
                    "personality3": data["personality3"],
                    "personality2": data["personality2"]
                }
            }
        ]
    }

    headers = {'Authorization': 'Bearer keyZvXD7UzKgvfgi1', 'Content-Type': 'application/json; charset=utf-8'}
    r = requests.put('https://api.airtable.com/v0/appfnMQGqRHw0PWOl/gifts', json=data, headers=headers)

    # update page
    if r.status_code == 200:
        flash("Tagged successfully!")
    else:
        flash("Tagging failed!")
    return redirect(url_for('survey'))


@app.route("/survey")
def survey():
    index = random.randint(1, 218)
    # find users by email
    headers = {
        'Authorization': 'Bearer keyZvXD7UzKgvfgi1',
    }

    filter_formula = "IF({index}=" + str(index) + ", 1, 0)"

    params = (
        ('view', 'Grid view'),
        ('filterByFormula', filter_formula),
    )

    r = requests.get(
        "https://api.airtable.com/v0/appfnMQGqRHw0PWOl/gifts",
        headers=headers, params=params)
    js = r.json()
    data = []

    for i in js["records"]:
        data.append(i["fields"])
    return render_template("survey.html", data=data[0])


@app.route("/signin")
def signin():
    return render_template("signin.html")


@app.route("/process", methods=["POST"])
def process():
    # form body
    email = request.form["email"]
    password = request.form["password"]
    remember = "remember" in request.form  # true or false

    # find users
    headers = {
        'Authorization': 'Bearer keyZvXD7UzKgvfgi1',
    }

    filter_formula = "IF({email}='" + email + "', 1, 0)"

    params = (
        ('view', 'Grid view'),
        ('filterByFormula', filter_formula),
    )

    requests.session()
    r = requests.get(
        "https://api.airtable.com/v0/appfnMQGqRHw0PWOl/user_info",
        headers=headers, params=params)

    user = []
    if 'records' in r.json():
        for i in r.json()['records']:
            user = i['fields']  # unique email

    # user not exist
    if not user:
        flash("User not exist!")

    # check password
    if user:
        hashed = user.get("password")

        # encoding
        hashed = hashed.encode('utf-8')
        password = password.encode('utf-8')

        if bcrypt.checkpw(password, hashed):

            # user data
            record_id = user["record_id"]
            username = user["username"]
            email = user["email"]
            subscribe = "subscribe" in user  # true or false

            # create session
            login_user(User(record_id, username, email, subscribe), remember=remember, duration=timedelta(hours=1))
            session["username"] = username
            session["email"] = email
            session["subscribe"] = subscribe
            flash("You've successfully signed in!")

            # go back or redirect
            next = request.args.get('next')
            return redirect(next or url_for("home"))

        else:
            flash("Wrong password!")

    return redirect(url_for("signin"))


@app.route("/signout")
@login_required
def signout():
    logout_user()
    flash('You have logged off.')
    return redirect(url_for("signin"))


@app.route("/signup")
def signup():
    return render_template("/signup.html")


@app.route("/addUser", methods=["POST"])
def add_user():
    # form body
    username = request.form['username']
    email = request.form['email']
    password = request.form['password']
    subscribe = "subscribe" in request.form  # true or false

    # find users by email
    headers = {
        'Authorization': 'Bearer keyZvXD7UzKgvfgi1',
    }

    filter_formula = "IF({email}='" + email + "', 1, 0)"

    params = (
        ('view', 'Grid view'),
        ('filterByFormula', filter_formula),
    )

    r = requests.get(
        "https://api.airtable.com/v0/appfnMQGqRHw0PWOl/user_info",
        headers=headers, params=params)

    user = []
    for i in r.json()['records']:
        user = i['fields']

    # user exist
    if user:
        flash("User exists!")
        redirect(url_for("signup"))

    # bcrypt
    password = password.encode('utf-8')
    salt = bcrypt.gensalt()
    password = bcrypt.hashpw(password, salt)  # byte

    # create entry
    data = {
        "fields": {
            'username': username,
            'email': email,
            'password': password,
            'subscribe': subscribe
        }
    }

    headers = {'Authorization': 'Bearer keyZvXD7UzKgvfgi1', 'Content-Type': 'application/json; charset=utf-8'}
    r = requests.post('https://api.airtable.com/v0/appfnMQGqRHw0PWOl/user_info', json=data, headers=headers)

    # success
    if r.status_code == 200:
        flash("You've sucessfully registered!")

    return redirect(url_for('home'))


@app.route("/profile")
@login_required
def profile():
    return render_template("profile.html")


@app.route("/updateUser", methods=['POST', 'PUT'])
@login_required
def update_user():
    # get user id
    record_id = session['user_id']

    # find user password
    headers = {
        'Authorization': 'Bearer keyZvXD7UzKgvfgi1',
    }
    r = requests.get('https://api.airtable.com/v0/appfnMQGqRHw0PWOl/user_info/' + record_id, headers=headers)

    password = r.json()["fields"]["password"]

    # new data
    data = request.form
    username = data["username"]
    email = data["email"]
    subscribe = "subscribe" in data

    data = {
        "records": [
            {
                "id": record_id,
                "fields": {
                    "username": username,
                    "email": email,
                    "subscribe": subscribe,
                    "password": password
                }
            }
        ]
    }

    headers = {'Authorization': 'Bearer keyZvXD7UzKgvfgi1', 'Content-Type': 'application/json; charset=utf-8'}
    r = requests.put('https://api.airtable.com/v0/appfnMQGqRHw0PWOl/user_info', json=data, headers=headers)

    # update page
    if r.status_code == 200:
        print("here")
        flash("Updated successfully!")
        session["username"] = username
        session["email"] = email
        session["subscribe"] = subscribe
    else:
        flash("Update failed!")

    return redirect(url_for("profile"))


@app.route("/deleteUser", methods=['POST', 'DELETE'])
def delete_user():
    record_id = session['user_id']

    url = "https://api.airtable.com/v0/appfnMQGqRHw0PWOl/user_info/"
    headers = {'Authorization': 'Bearer keyZvXD7UzKgvfgi1', 'Content-Type': 'application/x-www-form-urlencoded'}
    r = requests.delete(url + record_id, headers=headers)
    if r.status_code == 200:
        flash("Sorry to see you left! We hope to see you again!")
    else:
        flash("Some error encountered! Your account has not been deleted!")
    return redirect(url_for("signout"))


@app.route("/addOrder/<product>")
@login_required
def add_order(product):
    user = session["user_id"]

    # create entry
    data = {
        "records": [
            {
                "fields": {
                    "product_id": [product],
                    "user_id": [user]
                }
            }
        ]
    }

    headers = {'Authorization': 'Bearer keyZvXD7UzKgvfgi1', 'Content-Type': 'application/json; charset=utf-8'}
    r = requests.post('https://api.airtable.com/v0/appfnMQGqRHw0PWOl/order', json=data, headers=headers)

    # success
    if r.status_code == 200:
        flash("You've add this product to your cart!")
    else:
        flash("failed to add this product to your cart!")
    return redirect(url_for("gifts"))


@app.route("/deleteOrder/<order>")
@login_required
def delete_order(order):
    order_id = order

    url = "https://api.airtable.com/v0/appfnMQGqRHw0PWOl/order/"
    headers = {'Authorization': 'Bearer keyZvXD7UzKgvfgi1', 'Content-Type': 'application/x-www-form-urlencoded'}
    r = requests.delete(url + order_id, headers=headers)
    if r.status_code == 200:
        flash("This item has been removed from you Cart!")
    else:
        flash("Some error encountered! Your product has not been deleted!")
    return redirect(url_for("order"))


@app.route("/myCart")
@login_required
def order():
    user = session["user_id"]
    # find users by email
    headers = {
        'Authorization': 'Bearer keyZvXD7UzKgvfgi1',
    }

    filter_formula = "IF({user_id}='" + user + "', 1, 0)"

    params = (
        ('view', 'Grid view'),
        ('filterByFormula', filter_formula),
    )

    r = requests.get(
        "https://api.airtable.com/v0/appfnMQGqRHw0PWOl/order",
        headers=headers, params=params)
    js = r.json()
    data = []

    for i in js["records"]:
        data.append(i["fields"])

    return render_template("myCart.html", entries=data)

import os
from flask import Flask, flash, redirect, render_template, request, session, jsonify, url_for
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename
from flask_sqlalchemy import SQLAlchemy
from functools import wraps
import json
import base64

# Global Variables
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Setup folder for API Endpoint
# app.config['UPLOAD_FOLDER'] = "pest-advisor/captured"
# FOR TESTING
app.config['UPLOAD_FOLDER'] = "./captured"

# Converting binary image to readble image


def convert2base64(file):
    return base64.b64encode(file).decode('ascii')


app.jinja_env.filters["convert2base64"] = convert2base64

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
app.config["SECRET_KEY"] = "CSB02"
Session(app)


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


# Establish database connection
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///pestadvisor.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)


class user(db.Model):
    ID = db.Column("ID", db.Integer, nullable=False,
                   primary_key=True, autoincrement=True)
    Username = db.Column("Username", db.String(30),
                         nullable=False, unique=True)
    Email = db.Column("Email", db.String(125), nullable=False, unique=True)
    Password = db.Column("Password", db.String(100), nullable=False)
    Profile_Picture = db.Column("Profile_Picture", db.LargeBinary)

    farms = db.relationship('farm', backref='user',
                            lazy=True, cascade='all, delete-orphan')


class farm(db.Model):
    ID = db.Column("ID", db.Integer, nullable=False,
                   primary_key=True, autoincrement=True)
    User_ID = db.Column("User_ID", db.Integer, db.ForeignKey(
        'user.ID', ondelete='CASCADE'), nullable=False)
    Farm_Name = db.Column("Farm_Name", db.String(30),
                          nullable=False, unique=True)
    Farm_Picture = db.Column("Farm_Picture", db.LargeBinary)
    Latitude = db.Column("Latitude", db.Numeric)
    Longitude = db.Column("Longitude", db.Numeric)

    devices = db.relationship('device', backref='farm',
                              lazy=True, cascade='all, delete-orphan')

    images = db.relationship('capture', backref='farm',
                             lazy=True, cascade='all, delete-orphan')


class device(db.Model):
    ID = db.Column("ID", db.Integer, nullable=False,
                   primary_key=True, autoincrement=True)
    Farm_ID = db.Column("Farm_ID", db.Integer, db.ForeignKey(
        'farm.ID', ondelete='CASCADE'), nullable=False)
    Device_Name = db.Column("Device_Name", db.String(30),
                            nullable=False, unique=True)
    Latitude = db.Column("Latitude", db.Numeric)
    Longitude = db.Column("Longitude", db.Numeric)
    URL = db.Column("URL", db.String(255), nullable=False, unique=True)

    captures = db.relationship(
        'capture', backref='device', lazy=True, cascade='all, delete-orphan')


class capture(db.Model):
    ID = db.Column("ID", db.Integer, nullable=False,
                   primary_key=True, autoincrement=True)
    Device_ID = db.Column("Device_ID", db.Integer, db.ForeignKey(
        'device.ID', ondelete='CASCADE'), nullable=False)
    Farm_ID = db.Column("Farm_ID", db.Integer, db.ForeignKey(
        'farm.ID', ondelete='CASCADE'), nullable=False)
    Image_Name = db.Column("Image_Name", db.String(20), nullable=False)
    Image = db.Column("Image", db.LargeBinary, nullable=False)
    Date = db.Column("Date", db.Date, nullable=False)
    Time = db.Column("Time", db.Time, nullable=False)
    Prediction = db.Column("Prediction", db.LargeBinary, nullable=False)


def login_required(f):
    """
    Decorate routes to require login.

    https://flask.palletsprojects.com/en/1.1.x/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function


@app.route("/")
@login_required
def index():
    farms = farm.query.filter_by(User_ID=session["user_id"]).all()
    # Returning user's portfolio
    return render_template("index.html", farms=farms)


@app.context_processor
def utility_processor():
    def loadUsername():
        account = user.query.filter_by(ID=session["user_id"]).first()
        return account.Username

    def loadEmail():
        account = user.query.filter_by(ID=session["user_id"]).first()
        return account.Email

    return dict(loadUsername=loadUsername, loadEmail=loadEmail)


@app.route("/user_setting", methods=["POST"])
def userSetting():
    formType = request.form.get("form")
    account = user.query.filter_by(ID=session["user_id"]).first()

    if formType == "account":
        username = request.form.get("username")
        email = request.form.get("email")

        response = {'changed_both': False,
                    'changed_username': False, 'changed_email': False}

        if username == "" or email == "":
            return jsonify(response)

        if account.Username != username and account.Email != email:
            account.Username = username
            account.Email = email
            db.session.commit()
            response["changed_both"] = True
            return jsonify(response)

        elif account.Username != username:
            account.Username = username
            db.session.commit()
            response["changed_username"] = True
            return jsonify(response)

        elif account.Email != email:
            account.Email = email
            db.session.commit()
            response["changed_email"] = True
            return jsonify(response)

    elif formType == "security":
        oldPassword = request.form.get("oldPassword")
        newPassword = request.form.get("newPassword")
        repeatPassword = request.form.get("repeatPassword")

        response = {'wrong_password': False, 'password_different': False}

        if not check_password_hash(account.Password, oldPassword):
            response["wrong_password"] = True
            return jsonify(response)

        if newPassword != repeatPassword:
            response["password_different"] = True
            return jsonify(response)

        account.Password = generate_password_hash(newPassword)
        db.session.commit()
        return jsonify(response)

    elif formType == "delete-account":
        confirmPassword = request.form.get("confirmPassword")

        response = {'wrong_password': False}

        if not check_password_hash(account.Password, confirmPassword):
            response["wrong_password"] = True
            return jsonify(response)

        session.clear()

        db.session.delete(account)
        db.session.commit()
        return jsonify(response)


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method != "POST":
        # Forget any user_id
        session.clear()
        return render_template("login.html")

    if session.get("user_id") != None:
        print("index")
        return redirect("/")


@app.route("/logout", methods=['GET'])
def logout():
    session.clear()
    return redirect("/login")


@app.route("/check_signup", methods=['POST'])
def check_signup():
    form = request.form.get("form")

    if form == "first":
        email = request.form.get("email")
        password = request.form.get("password")

        response = {'wrong_email': False, 'wrong_password': False}

        # Query database for email
        account = user.query.filter_by(Email=email).first()
        if account == None:
            response["wrong_email"] = True
            return jsonify(response)

        # Ensure password is correct
        if not check_password_hash(account.Password, password):
            response["wrong_password"] = True
            return jsonify(response)

        if not response["wrong_email"] and not response["wrong_password"]:
            session["user_id"] = account.ID
            return jsonify(response)

    elif form == "second":
        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")
        repeatPass = request.form.get("repeatPassword")

        response = {'username_taken': False,
                    'email_taken': False, 'password_different': False}

        account = user.query.filter_by(Username=username).first()
        if account != None:
            response["username_taken"] = True
            return jsonify(response)

        account = user.query.filter_by(Email=email).first()
        if account != None:
            response["email_taken"] = True
            return jsonify(response)

        if password != repeatPass:
            response["password_different"] = True
            return jsonify(response)

        if not response["username_taken"] and not response["email_taken"] and not response["password_different"]:
            newUser = user(Username=username, Email=email,
                           Password=generate_password_hash(password))
            db.session.add(newUser)
            db.session.commit()
            account = user.query.filter_by(Email=email).first()
            session["user_id"] = account.ID
            return jsonify(response)


@app.route("/monitor")
@login_required
def monitor():
    farms = farm.query.filter_by(User_ID=session["user_id"]).all()

    return render_template("monitor.html", farms=farms)


@app.route("/add_farm", methods=['POST'])
def add_farm():
    farmName = request.form.get("farmName")
    latitude = request.form.get("latitude")
    longitude = request.form.get("longitude")
    id = session["user_id"]

    if latitude != "" and longitude != "":
        latitude = float(latitude)
        longitude = float(longitude)

    if 'farmPicture' in request.files:
        farmPicture = request.files['farmPicture'].read()
    else:
        farmPicture = ""

    if farmPicture == "" and latitude == "" and longitude == "":
        newFarm = farm(User_ID=id, Farm_Name=farmName)
        db.session.add(newFarm)
        db.session.commit()
        return 'Success'
    elif farmPicture != "" and latitude == "" and longitude == "":
        newFarm = farm(User_ID=id, Farm_Name=farmName,
                       Farm_Picture=farmPicture)
        db.session.add(newFarm)
        db.session.commit()
        return 'Success'
    elif farmPicture == "" and latitude != "" and longitude != "":
        newFarm = farm(User_ID=id, Farm_Name=farmName, Latitude=latitude,
                       Longitude=longitude)
        db.session.add(newFarm)
        db.session.commit()
        return 'Success'
    else:
        newFarm = farm(User_ID=id, Farm_Name=farmName, Farm_Picture=farmPicture,
                       Latitude=latitude, Longitude=longitude)
        db.session.add(newFarm)
        db.session.commit()
        return 'Success'


# TODO
# Change to dynamic link in future
# /monitor/[user]/[farm name]
@app.route("/monitor/farm")
@login_required
def farm_info():
    # Returning user's portfolio
    return render_template("farm.html")


@app.route("/organism")
@login_required
def organism():
    # Returning user's portfolio
    return render_template("organism.html")


# For receiving images from the Orange Pi PC
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/upload_image', methods=['GET', 'POST'])
def upload_image():
    image_info = json.loads(request.form['data'])
    print(image_info)

    if image_info.get('status') == "Fail":
        return redirect(request.url)

    # Receive the image data
    if 'image' not in request.files:
        return redirect(request.url)
    file = request.files['image']

    if file.filename == '':
        return redirect(request.url)

    # Create a directory called 'capture' if it doesn't exist
    # if not os.path.exists("pest-advisor/captured"):
    #     os.makedirs("pest-advisor/captured")

    # FOR TESTING
    if not os.path.exists("captured"):
        os.makedirs("captured")

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

    # Respond with a success message
    return jsonify({"message": "Image received and saved successfully"})


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        app.run(debug=True, host='0.0.0.0')

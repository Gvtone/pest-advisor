from datetime import datetime
import math
import os
from flask import Flask, flash, redirect, render_template, request, session, jsonify, url_for
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
from sqlalchemy.orm import joinedload
from functools import wraps
import json
import base64
from flask_apscheduler import APScheduler

from detect import predict, fileDatetime, stripExtension, requestJSON, latestFile, deleteFiles

# Global Variables
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

# Configure application
app = Flask(__name__)
sched = APScheduler()

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
                          nullable=False)
    Farm_Address = db.Column("Farm_Address", db.String(50),
                             nullable=False)
    Farm_Picture = db.Column("Farm_Picture", db.LargeBinary)
    Latitude = db.Column("Latitude", db.Numeric)
    Longitude = db.Column("Longitude", db.Numeric)
    Start_Date = db.Column("Date", db.Date)

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
                            nullable=False)
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


class report(db.Model):
    ID = db.Column("ID", db.Integer, nullable=False,
                   primary_key=True, autoincrement=True)
    Device_ID = db.Column("Device_ID", db.Integer, db.ForeignKey(
        'device.ID', ondelete='CASCADE'), nullable=False)
    Report = db.Column("Report", db.Text)
    Date = db.Column("Date", db.Date, nullable=False)


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

    devices = {}
    for field in farms:
        count = db.session.query(func.count(device.ID)).join(farm).join(
            user).filter(user.ID == session["user_id"], farm.ID == field.ID).scalar()
        devices[field.Farm_Name] = count

    return render_template("index.html", farms=farms, devices=devices)


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
    someone = user.query.filter_by(ID=session["user_id"]).first()

    username = someone.Username

    return render_template("monitor.html", farms=farms, username=username)


@app.route("/monitor/")
@login_required
def farm_info_redirect():

    return redirect("/monitor")


@app.route("/add_farm", methods=['POST'])
def add_farm():
    farmName = request.form.get("farmName")
    farmAddress = request.form.get("farmAddress")
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
        newFarm = farm(User_ID=id, Farm_Name=farmName,
                       Farm_Address=farmAddress)
        db.session.add(newFarm)
        db.session.commit()
        return 'Success'
    elif farmPicture != "" and latitude == "" and longitude == "":
        newFarm = farm(User_ID=id, Farm_Name=farmName, Farm_Address=farmAddress,
                       Farm_Picture=farmPicture)
        db.session.add(newFarm)
        db.session.commit()
        return 'Success'
    elif farmPicture == "" and latitude != "" and longitude != "":
        newFarm = farm(User_ID=id, Farm_Name=farmName, Farm_Address=farmAddress, Latitude=latitude,
                       Longitude=longitude)
        db.session.add(newFarm)
        db.session.commit()
        return 'Success'
    else:
        newFarm = farm(User_ID=id, Farm_Name=farmName, Farm_Address=farmAddress, Farm_Picture=farmPicture,
                       Latitude=latitude, Longitude=longitude)
        db.session.add(newFarm)
        db.session.commit()
        return 'Success'


# TODO
# Change to dynamic link in future
# /monitor/[user]/[farm name]
@app.route("/monitor/<username>/<int:id>")
@login_required
def farm_info(username, id):
    field = (
        db.session.query(farm)
        .join(user)
        .filter(user.Username == username, farm.ID == id)
        .first()
    )

    count = db.session.query(func.count(device.ID)).join(farm).join(
        user).filter(user.ID == session["user_id"], farm.ID == field.ID).scalar()
    deviceCount = count

    devices = db.session.query(device).join(farm).join(
        user).filter(user.ID == session["user_id"], farm.ID == field.ID).all()

    main = db.session.query(device).join(farm).join(
        user).filter(user.ID == session["user_id"], farm.ID == field.ID).first()

    if main != None:
        reports = (
            db.session.query(report)
            .join(device)
            .filter(report.Device_ID == main.ID)
            .order_by(report.Date.desc())
            .first()
        )
    else:
        reports = None

    currentDate = datetime.now()
    if field.Start_Date:
        dateStarted = datetime.combine(field.Start_Date, datetime.min.time())
        currentWeek = math.floor((currentDate - dateStarted).days / 7)
    else:
        currentWeek = None

    return render_template("farm.html", field=field, deviceCount=deviceCount,
                           devices=devices, currentWeek=currentWeek, reports=reports)


@app.route("/get_location/<int:id>")
def get_location(id):
    devices = db.session.query(device).join(farm).join(
        user).filter(user.ID == session["user_id"], farm.ID == id).all()

    # Convert the query result to a list of dictionaries
    result_dict_list = [row.__dict__ for row in devices]

    # Remove unnecessary keys from each dictionary (like '_sa_instance_state')
    for row_dict in result_dict_list:
        row_dict.pop('_sa_instance_state', None)

    print

    # Return the result as JSON using Flask's jsonify function
    return jsonify(result_dict_list)


@app.route("/set_date", methods=['POST'])
def set_date():
    isHarvest = request.form.get("isHarvest")

    if isHarvest:
        farmID = request.form.get("farmID")
        field = farm.query.filter_by(ID=farmID).first()
        field.Start_Date = None
        db.session.commit()

        return 'Success'
    else:
        startDate = request.form.get("startDate")
        farmID = request.form.get("farmID")
        y, m, d = startDate.split('-')
        date = datetime(int(y), int(m), int(d))

        field = farm.query.filter_by(ID=farmID).first()
        field.Start_Date = date
        db.session.commit()

        return 'Success'


@app.route("/add_device", methods=['POST'])
def add_device():
    farmID = request.form.get("id")
    deviceName = request.form.get("deviceName")
    latitude = request.form.get("latitude")
    longitude = request.form.get("longitude")
    deviceURL = request.form.get("deviceURL")

    if latitude != "" and longitude != "":
        latitude = float(latitude)
        longitude = float(longitude)

    response = {"location_missing": False}
    if latitude == "" and longitude == "":
        response["location_missing"] = True
        return jsonify(response)

    newdevice = device(Farm_ID=farmID, Device_Name=deviceName,
                       Latitude=latitude, Longitude=longitude, URL=deviceURL)
    db.session.add(newdevice)
    db.session.commit()
    return 'Success'


@app.route("/delete_device", methods=['POST'])
def delete_device():
    deviceID = request.form.get("deviceID")

    trap = device.query.filter_by(ID=deviceID).first()
    db.session.delete(trap)
    db.session.commit()
    return "Success"


@app.route("/organism")
@login_required
def organism():
    # Returning user's portfolio
    return render_template("organism.html")


@app.route("/yolo", methods=['POST'])
def yolo():
    deviceID = request.form.get("deviceID")
    trap = device.query.filter_by(ID=deviceID).first()
    person = (
        db.session.query(user)
        .join(farm)
        .join(device)
        .filter(farm.ID == trap.Farm_ID, device.ID == trap.ID)
        .first()
    )

    deleteFiles("./static/predictions")

    requestImg = requestJSON(trap.URL + "/capture?username=" + person.Username)

    filename = latestFile("./captured")

    with open(os.path.join("./captured/" + filename), 'rb') as file:
        image_data = file.read()

    imageDate, imageTime = fileDatetime(stripExtension(filename))

    if predict("./captured/" + filename, "./static/weight/best.pt"):
        with open(os.path.join("./static/predictions/" + stripExtension(filename) + ".json"), 'r') as file:
            jsonContent = json.load(file)

        newPred = capture(Device_ID=trap.ID,
                          Farm_ID=trap.Farm_ID, Image_Name=stripExtension(filename), Image=image_data,
                          Date=imageDate, Time=imageTime, Prediction=json.dumps(jsonContent).encode('utf-8'))

        db.session.add(newPred)
        db.session.commit()

    result = {'filename': stripExtension(filename)}

    return jsonify(result)


@app.route('/generate_report', methods=['POST'])
def generate_report():
    farmID = request.form.get("idFarm")
    deviceID = request.form.get("idDevice")

    field = (
        db.session.query(farm)
        .join(user)
        .filter(user.ID == session["user_id"], farm.ID == farmID)
        .first()
    )

    prediction = (
        db.session.query(capture)
        .join(device)
        .filter(capture.Device_ID == deviceID)
        .order_by(capture.Date.desc())
        .first()
    )

    currentDate = datetime.now()
    dateStarted = datetime.combine(field.Start_Date, datetime.min.time())
    currentWeek = math.floor((currentDate - dateStarted).days / 7)

    insectWarning = "These are the insects that can damage the crops in their current age:\n"
    if currentWeek > 0 and currentWeek < 14:
        insectWarning += "Brown Planthopper\n"

    if currentWeek > 0 and currentWeek < 5:
        insectWarning += "Green Leafhopper\nWhorl Maggot\n"

    insectWarning += "Armyworm\nLeaffolder\nStemborer\n"

    if currentWeek > 0 and currentWeek < 11:
        insectWarning += "Caseworm\n"

    if currentWeek > 0 and currentWeek < 8:
        insectWarning += "Rice Black Bug\n"

    if currentWeek > 10 and currentWeek < 15:
        insectWarning += "Rice Bug\n"

    insectWarning += "\n"

    loadPrediction = json.loads(prediction.Prediction)
    presentInsect = "Here are the currently trapped insects:\n"
    for key, value in loadPrediction.items():
        presentInsect += key + ": " + str(value) + "\n"

    presentInsect += "\n"

    giveWarn = False
    insectAlert = "Alert! Farm is infested\n"
    insecticide = "It is adviced to use this insecticide to lower their population:\n"
    for key, value in loadPrediction.items():
        if key == "Green Leafhopper" or key == "Zigzag Leafhopper" and value > 50:
            giveWarn = True
            insectAlert += "- Signs of infestation is showing for: " + key + "\n"
            insecticide + "Starkle or Terrapest or Primaphos "

    current_date = datetime.now().date()

    if giveWarn:
        finalMessage = insectWarning + presentInsect + insectAlert + insecticide
        newReport = report(Device_ID=deviceID,
                           Report=finalMessage, Date=current_date)
        db.session.add(newReport)
        db.session.commit()

    else:
        finalMessage = insectWarning + presentInsect
        newReport = report(Device_ID=deviceID,
                           Report=finalMessage, Date=current_date)
        db.session.add(newReport)
        db.session.commit()

    return "Success"

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

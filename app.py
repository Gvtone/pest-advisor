import os
from flask import Flask, flash, redirect, render_template, request, session, jsonify, url_for
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename

# Global Variables
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True
app.config['UPLOAD_FOLDER'] = "./captured"

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

@app.route("/")
def index():
    # Returning user's portfolio
    return render_template("index.html")

@app.route("/login")
def login():
    # Returning user's portfolio
    return render_template("login.html")

@app.route("/signup")
def signup():
    # Returning user's portfolio
    return render_template("signup.html")

@app.route("/monitor")
def monitor():
    # Returning user's portfolio
    return render_template("monitor.html")

# TODO
# Change to dynamic link in future
# /monitor/[user]/[farm name]
@app.route("/monitor/farm")
def farm():
    # Returning user's portfolio
    return render_template("farm.html")

@app.route("/organism")
def organism():
    # Returning user's portfolio
    return render_template("organism.html")


# For receiving images from the Orange Pi PC
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/upload_image', methods=['GET', 'POST'])
def upload_image():
    # Receive the image data
    if 'file' not in request.files:
        flash('Invalid file')
        return redirect(request.url)
    file = request.files['file']

    if file.filename == '':
        flash('No selected file')
        return redirect(request.url)
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

    # Respond with a success message
    return jsonify({"message": "Image received and saved successfully"})
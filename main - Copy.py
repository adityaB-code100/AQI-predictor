from flask import Flask, request, redirect, url_for, session, render_template, flash
from werkzeug.security import generate_password_hash, check_password_hash
from bson.objectid import ObjectId
from functools import wraps
from pymongo import MongoClient
import os, json
from datetime import datetime
from utils import get_html_page

# Your custom imports
from atlas import get_mongo_uri
from get_report_generator import get_report
from get_from_db import get_aqi_data, get_aqi_by_village
from get_health_alerts_institution import get_health_alert_institution
from get_health_alert import get_health_alert_personal

# ----------------- Flask App -----------------
app = Flask(__name__)
app.secret_key = "secretkey"

# ----------------- MongoDB Connection -----------------
mongo_uri = get_mongo_uri()
client = MongoClient(mongo_uri)

# Select DB from URI or explicitly
db = client["AQI_Project"]

# Collections
users_collection = db.users
institutions_collection = db.institutions

# ----------------- Helpers -----------------
def get_current_date():
    return datetime.now().strftime("%d-%m-%Y")

def login_required(f):
    """Protect routes from unauthorized access"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "type" not in session:
            flash("Please login first!", "danger")
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated_function

# ----------------- Routes -----------------

# ----------- REGISTER -----------
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        reg_type = request.form.get("reg_type")

        if reg_type == "personal":
            if users_collection.find_one({"email": request.form["email"]}):
                flash("Email already exists! Please login.", "danger")
                return redirect(url_for("login"))

            data = {
                "name": request.form["name"],
                "email": request.form["email"],
                "mobile": request.form["mobile"],
                "village": request.form["village"],
                "disease": request.form["disease"],
                "age": request.form["age"],
                "password": generate_password_hash(request.form["password"])
            }
            users_collection.insert_one(data)
            flash("Personal account registered successfully!", "success")
            return redirect(url_for("login"))

        elif reg_type == "institution":
            if institutions_collection.find_one({"email": request.form["email"]}):
                flash("Email already exists! Please login.", "danger")
                return redirect(url_for("login"))

            data = {
                "institution_name": request.form["institution_name"],
                "institution_type": request.form["institution_type"],
                "village": request.form["village"],
                "address": request.form["address"],
                "email": request.form["email"],
                "contact": request.form["contact"],
                "password": generate_password_hash(request.form["password"])
            }
            institutions_collection.insert_one(data)
            flash("Institution account registered successfully!", "success")
            return redirect(url_for("login"))

    return render_template("register.html")

# ----------- LOGIN -----------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        login_type = request.form.get("login_type")
        email = request.form["email"]
        password = request.form["password"]

        if login_type == "personal":
            user = users_collection.find_one({"email": email})
            if user and check_password_hash(user["password"], password):
                session["user"] = str(user["_id"])
                session["type"] = "personal"
                flash(f"Welcome, {user['name']}!", "success")
                return redirect(url_for("dashboard", village=user["village"], date=get_current_date()))

        elif login_type == "institution":
            inst = institutions_collection.find_one({"email": email})
            if inst and check_password_hash(inst["password"], password):
                session["institution"] = str(inst["_id"])
                session["type"] = "institution"
                flash(f"Welcome, {inst['institution_name']}!", "success")
                return redirect('/')

        flash("Invalid credentials!", "danger")

    return render_template("login.html")

# ----------- FORGOT PASSWORD -----------
@app.route("/forgot", methods=["GET", "POST"])
def forgot_password():
    if request.method == "POST":
        account_type = request.form.get("account_type")
        email = request.form["email"]
        new_password = generate_password_hash(request.form["new_password"])

        if account_type == "personal":
            users_collection.update_one({"email": email}, {"$set": {"password": new_password}})
            flash("Password updated successfully!", "success")
            return redirect(url_for("login"))

        elif account_type == "institution":
            institutions_collection.update_one({"email": email}, {"$set": {"password": new_password}})
            flash("Password updated successfully!", "success")
            return redirect(url_for("login"))

    return render_template("forgot.html")

# ----------- EDIT PROFILE -----------
@app.route("/edit", methods=["GET", "POST"])
@login_required
def edit_profile():
    if session.get("type") == "personal":
        user = users_collection.find_one({"_id": ObjectId(session["user"])})
        if request.method == "POST":
            update_data = {
                "name": request.form["name"],
                "mobile": request.form["mobile"],
                "village": request.form["village"],
                "disease": request.form["disease"],
                "age": request.form["age"]
            }
            if request.form.get("password"):
                update_data["password"] = generate_password_hash(request.form["password"])
            users_collection.update_one({"_id": user["_id"]}, {"$set": update_data})
            flash("Profile updated successfully!", "success")
            return redirect(url_for("profile"))
        return render_template("edit_personal.html", user=user)

    elif session.get("type") == "institution":
        inst = institutions_collection.find_one({"_id": ObjectId(session["institution"])})
        if request.method == "POST":
            update_data = {
                "institution_name": request.form["institution_name"],
                "institution_type": request.form["institution_type"],
                "contact": request.form["contact"]
            }
            if request.form.get("password"):
                update_data["password"] = generate_password_hash(request.form["password"])
            institutions_collection.update_one({"_id": inst["_id"]}, {"$set": update_data})
            flash("Institution profile updated successfully!", "success")
            return redirect(url_for("profile"))
        return render_template("edit_institution.html", inst=inst)

    return redirect(url_for("login"))

# ----------- LOGOUT -----------
@app.route("/logout")
def logout():
    session.clear()
    flash("Logged out successfully!", "info")
    return redirect(url_for("dashboard"))

# ----------- PROFILE -----------
@app.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    if session.get("type") == "personal":
        user = users_collection.find_one({"_id": ObjectId(session["user"])})
        if not user:
            return "User not found", 404
        
        village = user["village"]
        date = get_current_date()
        dict1 = get_aqi_data(date, village, mongo_uri="mongodb://localhost:27017/",
                             db_name="AQI_Project", collection_name="processed_data")
        aqi_all = dict1.get('village_aqi_data', {})  
        aqi = aqi_all.get(village) 
        health_alert = get_health_alert_personal(aqi, 'general')
        personalise = user['disease']
        if user['disease'] is not None:
            personalise = get_health_alert_personal(aqi, user['disease'])

        return render_template("user_profile.html", user=user, health_alert=health_alert,
                               personalise=personalise, **dict1)

    elif session.get("type") == "institution":
        inst = institutions_collection.find_one({"_id": ObjectId(session["institution"])})
        if not inst:
            return "Institution not found", 404
        village = inst["village"]
        date = get_current_date()
        dict1 = get_aqi_data(date, village, mongo_uri="mongodb://localhost:27017/",
                             db_name="AQI_Project", collection_name="processed_data")
        aqi_all = dict1.get('village_aqi_data', {})  
        aqi = aqi_all.get(village) 
        personalise = inst['institution_type']
        if inst['institution_type'] is not None:
            personalise = get_health_alert_institution(aqi, 'general')
        institute_alert = get_health_alert_institution(aqi, inst['institution_type'])

        return render_template("institution_profile.html", inst=inst, **dict1,
                               institute_alert=institute_alert, personalise=personalise)

    return redirect(url_for("login"))

# ----------- DASHBOARD -----------
@app.route("/", methods=["GET", "POST"])
def dashboard():
    if request.method == "POST":
        village = request.form.get("village")
        date = request.form.get("date")
        return redirect(url_for("dashboard", village=village, date=date))
    else:
        village = request.args.get("village", "Pune")
        date = request.args.get("date", get_current_date())

    dict1 = get_aqi_data(date, village, mongo_uri=get_mongo_uri(),
                         db_name="AQI_Project", collection_name="processed_data")
    aqi_all = dict1.get('village_aqi_data', {})  
    aqi = aqi_all.get(village) 
    health_alert = get_health_alert_personal(aqi, 'general')

    return render_template("aqi.html", **dict1, health_alert=health_alert)

# ----------- OTHER ROUTES -----------
@app.route('/coverage')
def coverage():
    date = get_current_date()
    village = "Pune"
    dict1 = get_aqi_data(date, village, mongo_uri=get_mongo_uri(),
                         db_name="AQI_Project", collection_name="processed_data")
    return render_template('coverage.html', **dict1)

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/generate', methods=['POST'])
def generate():
    village = request.form.get("village")
    date1 = request.form.get("date")
    report = get_report(village, date1)
    now = datetime.now()
    current_date = now.strftime("%d-%m-%Y")
    current_time = now.strftime("%H:%M:%S")
    return render_template('report.html', report=report,
                           current_date=current_date, current_time=current_time)

# ----------- ERROR HANDLERS -----------
@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template("500.html"), 500

# ----------- DISABLE CACHING -----------
@app.after_request
def add_header(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response

# ----------------- RUN APP -----------------
if __name__ == "__main__":
    app.run(debug=True)

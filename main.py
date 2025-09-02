from flask import Flask, request, redirect, url_for, session, render_template, flash, jsonify,render_template_string,send_from_directory
from flask_pymongo import PyMongo
from werkzeug.security import generate_password_hash, check_password_hash
from bson.objectid import ObjectId
from functools import wraps
from Fastserver import save_or_update_data
# AQI imports
from datetime import datetime
# #from get_map import mapgenerator
# #from data_function import next_seven_days
from get_from_db import get_aqi_data, get_aqi_by_village
# from filter_function import filter_off, classify_pollutants
# from data_graph import create_aqi_forecast_chart
# from get_avg_graph import plot_monthly_aqi
# from get_user import get_data
from get_health_alert import get_health_alert
app = Flask(__name__)
app.secret_key = "secretkey"

# MongoDB Config
app.config["MONGO_URI"] = "mongodb://localhost:27017/AQI_Project"
mongo = PyMongo(app)

# Collections
users_collection = mongo.db.users
institutions_collection = mongo.db.institutions

# ---------- Helpers ----------
def get_current_date():
    return datetime.now().strftime("%d-%m-%Y")   # DD

def login_required(f):
    """Protect routes from unauthorized access"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "type" not in session:
            flash("Please login first!", "danger")
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated_function

# ---------- Home ----------
# @app.route("/login_page")
# def home():
#     return render_template("index.html")

# ---------- REGISTER ----------
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
                print("Email already exists! Please login.", "danger")
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
            print(data)
            institutions_collection.insert_one(data)
            flash("Institution account registered successfully!", "success")
            return redirect(url_for("login"))

    return render_template("register.html")

# ---------- LOGIN ----------
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
                return redirect(url_for("dashboard"))

        elif login_type == "institution":
            inst = institutions_collection.find_one({"email": email})
            if inst and check_password_hash(inst["password"], password):
                session["institution"] = str(inst["_id"])
                session["type"] = "institution"
                flash(f"Welcome, {inst['institution_name']}!", "success")
                return redirect('/')

        flash("Invalid credentials!", "danger")

    return render_template("login.html")

# ---------- FORGOT PASSWORD ----------
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

# ---------- EDIT PROFILE ----------
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
            return redirect(url_for("dashboard"))

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
            return redirect(url_for("dashboard"))

        return render_template("edit_institution.html", inst=inst)

    return redirect(url_for("login"))


# ---------- Logout ----------
@app.route("/logout")
def logout():
    session.clear()
    flash("Logged out successfully!", "info")
    return redirect(url_for("dashboard"))

# ---------- Disable caching ----------
@app.after_request
def add_header(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response







# ----------  PROFILE ----------
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
        health_alert = get_health_alert(aqi, 'general')
        personalise = user['disease']
        if user['disease'] is not None:
            personalise = get_health_alert(aqi, user['disease'])

        return render_template("profile.html", user=user, health_alert=health_alert,
                               personalise=personalise, **dict1)

    elif session.get("type") == "institution":
        inst = institutions_collection.find_one({"_id": ObjectId(session["institution"])})
        if not inst:
            return "Institution not found", 404
        
        return render_template("profile1.html", inst=inst)

    return redirect(url_for("login"))








# ---------- AQI Dashboard ----------
@app.route("/", methods=["GET", "POST"])
#@login_required
def dashboard():
  
    if request.method == "POST":
        village = request.form.get("village")
        date = request.form.get("date")
    else:
        village = "Pune"  # default
        date = get_current_date()

    print(date)

    #dict1=get_data("29-08-2025",village)
    dict1=get_aqi_data(date, village, mongo_uri="mongodb://localhost:27017/",
                 db_name="AQI_Project", collection_name="processed_data")
    aqi_all = dict1.get('village_aqi_data', {})   # Get all villages' AQI
    aqi = aqi_all.get(village) 
    print(aqi)
    health_alert = get_health_alert(aqi, 'general')

    return render_template(
        "aqi.html",
        # worst_aqi=worst_aqi,
        # best_aqi=best_aqi,
          **dict1,
         # map_name=
         health_alert=health_alert

    )

@app.route('/coverage')
def coverage():
      #dict1=get_data("29-08-2025",village)
    date = get_current_date()
    village = "Pune"  # default

    dict1=get_aqi_data(date, village, mongo_uri="mongodb://localhost:27017/",
                 db_name="AQI_Project", collection_name="processed_data")
    return render_template(
        'coverage.html',
        # worst_aqi=worst_aqi,
        # best_aqi=best_aqi,
          **dict1,
         # map_name=

    )

if __name__ == "__main__":
    app.run(debug=True)

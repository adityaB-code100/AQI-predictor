from flask import Flask, request, redirect, url_for, session, render_template, flash, jsonify
from flask_pymongo import PyMongo
from werkzeug.security import generate_password_hash, check_password_hash
from bson.objectid import ObjectId
from functools import wraps

# AQI imports
import statistics, math
from datetime import datetime
import pandas as pd
import numpy as np
from get_map import mapgenerator
from data_function import next_seven_days
from get_from_db import get_aqi_data, get_aqi_by_village
from filter_function import filter_off, classify_pollutants
from data_graph import create_aqi_forecast_chart

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
    return datetime.now().strftime("%Y-%m-%d")

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
@app.route("/")
def home():
    return render_template("index.html")

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
                flash("Email already exists! Please login.", "danger")
                return redirect(url_for("login"))

            data = {
                "institution_name": request.form["institution_name"],
                "institution_type": request.form["institution_type"],
                "email": request.form["email"],
                "contact": request.form["contact"],
                "password": generate_password_hash(request.form["password"])
            }
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
                return redirect(url_for("dashboard"))

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
            return redirect(url_for("aqi_dashboard"))

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
            return redirect(url_for("aqi_dashboard"))

        return render_template("edit_institution.html", inst=inst)

    return redirect(url_for("login"))

# ---------- AQI Dashboard ----------
@app.route("/dashboard", methods=["GET", "POST"])
@login_required
def dashboard():
    aqi_list, mean_list, pm_list = [], [], []
    avg_aqi_7_days = worst_aqi = best_aqi = None
    avg_3card_dict, passing_data, pollutants = {}, {}, None

    if request.method == "POST":
        village = request.form.get("village")
        date = request.form.get("date")
    else:
        village = "Pune"  # default
        date = get_current_date()

    date_list = next_seven_days(date)

    for date_i in date_list:
        data = get_aqi_data(date_i, village=village)
        if data:
            mean_list.append(data)
            if "Predicted_AQI" in data:
                aqi_list.append(data["Predicted_AQI"])
            if "PM2.5" in data:
                pm_list.append(data["PM2.5"])

    data = get_aqi_data(date, village=village)
    if data:
        pollutants = classify_pollutants(filter_off(data))

    village_aqi_data = get_aqi_by_village(date)
    if village_aqi_data:
        mapgenerator(village_aqi_data)

    if aqi_list:
        avg_aqi_7_days = int(np.mean(aqi_list)) if not math.isnan(np.mean(aqi_list)) else None
        worst_aqi = np.max(aqi_list)
        best_aqi = np.min([x for x in aqi_list if x is not None and not np.isnan(x)])

    paired_data = dict(zip(aqi_list, date_list))
    avg_3card_dict["worst_aqi"] = paired_data.get(worst_aqi)
    avg_3card_dict["best_aqi"] = paired_data.get(best_aqi)

    passing_data = dict(zip(date_list, aqi_list))
    passing_pollutant = dict(zip(date_list, pm_list))
    graph_html = create_aqi_forecast_chart(date_list, aqi_list)

    return render_template(
        "aqi.html",
        passing_data=passing_data,
        avg_3card_dict=avg_3card_dict,
        avg_aqi_7_days=avg_aqi_7_days,
        worst_aqi=worst_aqi,
        best_aqi=best_aqi,
        pollutants=pollutants,
        passing_pollutant=passing_pollutant,
        graph_html=graph_html,
        date=date,
        village=village,
    )

# ---------- Save Coordinates ----------
@app.route("/save_coords", methods=["POST"])
def save_coords():
    data = request.json
    lat, lng = data.get("lat"), data.get("lng")
    print(f"Received coordinates: {lat}, {lng}")
    return jsonify({"status": "success", "lat": lat, "lng": lng})

# ---------- Logout ----------
@app.route("/logout")
def logout():
    session.clear()
    flash("Logged out successfully!", "info")
    return redirect(url_for("home"))

# ---------- Disable caching ----------
@app.after_request
def add_header(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response

if __name__ == "__main__":
    app.run(debug=True)

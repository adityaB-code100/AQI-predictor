from flask import Flask, abort, jsonify, request, redirect, url_for, session, render_template, flash
from werkzeug.security import generate_password_hash, check_password_hash
from bson.objectid import ObjectId
from functools import wraps
from pymongo import MongoClient
import os, json
import traceback
from datetime import datetime
from utils import get_html_page

# Your custom imports
from atlas import get_mongo_uri
from get_report_generator import get_report
from get_from_db import get_aqi_data, get_aqi_by_village
from get_health_alerts_institution import get_health_alert_institution
from get_health_alert import get_health_alert_personal
from notes_db import add_note, get_notes_by_user, update_note, delete_note
from get_note import get_notes_for_matching_aqi
from keyword_chatbot import ALLOWED_KEYWORDS
import google.generativeai as genai
import json
import re
from data_chatbot import data_chat
#from run_me import auto_app
import threading
import time

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
notes_collection = db.notes
# # 


# def schedule_auto_app():
#     while True:
#         now = datetime.now()
#         # Run only between 12:00 AM and 12:05 AM
#         if now.hour == 0 and 0 <= now.minute < 5:
#             print(f"Running auto_app at {now}")
#             auto_app()
#             # Sleep for 5 minutes to avoid running multiple times in the same window
#             time.sleep(300)
#         else:
#             # Check every 30 seconds until the window
#             time.sleep(30)

# # Start the scheduler in a background thread
# threading.Thread(target=schedule_auto_app, daemon=True).start()

# Configure Gemini
with open("config.json") as f:
    config = json.load(f)


#-------------API Key Setup-------------
api_key = config["API_KEY"]["key"] 
genai.configure(api_key=api_key)
model = genai.GenerativeModel("gemini-1.5-flash")
# response = model.generate_content([context, f"Question: {user_input}"])

    

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
                "language": request.form["target"],
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
                "language": request.form["target"],
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
        dict1 = get_aqi_data(date, village, mongo_uri=get_mongo_uri(),
                             db_name="AQI_Project", collection_name="processed_data")
        aqi_all = dict1.get('village_aqi_data', {})  
        aqi = aqi_all.get(village) 
        health_alert = get_health_alert_personal(aqi, 'general')
        personalise = user['disease']
        if user['disease'] is not None:
            personalise = get_health_alert_personal(aqi, user['disease'])
        note=get_notes_for_matching_aqi(session.get("user"), village)
        print(note)
        return render_template("user_profile.html", user=user, health_alert=health_alert,
                               personalise=personalise, **dict1,note=note)

    elif session.get("type") == "institution":
        inst = institutions_collection.find_one({"_id": ObjectId(session["institution"])})
        if not inst:
            return "Institution not found", 404
        village = inst["village"]
        date = get_current_date()
        dict1 = get_aqi_data(date, village, mongo_uri=get_mongo_uri(),
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
    uri_1=get_mongo_uri()
    dict1 = get_aqi_data(date, village, mongo_uri=uri_1,
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
# ---------- NOTES ----
@app.route("/note/add", methods=["POST"])
@login_required
def add_note_route():
    
        user_id = session.get("user")

        # Get note details from form
        title = request.form.get("title")
        content = request.form.get("content")

        if not title or not content:
            flash("Title and Content are required!", "danger")
            return redirect(url_for("note"))

        # Fetch user info
        user = users_collection.find_one({"_id": ObjectId(user_id)})
        if not user:
            return "User not found", 404

        # Get village and live AQI
        village = user["village"]
        date = get_current_date()
        dict1 = get_aqi_data(
            date, village,
            mongo_uri=get_mongo_uri(),
            db_name="AQI_Project",
            collection_name="processed_data"
        )

        # Extract live AQI value (assuming key "live_AQI" exists in dict1)
        live_aqi = dict1.get("live_AQI", None)

        # Save note with extra fields
        note_data = {
            "user_id": user_id,
            "title": title,
            "content": content,
            "village": village,
            "live_aqi": live_aqi,
            "created_at":  get_current_date()
        }

        notes_collection.insert_one(note_data)

        flash("Note added successfully with AQI data!", "success")
        return redirect(url_for("note"))

    

@app.route("/note/edit/<id>", methods=["POST"])
@login_required
def edit_note_route(id):
    try:
        title = request.form.get("title")
        content = request.form.get("content")
        update_note(notes_collection, id, title, content)
        flash("Note updated successfully!", "info")
        return redirect(url_for("note"))
    except Exception as e:
        print(f"[ERROR] Edit note failed: {e}")


@app.route("/note/delete/<id>")
@login_required
def delete_note_route(id):
    try:
        delete_note(notes_collection, id)
        flash("Note deleted successfully!", "warning")
        return redirect(url_for("note"))
    except Exception as e:
        print(f"[ERROR] Delete note failed: {e}")


@app.route('/note')
@login_required
def note():
    try:
        if session.get("type") == "personal":
            user = users_collection.find_one({"_id": ObjectId(session["user"])})
        if not user:
            return "User not found", 404
        
        name = user["name"]

        return render_template('note.html', name=name,date=get_current_date())
    except Exception as e:
        print(f"[ERROR] Note page failed: {e}")
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




def is_allowed_question(user_input):
    text = user_input.lower()
    for keyword in ALLOWED_KEYWORDS:
        if re.search(rf"\b{keyword}\b", text):
            return True
    return False

@app.route("/chat_bot")
def chatbot():
    return render_template("index.html")



@app.route("/ask", methods=["POST"])
def ask():
    user_input = request.json.get("question", "")

    # Step 1: Filter out irrelevant questions
    if not is_allowed_question(user_input):
        return jsonify({"answer": "Sorry, I can only answer Weather and Pollution/AQI related questions."})

    # Step 2: Pass only dataset as context
    context = f"""
    Dataset:
    {data_chat(str(get_current_date()))}
    """

    try:
        # Step 3: Call Gemini with dataset + user question separately
        model = genai.GenerativeModel("models/gemini-1.5-flash")
        response = model.generate_content([context, f"Question: {user_input}"])

        # Debug print Gemini raw response
        print("Gemini raw response:", response)

        # Step 4: Extract answer safely
        answer = None
        if hasattr(response, "text") and response.text:
            answer = response.text.strip()
        elif hasattr(response, "candidates") and response.candidates:
            parts = response.candidates[0].content.parts
            if parts and hasattr(parts[0], "text"):
                answer = parts[0].text.strip()

        if not answer:
            answer = "⚠️ Sorry, I couldn’t fetch an answer right now."

        return jsonify({"answer": answer})

    except Exception as e:
        print("Gemini error:", str(e))
        traceback.print_exc()  # 🔥 full error log
        return jsonify({"answer": "Error while fetching answer from Gemini."})


@app.route("/compare", methods=["GET", "POST"])
def compare():
    try:
        if request.method == "POST":
            village1 = request.form.get("village1")
            village2 = request.form.get("village2")
            village1_data = get_aqi_data(get_current_date(), village1, mongo_uri=get_mongo_uri(),
                         db_name="AQI_Project", collection_name="processed_data")
            print(village1_data)
            village2_data = get_aqi_data(get_current_date(), village2, mongo_uri=get_mongo_uri(),
                         db_name="AQI_Project", collection_name="processed_data")

            return render_template("compare.html", village1=village1_data, village2=village2_data)
        
        else:

            return render_template('compare_form.html')
    except Exception as e:
        print(f"[ERROR] Compare page failed: {e}")
        abort(500)
    return render_template("compare.html")
# ---------- Error Handlers ----------
@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404

@app.errorhandler(500)
def internal_server_error(e):
    print(f"[ERROR] Internal server error: {e}")
    return render_template("500.html"), 500


# ----------------- RUN APP -----------------
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))

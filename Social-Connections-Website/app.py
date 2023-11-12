import os, firebase_admin, uuid

from firebase_admin import credentials, db, firestore
from flask import Flask, redirect, render_template, request, session, jsonify, url_for
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename
from helpers import apology, login_required, reg_required
from datetime import datetime

# Configure application
app = Flask(__name__)

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(
    cred,
    {
        "databaseURL": "https://finalproject-fcb22-default-rtdb.europe-west1.firebasedatabase.app"
    },
)


# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db_firestore = firestore.client()
db_realtime = db.reference("chats")

"""Global Values"""

likings = [
    "Photography",
    "Reading",
    "Cooking",
    "Writing",
    "Painting",
    "Music",
    "Drawing",
    "Blog",
    "Art",
    "Video Games",
    "Fishing",
    "Hiking",
    "Computer Programming",
    "Martial arts",
    "Football",
    "Anime",
    "News",
    "Technology",
    "Traveling",
]


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


# Home screen used to render options for login/register
@app.route("/")
def index():
    if not session:
        return render_template("index.html")

    profile = db_firestore.collection("usrProfile").document(session["user_id"]).get()

    liking = db_firestore.collection("likes").document(session["user_id"]).get()

    if not profile.to_dict():
        return render_template("FirstRegister.html")

    if not liking.to_dict():
        return render_template("firstLikings.html", likings=likings)

    session["filename"] = None
    session["chat_id"] = ""

    person_doc = db_firestore.collection("users").document(session["user_id"]).get()
    person = person_doc.to_dict()
    return render_template("index.html", person=person)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username

        rows = (
            db_firestore.collection("users")
            .where("username", "==", request.form.get("username"))
            .get()
        )

        # Ensure username exists and password is correct
        user_data = rows[0].to_dict()
        if len(rows) != 1 or not check_password_hash(
            user_data["hash"], request.form.get("password")
        ):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0].id

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    session.clear()

    """Register user"""
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        confirm = request.form.get("confirmation")

        info = db_firestore.collection("users").where("username", "==", username).get()

        if not username:
            return apology("Didnt input a username")
        elif info:
            return apology("Username already taken")
        elif not password:
            return apology("Didnt input password")
        elif not confirm:
            return apology("Didnt input confirmation")
        elif password != confirm:
            return apology("passwords do not match")

        hash = generate_password_hash(password)

        db_firestore.collection("users").add({"username": username, "hash": hash})

        # Query database for username
        rows = (
            db_firestore.collection("users")
            .where("username", "==", request.form.get("username"))
            .get()
        )

        # Remember which user has logged in
        session["user_id"] = rows[0].id

        return redirect("/")
    else:
        return render_template("register.html")


@app.route("/profile", methods=["GET", "POST"])
@login_required
@reg_required
def profile():
    if request.method == "POST":
        return apology("Error")

    else:
        usrInfo_doc = (
            db_firestore.collection("usrProfile").document(session["user_id"]).get()
        )

        usrInfo_data = usrInfo_doc.to_dict()

        liking_doc = db_firestore.collection("likes").document(session["user_id"]).get()

        if liking_doc.exists:
            liking_data = liking_doc.to_dict()
            likes = liking_data.get("likings", [])
        else:
            likes = []

        return render_template(
            "profile.html", usrInfo=usrInfo_data, likings=likings, likes=likes
        )


@app.route("/upload_info", methods=["GET", "POST"])
@login_required
def update_prof():
    user = db_firestore.collection("usrProfile").document(session["user_id"]).get()
    userInfo = db_firestore.collection("users").document(session["user_id"]).get()

    nickname = request.form.get("nickname")
    gender = request.form.get("gender")
    looking = request.form.get("looking")
    age = request.form.get("age")
    username = userInfo.to_dict()["username"]

    if not nickname or not gender or not looking or not age:
        return apology("You didnt fill some required information")

    try:
        age = int(age)
    except ValueError:
        return apology("Invalid input for age")

    if age < 18:
        return apology("You are to young")

    if not os.path.exists("static/" + username):
        os.makedirs("static/" + username)

    if "file" in request.files and request.files["file"].filename != "":
        file = request.files["file"]
        filename = secure_filename(file.filename)
        filepath = os.path.join("static", username, filename)
        file.save(filepath)
        filepath = username + "/" + filename

    else:
        filepath = "none.jpg"

    if not user.to_dict():
        db_firestore.collection("usrProfile").document(session["user_id"]).set(
            {
                "nickname": nickname,
                "gender": gender,
                "age": age,
                "looking": looking,
                "img_path": filepath,
            }
        )

        return redirect("/firstLikings")

    return redirect("/")


@app.route("/logout")
@login_required
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/firstLikings", methods=["GET", "POST"])
@login_required
def firstL():
    """Creating and ready to display likings"""

    return render_template("firstLikings.html", likings=likings)


@app.route("/likings", methods=["GET", "POST"])
@login_required
def like():
    """ready to update or create the linkigs for the user"""

    likings = request.form.getlist("selectedWord")

    if len(likings) < 3:
        return redirect("/firstLikings")

    db_firestore.collection("likes").document(session["user_id"]).delete()

    db_firestore.collection("likes").document(session["user_id"]).set(
        {"likings": likings}
    )

    return redirect("/")


@app.route("/update_profile", methods=["GET", "POST"])
@login_required
@reg_required
def updateProf():
    db_firestore.collection("matches").document(session["user_id"]).delete()

    nickname = request.form.get("nickname")
    gender = request.form.get("gender")
    age = request.form.get("age")
    looking = request.form.get("looking")

    if not nickname or not gender or not age or not looking:
        return apology("Invalid input")

    try:
        age = int(age)
    except ValueError:
        return apology("Invalid input for age")

    if age < 18:
        return apology("You are to young")

    usrInfo_doc = (
        db_firestore.collection("usrProfile").document(session["user_id"]).get()
    )
    usrInfo = usrInfo_doc.to_dict()
    usr_doc = db_firestore.collection("users").document(session["user_id"]).get()
    usr = usr_doc.to_dict()

    old_filepath = usrInfo["img_path"]
    file = request.files["file"]

    if file:
        if os.path.exists(old_filepath):
            os.remove(old_filepath)

        filename = secure_filename(file.filename)
        new_filepath = os.path.join("static", usr["username"], filename)
        file.save(new_filepath)

        new_filepath = usr["username"] + "/" + filename
    else:
        new_filepath = old_filepath

    db_firestore.collection("usrProfile").document(session["user_id"]).update(
        {
            "nickname": nickname,
            "gender": gender,
            "age": age,
            "looking": looking,
            "img_path": new_filepath,
        }
    )

    return redirect("/profile")


@app.route("/update_likings", methods=["GET", "POST"])
@login_required
@reg_required
def updateLike():
    likings = request.form.getlist("selectedWord")
    if len(likings) < 3:
        return redirect("/profile")

    db_firestore.collection("likes").document(session["user_id"]).delete()

    db_firestore.collection("likes").document(session["user_id"]).set(
        {"likings": likings}
    )

    return redirect("/profile")


@app.route("/swipe", methods=["GET", "POST"])
@login_required
@reg_required
def swipe():
    profiles = []
    show = {}
    if request.method == "POST":
        return apology("sorry man")
    else:
        User_doc = (
            db_firestore.collection("usrProfile").document(session["user_id"]).get()
        )
        User = User_doc.to_dict()

        applicants_query = (
            db_firestore.collection("usrProfile")
            .where("gender", "==", User["looking"])
            .get()
        )
        applicants = []

        for doc in applicants_query:
            applicants_data = doc.to_dict()
            applicants_data["id"] = doc.id
            if applicants_data["id"] != session["user_id"]:
                applicants.append(applicants_data)

        UsersLikings = (
            db_firestore.collection("likes").document(session["user_id"]).get()
        )

        UsersLikings_data = UsersLikings.to_dict()

        if UsersLikings_data is not None:
            UsersLikings_values = UsersLikings_data.get("likings", [])
        else:
            UsersLikings_values = []

        for applicant in applicants:
            applicant_data = (
                applicant  # Here, 'applicant' is a dictionary that includes the ID
            )
            doc_id = applicant_data["id"]

            possible_match_doc = db_firestore.collection("likes").document(doc_id).get()
            possible_match = possible_match_doc.to_dict()

            if possible_match:
                possible_match_values = possible_match["likings"]
            else:
                possible_match_values = []
            likes_in_common = 0

            for value in possible_match_values:
                if value in UsersLikings_values:
                    likes_in_common = likes_in_common + 1
            if likes_in_common != 0:
                check_doc = (
                    db_firestore.collection("matches")
                    .where("other_id", "==", doc_id)
                    .where("user_id", "==", session["user_id"])
                    .get()
                )
                # Check if the query result is empty
                if not check_doc:
                    # Query result is empty, so no matching document was found
                    db_firestore.collection("matches").add(
                        {
                            "user_id": session["user_id"],
                            "other_id": doc_id,
                            "amount_common": likes_in_common,
                            "users_option": "NULL",
                            "chat_id": "NULL",
                        }
                    )
                else:
                    # Query result is not empty, so at least one matching document was found
                    # You may want to loop through the results and update each matching document

                    value = (
                        db_firestore.collection("matches")
                        .where("user_id", "==", session["user_id"])
                        .where("other_id", "==", doc_id)
                        .get()
                    )
                    for doc in value:
                        key = doc.id
                        db_firestore.collection("matches").document(key).update(
                            {
                                "user_id": session["user_id"],
                                "other_id": doc_id,
                                "amount_common": likes_in_common,
                            }
                        )

                shows = (
                    db_firestore.collection("matches")
                    .where("users_option", "==", "NULL")
                    .where("user_id", "==", session["user_id"])
                    .get()
                )

                profiles = []
                nicknames = {}
                likings = {}
                show_list = {doc.id: doc.to_dict() for doc in shows}

                for user in show_list:
                    img_doc = (
                        db_firestore.collection("usrProfile")
                        .document(show_list[user]["other_id"])
                        .get()
                    )
                    img_data = img_doc.to_dict()
                    nicknames[show_list[user]["other_id"]] = img_data["nickname"]

                    likings_doc = (
                        db_firestore.collection("likes")
                        .document(show_list[user]["other_id"])
                        .get()
                    )
                    likingArr = likings_doc.to_dict()
                    likings[show_list[user]["other_id"]] = likingArr

                    if img_data and "img_path" in img_data:
                        profiles.append(img_data["img_path"])

        return render_template(
            "swiping.html",
            shows=show_list,
            profiles=profiles,
            nicknames=nicknames,
            likings=likings,
        )


@app.route("/updateUserOption", methods=["POST"])
@login_required
@reg_required
def update_matches():
    data = request.get_json()
    choice = data["choice"]
    otherId = data["usrId"]

    if choice == "agree":
        value = (
            db_firestore.collection("matches")
            .where("user_id", "==", session["user_id"])
            .where("other_id", "==", otherId)
            .get()
        )
        for doc in value:
            key = doc.id
            db_firestore.collection("matches").document(key).update(
                {
                    "users_option": "1",
                }
            )
    elif choice == "decline":
        value = (
            db_firestore.collection("matches")
            .where("user_id", "==", session["user_id"])
            .where("other_id", "==", otherId)
            .get()
        )
        for doc in value:
            key = doc.id
            db_firestore.collection("matches").document(key).update(
                {
                    "users_option": "0",
                }
            )
    return jsonify({"status": "success"})


@app.route("/messages", methods=["GET", "POST"])
@app.route("/messages/<selected_user>", methods=["GET", "POST"])
@login_required
@reg_required
def message(selected_user=None):
    if request.method == "POST":
        return apology("Error")
    else:
        matches = []
        usrProfiles = []
        other_id = None
        possible_match_query = (
            db_firestore.collection("matches")
            .where("other_id", "==", session["user_id"])
            .where("users_option", "==", "1")
            .get()
        )
        for query in possible_match_query:
            possible_match = query.to_dict()
            other_id = possible_match["user_id"]

            if other_id != None:
                check_for_like_query = (
                    db_firestore.collection("matches")
                    .where("user_id", "==", session["user_id"])
                    .where("other_id", "==", other_id)
                    .where("users_option", "==", "1")
                    .get()
                )
                for querys in check_for_like_query:
                    check_for_like = querys.to_dict()

                    if len(check_for_like) != 0:
                        matches.append(other_id)

        for match in matches:
            usrProfile_doc = db_firestore.collection("usrProfile").document(match).get()

            usrProfile = usrProfile_doc.to_dict()

            usrProfiles.append({"profile": usrProfile, "id": usrProfile_doc.id})
        if selected_user:
            chat_ref = db_realtime.child(session["chat_id"])
            chat_data = chat_ref.get()
        else:
            chat_data = None

        return render_template(
            "messages.html",
            matches=matches,
            usrProfiles=usrProfiles,
            selected_user=selected_user,
            filepath=session["filename"],
            chat_data=chat_data,
            user=session["user_id"],
        )


def send_messages(chat_id, sender_id, text):
    current_time = datetime.now().isoformat()
    chat_ref = db_realtime.child(chat_id)
    new_message_ref = chat_ref.push()
    new_message_ref.set({"sender": sender_id, "text": text, "timestamp": current_time})


def listen_for_messages(chat_id, callback):
    ref = db_realtime.reference(session["chat_id"])
    ref.order_by_child("timestamp").on("child_added", callback)


@app.route("/send_message", methods=["POST"])
@login_required
@reg_required
def handle_send_message():
    chat_id = session["chat_id"]
    sender_id = session["user_id"]
    text = request.form["message"]
    send_messages(chat_id, sender_id, text)
    session["selected_user"]
    return redirect(url_for("message", selected_user=session["selected_user"]))


def create_chat_id():
    new_chat_id = str(uuid.uuid4())

    return new_chat_id


@app.route("/select_user")
@login_required
@reg_required
def select_user():
    selected_user = request.args.get("selected_user")
    session["selected_user"] = selected_user
    img_doc = (
        db_firestore.collection("usrProfile").document(request.args.get("id")).get()
    )

    img = img_doc.to_dict()

    session["filename"] = img["img_path"]

    # Check if users chat was created

    chat_query = (
        db_firestore.collection("matches")
        .where("user_id", "==", session["user_id"])
        .where("other_id", "==", request.args.get("id"))
        .get()
    )

    for query in chat_query:
        chat = query.to_dict()

    if chat["chat_id"] == "NULL":
        new_id = create_chat_id()
        session["chat_id"] = new_id
        user_1_doc = (
            db_firestore.collection("matches")
            .where("user_id", "==", session["user_id"])
            .where("other_id", "==", request.args.get("id"))
            .get()
        )
        user_2_doc = (
            db_firestore.collection("matches")
            .where("other_id", "==", session["user_id"])
            .where("user_id", "==", request.args.get("id"))
            .get()
        )
        for doc in user_1_doc:
            key = doc.id
            db_firestore.collection("matches").document(key).update({"chat_id": new_id})
        for doc in user_2_doc:
            key = doc.id
            db_firestore.collection("matches").document(key).update({"chat_id": new_id})
    else:
        session["chat_id"] = chat["chat_id"]
    return redirect(url_for("message", selected_user=session["selected_user"]))

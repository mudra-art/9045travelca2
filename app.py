from flask import Flask, render_template, request, redirect, session
import sqlite3
import os

app = Flask(__name__)
app.secret_key = "travelsecret123"

# ---------- DATABASE ----------
def get_db():
    conn = sqlite3.connect("travel.db")
    conn.row_factory = sqlite3.Row
    return conn

# ---------- CREATE TABLES ----------
def init_db():
    db = get_db()
    cursor = db.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        email TEXT,
        password TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS bookings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        destination TEXT,
        travel_date TEXT,
        persons INTEGER
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS contact_messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        email TEXT,
        message TEXT
    )
    """)

    db.commit()
    db.close()

init_db()

# ---------- HOME ----------
@app.route("/")
def home():
    return render_template("index.html", user=session.get("user"))

# ---------- REGISTER ----------
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]

        db = get_db()
        db.execute(
            "INSERT INTO users (username, email, password) VALUES (?, ?, ?)",
            (username, email, password)
        )
        db.commit()
        db.close()

        return redirect("/login")

    return render_template("register.html")

# ---------- LOGIN ----------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        db = get_db()
        user = db.execute(
            "SELECT * FROM users WHERE email=? AND password=?",
            (email, password)
        ).fetchone()
        db.close()

        if user:
            session["user"] = user["username"]
            return redirect("/")
        else:
            return "Invalid email or password"

    return render_template("login.html")

# ---------- LOGOUT ----------
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

# ---------- BOOK TRIP ----------
@app.route("/book", methods=["POST"])
def book():
    if "user" not in session:
        return redirect("/login")

    destination = request.form["destination"]
    travel_date = request.form["travel_date"]
    persons = request.form["persons"]

    db = get_db()
    db.execute(
        "INSERT INTO bookings (username, destination, travel_date, persons) VALUES (?, ?, ?, ?)",
        (session["user"], destination, travel_date, persons)
    )
    db.commit()
    db.close()

    return redirect("/")

# ---------- CONTACT ----------
@app.route("/contact", methods=["POST"])
def contact():
    name = request.form["name"]
    email = request.form["email"]
    message = request.form["message"]

    db = get_db()
    db.execute(
        "INSERT INTO contact_messages (name, email, message) VALUES (?, ?, ?)",
        (name, email, message)
    )
    db.commit()
    db.close()

    return redirect("/")

# ---------- RUN (Render compatible) ----------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

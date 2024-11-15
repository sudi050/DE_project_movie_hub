import os
import psycopg2
from cryptography.fernet import Fernet, InvalidToken
from flask import Flask, render_template, redirect, url_for, request, flash, session, g
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user
from dash_dashboard import create_dash_app  # Import the function to create the Dash app
from flask_admin_dashboard import admin_bp  # Import the admin blueprint
from config_db_admin import get_db, server, close_connection

# app = Flask(__name__)

# # Register the admin blueprint
# app.register_blueprint(admin_bp)

# Key for encryption/decryption (securely store this for production)

# Create the Dash app
dash_app = create_dash_app(server, get_db)


key = b"yRn5s6K7bMl-P3SOM6BR6LhSKyV3AlKzg-Xp8pUxV3U="
cipher_suite = Fernet(key)


# Flask-Login setup
login_manager = LoginManager()
login_manager.init_app(server)


# User database simulation
class User(UserMixin):
    def __init__(self, email):
        self.id = email


@login_manager.user_loader
def load_user(user_id):
    return User(user_id) if user_id else None


@server.route("/")
def login():
    return render_template("login.html")

@server.route("/login", methods=["POST"])
def login_post():
    email = request.form.get("email")
    password = request.form.get("password")

    db = get_db()
    cursor = db.cursor()

    # Fetch encrypted password from the database
    cursor.execute(
        "SELECT password , access_id FROM user_account WHERE username = %s", (email,)
    )
    user = cursor.fetchone()

    if not user:
        flash("No user found with this email ID.", "error")
        return redirect(url_for("signup"))

    # Decrypt stored password and verify
    encrypted_password = user[0].encode()

    try:
        decrypted_password = cipher_suite.decrypt(encrypted_password).decode()
    except InvalidToken:
        flash(
            "An error occurred while processing your password. Please try again or contact support.",
            "error",
        )
        return redirect(url_for("login"))

    if decrypted_password != password:
        flash("Incorrect password!", "error")
        return redirect(url_for("login"))

    # Successful login
    # Successful login

    access_id = user[1]  # Get access_id
    print("****************", user, type(user[1]), access_id)
    user = User(email)

    login_user(user)
    session["user_id"] = email
    session["access_id"] = access_id
    session["logged_in"] = True
    flash("Login successful!", "success")

    # Redirect based on access_id
    if access_id == 1:
        print("GOING ERE")
        return redirect(url_for("admin.admin_dashboard"))  # Redirect to the admin page
    elif access_id == 2:
        # return redirect(url_for("dash_dashboard"))  # Redirect to the Dash dashboard
        # Create the Dash app
        # create_dash_app(server, get_db)
        return redirect(url_for("dashboard"))


@server.route("/signup")
def signup():
    return render_template("signup.html")


@server.route("/signup", methods=["POST"])
def signup_post():
    # name = request.form.get("username")
    email = request.form.get("email")
    dob = request.form.get("dob")
    password = request.form.get("password")
    conf_password = request.form.get("conf_password")
    access_id = request.form.get("access_id")

    access_id = "User"
    if access_id == "User":
        access_id = 2
    else:
        access_id = 1

    if password != conf_password:
        flash("Passwords do not match!", "error")
        return redirect(url_for("signup"))

    db = get_db()
    cursor = db.cursor()

    cursor.execute("SELECT * FROM user_account WHERE username = %s", (email,))
    existing_user = cursor.fetchone()

    if existing_user:
        flash("Email already registered. Please log in.", "error")
        return redirect(url_for("login"))

    # Encrypt the password before storing
    encrypted_password = cipher_suite.encrypt(password.encode()).decode()

    cursor.execute(
        "INSERT INTO user_account (username, password, access_id, date_of_birth) VALUES (%s, %s, %s, %s)",
        (email, encrypted_password, access_id, dob),  # assuming default access_id is 1
    )

    db.commit()

    flash("Signup successful! Please log in.", "success")
    return redirect(url_for("login"))


@server.route("/dashboard")
@login_required
def dashboard():
    return redirect("/dash/")  # Redirect to Dash app


@server.route("/logout")
@login_required
def logout():
    session.pop('logged_in', None)
    session.pop('user_id', None)
    session.pop('access_id', None)
    logout_user()
    flash("Logout successful!", "success")
    return redirect(url_for("login"))

@server.route("/login")
def login1():
    return render_template("login.html")

if __name__ == "__main__":
    server.run(debug=True)

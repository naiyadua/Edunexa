from flask import Flask, render_template, request, redirect, session, url_for
import sqlite3
from werkzeug.security import check_password_hash

app = Flask(__name__)

# Secret Key for Login Session
app.secret_key = "edunexa_secret_key"


# -----------------------------
# Database Connection
# -----------------------------
def get_connection():
    conn = sqlite3.connect("college.db")
    conn.row_factory = sqlite3.Row
    return conn


# -----------------------------
# Login Page
# -----------------------------
@app.route("/login", methods=["GET", "POST"])
def login():

    error = ""

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM admin WHERE username=?",
            (username,)
        )

        admin = cursor.fetchone()

        conn.close()

        if admin and check_password_hash(admin["password"], password):

            session["admin"] = True
            session["username"] = username

            return redirect("/")

        else:

            error = "Invalid Username or Password"

    return render_template(
        "login.html",
        error=error
    )
from werkzeug.security import generate_password_hash


# -----------------------------
# Register Admin
# -----------------------------
@app.route("/register", methods=["GET", "POST"])
def register():

    message = ""

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        conn = get_connection()
        cursor = conn.cursor()

        # Check if username already exists
        cursor.execute(
            "SELECT * FROM admin WHERE username=?",
            (username,)
        )

        existing = cursor.fetchone()

        if existing:

            message = "Username already exists!"

        else:

            hashed_password = generate_password_hash(password)

            cursor.execute(
                """
                INSERT INTO admin(username, password)
                VALUES(?, ?)
                """,
                (username, hashed_password)
            )

            conn.commit()
            conn.close()

            return redirect("/login")

        conn.close()

    return render_template(
        "register.html",
        message=message
    )
# -----------------------------
# Logout
# -----------------------------
@app.route("/logout")
def logout():

    session.clear()

    return redirect("/login")


# -----------------------------
# Home Page
# -----------------------------
@app.route("/", methods=["GET", "POST"])
def home():

    conn = get_connection()
    cursor = conn.cursor()

    # Dashboard Statistics
    cursor.execute("SELECT COUNT(*) FROM institutions")
    total = cursor.fetchone()[0]

    cursor.execute(
        "SELECT COUNT(*) FROM institutions WHERE type='School'"
    )
    schools = cursor.fetchone()[0]

    cursor.execute(
        "SELECT COUNT(*) FROM institutions WHERE type='College'"
    )
    colleges = cursor.fetchone()[0]

    results = []

    if request.method == "POST":

        search = request.form["city"]
        inst_type = request.form["type"]

        if inst_type == "All":

            cursor.execute(
                """
                SELECT id, name, city, type
                FROM institutions
                WHERE city LIKE ?
                OR name LIKE ?
                """,
                (
                    f"%{search}%",
                    f"%{search}%"
                )
            )

        else:

            cursor.execute(
                """
                SELECT id, name, city, type
                FROM institutions
                WHERE
                (city LIKE ?
                OR name LIKE ?)
                AND type=?
                """,
                (
                    f"%{search}%",
                    f"%{search}%",
                    inst_type
                )
            )

        results = cursor.fetchall()

    conn.close()

    return render_template(
        "index.html",
        results=results,
        total=total,
        schools=schools,
        colleges=colleges
    )
# -----------------------------
# Add Institution
# -----------------------------
@app.route("/add", methods=["GET", "POST"])
def add():

    if not session.get("admin"):
        return redirect("/login")

    if request.method == "POST":

        name = request.form["name"]
        city = request.form["city"]
        inst_type = request.form["type"]

        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO institutions (name, city, type)
            VALUES (?, ?, ?)
            """,
            (name, city, inst_type)
        )

        conn.commit()
        conn.close()

        return redirect("/view")

    return render_template("add.html")


# -----------------------------
# View All Institutions
# -----------------------------
@app.route("/view")
def view():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT id, name, city, type
        FROM institutions
        ORDER BY name
        """
    )

    institutions = cursor.fetchall()

    conn.close()

    return render_template(
        "view.html",
        institutions=institutions
    )


# -----------------------------
# Edit Institution
# -----------------------------
@app.route("/edit/<int:id>", methods=["GET", "POST"])
def edit(id):

    if not session.get("admin"):
        return redirect("/login")

    conn = get_connection()
    cursor = conn.cursor()

    if request.method == "POST":

        name = request.form["name"]
        city = request.form["city"]
        inst_type = request.form["type"]

        cursor.execute(
            """
            UPDATE institutions
            SET name=?, city=?, type=?
            WHERE id=?
            """,
            (name, city, inst_type, id)
        )

        conn.commit()
        conn.close()

        return redirect("/view")

    cursor.execute(
        """
        SELECT id, name, city, type
        FROM institutions
        WHERE id=?
        """,
        (id,)
    )

    institution = cursor.fetchone()

    conn.close()

    return render_template(
        "edit.html",
        institution=institution
    )


# -----------------------------
# Delete Institution
# -----------------------------
@app.route("/delete/<int:id>")
def delete(id):

    if not session.get("admin"):
        return redirect("/login")

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM institutions WHERE id=?",
        (id,)
    )

    conn.commit()
    conn.close()

    return redirect("/view")


# -----------------------------
# Run Application
# -----------------------------
if __name__ == "__main__":
    app.run(debug=True)
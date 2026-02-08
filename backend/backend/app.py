from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
import os
from datetime import datetime

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

DB_NAME = "database.db"

# ---------- DATABASE ----------
def get_db():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        category TEXT,
        location TEXT,
        quantity REAL,
        unit TEXT,
        expiryDate TEXT,
        consumed INTEGER DEFAULT 0
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS donations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        donor_name TEXT,
        contact TEXT,
        food_type TEXT,
        quantity TEXT,
        location TEXT,
        expiry_time TEXT,
        image_path TEXT,
        timestamp TEXT
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS ngos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        contact TEXT,
        address TEXT
    )
    """)

    conn.commit()
    conn.close()

init_db()

# ---------- INVENTORY APIs ----------
@app.route("/api/items", methods=["GET", "POST"])
def items():
    conn = get_db()
    cur = conn.cursor()

    if request.method == "POST":
        data = request.json
        cur.execute("""
        INSERT INTO items (name, category, location, quantity, unit, expiryDate)
        VALUES (?, ?, ?, ?, ?, ?)
        """, (
            data["name"], data["category"], data["location"],
            data["quantity"], data["unit"], data["expiryDate"]
        ))
        conn.commit()
        return jsonify(success=True)

    cur.execute("SELECT * FROM items")
    items = [dict(row) for row in cur.fetchall()]
    return jsonify(success=True, items=items)

@app.route("/api/items/<int:item_id>/consume", methods=["PATCH"])
def consume_item(item_id):
    conn = get_db()
    conn.execute("UPDATE items SET consumed=1 WHERE id=?", (item_id,))
    conn.commit()
    return jsonify(success=True)

@app.route("/api/items/<int:item_id>", methods=["DELETE"])
def delete_item(item_id):
    conn = get_db()
    conn.execute("DELETE FROM items WHERE id=?", (item_id,))
    conn.commit()
    return jsonify(success=True)

# ---------- STATS ----------
@app.route("/api/stats")
def stats():
    conn = get_db()
    cur = conn.cursor()

    cur.execute("SELECT COUNT(*) FROM items WHERE consumed=0")
    total = cur.fetchone()[0]

    return jsonify(success=True, stats={
        "total": total,
        "critical": 0,
        "warning": 0,
        "expired": 0
    })

# ---------- DONATION ----------
@app.route("/api/donate", methods=["POST"])
def donate():
    image = request.files["food_image"]
    filename = f"{datetime.now().timestamp()}_{image.filename}"
    path = os.path.join(UPLOAD_FOLDER, filename)
    image.save(path)

    conn = get_db()
    conn.execute("""
    INSERT INTO donations
    (donor_name, contact, food_type, quantity, location, expiry_time, image_path, timestamp)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        request.form["name"],
        request.form["contact"],
        request.form["food_type"],
        request.form["quantity"],
        request.form["location"],
        request.form["expiry_time"],
        path,
        datetime.now().isoformat()
    ))
    conn.commit()

    return jsonify(success=True, message="Donation submitted")

# ---------- NGO ----------
@app.route("/api/ngos", methods=["GET", "POST"])
def ngos():
    conn = get_db()
    cur = conn.cursor()

    if request.method == "POST":
        data = request.json
        cur.execute("""
        INSERT INTO ngos (name, contact, address)
        VALUES (?, ?, ?)
        """, (data["name"], data["contact"], data["address"]))
        conn.commit()
        return jsonify(success=True)

    cur.execute("SELECT * FROM ngos")
    ngos = [dict(row) for row in cur.fetchall()]
    return jsonify(success=True, ngos=ngos)

if __name__ == "__main__":
    app.run(debug=True)

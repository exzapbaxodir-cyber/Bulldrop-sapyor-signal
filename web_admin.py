from flask import Flask, render_template, request, redirect
import database as db
from config import ADMIN_ID

app = Flask(__name__)

# Admin panel asosiy sahifa
@app.route("/")
def index():
    users = db.cursor.execute("SELECT user_id, balance, referrals FROM users").fetchall()
    return render_template("index.html", users=users)


# Coin qo'shish
@app.route("/add_coin", methods=["POST"])
def add_coin():
    user_id = int(request.form["user_id"])
    amount = int(request.form["amount"])
    db.update_balance(user_id, amount)
    return redirect("/")


# Promokod yaratish
@app.route("/create_promo", methods=["POST"])
def create_promo():
    code = request.form["code"]
    reward = int(request.form["reward"])
    db.cursor.execute("INSERT INTO promocodes VALUES (?,?)", (code, reward))
    db.conn.commit()
    return redirect("/")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

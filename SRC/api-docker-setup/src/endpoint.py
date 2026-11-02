import logging

from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

# initialize the flask app
app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"
db = SQLAlchemy(app)

class MyTask(db.Model):
	id = db.Column(db.String(50), primary_key=True)
	day = db.Column(db.Integer, nullable=False)
	month = db.Column(db.Integer, nullable=False)
	year = db.Column(db.Integer, nullable=False)
	weekday = db.Column(db.String(50), nullable=False)
	available_time = db.Column(db.String(50), nullable=True)

	def __repr__(self):
		return f"<MyTask {self.id}>"

# setup logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")


@app.route("/")
def admin_index_page():
	"""
	Displays the admin/dashboard page
	"""
	logging.info("Accessed index page")
	return render_template("index.html")



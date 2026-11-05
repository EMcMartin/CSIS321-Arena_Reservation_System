import logging
import os

from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

# initialize the flask app
app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
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

#home page 
@app.route("/",methods=["GET","POST"])
def admin_index_page():
	if request.method == "POST":
		# handle form submission
		day = request.form.get("day")
		month = request.form.get("month")
		year = request.form.get("year")
		weekday = request.form.get("weekday")
		available_time = request.form.get("available_time")

		if not (day and month and year and weekday):
			logging.warning("Missing required fields in form submission")
			return render_template("index.html", error="Please fill in all required fields.")

		try:
			new_task = MyTask(
				id=f"{year}-{month}-{day}",
				day=int(day),
				month=int(month),
				year=int(year),
				weekday=weekday,
				available_time=available_time
			)
			db.session.add(new_task)
			db.session.commit()
			logging.info(f"Added new task: {new_task}")
			return redirect("/")
		except Exception as e:
			logging.error(f"Error adding task: {e}")
			return render_template("index.html", error="An error occurred while adding the task.")
	
	
	
	
	"""
	Displays the admin/dashboard page
	"""
	logging.info("Accessed index page")
	return render_template('index.html')



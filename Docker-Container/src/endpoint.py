import logging
import os


from flask import Flask, render_template, request, redirect, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from dotenv import load_dotenv
from sqlalchemy.dialects.postgresql import INT4MULTIRANGE
from psycopg.types.range import Range
from sqlalchemy import text


# load environment variables
load_dotenv()

# initialize the flask app
app = Flask(__name__)

# identify the database URI from environment variable
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")


db = SQLAlchemy(app)


# defines database information for the Event table
class Event(db.Model):
	__tablename__ = "events"

	id = db.Column(db.String(50), primary_key=True)
	day = db.Column(db.Integer, nullable=False)
	month = db.Column(db.Integer, nullable=False)
	year = db.Column(db.Integer, nullable=False)
	weekday = db.Column(db.String(50), nullable=False)
	available_time = db.Column(INT4MULTIRANGE, nullable=True)

	def to_dict(self):
		return {
			"id": self.id,
			"day": self.day,
			"month": self.month,
			"year": self.year,
			"weekday": self.weekday,
			"available_time":
			[
				{
					"lower": r.lower,
					"upper": r.upper,
					"bounds": r.bounds
				}
				for r in (self.available_time or [])
			],
		}

# setup logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")



@app.route("/health", methods=["GET"])
def health_check():
    try:
        # Runs a minimal query to force an actual database round-trip
        db.session.execute(text("SELECT 1"))
        return jsonify({
            "status": "healthy",
            "database": "connected"
        }), 200
    except Exception as e:
        return jsonify({
            "status": "unhealthy",
            "database": "disconnected",
            "error": str(e)
        }), 500
	
@app.route("/events", methods=["GET"])
def view_events():
	events = Event.query.all()
	for event in events:
		print(event.id)
	return render_template("events.html", events=events)	


@app.route("/api/schedules/<int:available_time_id>", methods=["GET"])
def get_available_time(event_id):
    event = Event.query.get_or_404(event_id)
    return jsonify(event.to_dict())


#home page 
@app.route("/",methods=["GET","POST"])
def admin_index_page():
	if request.method == "POST":
		# handle form submission
		day = request.form.get("day")
		month = request.form.get("month")
		year = request.form.get("year")
		weekday = request.form.get("weekday")
		raw_time = request.form.get("available_time")

		
		if not (day and month and year and weekday):
			logging.warning("Missing required fields in form submission")
			return render_template("index.html", error="Please fill in all required fields.")

		try:
			parsed_range = []
			if raw_time and raw_time.strip():
				paresed_range = []
				for part in raw_time.split(","):
					start, end = part.strip().split("-")
					parsed_range.append(Range(int(start), int(end)))
			
			new_event = Event(
				id=f"{year}-{month}-{day}",
				day=int(day),
				month=int(month),
				year=int(year),
				weekday=weekday,
				available_time=parsed_range,
			)
			db.session.add(new_event)
			db.session.commit()
			logging.info(f"Added new event: {new_event}")
			return redirect("/")
		except Exception as e:
			db.session.rollback()
			logging.error(f"Error adding event: {e}")
			return render_template("index.html", error="An error occurred while adding the task.")

	"""
	Displays the admin/dashboard page
	"""
	logging.info("Accessed index page")
	return render_template('index.html')

if __name__ == "__main__": 
	app.run(host="0.0.0.0", port=8887, debug=True)


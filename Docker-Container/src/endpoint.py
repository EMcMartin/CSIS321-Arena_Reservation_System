from ast import stmt
import logging
import os


from flask import Flask, render_template, request, redirect, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from dotenv import load_dotenv
from sqlalchemy.dialects.postgresql import INT4MULTIRANGE
from psycopg.types.multirange import Multirange
from psycopg.types.range import Range
from sqlalchemy import text, update



# load environment variables
load_dotenv()

# initialize the flask app
app = Flask(__name__)

# identify the database URI from environment variable
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")


db = SQLAlchemy(app)



#defines event table for the database
class Event(db.Model):
	__tablename__ = "events"

	event_id = db.Column(db.Integer, primary_key=True)
	title = db.Column(db.String(50), nullable=False)
	organizer = db.Column(db.String(100), nullable=False)
	size = db.Column(db.Integer, nullable=False)
	day = db.Column(db.String(50), nullable=False)
	time_start = db.Column(db.Integer, nullable=False)
	time_end = db.Column(db.Integer, nullable=False)
	description = db.Column(db.String(255), nullable=True)
	

	def to_dict(self):
		return {
			"id": self.event_id,
			"title": self.title,
			"organizer": self.organizer,
			"size": self.size,
			"day": self.day,
			"start_time": self.time_start,
			"end_time": self.time_end,
			"description": self.description,
		}

# defines database information for the Days table
class calendar(db.Model):
	__tablename__ = "days"

	id = db.Column(db.String(50), primary_key=True)
	day = db.Column(db.Integer, nullable=False)
	month = db.Column(db.Integer, nullable=False)
	year = db.Column(db.Integer, nullable=False)
	weekday = db.Column(db.String(50), nullable=False)
	available_times = db.Column(INT4MULTIRANGE, nullable=True)

	def to_dict(self):
		return {
			"id": self.id,
			"day": self.day,
			"month": self.month,
			"year": self.year,
			"weekday": self.weekday,
			"available_times":
			[
				{
					"lower": r.lower,
					"upper": r.upper,
					"bounds": r.bounds
				}
				for r in (self.available_times or [])
			],
		}

# setup logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
#create a new day into the database
@app.route("/calendar", methods=["POST"])
def create_day():
	data = request.get_json()
	if not data:
		return jsonify({"error": "Invalid input"}), 400

	try:
		new_day = calendar(
			id="11/01/26",
			day=1,
			month=11,
			year=2026,
			weekday="sunday",
			available_times=Multirange([
				Range(3, 6, "[)"),
				Range(7, 10, "[)")
			])
		)
		db.session.add(new_day)
		db.session.commit()
		return jsonify({"message": "Day created successfully"}), 201
	except Exception as e:
		db.session.rollback()
		logging.error(f"Error creating day: {e}")
		return jsonify({"error": "An error occurred while creating the day"}), 500


#creates events into the database
@app.route("/event", methods=["POST"])
def create_event():
	data = request.get_json()
	if not data:
		return jsonify({"error": "Invalid input"}), 400

	day_id = data.get("day")
	time_start = data.get("time_start")
	time_end = data.get("time_end")

	if not day_id or time_start is None or time_end is None:
		return jsonify({"error": "'day', 'time_start', and 'time_end' are required."}), 400
	
	if time_start >= time_end:
		return jsonify({"error": "'time_start' must be less than 'time_end'."}), 400

	booking_range = Range(time_start, time_end, bounds="[)")

	try:
		stmt = (
    		update(calendar)
    		.where(
        		calendar.id == day_id,
        		calendar.available_times.isnot(None),
        		calendar.available_times.contains(booking_range),
    		)
    		.values(
        		available_times=calendar.available_times - booking_range
   			)
    		.returning(calendar.available_times)
		)

		updated_times = db.session.execute(stmt).scalar_one_or_none()

		if updated_times is None:
				db.session.rollback()
				return jsonify({
					"error": "Requested time is not within available times for this day."
				}), 409
		
		
			

		new_event = Event(
			title = data.get("title"),
			organizer = data.get("organizer"),
			description = data.get("description"),
			size=data.get("size"),
			time_start = data.get("time_start"),
			time_end = data.get("time_end"),
			day=data.get("day")
		)
		db.session.add(new_event)
		db.session.commit()
		return jsonify({"message": "Event created successfully"}), 201

	except Exception as e:
			db.session.rollback()
			logging.error(f"Error creating event: {e}")
			return jsonify({"error": "An error occurred while creating the event"}), 500
		
@app.route("/event", methods=["GET"])
def send_data():
	month = request.args.get("month")
	if not month:
		return jsonify({"error": "Please provide a day parameter."}), 400

	events = Event.query.filter(Event.day.contains(month + "/")).all()


	return jsonify([event.to_dict() for event in events]), 200





# checks the health of the application and database connection
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

#used to get the available time for a specific day in the calendar		
@app.route("/api/schedules/<int:available_time_id>", methods=["GET"])
def get_available_time(calendar_id):
    event = calendar.query.get_or_404(calendar_id)
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
		raw_time = request.form.get("available_times")

		
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
			
			new_event = calendar(
				id=f"{year}-{month}-{day}",
				day=int(day),
				month=int(month),
				year=int(year),
				weekday=weekday,
				available_times=parsed_range,
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


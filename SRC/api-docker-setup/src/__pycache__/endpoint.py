import logging

from flask import Flask


# initialize the flask app
app = Flask(__name__)

# setup logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")


@app.route("/")
def admin_index_page():
	"""
	Displays the admin/dashboard page
	"""
	logging.info("Accessed index page")
	return "Hello world"


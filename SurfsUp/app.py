# Import the dependencies.
import datetime as dt
import numpy as np
import pandas as pd
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from flask import Flask, jsonify

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
Base.prepare(engine, reflect=True)
# reflect the tables
Station = Base.classes.station
Measurement = Base.classes.measurement

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Flask Routes
#################################################
@app.route("/")

def welcome():
	return(
	'''
	Welcome to the Climate Analysis API!
	Available Routes:<br/>
	/api/v1.0/precipitation<br/>
	/api/v1.0/stations<br/>
	/api/v1.0/tobs<br/>
	/api/v1.0/temp/(start date: YYYY-MM-DD)<br/>
	/api/v1.0/temp/(start date: YYYY-MM-DD)/(end date: YYYY-MM-DD)
	''')

@app.route("/api/v1.0/precipitation")
def precipitation():
	prev_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)
	precipitation = session.query(Measurement.date,Measurement.prcp) .\
		filter(Measurement.date >= prev_year).all()
	precip = {date: prcp for date, prcp in precipitation}
	return jsonify(precip)

@app.route("/api/v1.0/stations")
def stations():
    results = session.query(Station.station).all()
    stations = list(np.ravel(results))
    return jsonify(stations=stations)

@app.route("/api/v1.0/tobs")
def temp_monthly():
	prev_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)
	results = session.query(Measurement.tobs).\
		filter(Measurement.station == 'USC00519281').\
		filter(Measurement.date >= prev_year).all()
	temps = list(np.ravel(results))
	return jsonify(temps=temps)

@app.route("/api/v1.0/temp/<start>")
def temps_start(start):
	query = (f'SELECT AVG(tobs) AS "Average Temp", MIN(tobs) \
        	AS "Minimum Temp", MAX(tobs) AS "Maximum Temp" \
        	FROM measurement WHERE date >= "{start}"')
	df = pd.read_sql(query, engine).to_dict(orient='records')
	return jsonify(df)

@app.route("/api/v1.0/temp/<start>/<end>")
def temps_startAndEnd(start, end):
    query = (f'SELECT AVG(tobs) AS "Average Temp", MIN(tobs) \
			AS "Minimum Temp", MAX(tobs) AS "Maximum Temp" \
			FROM measurement WHERE date >= "{start}" AND date <= "{end}"')
	df = pd.read_sql(query, engine).to_dict(orient='records')
	return jsonify(df)


if __name__ == "__main__":
    app.run(debug=True)
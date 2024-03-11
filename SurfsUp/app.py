# Import the dependencies.
from datetime import datetime, date
import datetime as dt
import numpy as np
import sqlalchemy
from flask import Flask, jsonify
from sqlalchemy import create_engine, func
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session

#################################################
# Database Setup
#################################################

# Create engine using the `hawaii.sqlite` database file
engine = create_engine("sqlite:///C:\\Users\\theoc\\Bootcamp\\sqlalchemy-challenge\\SurfsUp\\Resources\\hawaii.sqlite")


# Declare a Base using `automap_base()`
Base = automap_base()


# Use the Base class to reflect the database tables
Base.prepare(autoload_with= engine)

# Assign the measurement class to a variable called `Measurement` and
# the station class to a variable called `Station`
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create a session
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
    return (
        f"Welcome to the Hawaii Climate API!<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start_date<br/>"
        f"/api/v1.0/start_date/end_date"
    )

@app.route("/api/v1.0/precipitation")
def preciptitation():
   
    one_year_ago = dt.date(2017, 8, 23) - dt.timedelta(days=366)

    results = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= one_year_ago).filter(Measurement.prcp.isnot(None)).all()

    session.close()

    prcp_data = {date: prcp for date, prcp in results}

    return jsonify(prcp_data)

@app.route("/api/v1.0/stations")
def stations():

    stations = session.query(Station.station).all()

    session.close()

    station_list = list(np.ravel(stations))
    
    return jsonify(station_list)


@app.route("/api/v1.0/tobs")
def tobs():

    # Calculate the date 1 year ago from the last data point
    one_year_ago = dt.date(2017, 8, 23) - dt.timedelta(days=365)

    # Querying the most active station for the last year of temperature data
    most_active_station_tobs = session.query(Measurement.tobs).\
        filter(Measurement.station == 'USC00519281').\
        filter(Measurement.date >= one_year_ago).all()
    
    session.close()

    # Convert list of tuples into normal list
    tobs_list = list(np.ravel(most_active_station_tobs))
    
    return jsonify(tobs_list)



@app.route("/api/v1.0/<start>")
def temperature_start(start):
    one_year_ago = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    
    results = session.query(func.avg(Measurement.tobs), func.min(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= one_year_ago).all()

    temp_data = {
        "TMIN": results[0][1],
        "TAVG": results[0][0],
        "TMAX": results[0][2]
        }
    
    return jsonify(temp_data)


@app.route("/api/v1.0/<start>/<end>")
def temperature_range(start_date, end_date):  

    results = session.query(func.avg(Measurement.tobs), func.min(Measurement.tobs), func.max(Measurement.tobs)).\
        filter((Measurement.date >= start_date)&(Measurement.date <= end_date)).\
        all()

    temp_data = {
        "TMIN": results[0][1],
        "TAVG": results[0][0],
        "TMAX": results[0][2]
        }

    return jsonify(temp_data)



if __name__ == "__main__":
    app.run(debug=True)

    
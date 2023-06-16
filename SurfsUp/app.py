# Import the dependencies.
import datetime as dt
import numpy as np
import pandas as pd
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
# Create our session (link) from Python to the DB
import os

# Get the directory of the current script
current_directory = os.path.dirname(os.path.abspath(__file__))

# Specify the file path relative to the current directory
file_path = os.path.join(current_directory, "Resources/hawaii.sqlite")

# Create the engine using the relative file path
engine = create_engine(f"sqlite:///{file_path}")


# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(engine, reflect=True)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station


#################################################
# Flask Setup
#################################################
app = Flask(__name__)



#################################################
# Flask Routes
#################################################
def with_session(route_handler):
    def wrapper(*args, **kwargs):
        with Session(engine) as session:
            result = route_handler(session, *args, **kwargs)
        return result
    # Set the __name__ attribute of the wrapper function
    wrapper.__name__ = route_handler.__name__
    return wrapper

def welcome():
    return (
        f"Available Routes: <br/>"
        f"/api/v1.0/precipitation <br/>"
        f"/api/v1.0/stations <br/>"
        f"/api/v1.0/tobs <br/>"
        f"/api/v1.0/temp/<start>/<end> <br/>"
    )

@app.route("/api/v1.0/precipitation")
@with_session
def precip(session):
    last_date = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    precipitation = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date > last_date).all()
    precip = {date: prcp for date, prcp in precipitation}
    return jsonify(precip)

@app.route("/api/v1.0/stations")
@with_session
def stations(session):
    stations_list = list(np.ravel(session.query(Station.station).all()))
    return jsonify(stations_list)

@app.route("/api/v1.0/tobs")
@with_session
def monthly_temp(session):
    station_data = session.query(Measurement.station, Measurement.date, Measurement.prcp, Measurement.tobs)
    station_data_df = pd.DataFrame(station_data, columns=['station', 'date', 'prcp', 'tobs'])
    most_active = list(np.ravel(station_data_df.loc[(station_data_df['station'] == 'USC00519281')]))
    return jsonify(most_active)

@app.route("/api/v1.0/temp/<start>/<end>")
@with_session
def temps(session, start, end):
    start_date = dt.datetime.strptime(start, '%Y-%m-%d')
    end_date = dt.datetime.strptime(end, '%Y-%m-%d')
    temp_data = session.query(func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)) \
        .filter(Measurement.date.between(start_date, end_date)).all()
    temp_list = list(np.ravel(temp_data))
    return jsonify(temp_list)

if __name__ == "__main__":
    app.run(debug=True)
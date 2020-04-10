from flask import Flask, jsonify
import numpy as np
import pandas as pd
import datetime as dt

# Python SQL toolkit and Object Relational Mapper
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

app = Flask(__name__)

engine = create_engine("sqlite:///hawaii.sqlite")
base = automap_base()
base.prepare(engine, reflect=True)

Measurement = base.classes.measurement
Station = base.classes.station

# Home page.
@app.route("/")
def welcome():
    return (
        f"Welcome to the weather API!<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f'/api/v1.0/[start date in yyyy-mm-dd format]<br/>'
        f'/api/v1.0/[start date in yyyy-mm-dd format]/[end date in yyyy-mm-dd format]<br/>')

# Convert the query results to a dictionary using date as the key and prcp as the value.
# Return the JSON representation of your dictionary.
@app.route("/api/v1.0/precipitation")
def prcp():
    session = Session(engine)
    prcp = session.query(Measurement.date, Measurement.prcp).all()
    session.close()
    # prcp = list(np.ravel(prcp))
    dic_prcp = {}
    for p in prcp:
        dic_prcp[p[0]] = p[1]
    return jsonify(dic_prcp)

# Return a JSON list of stations from the dataset.
@app.route('/api/v1.0/stations')
def station():
    session = Session(engine)
    station = session.query(Station.station, Station.name).all()
    session.close()
    dic_station = {}
    for s in station:
        dic_station[s[0]] = s[1]
    return jsonify(dic_station)


# Query the dates and temperature observations of the most active station for the last year of data.
# Return a JSON list of temperature observations (TOBS) for the previous year.
@app.route('/api/v1.0/tobs')
def tobs():
    session = Session(engine)
    most_active = session.query(Measurement.station, func.count(Measurement.station)).\
        group_by(Measurement.station).\
        filter(func.strftime("%Y-%m-%d", Measurement.date)>= '2016-08-23').\
        order_by(func.count(Measurement.station).\
        desc())
    most_active = [m for m in most_active[0]]
    station_most_active = most_active[0]
    last_year = session.query(Measurement.date, Measurement.tobs).\
        filter(func.strftime("%Y-%m-%d", Measurement.date)>= '2016-08-23').\
        filter(Measurement.station == station_most_active).\
        order_by(Measurement.date)
    dic_lastyear = {}
    for l in last_year:
        dic_lastyear[l[0]] = l[1]
    return jsonify(dic_lastyear)

# Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start or start-end range.
# When given the start only, calculate TMIN, TAVG, and TMAX for all dates greater than and equal to the start date.
# When given the start and the end date, calculate the TMIN, TAVG, and TMAX for dates between the start and end date inclusive.
@app.route('/api/v1.0/<start_date>')
def start(start_date):
    session = Session(engine)
    start = session.query(Measurement.date, func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)).\
            filter(Measurement.date >= start_date).\
            group_by(Measurement.date).\
            all()
    dic_start = {}
    for s in start:
        dic_start[s[0]] = s[1]
    return jsonify(dic_start)

@app.route('/api/v1.0/<start_date>/<end_date>')
def start_end(start_date, end_date):
    session = Session(engine)
    end = session.query(Measurement.date, func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)).\
            filter(Measurement.date >= start_date).\
            filter(Measurement.date <= end_date).\
            group_by(Measurement.date).\
            all()
    dic_end = {}
    for e in end:
        dic_end[e[0]] = e[1]
    return jsonify(dic_end)

if __name__ == '__main__':
    app.run(debug=True)
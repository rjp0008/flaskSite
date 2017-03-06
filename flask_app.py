from io import BytesIO
from flask import make_response, Flask, jsonify, render_template, request
import random
import sqlite3
import datetime
import matplotlib.pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvas
from matplotlib.dates import DateFormatter
from matplotlib.figure import Figure
from pandas import date_range, Series
from io import StringIO
from intergraph.intergraph import random_member_response

import rasberry_pi.routes

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/random/', methods=['GET', 'POST'])
def random_route():
    if request.method == 'GET':
        return random_member_response()
    return random_member_response(request.form['user_name'], request.form['text'])



@app.route('/hotels/')
@app.route('/hotels/<group>/<category>')
@app.route('/hotels/<group>')
def show_entries(group=None, category=None):
    db = sqlite3.connect('hotel.db')
    sql_string = "select * from Hotels"
    data = ()
    if group or category:
        if category:
            sql_string = sql_string + " WHERE hotel_group=? and category=?"
            data = ((group), (category))
        else:
            sql_string = sql_string + " WHERE hotel_group=?"
            data = ((group),)
    cur = db.execute(sql_string, (data))
    entries = cur.fetchall()
    return render_template('show_entries.html', entries=entries)


@app.route('/north/')
@app.route('/north/<group>/<category>')
@app.route('/north/<group>')
def north(group=None, category=None):
    return geographic_finder(True, group, category)


@app.route('/south/')
@app.route('/south/<group>/<category>')
@app.route('/south/<group>')
def south(group=None, category=None):
    return geographic_finder(False, group, category)


def geographic_finder(max: bool, group=None, category=None):
    db = sqlite3.connect('hotel.db')
    type = "max"
    if max == False:
        type = "min"
    sql_string = "select " + type + "(lat) from Hotels"
    data = ()
    if group or category:
        if category:
            sql_string = sql_string + " where hotel_group=? and category=?"
            data = ((group), (category))
        else:
            sql_string = sql_string + " where hotel_group=?"
            data = ((group),)
    cur = db.execute(sql_string, (data))
    lat = cur.fetchone()[0]
    print(lat)
    cur = db.execute("SELECT * from Hotels WHERE lat='" + str(lat) + "'")
    entries = cur.fetchall()
    print((lat))
    return render_template('show_entries.html', entries=entries)


@app.route('/hotels/detail/<id>')
def detail(id: str = '0'):
    db = sqlite3.connect('hotel.db')
    sql_string = "select * from Hotels WHERE id=?"
    cur = db.execute(sql_string, ((id),))
    entry = cur.fetchone()
    # site = requests.get('https://maps.googleapis.com/maps/api/staticmap?center='+str(entry[3])+','+str(entry[4])+'&zoom=12&size=400x400&key=AIzaSyDXz9d7haybjrPP6iL2V0yknNb-aKwyK8w')

    return render_template('hotel_detail.html', entry=entry)


@app.route('/temperature/<humidity>/<temperature>')
def templog(humidity=None, temperature=None):
    db = sqlite3.connect('temp.db')
    c = db.cursor()
    sql_string = "insert into TempData (temperature, humidity, date) values (?,?,?)"
    data = ((temperature), (humidity), (datetime.datetime.now()))
    c.execute(sql_string, data)
    db.commit()
    db.close()
    return ""


def smoother(input):
    output = []
    for x in range(0, len(input)):
        slice_array = input[x - 2:x + 3]
        for item in slice_array:
            if item == 0:
                item = input[x]
        average = sum(slice_array)
        average = average / 5
        if len(slice_array) == 5:
            output.append(average)
    return output


@app.route('/tempMap/')
def tempmap():
    db = sqlite3.connect('temp.db')
    c = db.cursor()
    sql_string = "select * from TempData"  # " WHERE date > '" + str(datetime.datetime.now() - datetime.timedelta(hours=24))+"'"
    data = c.execute(sql_string)
    db.commit()
    entries = data.fetchall()
    temps = []
    hum = []
    time = []
    for x in entries:
        temps.append(x[1])
        hum.append(x[2])
        time.append(x[3])
    ts = Series(smoother(temps), index=time)
    hs = Series(smoother(hum), index=time)
    hs.plot()
    fig = ts.plot().get_figure()
    canvas = FigureCanvas(fig)
    png_output = BytesIO()
    canvas.print_png(png_output)
    response = make_response(png_output.getvalue())
    response.headers['Content-Type'] = 'image/png'
    return response


@app.route('/tempMap2/')
@app.route('/tempMap2/hours=<hours>')
def tempmap2(hours=None):
    db = sqlite3.connect('temp.db')
    c = db.cursor()
    sql_string = "select * from TempData"
    if hours != None:
        sql_string = sql_string + " WHERE date > '" + str(
            datetime.datetime.now() - datetime.timedelta(hours=int(hours))) + "'"
    data = c.execute(sql_string)
    db.commit()
    entries = data.fetchall()
    temps = []
    hum = []
    time = []
    for x in entries:
        temps.append(x[1])
        hum.append(x[2])
        time.append(datetime.datetime.strptime(x[3], "%Y-%m-%d %H:%M:%S.%f") - datetime.timedelta(hours=6))
    fig = Figure()
    ax = fig.add_subplot(111)
    t, = ax.plot_date(time, smoother(temps), '-', label="t")
    h, = ax.plot_date(time, smoother(hum), '-', label="h")
    ax.legend([t, h], ["Temperature (C)", "Humidity (0-100%)"], loc=3)
    ax.xaxis.set_major_formatter(DateFormatter('%m-%d %I:%M'))
    fig.autofmt_xdate()
    canvas = FigureCanvas(fig)
    png_output = BytesIO()
    canvas.print_png(png_output)
    response = make_response(png_output.getvalue())
    response.headers['Content-Type'] = 'image/png'
    return response


@app.route('/temperatureData/')
def temp_data():
    return rasberry_pi.routes.temp_data()


@app.route('/tempMap3/')
@app.route('/tempMap3/hours=<hours>')
def temptesting(hours=None):
    import plotly
    import json
    import pandas as pd
    import numpy as np
    rng = pd.date_range('1/1/2011', periods=7500, freq='H')
    ts = pd.Series(np.random.randn(len(rng)), index=rng)

    db = sqlite3.connect('temp.db')
    c = db.cursor()
    sql_string = "select * from TempData"
    if hours != None:
        sql_string = sql_string + " WHERE date > '" + str(
            datetime.datetime.now() - datetime.timedelta(hours=int(hours))) + "'"
    data = c.execute(sql_string)
    db.commit()
    entries = data.fetchall()
    temps = []
    hum = []
    time = []
    for x in entries:
        temps.append(x[1])
        hum.append(x[2])
        time.append(datetime.datetime.strptime(x[3], "%Y-%m-%d %H:%M:%S.%f") - datetime.timedelta(hours=6))

    graphs = [
        dict(
            data=[
                dict(
                    x=time,
                    y=smoother(temps),
                    type='line'
                ),
            ],
            layout=dict(
                title='Temperature (C)'
            )
        ),
        dict(
            data=[
                dict(
                    x=time,
                    y=smoother(hum),
                    type='line'
                ),
            ],
            layout=dict(
                title='Humidity (%)'
            )
        )
    ]

    # Add "ids" to each of the graphs to pass up to the client
    # for templating
    ids = ['graph-{}'.format(i) for i, _ in enumerate(graphs)]

    # Convert the figures to JSON
    # PlotlyJSONEncoder appropriately converts pandas, datetime, etc
    # objects to their JSON equivalents
    graphJSON = json.dumps(graphs, cls=plotly.utils.PlotlyJSONEncoder)

    return render_template('./graph.html',
                           ids=ids,
                           graphJSON=graphJSON)


if __name__ == '__main__':
    app.run()

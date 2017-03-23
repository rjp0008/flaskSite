import datetime
import http.client
import sqlite3
from io import BytesIO

from flask import make_response, Flask, render_template, request
from matplotlib.backends.backend_agg import FigureCanvas
from matplotlib.dates import DateFormatter
from matplotlib.figure import Figure
from pandas import Series

import rasberry_pi.routes
import secrets
from intergraph.intergraph import random_member_response

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
            sql_string += " WHERE hotel_group=? and category=?"
            data = (group, category)
        else:
            sql_string += " WHERE hotel_group=?"
            data = (group,)
    cur = db.execute(sql_string, data)
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
    if not max:
        type = "min"
    sql_string = "select " + type + "(lat) from Hotels"
    data = ()
    if group or category:
        if category:
            sql_string += " where hotel_group=? and category=?"
            data = (group, category)
        else:
            sql_string += " where hotel_group=?"
            data = (group,)
    cur = db.execute(sql_string, data)
    lat = cur.fetchone()[0]
    print(lat)
    cur = db.execute("SELECT * from Hotels WHERE lat='" + str(lat) + "'")
    entries = cur.fetchall()
    print(lat)
    return render_template('show_entries.html', entries=entries)


@app.route('/hotels/detail/<id>')
def detail(id: str = '0'):
    db = sqlite3.connect('hotel.db')
    sql_string = "select * from Hotels WHERE id=?"
    cur = db.execute(sql_string, (id,))
    entry = cur.fetchone()
    return render_template('hotel_detail.html', entry=entry)


@app.route('/temperature/<humidity>/<temperature>/<source>')
def templog(humidity=None, temperature=None, source="rp"):
    db = sqlite3.connect('temp.db')
    c = db.cursor()
    sql_string = "insert into TempData (temperature, humidity, date,source) values (?,?,?,?)"
    data = (temperature, humidity, (datetime.datetime.now()), source)
    c.execute(sql_string, data)
    db.commit()
    db.close()
    return ""


def smoother(input):
    output = []
    for x in range(0, len(input)):
        slice_array = input[x - 2:x + 3]
        average = sum(slice_array)
        average /= 5
        if len(slice_array) == 5:
            output.append(average)
    return output


@app.route('/tempMap/')
def tempmap():
    db = sqlite3.connect('temp.db')
    c = db.cursor()
    sql_string = "select * from TempData"
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
    if hours is not None:
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
    t, = ax.plot_date(time, temps, '-', label="t")
    h, = ax.plot_date(time, hum, '-', label="h")
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


@app.route('/groupme/', methods=['GET', 'POST'])
def brett_is_lazy():
    import json
    data = (json.loads(request.get_data().decode("utf-8")))

    if data['name'] == "dickbott":
        return ""

    conn = http.client.HTTPSConnection("discordapp.com")

    payload = "------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name=\"content\"\r\n\r\n" + str(
        data['text']) + " - " + str(data[
                                        'name']) + "\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name=\"username\"\r\n\r\nlazy_brett\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW--"
    payload = payload.encode('utf-8')

    headers = {
        'content-type': "multipart/form-data; boundary=----WebKitFormBoundary7MA4YWxkTrZu0gW",
        'cache-control': "no-cache",
        'postman-token': "76b0cd3b-5c0e-35e7-2b4a-5b6b149fae36"
    }

    conn.request("POST",
                 "/api/webhooks/" + secrets.webhook,
                 payload, headers)

    res = conn.getresponse()
    data = res.read()
    print(data.decode("utf-8"))
    return ""


@app.route('/tempMap3/')
@app.route('/tempMap3/hours=<hours>')
def temptesting(hours=None):
    import plotly
    import json

    temps = []
    hum = []
    time = []
    temps2 = []
    hum2 = []
    time2 = []

    db = sqlite3.connect('temp.db')
    c = db.cursor()
    sql_string = "select * from TempData"
    if hours is not None:
        sql_string = sql_string + " WHERE date > '" + str(
            datetime.datetime.now() - datetime.timedelta(hours=int(hours))) + "'"
    data = c.execute(sql_string)
    db.commit()
    entries = data.fetchall()

    for x in entries:
        if x[4] == "rp":
            temps.append(x[1])
            hum.append(x[2])
            time.append(datetime.datetime.strptime(x[3], "%Y-%m-%d %H:%M:%S.%f") - datetime.timedelta(hours=6))
        if x[4] == "web":
            temps2.append(x[1])
            hum2.append(x[2])
            time2.append(datetime.datetime.strptime(x[3], "%Y-%m-%d %H:%M:%S.%f") - datetime.timedelta(hours=6))
    graphs = [
        dict(
            data=[
                dict(
                    x=time,
                    y=smoother(temps),
                    type='line'
                ),
                dict(
                    x=time2,
                    y=smoother(temps2),
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
                dict(
                    x=time2,
                    y=smoother(hum2),
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

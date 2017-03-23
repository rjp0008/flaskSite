import sqlite3
from flask import make_response,Flask,jsonify,render_template,request


def temp_data():
    db = sqlite3.connect('temp.db')
    c = db.cursor()
    sql_string = "select * from TempData order by id desc limit 100"
    data = c.execute(sql_string)
    db.commit()
    return render_template('temp.html', entries=data.fetchall())
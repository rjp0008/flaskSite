import sqlite3
from flask import make_response,Flask,jsonify,render_template,request


def temp_data():
    db = sqlite3.connect('temp.db')
    c = db.cursor()
    sql_string = "select TOP(100) from TempData ORDER by id DESC"
    data = c.execute(sql_string)
    db.commit()
    return render_template('temp.html', entries=data.fetchall())
from flask import Flask
from flask import request
from flask import render_template
# flask.json is used to convert Python objects (list/dict) to JSON
from flask import json
from backend import backend
from DbAccess import DbAccess
from getPosterUrl import getPosterUrl

app = Flask(__name__)

app.debug = True

# I have this function that returns me a list of cmovies
# This function is called when following address is visited:
# /json/cities?q=B
def movies():
    """Return list of movies where first letters match query."""

    db = DbAccess('twolu',usr='root')

    q = request.args.get('q')

    # This is my query to find movies matching query
    db.cursor.execute(("SELECT Title FROM movies WHERE Title LIKE '{0}%' LIMIT 10").format(q))

    data = db.cursor.fetchall()

    # Matching movies are in a list
    movies = [title[0] for title in data]

    # Python list is converted to JSON string
    return json.dumps(movies)


# I have a dictionary that holds functions
# that respond to json requests
JSON = {
    'movies': movies,
}

@app.route('/')
def my_form():
    return render_template("index.html",message="",
        u1m1_val="",u1m2_val="",u1m3_val="",u1m4_val="",u1m5_val="",
        u2m1_val="",u2m2_val="",u2m3_val="",u2m4_val="",u2m5_val="",
        poster_url_1="")

@app.route('/', methods=['POST'])
def my_form_post():
    u1m1 = request.form['u1m1_name']
    u1m2 = request.form['u1m2_name']
    u1m3 = request.form['u1m3_name']
    u1m4 = request.form['u1m4_name']
    u1m5 = request.form['u1m5_name']
    u2m1 = request.form['u2m1_name']
    u2m2 = request.form['u2m2_name']
    u2m3 = request.form['u2m3_name']
    u2m4 = request.form['u2m4_name']
    u2m5 = request.form['u2m5_name']
    u1movies=filter(None,[u1m1,u1m2,u1m3,u1m4,u1m5]) #filter removes empty strings
    u2movies=filter(None,[u2m1,u2m2,u2m3,u2m4,u2m5]) #filter removes empty strings
    recs_tuples = backend(u1movies,u2movies)
    [recTitles,recPosterUrls]=zip(*recs_tuples)
    message="Your ranked recommendations: %s, %s, %s, %s, %s" % tuple(recTitles)
    return render_template("results.html",message=message,
        u1m1_val=u1m1,u1m2_val=u1m2,u1m3_val=u1m3,u1m4_val=u1m4,u1m5_val=u1m5,
        u2m1_val=u2m1,u2m2_val=u2m2,u2m3_val=u2m3,u2m4_val=u2m4,u2m5_val=u2m5,
        poster_url_1=recPosterUrls[0],poster_url_2=recPosterUrls[1],
        poster_url_3=recPosterUrls[2],poster_url_4=recPosterUrls[3],
        poster_url_5=recPosterUrls[4])

# `movies` function is called here
@app.route("/json/<what>")
def ajson(what):

    return JSON[what]()

if __name__ == '__main__':
    app.run("0.0.0.0",port=5000)

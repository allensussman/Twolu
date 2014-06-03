# Flask front-end
# Defines the behavior when:
#   - the home and slides pages are accessed,
#   - the button which computes recommendations is pressed
# 
# Also get_autocompleting_movies() returns movies which autocomplete a string.  This is used for the autcomplete drop down box.


from flask import Flask
from flask import request
from flask import render_template
# flask.json is used to convert Python objects (list/dict) to JSON
from flask import json
from twolu_backend import backend
from DbAccess import DbAccess

app = Flask(__name__)

app.debug = True


@app.route('/')
def render_home_page():
    # uxmx_val are the initial values of the movie input boxes
    return render_template("index.html",
        u1m1_val="",u1m2_val="",u1m3_val="",u1m4_val="",u1m5_val="",
        u2m1_val="",u2m2_val="",u2m3_val="",u2m4_val="",u2m5_val="")


@app.route('/', methods=['POST'])
def get_and_show_results():
    # get the movies the users input
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
    try:
        # twolu is the SQL database that contains movie names,
        # svd-10M-k100 is the ratings file on which svd has been performed
        recs_tuples = backend(u1movies,u2movies,'twolu','svd-10M-k100') 
        [recTitles,recPosterUrls,movieUrls]=zip(*recs_tuples)
        return render_template("results.html",
            poster_url_1=recPosterUrls[0],poster_url_2=recPosterUrls[1],
            poster_url_3=recPosterUrls[2],poster_url_4=recPosterUrls[3],
            poster_url_5=recPosterUrls[4],movie_url_1=movieUrls[0],
            movie_url_2=movieUrls[1],movie_url_3=movieUrls[2],movie_url_4=movieUrls[3],
            movie_url_5=movieUrls[4])
    except:
         return render_template("error.html")


@app.route('/slides.html')
def render_slides_page():
    return render_template("slides.html")

# This function is used for autocompletion.  See index.html
@app.route("/json/movies")
def get_autocompleting_movies():
    """Return list of movies where first letters match query."""
    # backend.getAutocompletingMovies('twolu')
    db = DbAccess('twolu',usr='root')

    q = request.args.get('q')

    # This is my query to find movies matching query
    db.cursor.execute(("SELECT Title FROM movies WHERE Title LIKE '{0}%' LIMIT 10").format(q))

    data = db.cursor.fetchall()

    # Matching movies are in a list
    movies = [title[0] for title in data]

    # Python list is converted to JSON string
    return json.dumps(movies)

if __name__ == '__main__':
    app.run("0.0.0.0",port=5000)

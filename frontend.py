from flask import Flask
from flask import request
from flask import render_template
import backend

app = Flask(__name__)

app.debug = True

@app.route('/')
def my_form():
    return render_template("index.html",message="",first_movie="",second_movie="")

@app.route('/', methods=['POST'])
def my_form_post():
    movie1 = request.form['movie1']
    movie2 = request.form['movie2']
    rec_movies = backend.recommendations([movie1],[movie2])
    message="Your ranked recommendations: %s, %s, %s, %s, %s" % tuple(rec_movies)
    return render_template("index.html",message=message,first_movie=movie1,second_movie=movie2)

if __name__ == '__main__':
    app.run()
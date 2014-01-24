from flask import Flask
from flask import request
from flask import render_template
import backend

app = Flask(__name__)

app.debug = True

@app.route('/')
def my_form():
    return render_template("index.html",message="",u1m1_val="",u1m2_val="",u2m1_val="",u2m2_val="")

@app.route('/', methods=['POST'])
def my_form_post():
    u1m1 = request.form['u1m1_name']
    u1m2 = request.form['u1m2_name']
    u2m1 = request.form['u2m1_name']
    u2m2 = request.form['u2m2_name']
    u1movies=filter(None,[u1m1,u1m2]) #filter removes empty strings
    u2movies=filter(None,[u2m1,u2m2]) #filter removes empty strings
    from code import interact; interact(local=locals())

    rec_movies = backend.recommendations(u1movies,u2movies)
    message="Your ranked recommendations: %s, %s, %s, %s, %s" % tuple(rec_movies)
    return render_template("index.html",message=message,u1m1_val=u1m1,u1m2_val=u1m2,u2m1_val=u2m1,u2m2_val=u2m2)

if __name__ == '__main__':
    app.run()
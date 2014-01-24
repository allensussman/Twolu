from flask import Flask
from flask import request
from flask import render_template
import backend

app = Flask(__name__)

app.debug = True

@app.route('/')
def my_form():
    return render_template("index.html",message="",
        u1m1_val="",u1m2_val="",u1m3_val="",u1m4_val="",u1m5_val="",u2m1_val="",u2m2_val="",u2m3_val="",u2m4_val="",u2m5_val="")

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
    from code import interact; interact(local=locals())

    rec_movies = backend.recommendations(u1movies,u2movies)
    message="Your ranked recommendations: %s, %s, %s, %s, %s" % tuple(rec_movies)
    return render_template("index.html",message=message,
        u1m1_val=u1m1,u1m2_val=u1m2,u1m3_val=u1m3,u1m4_val=u1m4,u1m5_val=u1m5,u2m1_val=u2m1,u2m2_val=u2m2,u2m3_val=u2m3,u2m4_val=u2m4,u2m5_val=u2m5)

if __name__ == '__main__':
    app.run()
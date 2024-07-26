from flask import Flask, redirect, render_template

app = Flask(__name__)

flow_rate = 2.52
p_ven = -11
p_int = 191
p_art = 180
t_art = 37.6
svo2 = 83.0
delta_p = 11


@app.route('/')
def index():
    return render_template('index.html')



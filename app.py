from flask import Flask, redirect, render_template, jsonify
import random
import json

# Initialize flask app
app = Flask(__name__)

# Define your safety range limits
safety_ranges = {
    'flow_rate': (2.0, 3.0),
    'p_ven': (-10, 10),
    'p_int': (150, 200),
    'p_art': (100, 180),
    't_art': (35, 40),
    'svo2': (70, 90),
    'delta_p': (5, 15),
}

# Example values
flow_rate = 2.52
p_ven = -11
p_int = 191
p_art = 180
t_art = 37.6
svo2 = 83.0
delta_p = 11
rpm = 4000

def load_data():
    with open('data.json', 'r') as f:
        return json.load(f)


def check_safety(value, range):
    return range[0] <= value <= range[1]

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/dashboard')
def dashboard():
    safety_status = {
        'flow_rate': check_safety(flow_rate, safety_ranges['flow_rate']),
        'p_ven': check_safety(p_ven, safety_ranges['p_ven']),
        'p_int': check_safety(p_int, safety_ranges['p_int']),
        'p_art': check_safety(p_art, safety_ranges['p_art']),
        't_art': check_safety(t_art, safety_ranges['t_art']),
        'svo2': check_safety(svo2, safety_ranges['svo2']),
        'delta_p': check_safety(delta_p, safety_ranges['delta_p']),
    }
    return render_template('dashboard.html', rpm=rpm, flow_rate=flow_rate, p_ven=p_ven, p_int=p_int, p_art=p_art, t_art=t_art, svo2=svo2, delta_p=delta_p, safety_status=safety_status)

@app.route('/admin')
def admin():
    return render_template("admin.html")

@app.route('/update')
def update():
    # Update example values (in a real application, these would be fetched from sensors or a database)
    global flow_rate, p_ven, p_int, p_art, t_art, svo2, delta_p, rpm
    flow_rate = round(random.uniform(2.0, 3.0), 2)
    p_ven = random.randint(-15, 15)
    p_int = random.randint(140, 210)
    p_art = random.randint(90, 190)
    t_art = round(random.uniform(34.0, 41.0), 1)
    svo2 = round(random.uniform(65.0, 95.0), 1)
    delta_p = random.randint(0, 20)
    rpm = random.randint(3500, 4500)

    safety_status = {
        'flow_rate': check_safety(flow_rate, safety_ranges['flow_rate']),
        'p_ven': check_safety(p_ven, safety_ranges['p_ven']),
        'p_int': check_safety(p_int, safety_ranges['p_int']),
        'p_art': check_safety(p_art, safety_ranges['p_art']),
        't_art': check_safety(t_art, safety_ranges['t_art']),
        'svo2': check_safety(svo2, safety_ranges['svo2']),
        'delta_p': check_safety(delta_p, safety_ranges['delta_p'])
    }
    return jsonify(
        flow_rate=flow_rate, 
        p_ven=p_ven, 
        p_int=p_int, 
        p_art=p_art, 
        t_art=t_art, 
        svo2=svo2, 
        delta_p=delta_p, 
        rpm=rpm, 
        safety_status=safety_status
    )

if __name__ == '__main__':
    app.run(debug=True)

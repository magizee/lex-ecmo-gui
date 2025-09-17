# Import Modules
from flask import Flask, redirect, render_template, jsonify, request
import random
import json
from flask_wtf import FlaskForm
from wtforms import DecimalRangeField
import time
import subprocess
import os


# Initialize flask app
app = Flask(__name__)


# Constants
FLOW_RATE_MAX = 20.0
FLOW_RATE_MIN = 0.0

P_VEN_MAX = 0.0
P_VEN_MIN = -100.0

P_ART_MAX = 500.0
P_ART_MIN = 0.0

P_INT_MAX = 500.0
P_INT_MIN = 0.0

T_ART_MAX = 45.0
T_ART_MIN = 30.0

DELTA_P_MAX = 60.0
DELTA_P_MIN = 0.0

SVO2_MAX = 100.0
SVO2_MIN = 30.0

RPM_MIN = 0
RPM_MAX = 30000
# Data Array
data = {"flow_rate": round((FLOW_RATE_MAX + FLOW_RATE_MIN) / 2, 2), #flow
        "p_ven": round((P_VEN_MAX + P_VEN_MIN) / 2, 2), #p_ven
        "p_int": round((P_INT_MAX + P_INT_MIN) / 2, 2), #p_int
        "delta_p": round((DELTA_P_MAX + DELTA_P_MIN) / 2, 2) , #deltap
        "rpm": 0, #rpm
        "p_art": round((P_ART_MAX + P_ART_MIN) / 2, 2),    #p_art
        "t_art": round((T_ART_MAX + T_ART_MIN) / 2, 2), #t_art
        "svo2": round((SVO2_MAX + SVO2_MIN) / 2, 2) #svo2
}

# Alarm ranges
YELLOW_ALARM = {
    "flow_rate": [2, 6], # Flow
    "p_ven": [-40, -10], #Pven
    "p_int": [60, 250], #Pint
    "p_art": [80, 300], #Part
    "delta_p": [0, 40], #Delta_P
    "t_art": [34.0, 38.5], #Tart
    "svo2": [60, 85] #SVO2
}

RED_ALARM = {
    "flow_rate": [1, 7.5], # Flow
    "p_ven": [-80, 5], #Pven
    "p_int": [30, 3000], #Pint
    "p_art": [50, 350], #Part
    "delta_p": [-5, 60], #Delta_P
    "t_art": [32.0, 39.5], #Tart
    "svo2": [50, 90] #SVO2
}


ALERT_MESSAGE = {
    "flow_rate": {
        "low": {1: "low ECMO flow", 2: "negative flow detected"},
        "high": {1: "high ECMO flow", 2: "excessive flow"}
    },
    "p_ven": {
        "low": {1: "p_ven magnitude high", 2: "p_ven magnitude very high"},
        "high": {1: "p_ven magnitude low", 2: "p_ven magnitude very low"}
    },
    "p_int": {
        "low": {1: "p_int low", 2: "p_int very low"},
        "high": {1: "p_int high", 2: "p_int very high"}
    },
    "p_art": {
        "low": {1: "p_art low", 2: "p_art very low"},
        "high": {1: "p_art high", 2: "p_art very high"}
    },
    "delta_p": {
        "low": {1: "delta_p low", 2: "delta_p very low"},
        "high": {1: "delta_p high", 2: "delta_p very high"}
    },
    "t_art": {
        "low": {1: "t_art low", 2: "t_art very low"},
        "high": {1: "t_art high", 2: "t_art very high"}
    },
    "svo2": {
        "low": {1: "svo2 low", 2: "svo2 very low"},
        "high": {1: "svo2 high", 2: "svo2 very high"}
    }
}

def initValues():
    global data
    data = [round((FLOW_RATE_MAX + FLOW_RATE_MIN) / 2, 2), #flow
        round((P_VEN_MAX + P_VEN_MIN) / 2, 2), #p_ven
        round((P_INT_MAX + P_INT_MIN) / 2, 2), #p_int
        round((DELTA_P_MAX + DELTA_P_MIN) / 2, 2) , #deltap
        0, #rpm
        round((P_ART_MAX + P_ART_MIN) / 2, 2),    #p_art
        round((T_ART_MAX + T_ART_MIN) / 2, 2), #t_art
        round((SVO2_MAX + SVO2_MIN) / 2, 2) #svo2
    ]

@app.route('/admin/setPresets')
def setPresets():
    return render_template('setPresets.html')

def to_float(x): 
    try: return float(x)
    except (TypeError, ValueError): return None

#only place to change max/min
@app.route('/admin/setPresets/send', methods=['POST'])
def setPresetsSend():
    global FLOW_RATE_MAX
    global FLOW_RATE_MIN
    global P_VEN_MAX
    global P_VEN_MIN
    global P_INT_MAX
    global P_INT_MIN
    global P_ART_MAX
    global P_ART_MIN
    global T_ART_MAX
    global T_ART_MIN
    global SVO2_MAX
    global SVO2_MIN
    global DELTA_P_MAX
    global DELTA_P_MIN
    if(request.form['VHigh'] != ""):
        FLOW_RATE_MAX = (request.form['VHigh'])
    if(request.form['VLow'] != ""):
        FLOW_RATE_MIN = (request.form['VLow'])
    if(request.form['PvenHigh'] != ""):
        P_VEN_MAX = (request.form['PvenHigh'])
    if(request.form['PvenLow'] != ""):
        P_VEN_MIN = (request.form['PvenLow'])
    if(request.form['PintHigh'] != ""):
        P_INT_MAX = (request.form['PintHigh'])
    if(request.form['PintLow'] != ""):
        P_INT_MIN = (request.form['PintLow'])
    if(request.form['PartHigh'] != ""):
        P_ART_MAX = (request.form['PartHigh'])
    if(request.form['PartLow'] != ""):
        P_ART_MIN = (request.form['PartLow'])
    if(request.form['TartHigh'] != ""):
        T_ART_MAX = (request.form['TartHigh'])
    if(request.form['TartLow'] != ""):
        T_ART_MIN = (request.form['TartLow'])
    if(request.form['SvO2High'] != ""):
        SVO2_MAX = (request.form['SvO2High'])
    if(request.form['SvO2Low'] != ""):
        SVO2_MIN = (request.form['SvO2Low'])
    if(request.form['DeltaPHigh'] != ""):
        DELTA_P_MAX = (request.form['DeltaPHigh'])
    if(request.form['DeltaPLow'] != ""):
        DELTA_P_MIN = (request.form['DeltaPLow'])
    initValues()
    return redirect('/admin')

@app.route('/admin/loading/<scen>', methods=['POST'])
def exampleScenario1Loading(scen):
    timer = request.form['example1Length']
    if timer:
        return render_template('loading.html', scen=scen, timer=timer)
    else:
        return render_template('loading.html', scen=scen, timer=5)

@app.route('/admin/exampleScenario1/<timer>', methods=['GET'])
def exampleScenario1(timer):
    global data
    if timer.isdigit() == False:
        return redirect('/admin')
    timer = int(timer)
    Vstatic = data["flow_rate"]
    PvenStatic = data["p_ven"]
    SvO2Static = data["t_art"]
    startTime = time.time()
    currentTimer = int(time.time() - startTime)
    print(Vstatic)
    while (currentTimer) <= timer:
        data["flow_rate"] = round(Vstatic + (currentTimer/timer) * (65-Vstatic),2)
        data["p_ven"] = round(PvenStatic + (currentTimer/timer) * (75-PvenStatic),2)
        data["t_art"] = round(SvO2Static + (currentTimer/timer) * (80-SvO2Static),2)
        currentTimer = int(time.time() - startTime)
    
    return redirect('/admin')
    
@app.route('/admin/sliders', methods=['POST'])
def sliders():
    global data
    print(request.form)
    data["flow_rate"] = to_float(request.form['VS'])
    data["p_ven"] = to_float(request.form['PvenS'])
    data["p_int"] = to_float(request.form['PintS'])
    data["delta_p"] = to_float(request.form['DeltaPS'])
    data["p_art"] = to_float(request.form['PartS'])
    data["t_art"] = to_float(request.form['TartS'])
    data["svo2"] = to_float(request.form['SvO2S'])
    return redirect('/admin')
    
@app.route('/admin')
def controlPanel():
    return render_template('admin.html', V=data["flow_rate"], Pven=data["p_ven"], Pint=data["p_int"], Part=data["p_art"], DeltaP=data["delta_p"], Tart=data["t_art"], SvO2=data["svo2"], VMin=FLOW_RATE_MIN, VMax=FLOW_RATE_MAX, PvenMin=P_VEN_MIN, PvenMax=P_VEN_MAX, PintMin=P_INT_MIN, PintMax=P_INT_MAX, PartMax=P_ART_MAX, PartMin=P_ART_MIN, TartMin=T_ART_MIN, TartMax=T_ART_MAX, SvO2Min=SVO2_MIN, SvO2Max=SVO2_MAX, DeltaPMin=DELTA_P_MIN, DeltaPMax=DELTA_P_MAX)

# Front end code
def load_data():
    with open('data.json', 'r') as f:
        return json.load(f)


def check_safety(value, y_range, r_range):
    if r_range[0] <= value <= r_range[1]:
        if y_range[0] <= value <= y_range[1]:
            return 0, "safe"
        else:
            if value > y_range[1]:
                return 1, "high"
            else:
                return 1, "low"
    else:
        if value > r_range[1]:
            return 2, "high"
        else:
            return 2, "low"
    


@app.route('/')
def home():
    return render_template('home.html')

@app.route('/dashboard')
def dashboard():
    safety_status = {}
    first_yellow_msg = None
    first_red_msg = None

    for key in data.keys():
        if key == "rpm":
            continue
        sev, direction = check_safety(data[key], YELLOW_ALARM[key], RED_ALARM[key])
        safety_status[key] = sev  # keep exactly as your JS expects

        if sev > 0:  # only build a message when in alarm
            msg = ALERT_MESSAGE.get(key, {}).get(direction, {}).get(sev)
            if sev == 2 and first_red_msg is None:
                first_red_msg = msg
            elif sev == 1 and first_yellow_msg is None:
                first_yellow_msg = msg

    banner_text = first_red_msg or first_yellow_msg

    return render_template('dashboard.html', rpm=data["rpm"], flow_rate=data["flow_rate"], p_ven=data["p_ven"], p_int=data["p_int"], p_art=data["p_art"], t_art=data["t_art"], svo2=data["svo2"], delta_p=data["delta_p"], safety_status=safety_status, banner_text=banner_text)

@app.route('/update')
def update():
    # Update example values (in a real application, these would be fetched from sensors or a database)
    """
    global flow_rate, p_ven, p_int, p_art, t_art, svo2, delta_p, rpm
    flow_rate = round(random.uniform(2.0, 3.0), 2)
    p_ven = random.randint(-15, 15)
    p_int = random.randint(140, 210)
    p_art = random.randint(90, 190)
    t_art = round(random.uniform(34.0, 41.0), 1)
    svo2 = round(random.uniform(65.0, 95.0), 1)
    delta_p = random.randint(0, 20)
    rpm = random.randint(3500, 4500)
    """
    safety_status = {}
    first_yellow_msg = None
    first_red_msg = None

    for key in data.keys():
        if key == "rpm":
            continue
        sev, direction = check_safety(data[key], YELLOW_ALARM[key], RED_ALARM[key])
        safety_status[key] = sev  # keep exactly as your JS expects

        if sev > 0:  # only build a message when in alarm
            msg = ALERT_MESSAGE.get(key, {}).get(direction, {}).get(sev)
            if sev == 2 and first_red_msg is None:
                first_red_msg = msg
            elif sev == 1 and first_yellow_msg is None:
                first_yellow_msg = msg

    banner_text = first_red_msg or first_yellow_msg

    return jsonify(
        flow_rate=data["flow_rate"], 
        p_ven=data["p_ven"], 
        p_int=data["p_int"], 
        p_art=data["p_art"], 
        t_art=data["t_art"], 
        svo2=data["svo2"], 
        delta_p=data["delta_p"], 
        rpm=data["rpm"], 
        safety_status=safety_status,
        banner_text=banner_text
    )

@app.route('/rpm')
def getRPM():
    global data
    return jsonify(
        rpm=data["rpm"]
        )

@app.route('/joystick-data', methods=['POST'])
def joystick_data():
    global data
    json_data = request.get_json()
    if 'rpm' in data:
        data["rpm"] = max(min(int(json_data['rpm']), RPM_MAX), RPM_MIN)  # clamp to safety bounds
        print("Joystick RPM updated to:", data["rpm"])
    return '', 204


@app.route('/exit', methods=['POST'])
def exit():
    result = subprocess.run(
        ["sudo", "pkill", "-f", "chromium"],
        capture_output=True,
        text=True
    )
    print("RETURN CODE:", result.returncode)
    print("STDOUT:", result.stdout)
    print("STDERR:", result.stderr)
    return '', 204

if __name__ == '__main__':
    app.run(host= '0.0.0.0', port=9000, debug=False)

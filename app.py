# Import Modules
from flask import Flask, redirect, render_template, jsonify, request
import random
import json
from flask_wtf import FlaskForm
from wtforms import DecimalRangeField
import time
import subprocess
import os

import os, json, time, tempfile, shutil
from pathlib import Path

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

# Data Dictionary
data = {"flow_rate": round((FLOW_RATE_MAX + FLOW_RATE_MIN) / 2, 2), #flow
        "p_ven": round((P_VEN_MAX + P_VEN_MIN) / 2, 2), #p_ven
        "p_int": round((P_INT_MAX + P_INT_MIN) / 2, 2), #p_int
        "delta_p": round((DELTA_P_MAX + DELTA_P_MIN) / 2, 2) , #deltap
        "rpm": 0, #rpm
        "p_art": round((P_ART_MAX + P_ART_MIN) / 2, 2),    #p_art
        "t_art": round((T_ART_MAX + T_ART_MIN) / 2, 2), #t_art
        "svo2": round((SVO2_MAX + SVO2_MIN) / 2, 2) #svo2
}

# Alarm ranges and text
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

#
def initValues():
    """
    Initializes data to be the midpoint of their maximums and minimums
    """
    global data
    data = {
        "flow_rate": round((FLOW_RATE_MAX + FLOW_RATE_MIN) / 2, 2),
        "p_ven":     round((P_VEN_MAX+ P_VEN_MIN)   / 2, 2),
        "p_int":     round((P_INT_MAX   + P_INT_MIN)   / 2, 2),
        "delta_p":   round((DELTA_P_MAX + DELTA_P_MIN) / 2, 2),
        "rpm":       0,
        "p_art":     round((P_ART_MAX   + P_ART_MIN)   / 2, 2),
        "t_art":     round((T_ART_MAX   + T_ART_MIN)   / 2, 2),
        "svo2":      round((SVO2_MAX    + SVO2_MIN)    / 2, 2),
    }

@app.route('/admin/setPresets')
def setPresets():
    """
    Flask route to show screen allowing admin to change maximum and minimum values
    """
    return render_template('setPresets.html')

def _to_float(v, default=None):
    """
    Returns a float if the parameter v is able to be converted into one
    """
    try: return float(v)
    except (TypeError, ValueError): return default

@app.route('/admin/setPresets/send', methods=['POST'])
def setPresetsSend():
    """
    Flask route that triggers after admin chooses to send preset values. T
    This is the only way to change global constants of maximums and minimums
    """
    global FLOW_RATE_MAX, FLOW_RATE_MIN, P_VEN_MAX, P_VEN_MIN, P_INT_MAX, P_INT_MIN
    global P_ART_MAX, P_ART_MIN, T_ART_MAX, T_ART_MIN, SVO2_MAX, SVO2_MIN, DELTA_P_MAX, DELTA_P_MIN

    VHigh = _to_float(request.form.get('VHigh'), FLOW_RATE_MAX)
    VLow  = _to_float(request.form.get('VLow'),  FLOW_RATE_MIN)
    if VHigh is not None: FLOW_RATE_MAX = VHigh
    if VLow  is not None: FLOW_RATE_MIN = VLow

    PvenHigh = _to_float(request.form.get('PvenHigh'), P_VEN_MAX)
    PvenLow  = _to_float(request.form.get('PvenLow'),  P_VEN_MIN)
    if PvenHigh is not None: P_VEN_MAX = PvenHigh
    if PvenLow  is not None: P_VEN_MIN = PvenLow

    PintHigh = _to_float(request.form.get('PintHigh'), P_INT_MAX)
    PintLow  = _to_float(request.form.get('PintLow'),  P_INT_MIN)
    if PintHigh is not None: P_INT_MAX = PintHigh
    if PintLow  is not None: P_INT_MIN = PintLow

    PartHigh = _to_float(request.form.get('PartHigh'), P_ART_MAX)
    PartLow  = _to_float(request.form.get('PartLow'),  P_ART_MIN)
    if PartHigh is not None: P_ART_MAX = PartHigh
    if PartLow  is not None: P_ART_MIN = PartLow

    TartHigh = _to_float(request.form.get('TartHigh'), T_ART_MAX)
    TartLow  = _to_float(request.form.get('TartLow'),  T_ART_MIN)
    if TartHigh is not None: T_ART_MAX = TartHigh
    if TartLow  is not None: T_ART_MIN = TartLow

    SvO2High = _to_float(request.form.get('SvO2High'), SVO2_MAX)
    SvO2Low  = _to_float(request.form.get('SvO2Low'),  SVO2_MIN)
    if SvO2High is not None: SVO2_MAX = SvO2High
    if SvO2Low  is not None: SVO2_MIN = SvO2Low

    DeltaPHigh = _to_float(request.form.get('DeltaPHigh'), DELTA_P_MAX)
    DeltaPLow  = _to_float(request.form.get('DeltaPLow'),  DELTA_P_MIN)
    if DeltaPHigh is not None: DELTA_P_MAX = DeltaPHigh
    if DeltaPLow  is not None: DELTA_P_MIN = DeltaPLow

    initValues()
    return redirect('/admin')


@app.route('/admin/loading/<scen>', methods=['POST'])
def exampleScenario1Loading(scen):
    """
    Flask route that shows loading screen when example timer is in use
    """
    timer = request.form['example1Length']
    if timer:
        return render_template('loading.html', scen=scen, timer=timer)
    else:
        return render_template('loading.html', scen=scen, timer=5)

@app.route('/admin/exampleScenario1/<timer>', methods=['GET'])
def exampleScenario1(timer):
    """
    creates an example scenario where flow, p_ven, and t_art approach
    preset values over a period of time
    """
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
    """
    gets data from the sliders and alters the values
    """
    global data
    data["flow_rate"] = _to_float(request.form.get('VS'),      data["flow_rate"])
    data["p_ven"]     = _to_float(request.form.get('PvenS'),   data["p_ven"])
    data["p_int"]     = _to_float(request.form.get('PintS'),   data["p_int"])
    data["delta_p"]   = _to_float(request.form.get('DeltaPS'), data["delta_p"])
    data["p_art"]     = _to_float(request.form.get('PartS'),   data["p_art"])
    data["t_art"]     = _to_float(request.form.get('TartS'),   data["t_art"])
    data["svo2"]      = _to_float(request.form.get('SvO2S'),   data["svo2"])
    return redirect('/admin')

    
@app.route('/admin')
def controlPanel():
    """
    renders administrator view
    """
    return render_template('admin.html', V=data["flow_rate"], Pven=data["p_ven"], Pint=data["p_int"], Part=data["p_art"], DeltaP=data["delta_p"], Tart=data["t_art"], SvO2=data["svo2"], VMin=FLOW_RATE_MIN, VMax=FLOW_RATE_MAX, PvenMin=P_VEN_MIN, PvenMax=P_VEN_MAX, PintMin=P_INT_MIN, PintMax=P_INT_MAX, PartMax=P_ART_MAX, PartMin=P_ART_MIN, TartMin=T_ART_MIN, TartMax=T_ART_MAX, SvO2Min=SVO2_MIN, SvO2Max=SVO2_MAX, DeltaPMin=DELTA_P_MIN, DeltaPMax=DELTA_P_MAX)

# Front end code
def load_data():
    """
    loads json data
    """
    with open('data.json', 'r') as f:
        return json.load(f)


def check_safety(value, y_range, r_range):
    """
    Function checks if a value is inside alert ranges and returns 
    the severity and direction of them
    Paremeters: 
        value (float): the piece of data i.e. flow_rate
        y_range (List): the range for a yellow alert
        r_range (List): the range for a red alert
    Returns:
        (int) The severity (safe, yellow, red)
        (str) The direction of the alert (too high or too low)
    """
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
    """
    renders the homescreen
    """
    return render_template('home.html')

@app.route('/dashboard')
def dashboard():
    """
    renders the dashboard
    """
    global data
    safety_status = {}
    first_yellow_msg = None
    first_red_msg = None

    #alert logic
    for key in data.keys():
        if key == "rpm":
            continue
        sev, direction = check_safety(data[key], YELLOW_ALARM[key], RED_ALARM[key])
        safety_status[key] = sev  

        if sev > 0:  
            msg = ALERT_MESSAGE.get(key, {}).get(direction, {}).get(sev)
            if sev == 2 and first_red_msg is None:
                first_red_msg = msg
            elif sev == 1 and first_yellow_msg is None:
                first_yellow_msg = msg

    banner_text = first_red_msg or first_yellow_msg

    return render_template('dashboard.html', rpm=data["rpm"], flow_rate=data["flow_rate"], p_ven=data["p_ven"], p_int=data["p_int"], p_art=data["p_art"], t_art=data["t_art"], svo2=data["svo2"], delta_p=data["delta_p"], safety_status=safety_status, banner_text=banner_text)

@app.route('/update')
def update():
    """
    Updates values
    Finds safety status for all entries
    Determines alert severity
    Returns everything as a json
    Called once a second
    """
    # Update example values (in a real application, these would be fetched from sensors or a database)
    safety_status = {}
    first_yellow_msg = None
    first_red_msg = None

    #alert logic
    for key in data.keys():
        if key == "rpm":
            continue
        sev, direction = check_safety(data[key], YELLOW_ALARM[key], RED_ALARM[key])
        safety_status[key] = sev  

        if sev > 0: 
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
    """
    Returns rpm every 100ms
    """
    global data
    return jsonify(
        rpm=data["rpm"]
        )

@app.route('/joystick-data', methods=['POST'])
def joystick_data():
    """
    backend for joystick
    """
    global data
    json_data = request.get_json(silent=True) or {}
    rpm_raw = json_data.get('rpm')
    try:
        rpm_val = int(rpm_raw)
    except (TypeError, ValueError):
        return '', 400  # bad payload

    data["rpm"] = max(min(rpm_val, RPM_MAX), RPM_MIN)  # clamp
    print("Joystick RPM updated to:", data["rpm"])
    return '', 204



@app.route('/exit', methods=['POST'])
def exit():
    """
    exits out of application
    """
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



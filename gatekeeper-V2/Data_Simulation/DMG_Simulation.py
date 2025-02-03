import pandas as pd
import numpy as np
from scipy import stats
from datetime import datetime
import time
import requests

dmg_data = {
    "mac_address": "99:AA:BB:CC:DD:EE",
    "data": {
    "dmg_data":[
        {
            "machine_status" : "on",
            "start_up" : None,
            "total_number" : None,
            "current_cycle" : 0,
            "current_run_time" : 0,
            "total_cutting_time" : 0,
            "tool_name" : None,
            "tool_radius" : None,
            "tool_length" : None,
            "current_program_name" : "____",
            "current_program_content" : "____",
            "x_axis_coordinate" : 0,
            "y_axis_coordinate" : 0,
            "z_axis_coordinate" : 0,
            "c_axis_coordinate" : 0,
            "a_axis_coordinate" : 0,
            "driveload_x" : 0,
            "driveload_y" : 0,
            "driveload_z" : 0,
            "driveload_c" : 0,
            "driveload_a" : 0,
            "spindle_load" : 0,
            "program_status" : 0,
            "spindle_speed" : 0,
            "spindle_feed" : 0,
            "spindle_override" : 0,
            "feed_override" : 0
        }]
    }
}

data_type = {
    "start_up" : int,
    "total_number" : int,
    "current_cycle" : int,
    "current_run_time" : int,
    "total_cutting_time" : int,
    "tool_radius" : float,
    "tool_length" : float,
    "spindle_speed" : int,
    "spindle_feed" : int,
    "spindle_override" : int,
    "feed_override" : int,
    "x_axis_coordinate" : float,
    "y_axis_coordinate" : float,
    "z_axis_coordinate" : float,
    "c_axis_coordinate" : float,
    "a_axis_coordinate" : float,
    "driveload_x" : float,
    "driveload_y" : float,
    "driveload_z" : float,
    "driveload_c" : float,
    "driveload_a" : float,
    "program_status" : int,
    "spindle_load" : float
}

def convert_data_type(data_type):
    for key in data_type.keys():
        if dmg_data["data"]["dmg_data"][0][key] is not None:
            dmg_data["data"]["dmg_data"][0][key] = data_type[key](dmg_data["data"]["dmg_data"][0][key])
    
    return 0

def manual_distributions(df, columns):
    distributions = {}
    for column in columns:
        distributions[column] = {"type": "manual"}
        dmg_data["data"]["dmg_data"][0][column] = df[column].iloc[-1]
    
    return distributions

def analyze_numerical_distributions(df):
    distributions = {}
    for column in ["x_axis_coordinate", "y_axis_coordinate", "z_axis_coordinate", "c_axis_coordinate", "a_axis_coordinate", "driveload_x", "driveload_y", "driveload_z", "driveload_c", "driveload_a", "spindle_load"]:
        mean, std = stats.norm.fit(df[column])
        distributions[column] = {"type": "numerical", "mean": mean, "std": std}

    return distributions

def analyze_categorical_distributions(df):
    distributions = {}
    for column in ["tool_name", "tool_radius", "tool_length", "current_program_name", "current_program_content", "program_status", "spindle_speed", "spindle_feed", "spindle_override", "feed_override"]:
        counts = df[column].value_counts(normalize=True)
        distributions[column] = {"type": "categorical", "probabilities": counts.to_dict()}
    
    return distributions

def generate_synthetic_data(distributions, start_up_time, total_number_time):
    for column, params in distributions.items():
        if params["type"] == "numerical":
            mean, std = params["mean"], params["std"]
            dmg_data["data"]["dmg_data"][0][column] = float(np.random.normal(mean, std, 1)[0])
        elif params["type"] == "categorical":
            categories, probabilities = zip(*params["probabilities"].items())
            dmg_data["data"]["dmg_data"][0][column] = str(np.random.choice(categories, size= 1, p= probabilities)[0])
        else:
            if column == "start_up":
                diff = datetime.now() - start_up_time
                if diff.total_seconds() > 1:
                    dmg_data["data"]["dmg_data"][0][column] += diff.total_seconds()
                    dmg_data["data"]["dmg_data"][0]["total_cutting_time"] += max(1, round(0.75*diff.total_seconds()))
                    start_up_time = datetime.now()
                
                    if dmg_data["data"]["dmg_data"][0]["current_run_time"] < dmg_data["data"]["dmg_data"][0]["current_cycle"]:
                        dmg_data["data"]["dmg_data"][0]["current_run_time"] += diff.total_seconds()
                    else:
                        dmg_data["data"]["dmg_data"][0]["current_cycle"] += 100*float(np.random.normal(0, 0.5, 1)[0])    
                        dmg_data["data"]["dmg_data"][0]["current_run_time"] = 0  
            elif column == "total_number":
                diff = datetime.now() - total_number_time
                if diff.total_seconds() / 3600 > 1:
                    dmg_data["data"]["dmg_data"][0][column] += 1
                    total_number_time = datetime.now()
    return start_up_time, total_number_time


file_path = 'data/past_dmg_data.csv'  # Replace with the path to your CSV file
df = pd.read_csv(file_path)
URL = "https://twin.zwillinglabs.io/api/iot/data"
# URL = "http://3.110.75.63/node/api/iot/data"


numerical_dis = analyze_numerical_distributions(df)
categorical_dis = analyze_categorical_distributions(df)
manual_dis = manual_distributions(df, columns= ["start_up", "total_number", "current_cycle", "current_run_time", "total_cutting_time"])
distributions = {**numerical_dis, **categorical_dis, **manual_dis}

start_up_time = datetime.now()
total_number_time = datetime.now()
while True:  
    start_up_time, total_number_time = generate_synthetic_data(distributions, start_up_time, total_number_time)
    convert_data_type(data_type)
    res = requests.post(URL, json= dmg_data)
    print(datetime.now().strftime("%m/%d/%Y %H:%M:%S"), "===================")
    print(dmg_data["data"]["dmg_data"][0])
    print("response: ", res.text)
    time.sleep(10)
    
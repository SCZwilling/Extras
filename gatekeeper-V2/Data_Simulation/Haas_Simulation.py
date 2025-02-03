import pandas as pd
import numpy as np
from scipy import stats
from datetime import datetime
import time
import requests

data = {
    "mac_address": "00:1A:2B:3C:4D:5E",
    "data": {
    "haas_data":[
        {
            "machine_status": "on",
            "total_number": 0,
            "current_cycle": 0,
            "cycle_remaining_time": 0,
            "total_run_time": 0,
            "current_program_name": None,
            "spindle_speed": 0,
            "spindle_override": 0,
            "feed_override": 0,
            "x_axis_coordinate": 0,
            "y_axis_coordinate": 0,
            "z_axis_coordinate": 0,
            "c_axis_coordinate": 0,
            "a_axis_coordinate": 0,
            "b_axis_coordinate": 0, 
            "program_status": None,
            "active_alarm": None,
            "coolant_status": None
        }]
    }
}

data_type = {
    "current_cycle": int,
    "cycle_remaining_time": int,
    "spindle_speed": float,
    "spindle_override": int,
    "feed_override": int,
    "x_axis_coordinate": float,
    "y_axis_coordinate": float,
    "z_axis_coordinate": float,
    "c_axis_coordinate": float,
    "a_axis_coordinate": float,
    "b_axis_coordinate": float, 
    "total_number": int,
    "total_run_time": int,
    "program_status": int
}

def convert_data_type(data_type):
    for key in data_type.keys():
        if data["data"]["haas_data"][0][key] is not None:
            data["data"]["haas_data"][0][key] = data_type[key](data["data"]["haas_data"][0][key])
    
    return 0

def manual_distributions(df, columns):
    distributions = {}
    for column in columns:
        distributions[column] = {"type": "manual"}
        data["data"]["haas_data"][0][column] = df[column].iloc[-1]
    
    return distributions

def analyze_numerical_distributions(df):
    distributions = {}
    for column in ["x_axis_coordinate", "y_axis_coordinate", "z_axis_coordinate", "c_axis_coordinate", "a_axis_coordinate", "b_axis_coordinate"]:
        mean, std = stats.norm.fit(df[column])
        distributions[column] = {"type": "numerical", "mean": mean, "std": std}

    return distributions

def analyze_categorical_distributions(df):
    distributions = {}
    for column in ["current_program_name", "spindle_speed", "spindle_override", "feed_override", "program_status", "active_alarm", "coolant_status"]:
        counts = df[column].value_counts(normalize=True)
        distributions[column] = {"type": "categorical", "probabilities": counts.to_dict()}
    
    return distributions

def generate_synthetic_data(distributions, start_up_time, total_number_time):
    for column, params in distributions.items():
        if params["type"] == "numerical":
            mean, std = params["mean"], params["std"]
            data["data"]["haas_data"][0][column] = float(np.random.normal(mean, std, 1)[0])
        elif params["type"] == "categorical":
            categories, probabilities = zip(*params["probabilities"].items())
            data["data"]["haas_data"][0][column] = str(np.random.choice(categories, size= 1, p= probabilities)[0])
        else:
            if column == "total_run_time":
                diff = datetime.now() - start_up_time
                if diff.total_seconds() > 1:
                    data["data"]["haas_data"][0][column] += diff.total_seconds()
                    start_up_time = datetime.now()
                
                    if data["data"]["haas_data"][0]["cycle_remaining_time"] > 10:
                        data["data"]["haas_data"][0]["cycle_remaining_time"] -= diff.total_seconds()
                    else:
                        data["data"]["haas_data"][0]["current_cycle"] += 100*float(np.random.normal(0, 0.5, 1)[0])    
                        data["data"]["haas_data"][0]["cycle_remaining_time"] = data["data"]["haas_data"][0]["current_cycle"]
            elif column == "total_number":
                diff = datetime.now() - total_number_time
                if diff.total_seconds() / 3600 > 1:
                    data["data"]["haas_data"][0][column] += 1
                    total_number_time = datetime.now()
    return start_up_time, total_number_time


file_path = 'data/past_haas_data.csv'  # Replace with the path to your CSV file
df = pd.read_csv(file_path)
# URL = "https://twin.zwillinglabs.io/api/iot/data"
# URL = "http://13.201.185.72/node/api/iot/data"
URL = "http://3.110.75.63/node/api/iot/data"

numerical_dis = analyze_numerical_distributions(df)
categorical_dis = analyze_categorical_distributions(df)
manual_dis = manual_distributions(df, columns= ["total_number", "current_cycle", "cycle_remaining_time", "total_run_time"])
distributions = {**numerical_dis, **categorical_dis, **manual_dis}

start_up_time = datetime.now()
total_number_time = datetime.now()
while True:  
    start_up_time, total_number_time = generate_synthetic_data(distributions, start_up_time, total_number_time)
    convert_data_type(data_type)
    res = requests.post(URL, json= data)
    print(datetime.now().strftime("%m/%d/%Y %H:%M:%S"), "===================")
    print(data["data"]["haas_data"][0])
    print("response: ", res.text)
    time.sleep(10)
    
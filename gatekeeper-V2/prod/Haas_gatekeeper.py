Node_dict = {
    "current_cycle": ".//ns:AccumulatedTime[@name='ThisCycle']",
    "cycle_remaining_time": ".//ns:AccumulatedTime[@name='CycleRemainingTime']",
    "current_program_name": ".//ns:Program[@name='Program']",
    "spindle_speed": ".//ns:SpindleSpeed[@name='SpindleSpeed']",
    "spindle_override": ".//ns:SpindleSpeed[@name='SpindleSpeedOverride']",
    "feed_override": ".//ns:PathFeedrate[@name='FeedrateOverride']",
    "x_axis_coordinate": ".//ns:PathPosition[@name='X_Axis_Actual_Position']",
    "y_axis_coordinate": ".//ns:PathPosition[@name='Y_Axis_Actual_Position']",
    "z_axis_coordinate": ".//ns:PathPosition[@name='Z_Axis_Actual_Position']",
    "c_axis_coordinate": ".//ns:PathPosition[@name='C_Axis_Actual_Position']",
    "a_axis_coordinate": ".//ns:PathPosition[@name='A_Axis_Actual_Position']",
    "b_axis_coordinate": ".//ns:PathPosition[@name='B_Axis_Actual_Position']",
    "total_number": ".//ns:Message[@name='M30Counter2']",
    "total_run_time": ".//ns:Message[@name='MachineRunTime']",
    "active_alarm": ".//ns:Message[@name='ActiveAlarms']",
    "coolant_status": ".//ns:Message[@name='ShowerCoolantEnabled']",
    "program_status": ".//ns:Execution[@name='RunStatus']"  
}

data_off = {
    "mac_address": "00:1A:2B:3C:4D:5E",
    "data": {
    "haas_data":[
        {
            "machine_status": "off",
            "current_cycle": 0,
            "cycle_remaining_time": 0,
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
            "total_number": 0,
            "total_run_time": 0,
            "active_alarm": None,
            "coolant_status": None,
            "program_status": None
        }]
    }
}

data = {
    "mac_address": "00:1A:2B:3C:4D:5E",
    "data": {
    "haas_data":[
        {
            "machine_status": "off",
            "current_cycle": 0,
            "cycle_remaining_time": 0,
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
            "total_number": 0,
            "total_run_time": 0,
            "active_alarm": None,
            "coolant_status": None,
            "program_status": None
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
}

def convert_data_type(value_dict, data_type):
    for key in data_type.keys():
        if value_dict[key] is not None:
            value_dict[key] = data_type[key](value_dict[key])
    
    return 0

import time
import requests
import platform, subprocess
import urllib
import xml.etree.ElementTree as ET

#URL = "https://twin.zwillinglabs.io/api/iot/data"
URL = "http://3.110.75.63/node/api/iot/data"

#  ping machine
def ping(ipA= '10.172.18.222'):
    param = '-n' if platform.system().lower()=='windows' else '-c'
    # Building the command. Ex: "ping -c 1 google.com"
    command = ['ping', param, '1', ipA]

    return subprocess.call(command) == 0 

while True:
    p = ping()
    try:
        file = urllib.request.urlopen('http://10.172.18.222:8082/UMC-1000SS/current')
        tree = ET.parse(file)
        file.close()
        root = tree.getroot()
        namespaces = {'ns': 'urn:mtconnect.org:MTConnectStreams:1.2'}
        node_value= "on"
        data["data"]["haas_data"][0].update({"machine_status": node_value})

        for key, value in Node_dict.items():
            try:
                node_value = root.find(value, namespaces= namespaces).text
                data["data"]["haas_data"][0].update({key: node_value})
            except:
                pass
        convert_data_type(data["data"]["haas_data"][0], data_type)
        res = requests.post(URL, json= data)
        print(data["data"]["haas_data"][0])
        print("response: ", res.text)
        
    except:
        if p == False:
            convert_data_type(data_off["data"]["haas_data"][0], data_type)
            res = requests.post(URL, json= data_off)
            print(data_off["data"]["haas_data"][0])
            print("response: ", res.text)
            time.sleep(5)
            p=ping()
            if p == False:
                print("after 5 sec")
                
                time.sleep(10)
                q= ping()
                if q == False:
                    time.sleep(30)
                    print("after 25 sec")
                    while ping() == False:
                        print("before 600 sec")
                        time.sleep(600)
                else:
                    pass
            else:
                print("not in loop")
                pass
        else:
            print("Machine is on but something is wrong")
    time.sleep(1)    
Node_dict = { 
    'start_up': "ns=2;s=/Nck/ChannelDiagnose/poweronTime",
    'total_number': "ns=2;s=/Channel/State/totalParts",
    'current_cycle': "ns=2;s=/Channel/ChannelDiagnose/cycleTime",
    'current_run_time': "ns=2;s=/Channel/ChannelDiagnose/operatingTime",
    'total_cutting_time': "ns=2;s=/Channel/ChannelDiagnose/cuttingTime",
    'tool_name': "ns=2;s=/Channel/State/actToolIdent",
    'tool_radius': "ns=2;s=/Channel/State/actToolRadius",
    'tool_length': "ns=2;s=/Channel/State/actToolLength1",
    'current_program_name': "ns=2;s=/Channel/ProgramInfo/progName",
    'current_program_content': "ns=2;s=/Channel/ProgramInfo/block",
    'spindle_speed': "ns=2;s=/Channel/Spindle/actSpeed",
    'spindle_feed': "ns=2;s=/Channel/MachineAxis/actFeedRate",
    'spindle_override': "ns=2;s=/Channel/Spindle/speedOvr",
    'feed_override': "ns=2;s=/Nck/MachineAxis/feedRateOvr",
    'x_axis_coordinate': "ns=2;s=/Nck/MachineAxis/aaIm[u1, 1]",
    'y_axis_coordinate': "ns=2;s=/Nck/MachineAxis/aaIm[u1, 2]",
    'z_axis_coordinate': "ns=2;s=/Nck/MachineAxis/aaIm[u1, 3]",
    'c_axis_coordinate': "ns=2;s=/Nck/MachineAxis/aaIm[u1, 4]",
    'a_axis_coordinate': "ns=2;s=/Nck/MachineAxis/aaIm[u1, 5]",
    'driveload_x': "ns=2;s=/Nck/Spindle/driveLoad[u1, 1]",
    'driveload_y': "ns=2;s=/Nck/Spindle/driveLoad[u1, 2]",
    'driveload_z': "ns=2;s=/Nck/Spindle/driveLoad[u1, 3]",
    'driveload_c': "ns=2;s=/Nck/Spindle/driveLoad[u1, 4]",
    'driveload_a': "ns=2;s=/Nck/Spindle/driveLoad[u1, 5]",
    'program_status': "ns=2;s=/Channel/State/progStatus[u1, 1]",
    'spindle_load': "ns=2;s=/Nck/Spindle/driveLoad[u1, 6]",
}

data = {
    "mac_address": "99:AA:BB:CC:DD:EE",
    "data": {
    "dmg_data":[
        {
            "machine_status" : "off",
            "start_up" : None,
            "total_number" : None,
            "current_cycle" : 0,
            "current_run_time" : 0,
            "total_cutting_time" : 0,
            "tool_name" : None,
            "tool_radius" : None,
            "tool_length" : None,
            "current_program_name" : "Machine is off",
            "current_program_content" : "Machine is off",
            "spindle_speed" : 0,
            "spindle_feed" : 0,
            "spindle_override" : 0,
            "feed_override" : 0,
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
            "program_status" : 0,
            "spindle_load" : 0
        }]
    }
}

data_off = {
    "mac_address": "99:AA:BB:CC:DD:EE",
    "data": {
    "dmg_data":[
        {
            "machine_status" : "off",
            "start_up" : None,
            "total_number" : None,
            "current_cycle" : 0,
            "current_run_time" : 0,
            "total_cutting_time" : 0,
            "tool_name" : None,
            "tool_radius" : None,
            "tool_length" : None,
            "current_program_name" : "Machine is off",
            "current_program_content" : "Machine is off",
            "spindle_speed" : 0,
            "spindle_feed" : 0,
            "spindle_override" : 0,
            "feed_override" : 0,
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
            "program_status" : 0,
            "spindle_load" : 0
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

def convert_data_type(value_dict, data_type):
    for key in data_type.keys():
        if value_dict[key] is not None:
            value_dict[key] = data_type[key](value_dict[key])
    
    return 0

import time
from datetime import datetime
import requests
from opcua import Client
import platform, subprocess

#  url for post and OPCUA enpoint url
url = "opc.tcp://10.173.14.193:500"
#URL = "https://twin.zwillinglabs.io/api/iot/data"
URL = "http://3.110.75.63/node/api/iot/data"

def ping(ipA= '10.173.14.193'):
    param = '-n' if platform.system().lower()=='windows' else '-c'
    command = ['ping', param, '1', ipA] # Building the command. Ex: "ping -c 1 google.com"

    return subprocess.call(command) == 0 

while True:
    p = ping()
    try:
        client = Client(url) # COnnect the client
        client.set_user("OpcUaClient")
        client.set_password("OPCUA@g22")
        
        Value = "on"
        data["data"]["dmg_data"][0].update({"machine_status": Value})
        client.connect()
        print(f"Connected to: {url}")
        for key, value in Node_dict.items():
            node_id = f'"{value}"'
            servicelevel_node = client.get_node(value)
            node_Value = servicelevel_node.get_value()
            data["data"]["dmg_data"][0].update({key: node_Value})
        # data.update({"time": datetime.utcnow()})
	
        client.disconnect()
        
        convert_data_type(data["data"]["dmg_data"][0], data_type)
        res = requests.post(URL, json= data)
        print(data["data"]["dmg_data"])
        print("response: ", res.text)
        
    except:
        if p == False:
            # data.update({"time": datetime.utcnow()})   
            convert_data_type(data_off["data"]["dmg_data"][0], data_type)
            res = requests.post(URL, json= data_off)
            print(data_off["data"]["dmg_data"][0])
            print("response: ", res.text)
            time.sleep(5)
            p = ping()
            if p == False:
                print("after 5 sec")
                time.sleep(10)
                q = ping()
                if q == False:
                    time.sleep(30)
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
Node_dict = { 
'Start_up': "ns=2;s=/Nck/ChannelDiagnose/poweronTime",
'Total_Number': "ns=2;s=/Channel/State/totalParts",
'Current_Cycle': "ns=2;s=/Channel/ChannelDiagnose/cycleTime",
'Total_run_time': "ns=2;s=/Channel/ChannelDiagnose/operatingTime",
'Tool_Operating_Time': "ns=2;s=/Channel/ChannelDiagnose/cuttingTime",
'Tool_Name': "ns=2;s=/Channel/State/actToolIdent",
'Tool_Radius': "ns=2;s=/Channel/State/actToolRadius",
'Tool_Length': "ns=2;s=/Channel/State/actToolLength1",
'current_program': "ns=2;s=/Channel/ProgramInfo/progName",
'content_program': "ns=2;s=/Channel/ProgramInfo/block",
'Spindle_Speed': "ns=2;s=/Channel/Spindle/actSpeed",
'Spindle_Feed': "ns=2;s=/Channel/MachineAxis/actFeedRate",
'Spindle_Override': " ns=2;s=/Channel/Spindle/speedOvr",
'Feed_Override': "ns=2;s=/Nck/MachineAxis/feedRateOvr",
'X_axis': "ns=2;s=/Nck/MachineAxis/aaIm[u1, 1]",
'Y_axis': "ns=2;s=/Nck/MachineAxis/aaIm[u1, 2]",
'Z_axis': "ns=2;s=/Nck/MachineAxis/aaIm[u1, 3]",
'C_axis': "ns=2;s=/Nck/MachineAxis/aaIm[u1, 4]",
'A_axis': "ns=2;s=/Nck/MachineAxis/aaIm[u1, 5]",
'driveLoad_X': "ns=2;s=/Nck/Spindle/driveLoad[u1, 1]",
'driveLoad_Y': "ns=2;s=/Nck/Spindle/driveLoad[u1, 2]",
'driveLoad_Z': "ns=2;s=/Nck/Spindle/driveLoad[u1, 3]",
'driveLoad_C': "ns=2;s=/Nck/Spindle/driveLoad[u1, 4]",
'driveLoad_A': "ns=2;s=/Nck/Spindle/driveLoad[u1, 5]",
'Prog_status': "ns=2;s=/Channel/State/progStatus[u1, 1]",
'Spindle_Load': "ns=2;s=/Nck/Spindle/driveLoad[u1, 6]"

 }
off_dict = {'Machine_Stattus': 'off'
                          ,'Start_up': 0
                          ,'Total_Number': None
                          ,'Current_Cycle': 0
                          ,'Total_run_time': 0
                          ,'Tool_Operating_Time': 0
                          ,'Tool_Name': None
                          ,'Tool_Radius': None
                          ,'Tool_Length': None
                          ,'current_program': "Machine is off"
                          ,'content_program': "Machine is off"
                          ,'Spindle_Speed': 0
                          ,'Spindle_Feed': 0
                          ,'Spindle_Override': 0
                          ,'Feed_Override': 0
                          ,'X_axis': 0
                          ,'Y_axis': 0
                          ,'Z_axis': 0
                          ,'C_axis': 0
                          ,'A_axis': 0
                          ,'driveLoad_X': 0
                          ,'driveLoad_Y': 0
                          ,'driveLoad_Z': 0
                          ,'driveLoad_C': 0
                          ,'driveLoad_A': 0
                          ,'Prog_status': 0,
			  'Spindle_Load': 0
                         }

import opcua
import json
import time
from datetime import datetime
import requests
from opcua import Client, ua
import platform, subprocess

#  url for post and OPCUA enpoint url
url = "opc.tcp://10.173.14.193:500"
#URL = "http://216.10.245.209:80/opcua2cnc/opcua2cnc.php"
URL = "https://lab40.in/datafile/opcua2cnc.php"
URL1= "http://lab40.in/current_dmg/write_csv.php"
URL2= "http://lab40.in/dmg/datafile/write_csv.php"

#  ping machine
def ping(ipA= '10.173.14.193'):
    param = '-n' if platform.system().lower()=='windows' else '-c'

    # Building the command. Ex: "ping -c 1 google.com"
    command = ['ping', param, '1', ipA]

    return subprocess.call(command) == 0 

    
while True:
    value_dict= { }
    p = ping()
    # print(ping())
    try:
        # COnnect the client
        client = Client(url)
        # print(ping())
        client.set_user("OpcUaClient")
        client.set_password("OPCUA@g22")
        
        Value= "on"
        value_dict.update({"Machine_Stattus": Value})
        client.connect()
        print(f"Connected to: {url}")
        for key, value in Node_dict.items():
            # print(value)
            node_id= f'"{value}"'
            # print(node_id)
            servicelevel_node = client.get_node(value)
            node_Value = servicelevel_node.get_value()
            # print(key + " : " + str(node_Value))
            value_dict.update({key: node_Value})
        value_dict.update({'Date': time.strftime("%Y-%m-%d")})
        value_dict.update({'Time': time.strftime("%H:%M:%S")})
        
	
	
        client.disconnect()
        
        res = requests.post(URL, json=value_dict, headers={'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.54 Safari/537.36'
                                                           })
        
        res = requests.post(URL1, json=value_dict, headers={'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.54 Safari/537.36'
                                                            })
        res = requests.post(URL2, json=value_dict, headers={'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.54 Safari/537.36'
                                                          })
        print(value_dict)
        
    except:
        if p == False:
            # print(p)
            off_dict.update({'Date': time.strftime("%Y-%m-%d")})
            off_dict.update({'Time': time.strftime("%H:%M:%S")})
            
            
            res = requests.post(URL, json=off_dict, headers={'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.54 Safari/537.36'
                                                               })
            
            res = requests.post(URL1, json=off_dict, headers={'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.54 Safari/537.36'
                                                                })
            res = requests.post(URL2, json=off_dict, headers={'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.54 Safari/537.36'
                                                                })
        
            print(off_dict)
            print("off data sent")
      
            # print(ping())
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
    time.sleep(2)    
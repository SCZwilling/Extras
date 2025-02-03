import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/post_data/dynamic_post/', methods=['POST'])
def receive_data():
    url = "https://twin.zwillinglabs.io/api/iot/data"
    data = request.get_json()
    try:
        print("Received data:", repr(data))
        if data["data"]["fdxm_data"][0]["target_voltage"] == '':   
            print("Machine is Off")
        else:
            res = requests.post(url, json= data)
            print("Response:", res.text)
        print("==========================================================")
    except Exception as e:
        print(e)
    return jsonify({"status": "success", "received": data})

if __name__ == '__main__':
    # Replace '0.0.0.0' with your local IP if you want, but 0.0.0.0 works for all network interfaces.
    app.run(host='0.0.0.0', port=5000)



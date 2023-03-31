from flask import Flask, jsonify, render_template, request
from pylogix import PLC

app = Flask(__name__)

# Setup PLC Comms
comm = PLC()
comm.IPAddress = "192.168.123.100"
comm.ProcessorSlot = 2


# Process data requests and commands
@app.route("/data", methods=["GET", "POST"])
def data():
    if request.method == "POST":
        jsonData = request.get_json()
        if jsonData["cmd"] == "Start":
            ret = comm.Write([("Start", 1), ("Stop", 0)])
            return {"sts": jsonData["sts"] + " - " + ret[0].Status}
        else:
            ret = comm.Write([("Start", 0), ("Stop", 1)])
            return {"sts": jsonData["sts"] + " - " + ret[1].Status}
    if request.method == "GET":
        liveData = comm.Read("RunTime")
        return {"sts": liveData.Value}


# Create Index
@app.route("/")
def index():
    return render_template("index.html")


app.run()
# app.run(host="192.168.1.15")

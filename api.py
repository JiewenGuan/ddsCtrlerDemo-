class SineWave():
    def __init__(self, frequency=20, amplitude=-40, phase=0):
        self.frequency = frequency
        self.amplitude = amplitude
        self.phase = phase

    def setFromJson(self, json):
        self.frequency = json['frequency']
        self.amplitude = json['amplitude']
        self.phase = json['phase']

    def toString(self):
        return f"f:{self.frequency} a:{self.amplitude} p:{self.phase}"

    def toDict(self):
        return {
            'frequency': self.frequency,
            'amplitude': self.amplitude,
            'phase': self.phase
        }


class Machine():
    def __init__(self, digitalCount=4, sineWaveCount=4):
        self.digitalSwitchs = []
        self.sineWaves = []

        for i in range(0, digitalCount):
            self.digitalSwitchs.append(False)

        for i in range(0, sineWaveCount):
            self.sineWaves.append(SineWave())

    def digitalCount(self):
        return len(self.digitalSwitchs)

    def setDigitalCount(self, count):
        oldDigitalSwitchs = self.digitalSwitchs
        self.digitalSwitchs = []
        for i in range(0, count):
            if (i < len(oldDigitalSwitchs)):
                self.digitalSwitchs.append(oldDigitalSwitchs[i])
            else:
                self.digitalSwitchs.append(False)

    def sineWaveCount(self):
        return len(self.sineWaves)

    def setSineWaveCount(self, count):
        oldSineWaves = self.sineWaves
        self.sineWaves = []
        for i in range(0, count):
            if (i < len(oldSineWaves)):
                self.sineWaves.append(oldSineWaves[i])
            else:
                self.sineWaves.append(SineWave())

    def setDigitalSwitch(self, input):
        self.digitalSwitchs = input

    def setSineWave(self, input):
        self.sineWaves[input['id']].setFromJson(input)

    def getSineWaves(self):
        ret = []
        for si in self.sineWaves:
            ret.append(si.toDict())
        return ret

    def toDict(self):
        return {
            "digitalSwitch": self.digitalSwitchs,
            "sineWaves": self.getSineWaves()
        }


from flask import Flask, request
from flask_cors import CORS
from flask_socketio import SocketIO, emit
import time


app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'

#domain = r"(192.168.1.21|localhost)"
#CORS(app, origins=[r"^https?://"+domain+r":*"])
CORS(app)
'''
TODO: reconfig
socketio = SocketIO(
    app,
    cors_allowed_origins=[
        "http://localhost:8080",
        "http://localhost:5173",
        "http://192.168.1.21:5173/",
    ])  # must be exact, no regex
'''
machine = Machine()

states = {}

socketio = SocketIO(
    app,
    cors_allowed_origins='*')


@app.route("/stateNum")
def stateNum():
    return {"count": len(states)}


@app.route("/allStates")
def allStates():
    pass


@app.route("/newState", methods=["POST"])
def newState():
    name = request.json["name"]
    print(name)
    if len(name) == 0:
        name = "State "+len(states)
    states[name] = machine.toDict()
    return "ok"


@app.route("/greeting")
def greeting():
    return {"greeting": "Hello from Flask!"}


@app.route("/digitalCount", methods=["GET", "POST"])
def digitalCount():
    if (request.method == "POST"):
        machine.setDigitalCount(request.json["count"])
    return {"digitalCount": machine.digitalCount()}


@app.route("/getSwitchs", methods=["GET"])
def getSwitchs():
    return {"switchs": machine.digitalSwitchs}


@app.route("/sineWaveCount", methods=["GET", "POST"])
def sineWaveCount():
    if (request.method == "POST"):
        machine.setSineWaveCount(request.json["count"])
    return {"sineWaveCount": machine.sineWaveCount()}


@app.route("/getSineWaves", methods=["GET"])
def getSineWaves():
    return {"sineWaves": machine.getSineWaves()}


@socketio.on('message')
def handle_message(data):
    print('message: ' + data)
    emit("message", 'reply:'+data)


@socketio.on('timer')
def handle_my_custom_event(json):
    emit('timer', json)


@socketio.on('digitalSwitch')
def handle_my_custom_event(json):
    machine.setDigitalSwitch(json)
    print(machine.digitalSwitchs)
    print(time.time())


@socketio.on('sineWaveCtrl')
def handle_my_custom_event(json):
    machine.setSineWave(json)
    print(machine.sineWaves[json['id']].toString())
    print(time.time())


if __name__ == "__main__":
    #socketio.run(app, debug=True, host="0.0.0.0", port=5000)
    socketio.run(app, debug=True)
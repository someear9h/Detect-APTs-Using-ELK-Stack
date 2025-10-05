import requests
URL = "http://localhost:8000/exec"
for i in range(8):
    # each emits 200KB approx via bytes_out field
    r = requests.post(URL, json={"command_line": "upload chunk","user":"u1","bytes_out":250000})
    print(i, r.status_code)
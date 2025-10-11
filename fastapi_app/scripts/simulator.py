import csv
import requests
import time
from pathlib import Path

DATA_PATH = Path(__file__).parent.parent.parent / "data" / "10_1_1_15-windows-securityevents_labeled.csv"
LOGSTASH_URL = "http://localhost:5001"

def simulate_data(rows=10):
    with open(DATA_PATH, newline="", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        for i, row in enumerate(reader):
            if i >= rows:
                break
            row = {k: (v.strip() if isinstance(v, str) else v) for k, v in row.items()}
            try:
                response = requests.post(LOGSTASH_URL, json=row, timeout=5)
                if response.status_code == 200:
                    print(f"Sent row {i+1} successfully.")
                else:
                    print(f"Failed to send row {i+1}: {response.status_code} - {response.text}")
            except Exception as e:
                print(f"Error sending row {i+1}: {e}")

            time.sleep(0.01)

if __name__ == "__main__":
    simulate_data(100000)

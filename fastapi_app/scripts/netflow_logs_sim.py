import csv
import requests
import time
from pathlib import Path
import argparse
import math

# Default data path (same pattern you use)
DEFAULT_DATA_PATH = Path(__file__).parent.parent.parent / "data" / "net1011x_Flow_with_threats.csv"
DEFAULT_LOGSTASH_URL = "http://localhost:5001"

def clean_and_cast_value(v: str):
    if v is None:
        return None
    v = v.strip()
    if v == "" or v.lower() == "nan":
        return None
    try:
        f = float(v)
    except Exception:
        return v
    else:
        if math.isfinite(f) and float(int(f)) == f:
            return int(f)
        return f

def stream_top_bottom(data_path: Path, logstash_url: str, sleep: float):
    # Load entire CSV into memory
    with open(data_path, newline="", encoding="utf-8") as csvfile:
        reader = list(csv.DictReader(csvfile))

    top_idx = 0
    bottom_idx = len(reader) - 1

    while top_idx <= bottom_idx:
        # Send 10 rows from top
        for _ in range(10):
            if top_idx > bottom_idx:
                break
            row = reader[top_idx]
            send_row(row, logstash_url, top_idx+1)
            top_idx += 1
            time.sleep(sleep)

        # Send 1 row from bottom
        if bottom_idx >= top_idx:
            row = reader[bottom_idx]
            send_row(row, logstash_url, bottom_idx+1)
            bottom_idx -= 1
            time.sleep(sleep)

def send_row(row, logstash_url, row_number):
    cleaned = {k: clean_and_cast_value(v) for k, v in row.items()}
    try:
        resp = requests.post(logstash_url, json=cleaned, timeout=8)
        if resp.status_code == 200:
            print(f"[{row_number}] Sent OK  -> {cleaned.get('src_ip','?')} -> {cleaned.get('dst_ip','?')}")
        else:
            print(f"[{row_number}] Failed ({resp.status_code}): {resp.text[:200]}")
    except requests.RequestException as e:
        print(f"[{row_number}] Error sending: {e}")

def main():
    parser = argparse.ArgumentParser(description="Send netflow CSV rows to Logstash HTTP input (top-bottom pattern).")
    parser.add_argument("--data", type=Path, default=DEFAULT_DATA_PATH)
    parser.add_argument("--url", type=str, default=DEFAULT_LOGSTASH_URL)
    parser.add_argument("--sleep", type=float, default=0.01)
    args = parser.parse_args()

    data_path = args.data
    if not data_path.exists():
        raise SystemExit(f"Data file not found: {data_path}")

    print(f"-> Sending rows from: {data_path}")
    print(f"-> Logstash URL: {args.url}")
    print(f"-> Sleep between sends: {args.sleep}s\n")

    stream_top_bottom(data_path, args.url, args.sleep)
    print("\nDone.")

if __name__ == "__main__":
    main()
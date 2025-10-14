# Project Sentinel

**An Intelligence-Driven APT Detection Framework**

*Solution for the Smart India Hackathon 2025 — Problem Statement #25238 (National Technical Research Organisation)*

Project Sentinel is a functional, end-to-end threat detection framework built on the ELK Stack to proactively hunt and neutralize Advanced Persistent Threats (APTs). It moves beyond simple logging to provide high-fidelity, automated defense by focusing on attacker behavior rather than static signatures.

---

## Table of Contents

1. [Overview](#overview)
2. [Methodology — The Detection Engineering Cycle](#methodology---the-detection-engineering-cycle)
3. [Key Detections Implemented](#key-detections-implemented)
4. [Technology Stack](#technology-stack)
5. [Project Structure](#project-structure)
6. [Prerequisites](#prerequisites)
7. [Quick Start — Run the Project (Local)](#quick-start--run-the-project-local)

   * [Step 1 — Set up the environment](#step-1---set-up-the-environment)
   * [Step 2 — Ingest forensic data (one-time bulk import)](#step-2---ingest-forensic-data-one-time-bulk-import)
   * [Step 3 — Run the live demo (simulations)](#step-3---run-the-live-demo-simulations)
8. [Detection Rules (high level)](#detection-rules-high-level)
9. [Simulation & API](#simulation--api)
10. [Notes & Troubleshooting](#notes--troubleshooting)
11. [License & Contact](#license--contact)

---

## Overview

Project Sentinel packages a complete detection engineering workflow for hunting APTs using real-world forensic logs (Windows Event Logs, network flows) and the ELK Stack (Elasticsearch, Logstash, Kibana). The aim is to produce low-noise, high-confidence alerts by engineering detections around attacker tactics, techniques, and procedures (TTPs).

## Methodology — The Detection Engineering Cycle

A professional **Analyze → Automate → Validate** loop drives the project:

```
+--------------------------------------+    +--------------------------------------+    +--------------------------------------+
| 1. ANALYZE: The Forensic Hunt        | -> | 2. AUTOMATE: Detection Engineering   | -> | 3. VALIDATE: Prove Efficacy           |
| (Find adversary TTPs in real-world   |    | (Build high-fidelity KQL rules in    |    | (Test the rule with a simulator to    |
|  APT forensic log data)              |    |  Kibana to detect the TTP)           |    |  generate a conclusive alert)         |
+--------------------------------------+    +--------------------------------------+    +--------------------------------------+    
```

Each rule is derived from forensic evidence, implemented as KQL in Kibana, and validated by triggering realistic simulated activity via the included Python scripts.

## Key Detections Implemented

These are the main high-fidelity detections targeting stages of the APT lifecycle.

| Threat Detected                |       MITRE ATT&CK Tactic | Rule Description                                                                                               | Data Source                    |
| ------------------------------ | ------------------------: | -------------------------------------------------------------------------------------------------------------- | ------------------------------ |
| Credential Dumping Precursor   | Credential Access (T1003) | Detects assignment of `SeDebugPrivilege` — a common preparation step for dumping credentials from `lsass.exe`. | Host logs (Windows Event Logs) |
| Malicious PowerShell Execution |     Execution (T1059.001) | Hunts for fileless techniques such as `IEX` and `DownloadString` (living-off-the-land PowerShell).             | Host logs                      |
| Lateral Movement / Spreading   |  Lateral Movement (T1021) | Detects a host connecting to many machines on sensitive SMB/RPC ports — indicates lateral probing/spreading.   | Network logs (flows)           |
| Internal Reconnaissance        |         Discovery (T1046) | Identifies network & port scanning by recognizing a "one-to-many" connection pattern typical of recon tools.   | Network logs                   |

> These rules are authored in Kibana Query Language (KQL) and tuned to reduce false positives using contextual fields (process path, parent process, time windows, destination port sets, etc.).

## Technology Stack

* **Core Platform:** ELK Stack — Elasticsearch, Logstash, Kibana (tested on v7.17.10)
* **Containerization:** Docker & Docker Compose
* **Simulation & API:** Python 3.9 (FastAPI + Requests)
* **Detection Language:** Kibana Query Language (KQL)
* **Data Sources:** Windows Event Logs (host), Network flow logs (NetFlow/PCAP-derived CSV)

## Project Structure (example)

```
project-root/
├─ docker-compose.yml
├─ .env.example
├─ data/                     # forensic CSVs used for bulk ingest
├─ logstash/pipelines/       # ingest and live pipeline configs
│  ├─ ingest-security-pipeline.conf
│  └─ pipeline.conf
├─ kibana/rules/             # KQL rule definitions / JSON exports
├─ fastapi_app/              # simulation API + attack simulator scripts
│  ├─ app.py
│  └─ scripts/
│     ├─ credential_dumping.py
│     ├─ powershell_attack.py
│     └─ lateral_movement.py
└─ README_Project_Sentinel.md
```

## Prerequisites

* Docker (latest stable) and Docker Compose
* Python 3.9+ (for running simulators locally if not containerized)
* A copy of this repository

## Quick Start — Run the Project (Local)

These steps assume you cloned the repository and are in the project root.

### Step 1 — Set up the environment

```bash
# clone (replace with your repo URL)
git clone <your-repo-url>
cd <your-repo-name>

# copy the environment file
cp .env.example .env
# edit .env if you want custom passwords or ports
```

### Step 2 — Ingest forensic data (one-time bulk import)

Configure Logstash to use the ingestion pipeline. In `docker-compose.yml`, ensure the `logstash` service `volumes:` entry points to the ingest pipeline `ingest-security-pipeline.conf`.

Start the stack (this will run Logstash which reads CSVs from `./data` and ships to Elasticsearch):

```bash
docker-compose up --build
```

Logstash will perform the bulk import. This can take several minutes depending on data size. Once logs stop flowing, you may `Ctrl+C` to stop the stack.

### Step 3 — Run the live demo (simulations)

Switch Logstash to live mode by updating the `logstash` service in `docker-compose.yml` to mount `pipeline.conf` (the live pipeline) instead of the ingest pipeline.

Then perform a clean restart of the stack:

```bash
docker-compose down
docker-compose up -d --force-recreate
# wait ~1 minute for services to initialize
```

Run a simulation to generate an attack event (examples):

```bash
# run locally using Python
python fastapi_app/scripts/credential_dumping.py
python fastapi_app/scripts/powershell_attack.py
python fastapi_app/scripts/lateral_movement.py
```

Now open Kibana at `http://localhost:5601` → **Security > Alerts** and you should see the critical alert generated by the rule.

## Detection Rules (High Level)

* Rules are implemented as Kibana detection rules (KQL) and exported under `kibana/rules/` as JSON for import.
* Each rule contains:

  * Title & description (forensic rationale)
  * Index patterns / data sources
  * KQL query and time window
  * Severity and risk score mapping
  * False-positive metadata & suppression tuning

## Simulation & API

* The `fastapi_app` contains a minimal FastAPI service used by simulator scripts. The scripts send crafted events to Logstash (or directly to the live pipeline) to exercise rules and validate end-to-end detection.
* Example script files are located in `fastapi_app/scripts/` and are intentionally simple so you can read and modify the simulated TTPs.

## Notes & Troubleshooting

* **Kibana version:** This README and rule set were validated on ELK v7.17.10. If you use another minor version, check index templates and KQL compatibility.
* **Data mapping:** Ensure the Logstash pipelines set correct field types (ip, keyword, integer, date) to allow efficient queries and aggregations.
* **Timing:** After starting Elasticsearch and Kibana, allow Kibana to fully initialize (~30–60s) before importing rules or checking Security > Alerts.
* **Logstash pipelines:** There are two pipeline configurations: one for `ingest` (bulk import from CSV) and one for `live` (receiving simulator events). Make sure your `docker-compose.yml` volume mapping points to the correct pipeline for the step you’re executing.

## Appendix — Example KQL snippets

> These are illustrative; use the exported JSON rule files under `kibana/rules/` for production imports.

**Detect SeDebugPrivilege assignment (Credential Dumping Precursor):**

```
event.code:4624 and process.name:lsass.exe and winlog.event_data.Privileges: "SeDebugPrivilege"
```

**PowerShell fileless technique (IEX / DownloadString):**

```
process.name:powershell.exe and (process.command_line: "IEX" or process.command_line: "DownloadString")
```

**One-to-many SMB/RPC scanning (Lateral Movement):**

```
network.transport:tcp and destination.port:(445 or 139 or 135) and event.action: "connection_attempt" | stats dc(destination.ip) by source.ip | where dc(destination.ip) > 10
```

## License & Contact

This repository is provided as a proof-of-concept for Smart India Hackathon 2025. Modify and reuse according to your organizational policy.

If you want help tuning rules, adding new detections, or producing a clean export of Kibana rules for automated import, open an issue or contact the maintainers.

---

*Thank you for using Project Sentinel — built to hunt, detect, and validate APT activity with rigor and repeatability.*

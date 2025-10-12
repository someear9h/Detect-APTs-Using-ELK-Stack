import pandas as pd
import numpy as np
from pathlib import Path
import random

# === 1. Load Dataset ===
DATA_PATH = Path(__file__).parent.parent.parent / "data" / "net1011x_Flow_labeled.csv"
df = pd.read_csv(DATA_PATH, low_memory=False, on_bad_lines="skip", quotechar='"')

print(f"Original dataset size: {len(df)}")

# === 2. Clean minimal columns for manipulation ===
df = df.reset_index(drop=True)
num_rows = len(df)
num_threats = int(0.2 * num_rows)

# === 3. Create Internal Reconnaissance Threats ===
recon = df.sample(num_threats // 2, random_state=42).copy()

# Simulate scanning internal IPs (10.x.x.x)
recon["src_ip"] = ["10.0.0." + str(random.randint(1, 100)) for _ in range(len(recon))]
recon["dst_ip"] = ["10.0.1." + str(random.randint(1, 255)) for _ in range(len(recon))]
recon["dst_port"] = np.random.randint(20, 1024, size=len(recon))
recon["protocol"] = 6  # TCP
recon["bidirectional_packets"] = np.random.randint(50, 500, size=len(recon))
recon["bidirectional_duration_ms"] = np.random.randint(50, 500, size=len(recon))
recon["Activity"] = "Malicious"
recon["Stage"] = "Internal Reconnaissance"
recon["DefenderResponse"] = "Detected"
recon["Signature"] = "APT.Simulated.InternalRecon"
recon["threat"] = True

# === 4. Create Lateral Movement Threats ===
lateral = df.sample(num_threats // 2, random_state=99).copy()

# Simulate movement between internal hosts
lateral["src_ip"] = ["10.0.2." + str(random.randint(1, 255)) for _ in range(len(lateral))]
lateral["dst_ip"] = ["10.0.3." + str(random.randint(1, 255)) for _ in range(len(lateral))]
lateral["protocol"] = 6  # TCP
lateral["dst_port"] = np.random.choice([135, 139, 445, 3389], size=len(lateral))
lateral["bidirectional_packets"] = np.random.randint(500, 3000, size=len(lateral))
lateral["bidirectional_duration_ms"] = np.random.randint(1000, 10000, size=len(lateral))
lateral["Activity"] = "Malicious"
lateral["Stage"] = "Lateral Movement"
lateral["DefenderResponse"] = "Detected"
lateral["Signature"] = "APT.Simulated.LateralMove"
lateral["threat"] = True

# === 5. Combine benign + threat data ===
df["threat"] = False  # mark original benign
final_df = pd.concat([df, recon, lateral], ignore_index=True)
print(f"✅ New dataset size: {len(final_df)} (20% threat data added)")

# === 6. Save final dataset ===
output_path = Path(__file__).parent.parent.parent / "data" / "net1011x_Flow_with_threats.csv"
final_df.to_csv(output_path, index=False)
print(f"💾 Saved enhanced dataset with threats to: {output_path}")

# === Runtime Experiment: Varying Activity Complexity ===
# This script evaluates how the runtime changes as the number of activities (control-flow complexity) increases.
# For each activity mode level, it generates synthetic logs and records the runtime of both:
#   1. XES generation
#   2. OCEL conversion

import os
import json
import time
import csv
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from ocelgen.xes_generator import generate_xes_log
from ocelgen.xes_to_ocel_converter import convert_xes_to_ocel

# --- Output setup ---
OUTPUT_DIR = "runtime_by_activity"
CONFIG_DIR = os.path.join(OUTPUT_DIR, "configs")
os.makedirs(CONFIG_DIR, exist_ok=True)

RESULTS_FILE = os.path.join("csv_files", "runtime_results_by_activities.csv")

# --- Experiment parameters ---
activity_modes = [3, 6, 9, 12, 15, 18, 21, 25]  # Increasing number of activities
samples_per_mode = 25
num_traces = 100  # Fixed across all experiments

csv_header = ["log_id", "activity_mode", "xes_runtime_sec", "ocel_runtime_sec"]
rows = []

log_index = 1
for act_mode in activity_modes:
    for _ in range(samples_per_mode):
        log_id = f"log_{log_index:04}"
        seed = 10000 + log_index

        # Create configuration for current activity mode
        config = {
            "xes_log_path": os.path.join(OUTPUT_DIR, f"{log_id}.xes"),
            "output_ocel_path": os.path.join(OUTPUT_DIR, f"{log_id}.jsonocel"),
            "global_seed": seed,
            "process_tree_params": {
                "min": int(act_mode * 0.6),
                "mode": act_mode,
                "max": int(act_mode * 1.4),
                "sequence": 0.5,
                "choice": 0.3,
                "parallel": 0.15,
                "loop": 0.05,
                "silent": 0.0,
                "lt_dependency": 0.0,
                "duplicate": 0.0,
                "or": 0.0,
                "num_traces": num_traces
            },
            "ocel_generation_parameters": {
                "object_types_min": 3,
                "object_types_mode": 3,
                "object_types_max": 3,
                "object_types_per_event_min": 1,
                "object_types_per_event_mode": 2,
                "object_types_per_event_max": 2,
                "objects_per_type_per_event_min": 1,
                "objects_per_type_per_event_mode": 2,
                "objects_per_type_per_event_max": 3,
                "reuse_object_probability": 0.8,
                "case_object_type": "ProcessCase",
                "event_attributes_min": 1,
                "event_attributes_mode": 2,
                "event_attributes_max": 3,
                "object_attributes_min": 1,
                "object_attributes_mode": 2,
                "object_attributes_max": 3
            }
        }


        config_path = os.path.join(CONFIG_DIR, f"{log_id}.json")
        with open(config_path, "w") as f:
            json.dump(config, f, indent=2)

        # Time both generation and conversion
        try:
            t1 = time.time()
            generate_xes_log(config)
            t2 = time.time()
            convert_xes_to_ocel(config)
            t3 = time.time()

            xes_time = round(t2 - t1, 4)
            ocel_time = round(t3 - t2, 4)

            rows.append([log_id, act_mode, xes_time, ocel_time])
            print(f" {log_id}: activity_mode={act_mode}, XES={xes_time}s, OCEL={ocel_time}s")
        except Exception as e:
            print(f" {log_id} failed: {e}")

        log_index += 1


os.makedirs(os.path.dirname(RESULTS_FILE), exist_ok=True)
with open(RESULTS_FILE, "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(csv_header)
    writer.writerows(rows)

print(f"\n Runtime results saved to: {RESULTS_FILE}")

# === Runtime Experiment: Varying Object Type Mode ===
# This script measures how the number of object types in the event log generation 
# affects the runtime of both the XES log generation and OCEL conversion stages.

import os
import json
import time
import csv
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from ocelgen.xes_generator import generate_xes_log
from ocelgen.xes_to_ocel_converter import convert_xes_to_ocel


OUTPUT_DIR = "runtime_by_object_types"
CONFIG_DIR = os.path.join(OUTPUT_DIR, "configs")
os.makedirs(CONFIG_DIR, exist_ok=True)

RESULTS_FILE = os.path.join("csv_files", "runtime_results_by_objecttypes.csv")

# --- Experiment parameters are configured ---
object_type_modes = [1, 2, 3, 4, 5, 6, 7, 8]
samples_per_level = 20
activity_mode = 10
num_traces = 100
reuse_prob = 0.8

csv_header = ["log_id", "object_types_mode", "xes_runtime_sec", "ocel_runtime_sec"]
rows = []

# --- Experiments are run for each object type mode ---
log_index = 1
for obj_mode in object_type_modes:
    for _ in range(samples_per_level):
        log_id = f"log_{log_index:04}"
        seed = 12000 + log_index

        obj_min = max(1, obj_mode - 1)
        obj_max = obj_mode + 2
        prefixes = [f"Type{i}" for i in range(obj_max)]

        config = {
            "xes_log_path": os.path.join(OUTPUT_DIR, f"{log_id}.xes"),
            "output_ocel_path": os.path.join(OUTPUT_DIR, f"{log_id}.jsonocel"),
            "global_seed": seed,
            "process_tree_params": {
                "min": int(activity_mode * 0.6),
                "mode": activity_mode,
                "max": int(activity_mode * 1.4),
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
                "object_types_min": obj_min,
                "object_types_mode": obj_mode,
                "object_types_max": obj_max,
                "object_type_prefixes": prefixes,
                "object_types_per_event_min": 1,
                "object_types_per_event_mode": min(4, obj_mode),
                "object_types_per_event_max": obj_max,
                "objects_per_type_per_event_min": 1,
                "objects_per_type_per_event_mode": 2,
                "objects_per_type_per_event_max": 3,
                "reuse_object_probability": reuse_prob,
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

        # Timings for both log generation and conversion are captured
        try:
            t1 = time.time()
            generate_xes_log(config)
            t2 = time.time()
            convert_xes_to_ocel(config)
            t3 = time.time()

            xes_time = round(t2 - t1, 4)
            ocel_time = round(t3 - t2, 4)
            rows.append([log_id, obj_mode, xes_time, ocel_time])
            print(f" {log_id}: obj_types={obj_mode}, XES={xes_time}s, OCEL={ocel_time}s")
        except Exception as e:
            print(f" {log_id} failed: {e}")

        log_index += 1

# --- All runtime results are written to a CSV file ---
os.makedirs(os.path.dirname(RESULTS_FILE), exist_ok=True)
with open(RESULTS_FILE, "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(csv_header)
    writer.writerows(rows)

print(f"\n Runtime results saved to: {RESULTS_FILE}")

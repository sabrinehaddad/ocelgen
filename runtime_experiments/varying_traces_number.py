import os
import json
import time
import csv
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from ocelgen.xes_generator import generate_xes_log
from ocelgen.xes_to_ocel_converter import convert_xes_to_ocel

# === Output Setup ===
OUTPUT_DIR = "runtime_logs"
CONFIG_DIR = os.path.join(OUTPUT_DIR, "configs")
os.makedirs(CONFIG_DIR, exist_ok=True)
RESULTS_FILE = os.path.join("csv_files", "runtime_results_by_traces.csv")
PLOT_FILE = os.path.join("plots", "runtime_comparison_boxplot.png")

# === Experiment Parameters ===
activity_mode = 10
trace_counts = [10, 25, 50, 75, 100, 150, 200, 300, 400, 500]
samples_per_trace_count = 20  # Total 200 logs

csv_header = ["log_id", "num_traces", "xes_runtime_sec", "ocel_runtime_sec"]
rows = []

# === Run Benchmarks ===
log_index = 1
for num_traces in trace_counts:
    for _ in range(samples_per_trace_count):
        log_id = f"log_{log_index:04}"
        seed = 9000 + log_index

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
                "object_types_min": 2,
                "object_types_mode": 3,
                "object_types_max": 5,
                "object_types_per_event_min": 1,
                "object_types_per_event_mode": 2,
                "object_types_per_event_max": 3,
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

        try:
            t1 = time.time()
            generate_xes_log(config)
            t2 = time.time()
            convert_xes_to_ocel(config)
            t3 = time.time()

            xes_time = round(t2 - t1, 4)
            ocel_time = round(t3 - t2, 4)
            rows.append([log_id, num_traces, xes_time, ocel_time])
            print(f"✅ {log_id}: traces={num_traces}, XES={xes_time}s, OCEL={ocel_time}s")
        except Exception as e:
            print(f" {log_id} failed: {e}")

        log_index += 1

# === Save CSV ===
with open(RESULTS_FILE, "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(csv_header)
    writer.writerows(rows)
print(f"\n Runtime results saved to: {RESULTS_FILE}")


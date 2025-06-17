# # === Runtime Experiment: Varying Object Reuse Probability ===
# # This experiment evaluates how varying the reuse probability of objects affects the 
# # runtime performance of XES log generation and OCEL conversion.

# import os
# import json
# import time
# import csv
# import sys
# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
# from xes_generator import generate_xes_log
# from xes_to_ocel_converter import convert_xes_to_ocel

# # --- Output directories are created if they do not exist ---
# OUTPUT_DIR = "runtime_by_reuse"
# CONFIG_DIR = os.path.join(OUTPUT_DIR, "configs")
# os.makedirs(CONFIG_DIR, exist_ok=True)

# RESULTS_FILE = os.path.join("csv_files", "runtime_results_by_reuse.csv")

# # --- Experiment parameters are defined ---
# reuse_levels = [0.1, 0.3, 0.5, 0.7, 0.9, 0.95]
# samples_per_level = 25
# activity_mode = 10
# num_traces = 100

# csv_header = ["log_id", "reuse_probability", "xes_runtime_sec", "ocel_runtime_sec"]
# rows = []

# # --- reuse probability levels ---
# log_index = 1
# for reuse_prob in reuse_levels:
#     for _ in range(samples_per_level):
#         log_id = f"log_{log_index:04}"
#         seed = 11000 + log_index

#         config = {
#             "xes_log_path": os.path.join(OUTPUT_DIR, f"{log_id}.xes"),
#             "output_ocel_path": os.path.join(OUTPUT_DIR, f"{log_id}.jsonocel"),
#             "global_seed": seed,
#             "process_tree_params": {
#                 "min": int(activity_mode * 0.6),
#                 "mode": activity_mode,
#                 "max": int(activity_mode * 1.4),
#                 "sequence": 0.5,
#                 "choice": 0.3,
#                 "parallel": 0.15,
#                 "loop": 0.05,
#                 "silent": 0.0,
#                 "lt_dependency": 0.0,
#                 "duplicate": 0.0,
#                 "or": 0.0,
#                 "num_traces": num_traces
#             },
#             "ocel_generation_parameters": {
#                 "object_types_min": 3,
#                 "object_types_mode": 3,
#                 "object_types_max": 3,
#                 "object_types_per_event_min": 1,
#                 "object_types_per_event_mode": 2,
#                 "object_types_per_event_max": 2,
#                 "objects_per_type_per_event_min": 1,
#                 "objects_per_type_per_event_mode": 2,
#                 "objects_per_type_per_event_max": 3,
#                 "reuse_object_probability": reuse_prob,
#                 "case_object_type": "ProcessCase",
#                 "event_attributes_min": 1,
#                 "event_attributes_mode": 2,
#                 "event_attributes_max": 3,
#                 "object_attributes_min": 1,
#                 "object_attributes_mode": 2,
#                 "object_attributes_max": 3
#             }
#         }

#         config_path = os.path.join(CONFIG_DIR, f"{log_id}.json")
#         with open(config_path, "w") as f:
#             json.dump(config, f, indent=2)

#         # Timing of the generation and conversion process
#         try:
#             t1 = time.time()
#             generate_xes_log(config)
#             t2 = time.time()
#             convert_xes_to_ocel(config)
#             t3 = time.time()

#             xes_time = round(t2 - t1, 4)
#             ocel_time = round(t3 - t2, 4)
#             rows.append([log_id, reuse_prob, xes_time, ocel_time])
#             print(f"✅ {log_id}: reuse={reuse_prob}, XES={xes_time}s, OCEL={ocel_time}s")
#         except Exception as e:
#             print(f"❌ {log_id} failed: {e}")

#         log_index += 1


# os.makedirs(os.path.dirname(RESULTS_FILE), exist_ok=True)
# with open(RESULTS_FILE, "w", newline="") as f:
#     writer = csv.writer(f)
#     writer.writerow(csv_header)
#     writer.writerows(rows)

# print(f"\n Runtime results saved to: {RESULTS_FILE}")

# === Runtime Experiment: Varying Object Reuse Probability ===
# This experiment evaluates how varying the reuse probability of objects affects the 
# runtime performance of XES log generation and OCEL conversion.
# Total logs generated: 6 reuse levels × 84 samples = 504 logs

import os
import json
import time
import csv
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from ocelgen.xes_generator import generate_xes_log
from ocelgen.xes_to_ocel_converter import convert_xes_to_ocel

# --- Output directories are created if they do not exist ---
OUTPUT_DIR = "runtime_by_reuse"
CONFIG_DIR = os.path.join(OUTPUT_DIR, "configs")
os.makedirs(CONFIG_DIR, exist_ok=True)

RESULTS_FILE = os.path.join("csv_files1", "runtime_results_by_reuse.csv")

# --- Experiment parameters are defined ---
reuse_levels = [0.1, 0.3, 0.5, 0.7, 0.9, 0.95]  # 6 reuse levels
samples_per_level = 84  # 6 × 84 = 504 logs total
activity_mode = 10
num_traces = 100

csv_header = ["log_id", "reuse_probability", "xes_runtime_sec", "ocel_runtime_sec"]
rows = []

# --- Loop over reuse probability levels ---
log_index = 1
for reuse_prob in reuse_levels:
    for _ in range(samples_per_level):
        log_id = f"log_{log_index:04}"
        seed = 11000 + log_index

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
                "object_types_min": 3,
                "object_types_mode": 3,
                "object_types_max": 3,
                "object_types_per_event_min": 1,
                "object_types_per_event_mode": 2,
                "object_types_per_event_max": 2,
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

        # Timing of the generation and conversion process
        try:
            t1 = time.time()
            generate_xes_log(config)
            t2 = time.time()
            convert_xes_to_ocel(config)
            t3 = time.time()

            xes_time = round(t2 - t1, 4)
            ocel_time = round(t3 - t2, 4)
            rows.append([log_id, reuse_prob, xes_time, ocel_time])
            print(f"✅ {log_id}: reuse={reuse_prob}, XES={xes_time}s, OCEL={ocel_time}s")
        except Exception as e:
            print(f"❌ {log_id} failed: {e}")

        log_index += 1

# --- Save results to CSV ---
os.makedirs(os.path.dirname(RESULTS_FILE), exist_ok=True)
with open(RESULTS_FILE, "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(csv_header)
    writer.writerows(rows)

print(f"\n✅ Runtime results saved to: {RESULTS_FILE}")

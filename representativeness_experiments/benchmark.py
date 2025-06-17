import os
import json
import subprocess
import random
import shutil
import csv
from itertools import product

# === Setup directories for config files, XES and OCEL files outputs ===
CONFIG_DIR = "configsssss"
OUTPUT_DIR = "generated_logsssss"
XES_DIR = os.path.join(OUTPUT_DIR, "xes")
OCEL_DIR = os.path.join(OUTPUT_DIR, "ocel")
SUMMARY_FILE = os.path.join(OUTPUT_DIR, "benchmark_summary1111111.csv")

for directory in [CONFIG_DIR, XES_DIR, OCEL_DIR]:
    os.makedirs(directory, exist_ok=True)



def sample_triangular(min_val, mode, max_val):
    """
    Returns a float sampled from a triangular distribution (rounded to 2 decimals).
    """
    return round(random.triangular(min_val, mode, max_val), 2)

def control_flow_profile(profile: str):
    """
    Defines control-flow structure probabilities for process trees.
    """
    profiles = {
        "low":    dict(sequence=0.8, choice=0.1, parallel=0.05, loop=0.05),
        "medium": dict(sequence=0.5, choice=0.25, parallel=0.2, loop=0.05),
        "high":   dict(sequence=0.25, choice=0.35, parallel=0.3, loop=0.1),
    }
    return profiles.get(profile, profiles["medium"])

# === Defining parameter grid for the benchmark ===

activity_modes = [5, 9, 13]
object_type_modes = [2, 4, 6]
base_traces = [25, 50, 75]
object_pool_sizes = [50, 200, 500]  # Affects reuse probability + object count
control_profiles = ["low", "medium", "high"]

# Generate all parameter combinations and randomly sample 150
param_combinations = list(product(activity_modes, object_type_modes, base_traces, object_pool_sizes, control_profiles))
random.shuffle(param_combinations)
param_combinations = param_combinations[:150]


csv_header = [
    "log_id", "seed", "act_mode", "obj_mode", "traces",
    "sim_obj_pool", "reuse_prob",
    "objs_per_type_min", "objs_per_type_mode", "objs_per_type_max",
    "ctrl_profile", "sequence", "choice", "parallel", "loop"
]
summary_rows = []

# === Generate logs based on combinations ===

for i, (act_mode, obj_mode, traces, obj_pool_size, ctrl_profile) in enumerate(param_combinations, 1):
    log_id = f"log_{i:03}"
    config_path = os.path.join(CONFIG_DIR, f"{log_id}.json")
    xes_path = os.path.join(XES_DIR, f"{log_id}.xes")
    ocel_path = os.path.join(OCEL_DIR, f"{log_id}.jsonocel")
    seed = 42 + i

    # Adjust reuse probability and object-per-event stats based on pool size
    if obj_pool_size == 50:
        reuse_prob = 0.95
        traces = min(traces, 40)
        objs_min, objs_mode, objs_max = 1, 1, 2
    elif obj_pool_size == 200:
        reuse_prob = 0.7
        objs_min, objs_mode, objs_max = 1, 2, 3
    else:  # 500
        reuse_prob = 0.3
        traces = max(traces, 75)
        objs_min, objs_mode, objs_max = 2, 3, 5

    cf = control_flow_profile(ctrl_profile)


    config = {
        "xes_log_path": xes_path,
        "output_ocel_path": ocel_path,
        "global_seed": seed,
        "process_tree_params": {
            "min": int(act_mode * 0.6),
            "mode": act_mode,
            "max": int(act_mode * 1.4),
            "sequence": cf["sequence"],
            "choice": cf["choice"],
            "parallel": cf["parallel"],
            "loop": cf["loop"],
            "silent": sample_triangular(0.0, 0.05, 0.1),
            "lt_dependency": 0.0,
            "duplicate": 0.0,
            "or": sample_triangular(0.0, 0.05, 0.1),
            "num_traces": traces
        },
        "ocel_generation_parameters": {
            "object_types_min": max(1, obj_mode - 1),
            "object_types_mode": obj_mode,
            "object_types_max": obj_mode + 2,
            "object_type_prefixes": [f"Type{i}" for i in range(obj_mode + 2)],
            "object_types_per_event_min": 1,
            "object_types_per_event_mode": min(4, obj_mode),
            "object_types_per_event_max": obj_mode + 2,
            "objects_per_type_per_event_min": objs_min,
            "objects_per_type_per_event_mode": objs_mode,
            "objects_per_type_per_event_max": objs_max,
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

    # Save config file and run generator
    with open(config_path, "w") as f:
        json.dump(config, f, indent=2)

    shutil.copy(config_path, "config.json")  
    print(f" Generating {log_id}...")

    result = subprocess.run(["python", "main.py"], capture_output=True, text=True)

    if result.returncode == 0:
        print(f"✅ {log_id} generated successfully.")
        summary_rows.append([
            log_id, seed, act_mode, obj_mode, traces,
            obj_pool_size, reuse_prob,
            objs_min, objs_mode, objs_max,
            ctrl_profile, cf["sequence"], cf["choice"], cf["parallel"], cf["loop"]
        ])
    else:
        print(f" Failed to generate {log_id}:\n{result.stderr.strip()}")


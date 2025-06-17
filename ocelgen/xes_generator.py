import json
import random
import os
from datetime import datetime
from pm4py import generate_process_tree, write_xes
from pm4py.sim import play_out


def generate_xes_log(config: dict):
    """
    Generate a synthetic XES log using PM4Py’s Process Tree simulator.

    Args:
        config (dict): Configuration dictionary loaded from a JSON file.
    """

    # For reproducibility 
    random.seed(config.get("global_seed", 42))

    tree_params = config["process_tree_params"]
    xes_file = config["xes_log_path"]

    print("[INFO] Generating process tree...")  
    tree = generate_process_tree(parameters={
        "min": tree_params["min"],
        "max": tree_params["max"],
        "mode": tree_params["mode"],
        "sequence": tree_params["sequence"],
        "choice": tree_params["choice"],
        "parallel": tree_params["parallel"],
        "loop": tree_params["loop"],
        "silent": tree_params["silent"],
        "lt_dependency": tree_params["lt_dependency"],
        "duplicate": tree_params["duplicate"],
        "or": tree_params["or"],
        "no_models": 1
    })

    print("[INFO] Simulating event log...")
    log = play_out(tree, parameters={"num_traces": tree_params["num_traces"]})

    # Enrich events with attributes
    for i, trace in enumerate(log):
        trace.attributes['concept:name'] = str(i)  # trace ID as string
        for event in trace:
            event["time:timestamp"] = datetime.now()  
            event["lifecycle:transition"] = "complete"

    xes_dir = os.path.dirname(xes_file)
    if xes_dir:
        os.makedirs(xes_dir, exist_ok=True)

    write_xes(log, xes_file)
    print(f"[DONE] XES log saved to: {xes_file}")

import streamlit as st
import json
import os
from ocelgen.xes_generator import generate_xes_log
from ocelgen.xes_to_ocel_converter import convert_xes_to_ocel

def round_floats(obj, precision=4):
    if isinstance(obj, dict):
        return {k: round_floats(v, precision) for k, v in obj.items()}
    elif isinstance(obj, float):
        return round(obj, precision)
    elif isinstance(obj, list):
        return [round_floats(i, precision) for i in obj]
    return obj

st.set_page_config(page_title="OCEL-Gen", layout="wide")
st.title("Generating OCEL logs using OCEL-Gen")

tab1, tab2 = st.tabs([" PHASE 1: Generating XES log", " PHASE 2: Converting XES to OCEL"])

with tab1:
    st.header("Process Tree Generator Parameters")
    st.subheader("Specify the triangular distribution of the number of activities")
    col1, col2, col3 = st.columns(3)
    min_act = col1.number_input("Minimum activities", 1, value=5)
    mode_act = col2.number_input("Mode activities", 1, value=9)
    max_act = col3.number_input("Maximum activities", 1, value=12)

    st.subheader("Specify the probabilities for the process tree operators (sum must be equal to 1!)")
    col1, col2 = st.columns(2)
    with col1:
        seq = st.number_input("Probability sequence", 0.0, 1.0, value=0.8)
        par = st.number_input("Probability parallel", 0.0, 1.0, value=0.05)
        or_ = st.number_input("Probability or", 0.0, 1.0, value=0.03)
    with col2:
        choice = st.number_input("Probability choice", 0.0, 1.0, value=0.1)
        loop = st.number_input("Probability loop", 0.0, 1.0, value=0.05)
    
    st.subheader("Additional Constructs")
    col5=st.columns(1)[0]
    with col5:
        silent = st.number_input("Probability silent activities", 0.0, 1.0, value=0.05)
        lt_dep = st.number_input("Probability long-term dependency", 0.0, 1.0, value=0.0)
        dup = st.number_input("Probability duplicate activities", 0.0, 1.0, value=0.0)
    st.subheader("Log Size")
    num_traces = st.number_input("Number of traces to generate", min_value=1, value=75)

with tab2:
    st.header("XES-to-OCEL Conversion Parameters")
    st.subheader("Specify the triangular distribution of the number of object types")
    col1, col2, col3 = st.columns(3)
    obj_min = col1.number_input("Min object types", 1, value=3)
    obj_mode = col2.number_input("Mode object types", 1, value=4)
    obj_max = col3.number_input("Max object types", 1, value=6)

    st.subheader("Specify the triangular distribution of the number of object types per event")
    col1, col2, col3 = st.columns(3)
    otpe_min = col1.number_input("Min types/event", 1, value=1)
    otpe_mode = col2.number_input("Mode types/event", 1, value=4)
    otpe_max = col3.number_input("Max types/event", 1, value=6)

    st.subheader("Specify the triangular distribution of the number of objects per type per event")
    col1, col2, col3 = st.columns(3)
    oppte_min = col1.number_input("Min objects/type/event", 1, value=2)
    oppte_mode = col2.number_input("Mode objects/type/event", 1, value=3)
    oppte_max = col3.number_input("Max objects/type/event", 1, value=5)

    reuse_prob = st.slider(" Specify object reuse probability", 0.0, 1.0, value=0.3)

    st.subheader("Specify the triangular distribution of the number of event attributes")
    col1, col2, col3 = st.columns(3)
    eattr_min = col1.number_input("Event attrs minimum", 0, value=1)
    eattr_mode = col2.number_input("Event attrs mode", 0, value=2)
    eattr_max = col3.number_input("Event attrs maximum", 0, value=3)

    st.subheader("Specify the triangular distribution of the number of object attributes")
    col1, col2, col3 = st.columns(3)
    oattr_min = col1.number_input("Object attrs minimum", 0, value=1)
    oattr_mode = col2.number_input("Object attrs mode", 0, value=2)
    oattr_max = col3.number_input("Object attrs maximum", 0, value=3)

# === Assemble config ===
config = {
    "xes_log_path": "generated_logs/xes/log_150.xes",
    "output_ocel_path": "generated_logs/ocel/log_150.jsonocel",
    "global_seed": 192,
    "process_tree_params": {
        "min": min_act, "mode": mode_act, "max": max_act,
        "sequence": seq, "choice": choice, "parallel": par,
        "loop": loop, "silent": silent, "lt_dependency": lt_dep,
        "duplicate": dup, "or": or_, "num_traces": num_traces
    },
    "ocel_generation_parameters": {
        "object_types_min": obj_min, "object_types_mode": obj_mode, "object_types_max": obj_max,
        "object_type_prefixes": [f"Type{i}" for i in range(obj_max)],
        "object_types_per_event_min": otpe_min, "object_types_per_event_mode": otpe_mode, "object_types_per_event_max": otpe_max,
        "objects_per_type_per_event_min": oppte_min, "objects_per_type_per_event_mode": oppte_mode, "objects_per_type_per_event_max": oppte_max,
        "reuse_object_probability": reuse_prob,
        "case_object_type": "ProcessCase",
        "event_attributes_min": eattr_min, "event_attributes_mode": eattr_mode, "event_attributes_max": eattr_max,
        "object_attributes_min": oattr_min, "object_attributes_mode": oattr_mode, "object_attributes_max": oattr_max
    }
}

st.divider()

# === Generateing ocel log ===
if st.button(" Generate OCEL Log"):
    with st.spinner("Generating logs..."):
        os.makedirs("generated_logs/xes", exist_ok=True)
        os.makedirs("generated_logs/ocel", exist_ok=True)

        generate_xes_log(config)
        convert_xes_to_ocel(config)

    st.success(" Logs generated successfully!")


    with open(config["output_ocel_path"], "rb") as f:
        st.download_button("Download OCEL Log (.jsonocel)", f, file_name="log.jsonocel")

    rounded_config = round_floats(config, precision=4)
    config_str = json.dumps(rounded_config, indent=2)
    st.download_button("Download Config File", data=config_str, file_name="config.json", mime="application/json")

import os
import json
import random
from datetime import datetime
from collections import defaultdict
from pm4py.objects.log.importer.xes import importer as xes_importer


def convert_xes_to_ocel(config):
    """
    Converts an XES event log into an Object-Centric Event Log (OCEL 1.0).
    
    Notes:
        - Randomized object creation.
        - Object attributes are generated synthetically.
        - Output format follows OCEL 1.0 JSON spec.
    """

    xes_path = config["xes_log_path"]
    output_path = config["output_ocel_path"]
    random.seed(config.get("global_seed", 42))

    params = config["ocel_generation_parameters"]

    # --- Sample object type count ---
    ot_min = params["object_types_min"]
    ot_mode = params["object_types_mode"]
    ot_max = params["object_types_max"]
    num_object_types = int(random.triangular(ot_min, ot_mode, ot_max))
    object_types = [f"ot{i+1}" for i in range(num_object_types)]

    # --- Sample event-to-object relationships ---
    et_min = params["object_types_per_event_min"]
    et_mode = params["object_types_per_event_mode"]
    et_max = min(params["object_types_per_event_max"], num_object_types)

    case_type = params["case_object_type"]
    reuse_prob = params["reuse_object_probability"]
    min_objs = params["objects_per_type_per_event_min"]
    mode_objs = params["objects_per_type_per_event_mode"]
    max_objs = params["objects_per_type_per_event_max"]

    # --- Synthetic attribute sampling ---
    event_attr_min = params.get("event_attributes_min", 0)
    event_attr_mode = params.get("event_attributes_mode", 0)
    event_attr_max = params.get("event_attributes_max", 0)

    object_attr_min = params.get("object_attributes_min", 0)
    object_attr_mode = params.get("object_attributes_mode", 0)
    object_attr_max = params.get("object_attributes_max", 0)

    # --- Internal bookkeeping ---
    trace_objects = {}  # Keeps track of objects assigned per trace
    ocel_objects = {}
    ocel_events = {}
    object_id_counters = defaultdict(int)
    event_attr_keys = set()
    object_attr_keys = set()
    event_id = 1

    def generate_synthetic_attributes(prefix, count):
        """Create dummy attributes with random values."""
        return {
            f"{prefix}_attr{i+1}": f"{prefix}_val{random.randint(1, 999)}"
            for i in range(count)
        }

    print(f"[INFO] Loading XES log from: {xes_path}")
    xes_log = xes_importer.apply(xes_path)

    for trace_idx, trace in enumerate(xes_log):
        trace_id = trace.attributes.get("concept:name", f"Trace_{trace_idx}")
        trace_objects[trace_id] = {ot: [] for ot in object_types}
        trace_objects[trace_id][case_type] = [trace_id]  # Always include the trace ID as case object

        # --- Generate attributes for case-level object ---
        case_attrs = generate_synthetic_attributes(
            "object", int(random.triangular(object_attr_min, object_attr_mode, object_attr_max))
        )
        object_attr_keys.update(case_attrs.keys())
        ocel_objects[trace_id] = {
            "ocel:type": case_type,
            "ocel:ovmap": case_attrs
        }

        for event_idx, event in enumerate(trace):
            eid = f"e{event_id}"
            activity = event.get("concept:name", f"Activity_{event_idx}")
            timestamp = event.get("time:timestamp", datetime.now()).isoformat()

            omap = {case_type: [trace_id]}
            flat_omap = [trace_id]

            # --- Sample object types for this event ---
            n_types = int(random.triangular(et_min, et_mode, et_max))
            sampled_types = random.sample(object_types, min(n_types, len(object_types)))

            for ot in sampled_types:
                ids_for_event = []
                n_objs = int(random.triangular(min_objs, mode_objs, max_objs))
                pool = trace_objects[trace_id][ot]

                for _ in range(n_objs):
                    if random.random() < reuse_prob and pool:
                        obj_id = random.choice(pool)
                    else:
                        object_id_counters[ot] += 1
                        obj_id = f"{ot}_{object_id_counters[ot]:04d}"
                        pool.append(obj_id)

                        obj_attrs = generate_synthetic_attributes(
                            "object", int(random.triangular(object_attr_min, object_attr_mode, object_attr_max))
                        )
                        object_attr_keys.update(obj_attrs.keys())

                        ocel_objects[obj_id] = {
                            "ocel:type": ot,
                            "ocel:ovmap": obj_attrs
                        }

                    # Avoid duplicates in same event
                    if obj_id not in ids_for_event:
                        ids_for_event.append(obj_id)

                if ids_for_event:
                    omap[ot] = ids_for_event
                    flat_omap.extend(ids_for_event)

            # --- Merge original (XES) and new (OCEL) event attributes ---
            attr_map = {
                k: v for k, v in event.items()
                if k not in {"concept:name", "time:timestamp", "lifecycle:transition"}
            }
            event_attr_keys.update(attr_map.keys())

            synthetic_attrs = generate_synthetic_attributes(
                "event", int(random.triangular(event_attr_min, event_attr_mode, event_attr_max))
            )
            attr_map.update(synthetic_attrs)
            event_attr_keys.update(synthetic_attrs.keys())

            ocel_events[eid] = {
                "ocel:activity": activity,
                "ocel:timestamp": timestamp,
                "ocel:omap": flat_omap,
                "ocel:vmap": attr_map
            }

            event_id += 1

    # --- Compose OCEL structure ---
    ocel_log = {
        "ocel:global-log": {
            "ocel:version": "1.0",
            "ocel:ordering": "timestamp",
            "ocel:attribute-names": sorted(event_attr_keys | {"activity", "timestamp"}),
            "ocel:global-attribute-names": sorted(object_attr_keys),
            "ocel:object-types": sorted({v["ocel:type"] for v in ocel_objects.values()})
        },
        "ocel:global-event": {},
        "ocel:global-object": {},
        "ocel:events": ocel_events,
        "ocel:objects": ocel_objects
    }

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w") as f:
        json.dump(ocel_log, f, indent=2)

    print(f"[DONE] OCEL log saved to: {output_path}")
    print(f"[STATS] Events: {len(ocel_events)}, Objects: {len(ocel_objects)}")
    print(f"[STATS] Object Types: {len(ocel_log['ocel:global-log']['ocel:object-types'])}")

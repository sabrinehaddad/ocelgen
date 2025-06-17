import json
import sys
from ocelgen.xes_generator import generate_xes_log
from ocelgen.xes_to_ocel_converter import convert_xes_to_ocel


def load_config(config_path="config.json"):
    """
    Load configuration from JSON file.
    
    Exits the script if the file is missing or invalid.
    """
    try:
        with open(config_path, "r") as f:
            config = json.load(f)
            print(f"[INFO] Loaded config from: {config_path}")
            return config
    except FileNotFoundError:
        print(f"[ERROR] Config file not found: {config_path}")
    except json.JSONDecodeError as e:
        print(f"[ERROR] Invalid JSON format: {e}")
    except Exception as e:
        print(f"[ERROR] Unexpected issue loading config: {e}")
    
    sys.exit(1)


if __name__ == "__main__":
    # You can override the path, if needed
    config_file = "config.json" 
    config = load_config(config_file)

    print("[PHASE 1] Generating synthetic XES log...")
    generate_xes_log(config)

    print("[PHASE 2] Converting XES log to OCEL format...")
    convert_xes_to_ocel(config)

    print("[DONE] All tasks completed successfully.")

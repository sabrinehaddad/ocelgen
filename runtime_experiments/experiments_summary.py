import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns


def plot_runtime_summary(csv_dir="csv_files", plot_dir="plots"):
    """
    Reads runtime CSV results and generates a summary plot for five key parameters.

    Args:
        csv_dir (str): Path to the directory containing runtime CSVs.
        plot_dir (str): Path to the directory to save plots.

    Outputs:
        Saves a single figure with subplots for each parameter.
    """
    os.makedirs(plot_dir, exist_ok=True)

    EXPERIMENTS = [
        ("runtime_results_by_traces.csv", "Number of Traces", "num_traces"),
        ("runtime_results_by_activities.csv", "Activity Mode", "activity_mode"),
        ("runtime_results_by_reuse.csv", "Reuse Probability", "reuse_probability"),
        ("runtime_results_by_objecttypes.csv", "Object Types", "object_types_mode"),
        ("runtime_results_by_objecttypes_per_event.csv", "Types per Event", "types_per_event_mode"),
    ]

    PLOT_FILE = os.path.join(plot_dir, "runtime_summary_plots.png")

    fig, axes = plt.subplots(1, 5, figsize=(22, 4), sharey=True, constrained_layout=True)

    for i, (filename, x_label, x_col) in enumerate(EXPERIMENTS):
        csv_path = os.path.join(csv_dir, filename)

        if not os.path.exists(csv_path):
            print(f"[MISSING] {csv_path}")
            continue

        df = pd.read_csv(csv_path)

        df_melted = pd.melt(
            df,
            id_vars=[x_col],
            value_vars=["xes_runtime_sec", "ocel_runtime_sec"],
            var_name="Stage",
            value_name="Runtime"
        )

        df_melted["Stage"] = df_melted["Stage"].map({
            "xes_runtime_sec": "Generating XES",
            "ocel_runtime_sec": "Converting to OCEL"
        })

        ax = axes[i]
        sns.lineplot(
            data=df_melted,
            x=x_col,
            y="Runtime",
            hue="Stage",
            ci="sd",
            ax=ax,
            marker="o"
        )

        ax.set_title(x_label)
        ax.set_xlabel("")
        ax.set_ylabel("Runtime (seconds)" if i == 0 else "")
        ax.grid(True, linestyle="--", alpha=0.3)

        if i != len(EXPERIMENTS) - 1:
            ax.get_legend().remove()
        else:
            ax.legend(loc="upper left")

    fig.supxlabel("Varying Generator Parameters", fontsize=12)
    fig.suptitle("Runtime Trends while varying Generator Parameters", fontsize=14)

    plt.savefig(PLOT_FILE, dpi=300)
    print(f"[SAVED] {PLOT_FILE}")
    plt.show()


if __name__ == "__main__":
    plot_runtime_summary()

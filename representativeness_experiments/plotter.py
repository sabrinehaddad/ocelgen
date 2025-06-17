# import os
# import numpy as np
# import matplotlib.pyplot as plt
# from sklearn.decomposition import PCA
# from sklearn.metrics import pairwise_distances
# from scipy.spatial import ConvexHull
# from scipy.stats import entropy
# from ocelytics.feature_extractor import extract_features as extract_raw_features

# # Defining the features to extract
# FEATURES = ["rmc_object", "rt10_object", "rvpnot_object"]

# # Creating plots directory if it doesn’t exist
# PLOT_DIR = "plots"
# os.makedirs(PLOT_DIR, exist_ok=True)


# def extract_features(folder_path):
#     """
#     Go through a folder and extract feature vectors from all OCEL logs (.jsonocel).
#     Skips any logs that can't be parsed or have missing values.

#     Returns:
#         - matrix (np.ndarray): full feature matrix for valid logs
#         - by_feature (dict): dictionary mapping feature name → list of values
#     """
#     matrix = []
#     by_feature = {f: [] for f in FEATURES}

#     for fname in os.listdir(folder_path):
#         if fname.endswith(".jsonocel"):
#             path = os.path.join(folder_path, fname)
#             try:
#                 feats = extract_raw_features(path, FEATURES)
#                 vec = [feats[f] for f in FEATURES]
#                 if not any(np.isnan(vec)):
#                     matrix.append(vec)
#                     for i, f in enumerate(FEATURES):
#                         by_feature[f].append(vec[i])
#             except Exception as e:
#                 print(f"[WARN] Skipping {fname} due to error: {e}")
    
#     return np.array(matrix), by_feature


# def normalize_features(real_data, synthetic_data):
#     """
#     Min-max normalize all features across real and synthetic logs.
#     Keeps values in [0, 1] for comparison and plotting.
#     """
#     norm_real, norm_synth = {}, {}

#     for f in FEATURES:
#         combined = real_data[f] + synthetic_data[f]
#         if not combined:
#             norm_real[f], norm_synth[f] = [], []
#             continue

#         min_val, max_val = min(combined), max(combined)
#         range_val = max_val - min_val or 1.0  # avoid divide-by-zero

#         norm_real[f] = [(x - min_val) / range_val for x in real_data[f]]
#         norm_synth[f] = [(x - min_val) / range_val for x in synthetic_data[f]]

#     return norm_real, norm_synth


# def plot_pca_convex_hulls(real_matrix, synth_matrix):
#     """
#     Visualize 2D PCA projection of both real and synthetic logs with convex hulls.
#     """
#     if real_matrix.shape[0] < 3 or synth_matrix.shape[0] < 3:
#         print("[WARN] Not enough samples to compute convex hulls.")
#         return

#     combined = np.vstack((real_matrix, synth_matrix))
#     pca = PCA(n_components=2)
#     pca_result = pca.fit_transform(combined)

#     real_pca = pca_result[:len(real_matrix)]
#     synth_pca = pca_result[len(real_matrix):]

#     pc1_var = pca.explained_variance_ratio_[0] * 100
#     pc2_var = pca.explained_variance_ratio_[1] * 100

#     plt.figure(figsize=(8, 6))
#     plt.scatter(real_pca[:, 0], real_pca[:, 1], c='#FFA500', s=10, label="Real Logs", alpha=0.8)
#     plt.scatter(synth_pca[:, 0], synth_pca[:, 1], c='#1f77b4', s=10, label="Synthetic Logs", alpha=0.6)

#     # Draw convex hulls around each group (if possible)
#     try:
#         hull = ConvexHull(real_pca)
#         for simplex in hull.simplices:
#             plt.plot(real_pca[simplex, 0], real_pca[simplex, 1], color='#FFA500')
#     except Exception as e:
#         print(f"[WARN] Failed to draw real log hull: {e}")

#     try:
#         hull = ConvexHull(synth_pca)
#         pts = synth_pca[hull.vertices]
#         plt.fill(pts[:, 0], pts[:, 1], color='#1f77b4', alpha=0.2)
#         for simplex in hull.simplices:
#             plt.plot(synth_pca[simplex, 0], synth_pca[simplex, 1], color='#1f77b4')
#     except Exception as e:
#         print(f"[WARN] Failed to draw synthetic log hull: {e}")

#     plt.xlabel(f"PC1 ({pc1_var:.2f}%)")
#     plt.ylabel(f"PC2 ({pc2_var:.2f}%)")
#     plt.title("PCA Projection — Real vs. Synthetic")
#     plt.legend()
#     plt.grid(True, linestyle="--", alpha=0.3)

#     out_path = os.path.join(PLOT_DIR, "pca_convex_hulls.png")
#     plt.savefig(out_path, dpi=300)
#     print(f"[SAVED] PCA plot → {out_path}")
#     plt.show()


# def plot_stripplot(norm_real, norm_synth, filename="feature_stripplot_close.png"):
#     """
#     Plot normalized feature values for both log types with jitter.
#     """
#     fig, axes = plt.subplots(len(FEATURES), 1, figsize=(9, 6), sharex=True)

#     for i, f in enumerate(FEATURES):
#         ax = axes[i]
#         jitter_real = np.random.normal(0.005, 0.002, len(norm_real[f]))
#         jitter_synth = np.random.normal(-0.005, 0.002, len(norm_synth[f]))

#         ax.plot(norm_real[f], jitter_real, 'o', color='#FFA500', alpha=0.6, markersize=2,
#                 label="Real Logs" if i == 0 else "")
#         ax.plot(norm_synth[f], jitter_synth, 'o', color='#1f77b4', alpha=0.6, markersize=2,
#                 label="Synthetic Logs" if i == 0 else "")
        
#         ax.set_yticks([])
#         ax.set_xlim([0, 1])
#         ax.set_title(f)

#     axes[0].legend(loc="upper right")
#     plt.tight_layout()

#     out_path = os.path.join(PLOT_DIR, filename)
#     plt.savefig(out_path, dpi=300)
#     print(f"[SAVED] Strip plot → {out_path}")
#     plt.show()


# def compute_kl_divergence(real_matrix, synth_matrix, bins=20):
#     """
#     Compute KL divergence for each feature between real and synthetic distributions.
#     """
#     kl_scores = []
#     for i in range(real_matrix.shape[1]):
#         r_hist, _ = np.histogram(real_matrix[:, i], bins=bins, range=(0, 1), density=True)
#         s_hist, _ = np.histogram(synth_matrix[:, i], bins=bins, range=(0, 1), density=True)
#         kl_scores.append(entropy(r_hist + 1e-10, s_hist + 1e-10))
#     return kl_scores


# def compute_coverage(real_matrix, synth_matrix, threshold=0.1):
#     """
#     Compute how many real samples are 'covered' by synthetic ones within ε distance.
#     """
#     distances = pairwise_distances(real_matrix, synth_matrix)
#     return np.mean(np.min(distances, axis=1) < threshold)


# def plot_kl_and_coverage(kl_scores, coverage_score):
#     """
#     Plot KL divergence per feature and overlay coverage score as annotation.
#     """
#     fig, ax = plt.subplots(figsize=(8, 5))
#     bars = ax.bar(FEATURES, kl_scores, color='steelblue')

#     for bar in bars:
#         height = bar.get_height()
#         ax.annotate(f'{height:.3f}', xy=(bar.get_x() + bar.get_width() / 2, height),
#                     xytext=(0, 5), textcoords="offset points", ha='center', va='bottom')

#     ax.set_ylabel("KL Divergence")
#     ax.set_title("KL Divergence per Feature")
#     ax.text(0.5, max(kl_scores) * 1.1,
#             f"Coverage Score (ε=0.1): {coverage_score:.2%}",
#             ha='center', va='center', fontsize=12, color='orange')

#     plt.ylim(0, max(kl_scores) * 1.3)
#     plt.tight_layout()

#     out_path = os.path.join(PLOT_DIR, "kl_coverage.png")
#     plt.savefig(out_path, dpi=300)
#     print(f"[SAVED] KL & coverage plot → {out_path}")
#     plt.show()


# if __name__ == "__main__":
#     print("[STEP 1] Loading features from real and synthetic logs...")
#     real_matrix, real_dict = extract_features("data/real-world_logs")
#     synth_matrix, synth_dict = extract_features("data/generated_logs")

#     print("[STEP 2] PCA visualization...")
#     plot_pca_convex_hulls(real_matrix, synth_matrix)

#     print("[STEP 3] Plotting normalized distributions...")
#     norm_real, norm_synth = normalize_features(real_dict, synth_dict)
#     plot_stripplot(norm_real, norm_synth)

#     print("[STEP 4] Evaluating representativeness (KL + coverage)...")
#     kl_scores = compute_kl_divergence(real_matrix, synth_matrix)
#     coverage = compute_coverage(real_matrix, synth_matrix)
#     plot_kl_and_coverage(kl_scores, coverage)

import os
import numpy as np
import matplotlib.pyplot as plt
from sklearn.decomposition import PCA
from sklearn.metrics import pairwise_distances
from scipy.spatial import ConvexHull
from scipy.stats import entropy
from ocelytics.feature_extractor import extract_features as extract_raw_features

# Configurable features
FEATURES = ["rmc_object", "rt10_object", "rvpnot_object"]
PLOT_DIR = "plots"
os.makedirs(PLOT_DIR, exist_ok=True)


def extract_features(folder_path):
    matrix = []
    by_feature = {f: [] for f in FEATURES}

    for fname in os.listdir(folder_path):
        if fname.endswith(".jsonocel"):
            path = os.path.join(folder_path, fname)
            try:
                feats = extract_raw_features(path, FEATURES)
                vec = [feats[f] for f in FEATURES]
                if not any(np.isnan(vec)):
                    matrix.append(vec)
                    for i, f in enumerate(FEATURES):
                        by_feature[f].append(vec[i])
            except Exception as e:
                print(f"[WARN] Skipping {fname} due to error: {e}")
    
    return np.array(matrix), by_feature


def normalize_features(real_data, synthetic_data):
    norm_real, norm_synth = {}, {}

    for f in FEATURES:
        combined = real_data[f] + synthetic_data[f]
        if not combined:
            norm_real[f], norm_synth[f] = [], []
            continue

        min_val, max_val = min(combined), max(combined)
        range_val = max_val - min_val or 1.0

        norm_real[f] = [(x - min_val) / range_val for x in real_data[f]]
        norm_synth[f] = [(x - min_val) / range_val for x in synthetic_data[f]]

    return norm_real, norm_synth


def plot_pca_convex_hulls(real_matrix, synth_matrix):
    if real_matrix.shape[0] < 3 or synth_matrix.shape[0] < 3:
        print("[WARN] Not enough samples to compute convex hulls.")
        return

    combined = np.vstack((real_matrix, synth_matrix))
    pca = PCA(n_components=2)
    pca_result = pca.fit_transform(combined)

    real_pca = pca_result[:len(real_matrix)]
    synth_pca = pca_result[len(real_matrix):]

    pc1_var = pca.explained_variance_ratio_[0] * 100
    pc2_var = pca.explained_variance_ratio_[1] * 100

    plt.figure(figsize=(8, 6))
    plt.scatter(real_pca[:, 0], real_pca[:, 1], c='#FFA500', s=10, label="Real Logs", alpha=0.8)
    plt.scatter(synth_pca[:, 0], synth_pca[:, 1], c='#1f77b4', s=10, label="Synthetic Logs", alpha=0.6)

    try:
        hull = ConvexHull(real_pca)
        for simplex in hull.simplices:
            plt.plot(real_pca[simplex, 0], real_pca[simplex, 1], color='#FFA500')
    except Exception as e:
        print(f"[WARN] Failed to draw real log hull: {e}")

    try:
        hull = ConvexHull(synth_pca)
        pts = synth_pca[hull.vertices]
        plt.fill(pts[:, 0], pts[:, 1], color='#1f77b4', alpha=0.2)
        for simplex in hull.simplices:
            plt.plot(synth_pca[simplex, 0], synth_pca[simplex, 1], color='#1f77b4')
    except Exception as e:
        print(f"[WARN] Failed to draw synthetic log hull: {e}")

    plt.xlabel(f"PC1 ({pc1_var:.2f}%)")
    plt.ylabel(f"PC2 ({pc2_var:.2f}%)")
    plt.title("PCA Projection — Real vs. Synthetic")
    plt.legend()
    plt.grid(True, linestyle="--", alpha=0.3)

    out_path = os.path.join(PLOT_DIR, "pca_convex_hulls.png")
    plt.savefig(out_path, dpi=300)
    print(f"[SAVED] PCA plot → {out_path}")
    plt.show()


def plot_stripplot(norm_real, norm_synth, filename="feature_stripplot_close.png"):
    fig, axes = plt.subplots(len(FEATURES), 1, figsize=(9, 6), sharex=True)

    for i, f in enumerate(FEATURES):
        ax = axes[i]
        jitter_real = np.random.normal(0.005, 0.002, len(norm_real[f]))
        jitter_synth = np.random.normal(-0.005, 0.002, len(norm_synth[f]))

        ax.plot(norm_real[f], jitter_real, 'o', color='#FFA500', alpha=0.6, markersize=2,
                label="Real Logs" if i == 0 else "")
        ax.plot(norm_synth[f], jitter_synth, 'o', color='#1f77b4', alpha=0.6, markersize=2,
                label="Synthetic Logs" if i == 0 else "")
        
        ax.set_yticks([])
        ax.set_xlim([0, 1])
        ax.set_title(f)

    axes[0].legend(loc="upper right")
    plt.tight_layout()

    out_path = os.path.join(PLOT_DIR, filename)
    plt.savefig(out_path, dpi=300)
    print(f"[SAVED] Strip plot → {out_path}")
    plt.show()


def compute_kl_divergence(real_matrix, synth_matrix, bins=20):
    kl_scores = []
    for i in range(real_matrix.shape[1]):
        r_hist, _ = np.histogram(real_matrix[:, i], bins=bins, range=(0, 1), density=True)
        s_hist, _ = np.histogram(synth_matrix[:, i], bins=bins, range=(0, 1), density=True)
        kl_scores.append(entropy(r_hist + 1e-10, s_hist + 1e-10))
    return kl_scores


def compute_coverage(real_matrix, synth_matrix, threshold=0.1):
    distances = pairwise_distances(real_matrix, synth_matrix)
    return np.mean(np.min(distances, axis=1) < threshold)


def plot_kl_and_coverage(kl_scores, coverage_score):
    fig, ax = plt.subplots(figsize=(8, 5))
    bars = ax.bar(FEATURES, kl_scores, color='steelblue')

    for bar in bars:
        height = bar.get_height()
        ax.annotate(f'{height:.3f}', xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 5), textcoords="offset points", ha='center', va='bottom')

    ax.set_ylabel("KL Divergence")
    ax.set_title("KL Divergence per Feature")
    ax.text(0.5, max(kl_scores) * 1.1,
            f"Coverage Score (ε=0.1): {coverage_score:.2%}",
            ha='center', va='center', fontsize=12, color='orange')

    plt.ylim(0, max(kl_scores) * 1.3)
    plt.tight_layout()

    out_path = os.path.join(PLOT_DIR, "kl_coverage.png")
    plt.savefig(out_path, dpi=300)
    print(f"[SAVED] KL & coverage plot → {out_path}")
    plt.show()


def run_all_plots(real_dir, synth_dir):
    print("[STEP 1] Loading features from real and synthetic logs...")
    real_matrix, real_dict = extract_features(real_dir)
    synth_matrix, synth_dict = extract_features(synth_dir)

    print("[STEP 2] PCA visualization...")
    plot_pca_convex_hulls(real_matrix, synth_matrix)

    print("[STEP 3] Plotting normalized distributions...")
    norm_real, norm_synth = normalize_features(real_dict, synth_dict)
    plot_stripplot(norm_real, norm_synth)

    print("[STEP 4] Evaluating representativeness (KL + coverage)...")
    kl_scores = compute_kl_divergence(real_matrix, synth_matrix)
    coverage = compute_coverage(real_matrix, synth_matrix)
    plot_kl_and_coverage(kl_scores, coverage)

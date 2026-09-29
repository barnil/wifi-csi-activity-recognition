import csv
import numpy as np
import matplotlib.pyplot as plt


def load_csi(filename):
    all_amplitudes = []

    with open(filename, "r") as f:
        reader = csv.DictReader(f)

        for row in reader:
            try:
                values = [
                    int(x)
                    for x in row["csi_data"].split()
                ]

                # Need I/Q pairs
                if len(values) < 2:
                    continue

                # Make I/Q pairs
                iq = np.array(values, dtype=float).reshape(-1, 2)

                I = iq[:, 0]
                Q = iq[:, 1]

                # Magnitude of each CSI component
                amplitude = np.sqrt(I**2 + Q**2)

                all_amplitudes.append(amplitude)

            except (ValueError, KeyError):
                continue

    return all_amplitudes


baseline = load_csi("baseline.csv")
movement = load_csi("movement.csv")


print("Baseline CSI packets:", len(baseline))
print("Movement CSI packets:", len(movement))


# Use only packets with the same number of samples
def make_matrix(data):
    lengths = [len(x) for x in data]
    common_length = min(lengths)

    matrix = np.array([
        x[:common_length]
        for x in data
    ])

    return matrix


baseline_matrix = make_matrix(baseline)
movement_matrix = make_matrix(movement)


# -----------------------------
# Baseline heatmap
# -----------------------------

plt.figure(figsize=(12, 6))

plt.imshow(
    baseline_matrix.T,
    aspect="auto",
    origin="lower"
)

plt.xlabel("CSI packet / time")
plt.ylabel("CSI subcarrier")
plt.title("CSI Amplitude Heatmap — Static Baseline")

plt.colorbar(label="CSI amplitude")

plt.tight_layout()
plt.savefig("baseline_heatmap.png", dpi=300)

plt.show()


# -----------------------------
# Movement heatmap
# -----------------------------

plt.figure(figsize=(12, 6))

plt.imshow(
    movement_matrix.T,
    aspect="auto",
    origin="lower"
)

plt.xlabel("CSI packet / time")
plt.ylabel("CSI subcarrier")
plt.title("CSI Amplitude Heatmap — Human Movement")

plt.colorbar(label="CSI amplitude")

plt.tight_layout()
plt.savefig("movement_heatmap.png", dpi=300)

plt.show()

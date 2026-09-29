import csv
import numpy as np
import matplotlib.pyplot as plt


def load_csi(filename):
    timestamps = []
    amplitudes = []

    with open(filename, "r") as f:
        reader = csv.DictReader(f)

        for row in reader:
            try:
                timestamp = float(row["timestamp"])
                values = [
                    int(x)
                    for x in row["csi_data"].split()
                ]

                # CSI data is stored as interleaved I,Q values:
                # I0,Q0,I1,Q1,...

                if len(values) < 2:
                    continue

                # Make I/Q pairs
                iq = np.array(values, dtype=float).reshape(-1, 2)

                I = iq[:, 0]
                Q = iq[:, 1]

                # CSI magnitude
                magnitude = np.sqrt(I**2 + Q**2)

                # Average magnitude of this CSI packet
                mean_amplitude = np.mean(magnitude)

                timestamps.append(timestamp)
                amplitudes.append(mean_amplitude)

            except (ValueError, KeyError):
                continue

    timestamps = np.array(timestamps)
    amplitudes = np.array(amplitudes)

    # Convert Unix timestamps to relative time
    if len(timestamps) > 0:
        timestamps = timestamps - timestamps[0]

    return timestamps, amplitudes


# Load datasets
baseline_time, baseline_amp = load_csi("baseline.csv")
movement_time, movement_amp = load_csi("movement.csv")


print("Baseline:")
print(f"  Records: {len(baseline_amp)}")
print(f"  Mean amplitude: {np.mean(baseline_amp):.2f}")
print(f"  Standard deviation: {np.std(baseline_amp):.2f}")

print()

print("Movement:")
print(f"  Records: {len(movement_amp)}")
print(f"  Mean amplitude: {np.mean(movement_amp):.2f}")
print(f"  Standard deviation: {np.std(movement_amp):.2f}")


# -------------------------
# Plot 1: Baseline
# -------------------------

plt.figure(figsize=(12, 5))

plt.plot(baseline_time, baseline_amp)

plt.xlabel("Time (seconds)")
plt.ylabel("Mean CSI amplitude")
plt.title("CSI Amplitude — Static Baseline")

plt.grid(True)
plt.tight_layout()

plt.savefig("baseline_csi.png", dpi=300)

plt.show()


# -------------------------
# Plot 2: Movement
# -------------------------

plt.figure(figsize=(12, 5))

plt.plot(movement_time, movement_amp)

plt.xlabel("Time (seconds)")
plt.ylabel("Mean CSI amplitude")
plt.title("CSI Amplitude — Human Movement")

plt.grid(True)
plt.tight_layout()

plt.savefig("movement_csi.png", dpi=300)

plt.show()


# -------------------------
# Plot 3: Distribution
# -------------------------

plt.figure(figsize=(10, 5))

plt.hist(
    baseline_amp,
    bins=50,
    alpha=0.6,
    label="Baseline"
)

plt.hist(
    movement_amp,
    bins=50,
    alpha=0.6,
    label="Movement"
)

plt.xlabel("Mean CSI amplitude")
plt.ylabel("Number of measurements")
plt.title("CSI Amplitude Distribution")

plt.legend()
plt.grid(True)
plt.tight_layout()

plt.savefig("csi_distribution.png", dpi=300)

plt.show()

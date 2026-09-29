import serial
import csv
import time

PORT = "/dev/cu.usbserial-0001"
BAUDRATE = 115200
import sys

OUTPUT_FILE = sys.argv[1] if len(sys.argv) > 1 else "csi_data.csv"

ser = serial.Serial(PORT, BAUDRATE, timeout=1)

print("Waiting for CSI data...")

sample_count = 0
start_time = time.time()

with open(OUTPUT_FILE, "w", newline="") as f:
    writer = csv.writer(f)

    writer.writerow(["timestamp", "sample_number", "csi_data"])

    try:
        while True:
            line = ser.readline().decode("utf-8", errors="ignore").strip()

            if not line.startswith("CSI,"):
                continue

            timestamp = time.time() - start_time
            sample_count += 1

            writer.writerow([
                timestamp,
                sample_count,
                line
            ])

            f.flush()

            if sample_count % 100 == 0:
                print(f"Samples recorded: {sample_count}")

    except KeyboardInterrupt:
        print("\nRecording stopped.")

ser.close()

print(f"Total CSI samples: {sample_count}")
print(f"Saved to: {OUTPUT_FILE}")

import serial
import csv
import time

PORT = "/dev/cu.usbserial-0001"
BAUDRATE = 115200
OUTPUT = "movement.csv"

ser = serial.Serial(PORT, BAUDRATE, timeout=1)

print(f"Listening on {PORT}")
print(f"Saving data to {OUTPUT}")
print("Press Ctrl+C to stop.")

with open(OUTPUT, "w", newline="") as f:
    writer = csv.writer(f)

    writer.writerow([
        "timestamp",
        "rx_seq",
        "csi_len",
        "csi_data"
    ])

    try:
        while True:
            line = ser.readline().decode(
                "utf-8",
                errors="ignore"
            ).strip()

            if not line.startswith("CSI,"):
                continue

            parts = line.split(",")

            if len(parts) < 4:
                continue

            rx_seq = parts[1]
            csi_len = parts[2]
            csi_data = parts[3:]

            writer.writerow([
                time.time(),
                rx_seq,
                csi_len,
                " ".join(csi_data)
            ])

            f.flush()

            print(
                f"Captured CSI: "
                f"seq={rx_seq}, "
                f"len={csi_len}, "
                f"samples={len(csi_data)}"
            )

    except KeyboardInterrupt:
        print("\nStopping...")

    finally:
        ser.close()

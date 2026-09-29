# WiFi CSI-Based Human Activity Recognition

A recording-aware baseline for **human activity recognition using WiFi Channel State Information (CSI)** collected from ESP32 devices.

This project explores whether real-world WiFi CSI measurements can be used to distinguish between different human activity states using conventional machine learning methods.

The project was developed as part of the **IEEE Silchar Subsection Student Summer Internship Program – 2026 (IS3IP-2026)**.

---

## Overview

WiFi Channel State Information (CSI) describes how a wireless signal is affected as it travels between a transmitter and receiver. Changes in the surrounding environment, including human movement, can alter the CSI measurements.

This project uses recorded CSI data to investigate whether these changes can be used for **human activity recognition**.

Three activity classes are considered:

- **Empty** — no person present
- **Standing** — person standing
- **Moving** — person moving

The main objective was to establish a **recording-aware machine learning baseline** as a step toward more advanced WiFi sensing and eventually WiFi-based human pose estimation.

The project focuses on the transition from controlled or simulated CSI experiments toward **real recorded CSI data** and evaluates how well models generalize to previously unseen recordings.
---

## Project Pipeline

The overall workflow of the project is:

```text
ESP32 Transmitter
       │
       │ WiFi Signal
       ▼
ESP32 Receiver
       │
       │ CSI Data
       ▼
Serial Data Collection
       │
       ▼
CSV Dataset
       │
       ▼
CSI Parsing & Cleaning
       │
       ▼
Amplitude Extraction
       │
       ▼
Temporal Windowing
       │
       ▼
Feature Extraction
       │
       ▼
Machine Learning
       │
       ▼
Recording-Aware Evaluation
       │
       ▼
Human Activity Classification
```

The recorded CSI data is processed and converted into temporal windows. Statistical features are then extracted from the CSI measurements and used to train conventional machine learning models.
---

## Dataset

The project uses a real recorded CSI dataset consisting of **15 CSV recordings** across three activity classes.

Each class contains five recordings:

```text
dataset/
├── empty_01.csv
├── empty_02.csv
├── empty_03.csv
├── empty_04.csv
├── empty_05.csv
│
├── moving_01.csv
├── moving_02.csv
├── moving_03.csv
├── moving_04.csv
├── moving_05.csv
│
├── standing_01.csv
├── standing_02.csv
├── standing_03.csv
├── standing_04.csv
└── standing_05.csv
```

### Dataset Statistics

| Property | Value |
|---|---:|
| Total recordings | 15 |
| Activity classes | 3 |
| Raw CSI rows | 12,737 |
| Valid CSI rows | 12,721 |
| Malformed rows | 16 |
| CSI amplitude features | 62 |
| Empty packets | 3,006 |
| Moving packets | 5,090 |
| Standing packets | 4,625 |

The valid CSI packets are converted into an amplitude representation containing **62 subcarrier values**.

---

## Train/Test Split

The dataset is divided according to recordings rather than randomly splitting individual CSI packets.

### Development recordings

Recordings `01`–`04` from each activity class are used for model development:

```text
empty_01 → empty_04
moving_01 → moving_04
standing_01 → standing_04
```

### Final test recordings

Recording `05` from each class is kept completely separate for the final evaluation:

```text
empty_05
moving_05
standing_05
```

This recording-aware split is important because consecutive CSI measurements within the same recording can be highly correlated.

---

## Windowing

CSI packets are grouped into temporal windows before classification.

The project uses:

- **Window size:** 100 consecutive CSI packets
- **Step size:** 50 packets
- **Training windows:** 174
- **Test windows:** 57

This produces overlapping temporal windows that capture changes in CSI over time.
---

## CSI Processing

The recorded CSI data undergoes the following processing steps:

1. Read CSI measurements from the recorded CSV files.
2. Identify and remove malformed CSI rows.
3. Parse the CSI values into numerical measurements.
4. Extract the CSI values corresponding to the subcarriers.
5. Convert the CSI representation into amplitude values.
6. Organize the measurements into temporal windows.
7. Normalize the data using statistics calculated from the training recordings only.
8. Extract statistical features from each temporal window.

The final processed representation contains **62 CSI subcarrier amplitudes per packet**.

---

## Feature Extraction

For each of the 62 subcarriers, the following statistical features are calculated over each temporal window:

- Mean
- Standard deviation
- Minimum
- Maximum
- Range
- Mean absolute temporal difference
- Standard deviation of temporal difference

This results in:

```text
62 subcarriers × 7 features = 434 features
```

The feature representation therefore has **434 dimensions per temporal window**.

The standard deviation feature was particularly useful during feature-group evaluation, indicating that temporal variation in CSI contains useful information for distinguishing the activity classes.
---

## Machine Learning

The project evaluates several conventional machine learning approaches for CSI-based activity recognition.

The main models considered include:

- Random Forest
- Support Vector Machine (SVM)
- K-Nearest Neighbors (KNN)
- Logistic Regression
- Linear SVM
- Extra Trees
- HistGradientBoosting

The models are evaluated using the extracted statistical CSI features.

---

## Model Comparison

A recording-aware GroupKFold evaluation was used to compare the conventional classifiers.

| Model | Mean GroupKFold Accuracy |
|---|---:|
| RBF SVM | 70.89% |
| Random Forest | 69.13% |
| HistGradientBoosting | 65.46% |
| KNN | 65.33% |
| Extra Trees | 64.29% |
| Logistic Regression | 62.83% |
| Linear SVM | 59.54% |

The RBF SVM produced the strongest mean performance among the conventional classifiers in this comparison.

---

## PCA-Based Classification

Principal Component Analysis (PCA) was also evaluated as a dimensionality-reduction step before SVM classification.

The strongest result was obtained using **10 PCA components**.

```text
StandardScaler
      │
      ▼
PCA (10 components)
      │
      ▼
RBF SVM
C = 100
gamma = 0.001
```

The PCA + RBF-SVM configuration achieved a mean GroupKFold accuracy of approximately **72.28%** during model development.

---

## Final Model

The final selected pipeline consists of:

1. StandardScaler
2. PCA with 10 components
3. RBF-kernel Support Vector Machine

The model was retrained using all 12 development recordings and evaluated only on the three previously unseen recording-05 files.

This evaluation was designed to measure generalization to recordings that were not used during model development.

---

## Evaluation Strategy

Two different evaluation settings were considered.

### Random / Stratified Evaluation

Randomly splitting windows can produce high accuracy because windows originating from the same recording can be highly similar.

For example, the feature-based Random Forest achieved:

```text
Stratified 5-fold accuracy: 92.00%
```

### Recording-Aware Evaluation

A recording-aware split keeps entire recordings together instead of distributing windows from the same recording across training and validation sets.

Under this evaluation:

```text
Recording-aware mean accuracy: 66.12%
```

The difference between these results demonstrates the importance of evaluating CSI activity-recognition models on **unseen recordings** rather than relying only on randomly split windows.---

## Results

The project evaluated both direct CSI representations and statistical feature-based representations.

| Approach | Evaluation | Accuracy |
|---|---|---:|
| Direct CSI + Random Forest | Unseen test windows | 64.91% |
| Statistical Features + Random Forest | Unseen test windows | 91.23% |
| RBF SVM | GroupKFold | 70.89% |
| PCA + RBF SVM | GroupKFold | 72.28% |
| Final PCA + RBF SVM | Unseen test windows | 57.89% |
| Final PCA + RBF SVM | Recording-level | 66.67% |

The feature-based Random Forest achieved high accuracy on the unseen test windows, while the recording-aware evaluation showed that performance can decrease substantially when generalizing to completely unseen recordings.

This highlights the effect of **recording/session variation** in real-world CSI sensing.

---

## Recording-Level Evaluation

For the final PCA + RBF-SVM model, predictions were also aggregated at the recording level.

Three unseen recordings were evaluated:

| Recording | True Class | Predicted Class |
|---|---|---|
| `empty_05.csv` | Empty | Empty |
| `moving_05.csv` | Moving | Moving |
| `standing_05.csv` | Standing | Empty |

Using mean decision-score aggregation, the recording-level accuracy was:

```text
66.67%
```

The model correctly identified the unseen empty and moving recordings but classified the standing recording as empty.

---

## Key Observation

A major observation from the experiments is the gap between randomly or stratified-split evaluation and recording-aware evaluation.

High performance can be obtained when highly correlated windows from the same recording are distributed across training and validation sets. However, when complete recordings are held out, performance decreases.

This suggests that **recording/session variation is an important challenge for real-world WiFi CSI-based activity recognition**.

The results therefore provide a baseline for investigating more robust CSI sensing systems and future WiFi-based human pose estimation.
---

## Hardware

The project uses ESP32 devices for WiFi CSI collection.

The experimental setup consists of:

- ESP32 transmitter
- ESP32 receiver
- Computer for serial data collection and analysis
- WiFi network

CSI measurements are transmitted from the receiver to the computer through a serial connection for recording and analysis.

---

## Software

### Data Collection

- ESP-IDF
- ESP32 CSI APIs
- Python
- Serial communication

### Data Analysis

- Python
- NumPy
- Pandas
- Matplotlib
- Scikit-learn
- Jupyter Notebook

---

## Repository Structure

```text
wifi-csi-activity-recognition/
│
├── dataset/
│   ├── empty_01.csv
│   ├── ...
│   ├── moving_01.csv
│   ├── ...
│   └── standing_05.csv
│
├── firmware/
│   ├── receiver/
│   │   ├── main/
│   │   │   ├── csi_receiver.c
│   │   │   └── main.c
│   │   └── CMakeLists.txt
│   │
│   └── transmitter/
│       ├── main/
│       │   ├── csi_transmitter.c
│       │   └── main.c
│       └── CMakeLists.txt
│
├── notebooks/
│   └── CSI_Activity_Recognition.ipynb
│
├── src/
│   ├── collect_csi.py
│   ├── csi_logger.py
│   ├── analyze_csi.py
│   └── csi_heatmap.py
│
├── results/
│   └── figures and evaluation results
│
├── docs/
│   └── internship-report.pdf
│
├── README.md
└── LICENSE
```
---

## Running the Analysis

### 1. Clone the repository

```bash
git clone git@github.com:barnil/wifi-csi-activity-recognition.git
cd wifi-csi-activity-recognition
```

### 2. Install Python dependencies

```bash
pip install numpy pandas matplotlib scikit-learn jupyter
```

### 3. Run the analysis notebook

Start Jupyter:

```bash
jupyter notebook
```

Then open:

```text
notebooks/CSI_Activity_Recognition.ipynb
```

The notebook loads the recordings from the `dataset/` directory and performs CSI processing, feature extraction, model training, validation, and evaluation.

---

## ESP32 Firmware

The repository contains separate ESP-IDF projects for the CSI transmitter and receiver.

### Receiver

```text
firmware/receiver/
```

The receiver captures WiFi CSI measurements and sends the recorded information through the serial interface.

### Transmitter

```text
firmware/transmitter/
```

The transmitter provides the WiFi transmission used during CSI collection.

Both projects can be built and flashed using the ESP-IDF toolchain.

> Before building the firmware, configure the WiFi settings for your own experimental environment. Do not commit passwords or other private credentials to the repository.

---

## Limitations

The current study has several limitations:

- The dataset contains only **15 recordings**.
- Only three activity classes are considered.
- One recording from each class is used as the final held-out test set.
- Subject-independent and environment-independent generalization has not been established.
- The analysis primarily uses CSI amplitude information.
- A complete phase-sanitization pipeline was not implemented.
- No synchronized RGB/DensePose ground truth is available.
- Overlapping temporal windows can be correlated.
- The current system performs activity classification rather than direct human pose estimation.

These limitations mean that the results should be considered a **baseline study** rather than a complete WiFi-DensePose implementation.

---

## Future Work

Potential directions for extending the project include:

### Dataset Expansion

- Collect more recordings.
- Include multiple subjects.
- Collect data across different rooms and environments.
- Vary transmitter and receiver placements.
- Include multiple sessions and recording conditions.

### CSI Processing

- Investigate CSI phase information.
- Explore amplitude-phase fusion.
- Perform subcarrier selection.
- Investigate frequency-domain and time-frequency representations.
- Explore wavelet-based representations.

### Machine Learning

- CNN-based CSI models.
- RNN-based temporal models.
- Transformer-based architectures.
- Transfer learning.
- Domain adaptation.

### WiFi-Based Pose Estimation

The longer-term direction is to move beyond coarse activity recognition toward **human pose estimation from WiFi CSI**, including:

- Human keypoint estimation.
- Pose sequence modeling.
- Richer activity classes.
- Synchronized RGB/DensePose ground truth.
- Multiple sensing nodes.
- Real-time inference.

---

## Relation to WiFi-DensePose

This project serves as a baseline toward WiFi-based human pose estimation.

It does **not** implement the complete WiFi-DensePose system. Instead, it establishes a real-recorded CSI activity-recognition pipeline and investigates the challenges of generalizing across recordings.

The results provide a starting point for future work involving richer datasets, deep learning, temporal modeling, and human pose estimation.

---

## Documentation

The detailed methodology, experiments, results, and discussion are available in the internship report:

```text
docs/internship-report.pdf
```

The main experimental workflow is implemented in:

```text
notebooks/CSI_Activity_Recognition.ipynb
```

---

## Acknowledgements

This project was carried out as part of the **IEEE Silchar Subsection Student Summer Internship Program – 2026 (IS3IP-2026)**.

Special thanks to **Dr. Partha Pakray**, IEEE Silchar Subsection, for mentorship and guidance during the internship.

---

## Authors

**Barnil Mahanta**  
B.Tech CSE (AI/ML)  
Assam Science and Technology University

**Arpan Goswami**  
B.Tech CSE (AI/ML)  
Assam Science and Technology University

---

## References

The project builds upon research in WiFi sensing, Channel State Information (CSI), human activity recognition, and WiFi-based human pose estimation.

Relevant works include:

- WiFi DensePose
- DensePose From WiFi
- Person-in-WiFi
- CSI-Net
- WiFi Vision

See the internship report in `docs/internship-report.pdf` for the complete reference list.

---

## License

This project is provided for academic and research purposes.

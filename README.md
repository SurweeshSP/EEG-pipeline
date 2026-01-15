# NEUROSENSE AI - BioAmp EXG Pill Edition

**BioAmp EXG Pill based Brain-Computer Interface (BCI) System**

This project implements a single-channel Motor Imagery BCI using the BioAmp EXG Pill and Arduino Uno. It captures EEG signals from the C3 (Motor Cortex) position, processes them to extract Mu and Beta band power, and classifies them into "LEFT HAND IMAGERY" vs "REST" states to control a robotic chassis.

## Project Structure

- `arduino/` - Firmware for Arduino Uno
- `config/` - Configuration settings
- `hardware/` - Interfaces for BioAmp and Robot
- `src/` - Core source code
    - `acquisition/` - Data buffering
    - `preprocessing/` - Filtering and artifact removal
    - `features/` - Feature extraction
    - `models/` - Machine learning classifiers
    - `control/` - Command mapping logic
    - `pipeline/` - Main real-time loop
- `scripts/` - Operational scripts
- `tests/` - Unit tests
- `docs/` - Documentation

## Setup & installation

1. **Install Python requirements:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Upload Firmware:**
   Upload `arduino/bioamp_stream.ino` to your Arduino Uno.

## Usage

1. **Test Connection:**
   ```bash
   python scripts/1_test_bioamp.py
   ```

2. **Calibrate User:**
   ```bash
   python scripts/2_calibrate_user.py "YourName"
   ```

3. **Train Model:**
   ```bash
   python scripts/3_train_model.py
   ```

4. **Run Live BCI:**
   ```bash
   python scripts/5_run_live_bci.py
   ```

See [HARDWARE_GUIDE.md](HARDWARE_GUIDE.md) for detailed hardware setup instructions.

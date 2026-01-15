"""
Test BioAmp EXG Pill connection and data quality
"""
import sys
from pathlib import Path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import time
import numpy as np
import matplotlib.pyplot as plt
from hardware.bioamp_reader import BioAmpReader
from config.settings import Config

def test_bioamp(duration=10):
    """
    Test BioAmp sensor connection and data quality
    """
    print("="*60)
    print("NEUROSENSE AI - BioAmp EXG Pill Test")
    print("="*60)
    
    # Connect
    bioamp = BioAmpReader()
    
    print(f"\nConnecting to Arduino on {Config.ARDUINO_PORT}...")
    if not bioamp.connect():
        print("Connection failed!")
        print("Check:")
        print("1. Arduino connected via USB")
        print("2. Correct port in config.py")
        print("3. Firmware uploaded to Arduino")
        return
    
    print("✓ Connected successfully!")
    
    # Calibrate baseline
    print("\nCalibrating baseline...")
    bioamp.calibrate_baseline(duration=5)
    
    # Collect samples
    print(f"\nRecording EEG data for {duration} seconds...")
    print("Channel: C3 (Left Motor Cortex)")
    
    samples = []
    timestamps = []
    sample_count = 0
    start_time = time.time()
    
    for sample, timestamp in bioamp.stream_continuous():
        if sample is None:
            continue
        
        samples.append(sample)
        timestamps.append(timestamp)
        sample_count += 1
        
        # Print every 100 samples
        if sample_count % 100 == 0:
            print(f"[{timestamp:5.2f}s] Sample {sample_count}: {sample:7.2f} μV")
        
        # Stop after duration
        if timestamp >= duration:
            break
    
    bioamp.disconnect()
    
    # Analyze data
    print("\n" + "="*60)
    print("DATA QUALITY REPORT")
    print("="*60)
    
    data = np.array(samples)
    timestamps = np.array(timestamps)
    
    print(f"Total samples: {len(samples)}")
    print(f"Duration: {timestamps[-1]:.2f} seconds")
    print(f"Sampling rate: {len(samples) / timestamps[-1]:.1f} Hz")
    print(f"Expected: {Config.SAMPLING_RATE} Hz")
    
    print(f"\nSignal Statistics (μV):")
    print(f"  Mean:   {np.mean(data):7.2f}")
    print(f"  Std:    {np.std(data):7.2f}")
    print(f"  Min:    {np.min(data):7.2f}")
    print(f"  Max:    {np.max(data):7.2f}")
    print(f"  Range:  {np.max(data) - np.min(data):7.2f}")
    
    # Check for artifacts
    max_amplitude = np.max(np.abs(data))
    print(f"\nMax amplitude: {max_amplitude:.2f} μV")
    
    if max_amplitude > 150:
        print("⚠ High amplitude detected - check electrode contact!")
    else:
        print("✓ Signal quality looks good")
    
    # Plot
    print("\nGenerating plots...")
    
    plt.figure(figsize=(12, 8))
    
    # Time series
    plt.subplot(2, 1, 1)
    plt.plot(timestamps, data)
    plt.xlabel('Time (s)')
    plt.ylabel('Amplitude (μV)')
    plt.title('EEG Signal (C3 - Left Motor Cortex)')
    plt.grid(True)
    
    # Power spectrum
    from scipy.signal import welch
    freqs, psd = welch(data, fs=Config.SAMPLING_RATE, nperseg=512)
    
    plt.subplot(2, 1, 2)
    plt.semilogy(freqs, psd)
    plt.xlabel('Frequency (Hz)')
    plt.ylabel('Power (μV²/Hz)')
    plt.title('Power Spectral Density')
    plt.xlim([0, 50])
    plt.grid(True)
    
    # Mark mu and beta bands
    plt.axvspan(8, 13, alpha=0.3, color='blue', label='Mu band')
    plt.axvspan(13, 30, alpha=0.3, color='red', label='Beta band')
    plt.legend()
    
    plt.tight_layout()
    plt.savefig('bioamp_test.png')
    print("✓ Plot saved to bioamp_test.png")
    
    print("\n✓ Test complete!")

if __name__ == "__main__":
    duration = int(sys.argv[1]) if len(sys.argv) > 1 else 10
    test_bioamp(duration)

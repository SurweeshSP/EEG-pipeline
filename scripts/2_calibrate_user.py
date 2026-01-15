"""
Collect calibration data for binary BCI (IMAGERY vs REST)
"""
import sys
from pathlib import Path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import time
import numpy as np
from hardware.bioamp_reader import BioAmpReader
from src.preprocessing.filters import RealtimePreprocessor
from src.features.band_power import BandPowerExtractor
from config.settings import Config

def calibrate_user(user_name):
    """
    Run calibration session for binary classification
    
    Collects 15 trials × 2 classes (REST, IMAGERY)
    """
    print(f"\n{'='*60}")
    print(f"NEUROSENSE AI - CALIBRATION: {user_name}")
    print(f"{'='*60}\n")
    
    # Connect to BioAmp
    bioamp = BioAmpReader()
    if not bioamp.connect():
        print("Failed to connect to BioAmp sensor!")
        return
    
    # Baseline calibration
    print("=== Baseline Calibration ===")
    bioamp.calibrate_baseline(duration=5)
    
    # Processing components
    preprocessor = RealtimePreprocessor()
    feature_extractor = BandPowerExtractor()
    
    # Task instructions
    tasks = [
        (0, 'REST', 'Relax, clear your mind, no specific thought'),
        (1, 'MOTOR IMAGERY', 'Imagine moving LEFT hand (squeeze/open fist)')
    ]
    
    all_features = []
    all_labels = []
    
    print("\nInstructions:")
    print("- Each trial: 2s preparation + 4s task")
    print("- IMAGERY: Imagine moving your LEFT hand")
    print("- REST: Relax, think of nothing specific")
    print("- Keep eyes open, minimize movement\n")
    
    input("Press ENTER to start calibration...")
    
    for task_id, task_name, instruction in tasks:
        print(f"\n{'='*60}")
        print(f"Task: {task_name}")
        print(f"Instruction: {instruction}")
        print(f"{'='*60}")
        
        for trial in range(Config.TRIALS_PER_CLASS):
            input(f"\nTrial {trial+1}/{Config.TRIALS_PER_CLASS} - Press ENTER when ready...")
            
            # Preparation phase
            print("PREPARE... (2s)")
            time.sleep(Config.PREP_DURATION)
            
            # Task phase
            if task_id == 0:
                print("REST - Relax! (4s)")
            else:
                print("IMAGINE LEFT HAND MOVEMENT! (4s)")
            
            # Collect EEG data
            trial_samples = []
            trial_start = time.time()
            
            for sample, timestamp in bioamp.stream_continuous():
                if sample is not None:
                    trial_samples.append(sample)
                
                # Stop after trial duration
                if time.time() - trial_start >= Config.TRIAL_DURATION:
                    break
            
            # Convert to array
            trial_data = np.array(trial_samples)  # (n_samples,)
            
            print(f"RELAX (3s) - Collected {len(trial_samples)} samples")
            time.sleep(Config.REST_DURATION)
            
            # Process trial
            preprocessed, is_clean = preprocessor.preprocess(trial_data)
            
            if not is_clean:
                print("⚠ Artifact detected - retrying trial")
                trial -= 1
                continue
            
            # Extract features
            features = feature_extractor.extract(preprocessed)
            
            all_features.append(features)
            all_labels.append(task_id)
            
            print(f"✓ Trial {trial+1} complete - Features: {features}")
    
    # Save calibration data
    X = np.array(all_features)  # (30, 2)
    y = np.array(all_labels)    # (30,)
    
    save_path = Config.CALIBRATION_DIR / f"{user_name}_calibration.npz"
    np.savez(save_path,
             features=X,
             labels=y,
             user_name=user_name,
             channel=Config.CHANNEL_NAME,
             timestamp=time.strftime("%Y-%m-%d %H:%M:%S"))
    
    print(f"\n{'='*60}")
    print("CALIBRATION COMPLETE!")
    print(f"{'='*60}")
    print(f"Saved to: {save_path}")
    print(f"Total samples: {len(y)}")
    print(f"Label distribution: REST={np.sum(y==0)}, IMAGERY={np.sum(y==1)}")
    print(f"\nFeature statistics:")
    print(f"  REST:    Mu={np.mean(X[y==0, 0]):.2f}, Beta={np.mean(X[y==0, 1]):.2f}")
    print(f"  IMAGERY: Mu={np.mean(X[y==1, 0]):.2f}, Beta={np.mean(X[y==1, 1]):.2f}")
    
    bioamp.disconnect()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        user = input("Enter user name: ")
    else:
        user = sys.argv[1]
    
    calibrate_user(user)

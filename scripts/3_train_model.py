"""
Train binary classifier from calibration data
"""
import sys
from pathlib import Path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import numpy as np
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
from src.models.classifier import MotorImageryClassifier
from src.features.normalizer import FeatureNormalizer
from config.settings import Config

def train_model():
    """Train binary classifier on calibration data"""
    
    print("="*60)
    print("NEUROSENSE AI - BINARY MODEL TRAINING")
    print("="*60)
    
    # Load calibration files
    cal_files = list(Config.CALIBRATION_DIR.glob("*_calibration.npz"))
    
    if not cal_files:
        print("No calibration files found!")
        print(f"Run: python scripts/2_calibrate_user.py")
        return
    
    print(f"\nFound {len(cal_files)} calibration files:")
    for f in cal_files:
        print(f"  - {f.name}")
    
    # Load all data
    all_features = []
    all_labels = []
    
    for cal_file in cal_files:
        data = np.load(cal_file)
        all_features.append(data['features'])
        all_labels.append(data['labels'])
        print(f"  Loaded: {data['user_name']} ({data['channel']})")
    
    X = np.vstack(all_features)
    y = np.concatenate(all_labels)
    
    print(f"\nDataset:")
    print(f"  Total samples: {len(y)}")
    print(f"  Features per sample: {X.shape[1]}")
    print(f"  Classes: {np.unique(y)}")
    print(f"  Distribution: REST={np.sum(y==0)}, IMAGERY={np.sum(y==1)}")
    
    print(f"\nFeature ranges:")
    print(f"  Mu power:   [{np.min(X[:, 0]):.2f}, {np.max(X[:, 0]):.2f}]")
    print(f"  Beta power: [{np.min(X[:, 1]):.2f}, {np.max(X[:, 1]):.2f}]")
    
    # Fit normalizer
    print("\nFitting normalizer...")
    normalizer = FeatureNormalizer()
    normalizer.fit(X)
    
    # Normalize
    X_norm = normalizer.normalize(X)
    
    # Train/test split
    X_train, X_test, y_train, y_test = train_test_split(
        X_norm, y,
        test_size=0.2,
        random_state=42,
        stratify=y
    )
    
    print(f"\nTrain set: {len(y_train)} samples")
    print(f"Test set:  {len(y_test)} samples")
    
    # Train model
    print(f"\nTraining {Config.MODEL_TYPE} classifier...")
    classifier = MotorImageryClassifier(model_type=Config.MODEL_TYPE)
    classifier.train(X_train, y_train)
    
    # Cross-validation
    print("\nCross-validation (5-fold)...")
    cv_scores = cross_val_score(classifier.model, X_norm, y, cv=5)
    print(f"CV Accuracy: {np.mean(cv_scores):.2%} (±{np.std(cv_scores):.2%})")
    
    # Evaluate
    y_pred = classifier.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    
    print("\n" + "="*60)
    print("EVALUATION RESULTS")
    print("="*60)
    print(f"Test Accuracy: {acc:.2%}")
    
    if acc >= Config.TARGET_ACCURACY:
        print(f"✓ Target met! Accuracy {acc:.2%} >= {Config.TARGET_ACCURACY:.0%}")
    else:
        print(f"⚠ Target missed! Accuracy {acc:.2%} < {Config.TARGET_ACCURACY:.0%}")
        print("Consider: More calibration trials, different channel (C4), or feature engineering")
    
    print("\nClassification Report:")
    print(classification_report(
        y_test, y_pred,
        target_names=['REST', 'IMAGERY']
    ))
    
    print("\nConfusion Matrix:")
    cm = confusion_matrix(y_test, y_pred)
    print(cm)
    print(f"\n  [[TN={cm[0,0]}  FP={cm[0,1]}]")
    print(f"   [FN={cm[1,0]}  TP={cm[1,1]}]]")
    
    # Save model
    model_path = Config.MODEL_DIR / 'neurosense_binary_model.pkl'
    classifier.save(model_path)
    
    # Save normalizer
    norm_path = Config.MODEL_DIR / 'normalizer.pkl'
    normalizer.save(norm_path)
    
    print(f"\n✓ Model saved to: {model_path}")
    print(f"✓ Normalizer saved to: {norm_path}")
    
    return classifier, normalizer, acc

if __name__ == "__main__":
    train_model()

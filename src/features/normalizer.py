"""
Feature Normalizer for EEG features
"""
import joblib
from sklearn.preprocessing import StandardScaler
import numpy as np

class FeatureNormalizer:
    def __init__(self):
        self.scaler = StandardScaler()
        self.is_fitted = False

    def fit(self, X):
        """
        Fit the normalizer to the data
        
        Args:
            X: (n_samples, n_features)
        """
        self.scaler.fit(X)
        self.is_fitted = True

    def normalize(self, X):
        """
        Normalize features
        
        Args:
            X: (n_samples, n_features) or (n_features,)
            
        Returns:
            normalized_X: same shape as X
        """
        if not self.is_fitted:
            # If not fitted, return as is or raise error. 
            # For robustness in inferenced before training, we might warn.
            # But let's assume it should be fitted or loaded.
            # If input is 1D array
            if X.ndim == 1:
                return X
            return X
            
        if X.ndim == 1:
            X_reshaped = X.reshape(1, -1)
            X_norm = self.scaler.transform(X_reshaped)
            return X_norm.flatten()
        else:
            return self.scaler.transform(X)

    def save(self, filepath):
        """Save normalizer state"""
        joblib.dump(self.scaler, filepath)
        print(f"Normalizer saved to {filepath}")

    def load(self, filepath):
        """Load normalizer state"""
        self.scaler = joblib.load(filepath)
        self.is_fitted = True
        print(f"Normalizer loaded from {filepath}")

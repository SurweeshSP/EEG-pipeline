"""
Band power feature extraction (Mu + Beta) for single channel
"""
import numpy as np
from scipy.signal import welch
from config.settings import Config

class BandPowerExtractor:
    def __init__(self, fs=Config.SAMPLING_RATE):
        self.fs = fs
        self.mu_band = Config.MU_BAND
        self.beta_band = Config.BETA_BAND
        
        # Baseline power (for ERD calculation)
        self.baseline_mu = None
        self.baseline_beta = None
        
    def extract(self, window):
        """
        Extract mu and beta band power
        
        Args:
            window: (n_samples,) single channel
            
        Returns:
            features: (2,) [mu_power, beta_power]
        """
        # Power spectral density
        freqs, psd = welch(window, 
                          fs=self.fs,
                          nperseg=min(256, len(window)))
        
        # Mu band (8-13 Hz) - Primary motor imagery band
        mu_idx = (freqs >= self.mu_band[0]) & (freqs <= self.mu_band[1])
        mu_power = np.mean(psd[mu_idx])
        
        # Beta band (13-30 Hz) - Secondary motor imagery band
        beta_idx = (freqs >= self.beta_band[0]) & (freqs <= self.beta_band[1])
        beta_power = np.mean(psd[beta_idx])
        
        return np.array([mu_power, beta_power])
    
    def set_baseline(self, baseline_windows):
        """
        Set baseline power from rest state
        
        Args:
            baseline_windows: list of rest state windows
        """
        baseline_features = []
        for window in baseline_windows:
            features = self.extract(window)
            baseline_features.append(features)
        
        baseline_features = np.array(baseline_features)
        self.baseline_mu = np.mean(baseline_features[:, 0])
        self.baseline_beta = np.mean(baseline_features[:, 1])
        
        print(f"Baseline set: Mu={self.baseline_mu:.2f}, Beta={self.baseline_beta:.2f}")
    
    def calculate_erd(self, features):
        """
        Calculate Event-Related Desynchronization
        
        ERD = (Baseline - Task) / Baseline
        Negative ERD = power decrease = motor imagery
        
        Args:
            features: (2,) [mu_power, beta_power]
            
        Returns:
            erd: (2,) [mu_erd, beta_erd]
        """
        if self.baseline_mu is None or self.baseline_beta is None:
            return np.array([0.0, 0.0])
        
        mu_erd = (self.baseline_mu - features[0]) / self.baseline_mu
        beta_erd = (self.baseline_beta - features[1]) / self.baseline_beta
        
        return np.array([mu_erd, beta_erd])

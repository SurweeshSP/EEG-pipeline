"""
Signal preprocessing for single-channel EEG
"""
import numpy as np
from scipy.signal import butter, filtfilt, iirnotch
from config.settings import Config

class RealtimePreprocessor:
    def __init__(self, 
                 lowcut=Config.BANDPASS_LOW,
                 highcut=Config.BANDPASS_HIGH,
                 notch_freq=Config.NOTCH_FREQ,
                 fs=Config.SAMPLING_RATE,
                 order=Config.FILTER_ORDER):
        
        self.fs = fs
        self.lowcut = lowcut
        self.highcut = highcut
        self.notch_freq = notch_freq
        self.order = order
        
        # Design bandpass filter
        nyq = 0.5 * fs
        low = lowcut / nyq
        high = highcut / nyq
        self.bp_b, self.bp_a = butter(order, [low, high], btype='band')
        
        # Design notch filter (50 Hz / 60 Hz)
        self.notch_b, self.notch_a = iirnotch(notch_freq, Q=30, fs=fs)
        
    def bandpass_filter(self, data):
        """
        Apply bandpass filter (8-30 Hz)
        
        Args:
            data: (n_samples,) single channel
            
        Returns:
            filtered: (n_samples,)
        """
        return filtfilt(self.bp_b, self.bp_a, data)
    
    def notch_filter(self, data):
        """
        Apply notch filter (remove 50/60 Hz powerline noise)
        
        Args:
            data: (n_samples,)
            
        Returns:
            filtered: (n_samples,)
        """
        return filtfilt(self.notch_b, self.notch_a, data)
    
    def remove_artifacts(self, data, threshold=150):
        """
        Check for artifacts (amplitude > threshold μV)
        
        Returns:
            bool: True if clean, False if artifact detected
        """
        max_amp = np.max(np.abs(data))
        return max_amp < threshold
    
    def detrend(self, data):
        """Remove linear trend"""
        from scipy.signal import detrend
        return detrend(data)
    
    def preprocess(self, window):
        """
        Complete preprocessing pipeline
        
        Args:
            window: (n_samples,) single channel
            
        Returns:
            tuple: (preprocessed, is_clean)
                preprocessed: (n_samples,)
                is_clean: bool
        """
        # Detrend
        detrended = self.detrend(window)
        
        # Notch filter (remove powerline noise)
        notched = self.notch_filter(detrended)
        
        # Bandpass filter
        filtered = self.bandpass_filter(notched)
        
        # Artifact detection
        is_clean = self.remove_artifacts(filtered)
        
        return filtered, is_clean

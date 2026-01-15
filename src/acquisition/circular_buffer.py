"""
Circular buffer for sliding window segmentation (single channel)
"""
import numpy as np
from collections import deque
from config.settings import Config

class CircularBuffer:
    def __init__(self, 
                 window_size=Config.WINDOW_SAMPLES,
                 step_size=Config.STEP_SAMPLES):
        
        self.window_size = window_size  # 1000 samples (2 seconds)
        self.step_size = step_size      # 250 samples (0.5 seconds)
        
        # Buffer holds 3 seconds of data
        self.buffer = deque(maxlen=window_size + step_size)
        self.sample_count = 0
        
    def add_sample(self, sample):
        """
        Add new sample to buffer
        
        Args:
            sample: float (single channel value)
        """
        self.buffer.append(sample)
        self.sample_count += 1
    
    def is_ready(self):
        """Check if we have enough samples for a window"""
        return len(self.buffer) >= self.window_size
    
    def get_window(self):
        """
        Extract latest window if step condition met
        
        Returns:
            np.array or None: (window_size,) or None
        """
        if not self.is_ready():
            return None
        
        # Check if we've stepped forward enough
        if self.sample_count % self.step_size == 0:
            # Extract last window_size samples
            window_list = list(self.buffer)[-self.window_size:]
            window = np.array(window_list)  # Shape: (1000,)
            return window
        
        return None
    
    def reset(self):
        """Clear buffer"""
        self.buffer.clear()
        self.sample_count = 0

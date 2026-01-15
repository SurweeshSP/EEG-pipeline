"""
Map binary predictions to robot commands
"""
import numpy as np
from collections import deque
from config.settings import Config
import time

class CommandMapper:
    def __init__(self, 
                 smoothing_window=Config.SMOOTHING_WINDOW,
                 confidence_threshold=Config.CONFIDENCE_THRESHOLD):
        
        self.smoothing_window = smoothing_window
        self.confidence_threshold = confidence_threshold
        self.recent_predictions = deque(maxlen=smoothing_window)
        self.command_map = Config.COMMAND_MAP
        
        # For duration-based commands
        self.imagery_start_time = None
        self.imagery_duration = 0
        
    def map_binary(self, prediction, confidence):
        """
        Simple binary mapping (STOP vs ACTIVE)
        
        Args:
            prediction: int (0=REST, 1=IMAGERY)
            confidence: float (0-1)
            
        Returns:
            str: Command ('STOP' or 'ACTIVE')
        """
        # Safety: auto-stop on low confidence
        if confidence < self.confidence_threshold:
            return 'STOP'
        
        # Add to recent predictions
        self.recent_predictions.append(prediction)
        
        # Majority voting
        if len(self.recent_predictions) >= self.smoothing_window:
            counts = np.bincount(list(self.recent_predictions), minlength=2)
            stable_prediction = np.argmax(counts)
        else:
            stable_prediction = prediction
        
        return self.command_map[stable_prediction]
    
    def map_duration(self, prediction, confidence):
        """
        Duration-based mapping (LEFT/FORWARD/RIGHT based on how long)
        
        Args:
            prediction: int (0=REST, 1=IMAGERY)
            confidence: float
            
        Returns:
            str: Command ('STOP', 'LEFT', 'FORWARD', 'RIGHT')
        """
        current_time = time.time()
        
        # Safety check
        if confidence < self.confidence_threshold:
            self.imagery_start_time = None
            return 'STOP'
        
        if prediction == 1:  # IMAGERY detected
            if self.imagery_start_time is None:
                # Start of imagery
                self.imagery_start_time = current_time
                return 'STOP'  # Wait to determine duration
            else:
                # Ongoing imagery
                self.imagery_duration = current_time - self.imagery_start_time
                
                # Don't send command until imagery stops
                return 'STOP'
        else:  # REST
            if self.imagery_start_time is not None:
                # End of imagery - determine command based on duration
                duration = self.imagery_duration
                self.imagery_start_time = None
                self.imagery_duration = 0
                
                if duration < 1.5:
                    return 'STOP'  # Too short
                elif duration < 2.5:
                    return 'LEFT'
                elif duration < 3.5:
                    return 'FORWARD'
                else:
                    return 'RIGHT'
            else:
                return 'STOP'
    
    def reset(self):
        """Clear prediction history"""
        self.recent_predictions.clear()
        self.imagery_start_time = None
        self.imagery_duration = 0

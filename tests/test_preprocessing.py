import unittest
import numpy as np
import sys
from pathlib import Path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.preprocessing.filters import RealtimePreprocessor
from config.settings import Config

class TestPreprocessing(unittest.TestCase):
    def setUp(self):
        self.preprocessor = RealtimePreprocessor()
        self.fs = Config.SAMPLING_RATE
        
    def test_bandpass_filter(self):
        # Create a signal with 10Hz (in band) and 100Hz (out of band) components
        t = np.arange(0, 1.0, 1.0/self.fs)
        sig_10hz = np.sin(2 * np.pi * 10 * t)
        sig_100hz = 0.5 * np.sin(2 * np.pi * 100 * t)
        combined = sig_10hz + sig_100hz
        
        filtered, _ = self.preprocessor.preprocess(combined)
        
        # Check that 100Hz component is attenuated
        # Simply check if variance is reduced significantly but not zero
        # 10Hz should pass, 100Hz should stop.
        # Original var approx 0.5 + 0.125 = 0.625
        # 10Hz var approx 0.5
        
        original_std = np.std(combined)
        filtered_std = np.std(filtered)
        
        # It should retain the 10Hz signal mostly
        self.assertLess(filtered_std, original_std)
        self.assertGreater(filtered_std, 0.3)  # Arbitrary check for signal presence

    def test_artifact_detection(self):
        clean_sig = np.zeros(100)
        noisy_sig = np.zeros(100)
        noisy_sig[50] = 200 # > 150 threshold
        
        _, is_clean = self.preprocessor.preprocess(clean_sig)
        self.assertTrue(is_clean)
        
        _, is_clean_noisy = self.preprocessor.preprocess(noisy_sig)
        self.assertFalse(is_clean_noisy)

if __name__ == '__main__':
    unittest.main()

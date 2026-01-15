import unittest
import numpy as np
import sys
from pathlib import Path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.features.band_power import BandPowerExtractor
from config.settings import Config

class TestFeatureExtraction(unittest.TestCase):
    def setUp(self):
        self.extractor = BandPowerExtractor()
        
    def test_bands(self):
        # Generate 10Hz sine wave (Mu band)
        fs = Config.SAMPLING_RATE
        t = np.arange(0, 1.0, 1.0/fs)
        sig_10hz = np.sin(2 * np.pi * 10 * t)
        
        mu, beta = self.extractor.extract(sig_10hz)
        
        # Mu power should be high, Beta power low
        self.assertGreater(mu, beta)
        
        # Generate 20Hz sine wave (Beta band)
        sig_20hz = np.sin(2 * np.pi * 20 * t)
        mu_2, beta_2 = self.extractor.extract(sig_20hz)
        
        self.assertGreater(beta_2, mu_2)

if __name__ == '__main__':
    unittest.main()

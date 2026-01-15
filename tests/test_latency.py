import unittest
import time
import sys
from pathlib import Path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.pipeline.realtime_bci import RealtimeBCIPipeline
# Use mock/simulated hardware for latency test? 
# Or just test processing steps.

from src.preprocessing.filters import RealtimePreprocessor
from src.features.band_power import BandPowerExtractor
from config.settings import Config
import numpy as np

class TestLatency(unittest.TestCase):
    def setUp(self):
        self.preprocessor = RealtimePreprocessor()
        self.extractor = BandPowerExtractor()
        
    def test_processing_latency(self):
        # Generate 2 seconds of data (1000 samples)
        window = np.random.randn(Config.WINDOW_SAMPLES)
        
        start_time = time.perf_counter()
        
        # 1. Preprocess
        prep, _ = self.preprocessor.preprocess(window)
        
        # 2. Extract
        feat = self.extractor.extract(prep)
        
        end_time = time.perf_counter()
        duration_ms = (end_time - start_time) * 1000
        
        print(f"Processing latency: {duration_ms:.2f} ms")
        
        # Should be well under 400ms target (realistically < 50ms on modern CPU)
        self.assertLess(duration_ms, 100) 

if __name__ == '__main__':
    unittest.main()

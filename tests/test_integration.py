import unittest
import sys
from pathlib import Path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.pipeline.realtime_bci import RealtimeBCIPipeline

class TestIntegration(unittest.TestCase):
    def test_pipeline_instantiation(self):
        try:
            # Should instantiate without error (even if model missing, it warns)
            pipeline = RealtimeBCIPipeline(model_path="dummy.pkl")
            self.assertIsNotNone(pipeline)
        except Exception as e:
            self.fail(f"Pipeline instantiation failed: {e}")

if __name__ == '__main__':
    unittest.main()

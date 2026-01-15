import unittest
import numpy as np
import sys
from pathlib import Path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.models.classifier import MotorImageryClassifier
from config.settings import Config

class TestClassifier(unittest.TestCase):
    def setUp(self):
        self.classifier = MotorImageryClassifier(model_type='LDA')
        
    def test_train_predict(self):
        # Generate synthetic data
        # Class 0: Mean [1, 1]
        # Class 1: Mean [5, 5]
        X0 = np.random.randn(20, 2) + 1
        X1 = np.random.randn(20, 2) + 5
        
        X = np.vstack([X0, X1])
        y = np.array([0]*20 + [1]*20)
        
        self.classifier.train(X, y)
        
        # Test predictions
        test_X0 = np.array([[1.0, 1.0]])
        test_X1 = np.array([[5.0, 5.0]])
        
        pred0 = self.classifier.predict(test_X0)
        pred1 = self.classifier.predict(test_X1)
        
        self.assertEqual(pred0[0], 0)
        self.assertEqual(pred1[0], 1)

if __name__ == '__main__':
    unittest.main()

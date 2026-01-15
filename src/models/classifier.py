"""
Binary classifier for single-channel motor imagery (LEFT/RIGHT vs REST)
"""
import numpy as np
import joblib
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
from sklearn.svm import SVC
from sklearn.linear_model import LogisticRegression
from config.settings import Config

class MotorImageryClassifier:
    def __init__(self, model_type=Config.MODEL_TYPE):
        self.model_type = model_type
        self.model = self._create_model()
        self.n_classes = Config.N_CLASSES
        
    def _create_model(self):
        """Initialize classifier"""
        if self.model_type == 'LDA':
            return LinearDiscriminantAnalysis()
        elif self.model_type == 'SVM':
            return SVC(kernel='rbf', C=1.0, gamma='scale', probability=True)
        elif self.model_type == 'LogisticRegression':
            return LogisticRegression(max_iter=1000)
        else:
            raise ValueError(f"Unknown model type: {self.model_type}")
    
    def train(self, X_train, y_train):
        """
        Train binary classifier
        
        Args:
            X_train: (n_samples, 2) features [mu_power, beta_power]
            y_train: (n_samples,) labels 0=REST, 1=IMAGERY
        """
        print(f"Training {self.model_type} for binary classification...")
        print(f"Classes: {np.unique(y_train)}")
        print(f"Distribution: {np.bincount(y_train)}")
        
        self.model.fit(X_train, y_train)
        print("Training complete!")
        
    def predict(self, X):
        """
        Predict class
        
        Args:
            X: (n_samples, 2) or (2,)
            
        Returns:
            predictions: (n_samples,) or int
        """
        if X.ndim == 1:
            X = X.reshape(1, -1)
        return self.model.predict(X)
    
    def predict_proba(self, X):
        """Get class probabilities"""
        if X.ndim == 1:
            X = X.reshape(1, -1)
        
        if hasattr(self.model, 'predict_proba'):
            return self.model.predict_proba(X)
        else:
            pred = self.predict(X)
            proba = np.zeros((len(pred), self.n_classes))
            proba[np.arange(len(pred)), pred] = 1.0
            return proba
    
    def save(self, filepath):
        """Save trained model"""
        joblib.dump(self.model, filepath)
        print(f"Model saved to {filepath}")
        
    def load(self, filepath):
        """Load trained model"""
        self.model = joblib.load(filepath)
        print(f"Model loaded from {filepath}")

class ThresholdClassifier:
    """
    Simple threshold-based classifier using ERD
    (Alternative to ML models for very limited data)
    """
    def __init__(self, mu_threshold=Config.ERD_THRESHOLD):
        self.mu_threshold = mu_threshold
        
    def predict(self, erd):
        """
        Predict based on ERD threshold
        
        Args:
            erd: (2,) [mu_erd, beta_erd]
            
        Returns:
            int: 0=REST, 1=IMAGERY
        """
        mu_erd = erd[0] if isinstance(erd, np.ndarray) else erd
        
        # Negative ERD (power decrease) = motor imagery
        if mu_erd < self.mu_threshold:
            return 1  # IMAGERY detected
        else:
            return 0  # REST
    
    def predict_proba(self, erd):
        """Simulate probabilities"""
        pred = self.predict(erd)
        confidence = abs(erd[0]) / abs(self.mu_threshold)
        confidence = min(max(confidence, 0.5), 0.95)
        
        if pred == 1:
            return np.array([[1-confidence, confidence]])
        else:
            return np.array([[confidence, 1-confidence]])

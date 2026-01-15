"""
Complete real-time BCI pipeline for BioAmp EXG Pill
"""
import time
import numpy as np
from hardware.bioamp_reader import BioAmpReader
from hardware.robot_controller import RobotController
from src.acquisition.circular_buffer import CircularBuffer
from src.preprocessing.filters import RealtimePreprocessor
from src.features.band_power import BandPowerExtractor
from src.features.normalizer import FeatureNormalizer
from src.models.classifier import MotorImageryClassifier, ThresholdClassifier
from src.control.command_mapper import CommandMapper
from config.settings import Config

class RealtimeBCIPipeline:
    def __init__(self, model_path, normalizer_path=None, use_duration=False):
        print("Initializing NEUROSENSE AI Pipeline (BioAmp Edition)...")
        
        # Hardware
        self.bioamp = BioAmpReader()
        self.robot = RobotController()
        
        # Processing components
        self.buffer = CircularBuffer()
        self.preprocessor = RealtimePreprocessor()
        self.feature_extractor = BandPowerExtractor()
        self.normalizer = FeatureNormalizer()
        self.classifier = MotorImageryClassifier()
        self.command_mapper = CommandMapper()
        
        # Duration-based commands
        self.use_duration = use_duration
        
        # Load trained model
        try:
            self.classifier.load(model_path)
        except:
            print("Warning: Could not load model, using threshold classifier")
            self.classifier = ThresholdClassifier()
        
        # Load normalizer if available
        if normalizer_path:
            try:
                self.normalizer.load(normalizer_path)
            except:
                print("Warning: Could not load normalizer")
        
        # Performance tracking
        self.latencies = []
        self.predictions_log = []
        
    def connect_hardware(self):
        """Connect to BioAmp and robot"""
        print("\n=== Connecting Hardware ===")
        
        bioamp_ok = self.bioamp.connect()
        robot_ok = self.robot.connect()
        
        if not bioamp_ok:
            raise ConnectionError("Failed to connect to BioAmp sensor!")
        
        if not robot_ok:
            print("Warning: Robot not connected (simulation mode)")
        
        # Calibrate baseline
        print("\n=== Baseline Calibration ===")
        self.bioamp.calibrate_baseline(duration=5)
        
        return bioamp_ok
    
    def process_window(self, window):
        """
        Process one window through pipeline
        
        Args:
            window: (n_samples,) single channel
            
        Returns:
            tuple: (command, confidence, latency_ms)
        """
        start_time = time.time()
        
        # Stage 1: Preprocessing
        preprocessed, is_clean = self.preprocessor.preprocess(window)
        
        if not is_clean:
            latency = (time.time() - start_time) * 1000
            return 'STOP', 0.0, latency
        
        # Stage 2: Feature extraction
        features = self.feature_extractor.extract(preprocessed)
        
        # Optional: Calculate ERD
        erd = self.feature_extractor.calculate_erd(features)
        
        # Stage 3: Normalization
        normalized = self.normalizer.normalize(features)
        
        # Stage 4: Classification
        if isinstance(self.classifier, ThresholdClassifier):
            prediction = self.classifier.predict(erd)
            confidence = self.classifier.predict_proba(erd)[0][prediction]
        else:
            prediction = self.classifier.predict(normalized)[0]
            confidence = self.classifier.predict_proba(normalized)[0][prediction]
        
        # Stage 5: Command mapping
        if self.use_duration:
            command = self.command_mapper.map_duration(prediction, confidence)
        else:
            command = self.command_mapper.map_binary(prediction, confidence)
        
        # Calculate latency
        latency = (time.time() - start_time) * 1000
        
        return command, confidence, latency
    
    def run(self, duration=None):
        """
        Run real-time BCI control loop
        
        Args:
            duration: Run duration in seconds (None = infinite)
        """
        print("\n=== Starting Real-Time BCI ===")
        print(f"Target latency: <{Config.TARGET_LATENCY_MS}ms")
        print(f"Window: {Config.WINDOW_LENGTH}s, Overlap: {Config.WINDOW_OVERLAP*100}%")
        print(f"Command mode: {'Duration-based' if self.use_duration else 'Binary'}")
        print("\nPress Ctrl+C to stop\n")
        
        self.command_mapper.reset()
        start_time = time.time()
        window_count = 0
        
        try:
            for sample, timestamp in self.bioamp.stream_continuous():
                # Check duration limit
                if duration and timestamp >= duration:
                    break
                
                # Add sample to buffer
                self.buffer.add_sample(sample)
                
                # Get window if ready
                window = self.buffer.get_window()
                
                if window is None:
                    continue
                
                # Process window
                command, confidence, latency = self.process_window(window)
                
                # Send to robot (only if not STOP or changed)
                self.robot.send_command(command)
                
                # Log performance
                self.latencies.append(latency)
                self.predictions_log.append({
                    'timestamp': timestamp,
                    'command': command,
                    'confidence': confidence,
                    'latency_ms': latency
                })
                
                window_count += 1
                
                # Print status
                print(f"[{timestamp:6.2f}s] {command:8s} (conf: {confidence:.2f}, latency: {latency:5.1f}ms)")
                
        except KeyboardInterrupt:
            print("\n\nStopped by user")
        
        # Report performance
        self.report_performance(window_count)
    
    def report_performance(self, window_count):
        """Print performance statistics"""
        print("\n" + "="*60)
        print("PERFORMANCE REPORT")
        print("="*60)
        
        if len(self.latencies) > 0:
            latencies = np.array(self.latencies)
            
            print(f"Windows processed: {window_count}")
            print(f"\nLatency Statistics:")
            print(f"  Mean:  {np.mean(latencies):6.1f} ms")
            print(f"  Median: {np.median(latencies):6.1f} ms")
            print(f"  P95:   {np.percentile(latencies, 95):6.1f} ms")
            print(f"  Max:   {np.max(latencies):6.1f} ms")
            
            # Check target
            p95 = np.percentile(latencies, 95)
            if p95 < Config.TARGET_LATENCY_MS:
                print(f"\n✓ Target met! P95 latency: {p95:.1f}ms < {Config.TARGET_LATENCY_MS}ms")
            else:
                print(f"\n✗ Target missed! P95 latency: {p95:.1f}ms > {Config.TARGET_LATENCY_MS}ms")
        
        print("="*60)
    
    def disconnect_hardware(self):
        """Disconnect from hardware"""
        print("\nDisconnecting hardware...")
        self.bioamp.disconnect()
        self.robot.disconnect()

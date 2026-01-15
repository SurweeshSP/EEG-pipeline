"""
NEUROSENSE AI - BioAmp EXG Pill Configuration
Single-channel EEG system
"""
import os
from pathlib import Path

class Config:
    # Project paths
    PROJECT_ROOT = Path(__file__).parent.parent
    DATA_DIR = PROJECT_ROOT / 'data'
    CALIBRATION_DIR = DATA_DIR / 'calibration'
    MODEL_DIR = DATA_DIR / 'models'
    
    # Create directories
    for dir_path in [DATA_DIR, CALIBRATION_DIR, MODEL_DIR]:
        dir_path.mkdir(exist_ok=True, parents=True)
    
    # Hardware settings - BioAmp EXG Pill + Arduino Uno
    ARDUINO_PORT = '/dev/ttyUSB0'  # Linux: /dev/ttyUSB0, Windows: COM3, Mac: /dev/cu.usbserial
    BAUD_RATE = 115200
    N_CHANNELS = 1  # Single channel for BioAmp
    SAMPLING_RATE = 500  # Hz (Arduino Uno can do 500 Hz for 1 channel)
    
    # Channel configuration
    CHANNEL_NAME = 'C3'  # Left motor cortex (change to C4 for right hand)
    ELECTRODE_POSITIONS = {
        'SIGNAL': 'C3',      # Primary motor cortex signal
        'REFERENCE': 'A1',   # Left mastoid (behind ear)
        'GROUND': 'Fpz'      # Forehead
    }
    
    # BioAmp EXG Pill specifications
    BIOAMP_GAIN = 2420  # Fixed gain
    BIOAMP_BANDPASS = (0.5, 250)  # Hz - Hardware bandpass
    ADC_RESOLUTION = 10  # bits (Arduino Uno)
    ADC_VREF = 5.0  # Volts
    
    # Signal processing
    BANDPASS_LOW = 8.0   # Hz (mu band start)
    BANDPASS_HIGH = 30.0  # Hz (beta band end)
    FILTER_ORDER = 5
    NOTCH_FREQ = 50.0  # Hz (India: 50 Hz, US: 60 Hz)
    
    # Windowing
    WINDOW_LENGTH = 2.0   # seconds (longer for single channel)
    WINDOW_SAMPLES = int(WINDOW_LENGTH * SAMPLING_RATE)  # 1000 samples
    WINDOW_OVERLAP = 0.75  # 75% overlap
    STEP_SAMPLES = int(WINDOW_SAMPLES * (1 - WINDOW_OVERLAP))  # 250 samples
    
    # Feature extraction
    MU_BAND = (8, 13)    # Hz - Motor imagery primary band
    BETA_BAND = (13, 30)  # Hz - Motor imagery secondary band
    N_FEATURES = 2  # mu + beta power (single channel)
    
    # Model settings - Binary classifier for 1-channel
    MODEL_TYPE = 'LDA'  # LDA, SVM, LogisticRegression
    N_CLASSES = 2  # LEFT vs REST (or RIGHT vs REST)
    
    # Command mapping (simplified for 1-channel)
    COMMAND_MAP = {
        0: 'STOP',    # Rest state
        1: 'ACTIVE'   # Motor imagery detected (LEFT or RIGHT or FORWARD)
    }
    
    # Extended commands (requires clever strategy)
    EXTENDED_COMMANDS = {
        'SHORT': 'LEFT',      # 1-2 seconds imagery
        'MEDIUM': 'FORWARD',  # 2-3 seconds imagery
        'LONG': 'RIGHT',      # 3-4 seconds imagery
        'NONE': 'STOP'        # No imagery
    }
    
    # Robot commands
    ROBOT_COMMANDS = {
        'STOP': 'S',
        'FORWARD': 'F',
        'LEFT': 'L',
        'RIGHT': 'R'
    }
    
    # Control parameters
    SMOOTHING_WINDOW = 5  # Majority voting (longer for single channel)
    CONFIDENCE_THRESHOLD = 0.65  # Higher threshold for reliability
    MAX_COMMAND_RATE = 3  # Max 3 commands per second (more conservative)
    
    # ERD/ERS Detection (Event-Related Desynchronization/Synchronization)
    ERD_THRESHOLD = -0.3  # 30% power decrease = motor imagery
    ERS_THRESHOLD = 0.2   # 20% power increase = rest
    
    # Robot interface
    ROBOT_PORT = '/dev/ttyUSB1'  # Separate port for robot
    ROBOT_BAUD = 9600
    
    # Calibration
    TRIALS_PER_CLASS = 15  # More trials for single channel
    TRIAL_DURATION = 4.0   # seconds
    PREP_DURATION = 2.0    # seconds
    REST_DURATION = 3.0    # seconds (longer rest for single channel)
    
    # Performance targets (lower for single channel)
    TARGET_LATENCY_MS = 400  # milliseconds (allow more time)
    TARGET_ACCURACY = 0.65   # 65% (realistic for 1-channel)
    MIN_USER_ACCURACY = 0.60  # 60% minimum
    
    # Voltage conversion
    @staticmethod
    def adc_to_voltage(adc_value):
        """Convert Arduino ADC value to voltage"""
        return (adc_value / 1024.0) * Config.ADC_VREF
    
    @staticmethod
    def voltage_to_uv(voltage):
        """Convert voltage to microvolts (accounting for BioAmp gain)"""
        return (voltage - 2.5) * 1000000 / Config.BIOAMP_GAIN

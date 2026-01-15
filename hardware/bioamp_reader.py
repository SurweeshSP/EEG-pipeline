"""
Real-time EEG data acquisition from BioAmp EXG Pill via Arduino
"""
import serial
import numpy as np
import time
from config.settings import Config

class BioAmpReader:
    def __init__(self, port=Config.ARDUINO_PORT, baudrate=Config.BAUD_RATE):
        self.port = port
        self.baudrate = baudrate
        self.fs = Config.SAMPLING_RATE
        self.ser = None
        self.connected = False
        
        # Calibration offset (DC removal)
        self.baseline = None
        self.baseline_samples = []
        
    def connect(self):
        """Connect to Arduino via Serial"""
        try:
            self.ser = serial.Serial(self.port, self.baudrate, timeout=1)
            time.sleep(2)  # Wait for Arduino reset
            
            # Flush initial garbage
            self.ser.flushInput()
            
            # Read first line to verify
            line = self.ser.readline().decode().strip()
            print(f"BioAmp connected: {line}")
            
            self.connected = True
            return True
            
        except serial.SerialException as e:
            print(f"Failed to connect to Arduino: {e}")
            print(f"Available ports: {self._list_ports()}")
            return False
    
    def _list_ports(self):
        """List available serial ports"""
        import serial.tools.list_ports
        ports = serial.tools.list_ports.comports()
        return [port.device for port in ports]
    
    def calibrate_baseline(self, duration=5):
        """
        Collect baseline for DC offset removal
        
        Args:
            duration: seconds to collect baseline
        """
        print(f"Calibrating baseline ({duration}s)...")
        print("Please relax and minimize movement.")
        
        self.baseline_samples = []
        start_time = time.time()
        
        while time.time() - start_time < duration:
            sample = self.read_sample()
            if sample is not None:
                self.baseline_samples.append(sample)
        
        self.baseline = np.mean(self.baseline_samples)
        baseline_std = np.std(self.baseline_samples)
        
        print(f"Baseline: {self.baseline:.2f} μV (std: {baseline_std:.2f} μV)")
        
        return self.baseline
    
    def read_sample(self):
        """
        Read one EEG sample (single channel)
        
        Returns:
            float: voltage value in microvolts (or None if invalid)
        """
        if not self.connected:
            raise ConnectionError("BioAmp not connected!")
        
        try:
            line = self.ser.readline().decode().strip()
            
            if not line or line.startswith("BioAmp"):
                return None  # Skip header/empty lines
            
            # Convert ADC value to microvolts
            adc_value = int(line)
            
            # ADC → Voltage → Microvolts
            voltage = Config.adc_to_voltage(adc_value)
            microvolts = Config.voltage_to_uv(voltage)
            
            # Remove baseline if calibrated
            if self.baseline is not None:
                microvolts -= self.baseline
            
            return microvolts
            
        except (ValueError, UnicodeDecodeError):
            return None  # Corrupted sample
    
    def stream_continuous(self):
        """
        Generator: yields EEG samples continuously
        
        Yields:
            tuple: (sample, timestamp)
                sample: float (microvolts)
                timestamp: float (seconds)
        """
        start_time = time.time()
        sample_count = 0
        
        while self.connected:
            sample = self.read_sample()
            
            if sample is not None:
                timestamp = time.time() - start_time
                sample_count += 1
                yield sample, timestamp
    
    def disconnect(self):
        """Close serial connection"""
        if self.ser and self.ser.is_open:
            self.ser.close()
            self.connected = False
            print("BioAmp disconnected")

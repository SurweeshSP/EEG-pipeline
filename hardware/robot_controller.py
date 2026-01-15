"""
Robot Controller Interface
"""
import serial
import time
from config.settings import Config

class RobotController:
    def __init__(self, port=Config.ROBOT_PORT, baudrate=Config.ROBOT_BAUD):
        self.port = port
        self.baudrate = baudrate
        self.ser = None
        self.connected = False
        self.commands = Config.ROBOT_COMMANDS

    def connect(self):
        """Connect to robot via Serial"""
        try:
            self.ser = serial.Serial(self.port, self.baudrate, timeout=1)
            time.sleep(2)  # Wait for Arduino reset
            self.connected = True
            print(f"Robot controller connected on {self.port}")
            return True
        except Exception as e:
            print(f"Failed to connect to robot: {e}")
            # print(f"Available ports: {self._list_ports()}")
            return False

    def send_command(self, command_name):
        """
        Send command to robot
        
        Args:
            command_name: str (e.g. 'STOP', 'FORWARD')
        """
        if not self.connected:
            return
        
        if command_name in self.commands:
            cmd_char = self.commands[command_name]
            try:
                self.ser.write(cmd_char.encode())
                # print(f"Sent command: {command_name} ({cmd_char})")
            except Exception as e:
                print(f"Error sending command: {e}")
    
    def disconnect(self):
        """Close serial connection"""
        if self.ser and self.ser.is_open:
            self.ser.close()
            self.connected = False
            print("Robot controller disconnected")

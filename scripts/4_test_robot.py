"""
Test Robot Controller connection and commands
"""
import sys
from pathlib import Path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import time
from hardware.robot_controller import RobotController
from config.settings import Config

def test_robot():
    print("="*60)
    print("NEUROSENSE AI - Robot Controller Test")
    print("="*60)
    
    robot = RobotController()
    
    print(f"\nConnecting to Robot on {Config.ROBOT_PORT}...")
    if not robot.connect():
        print("Connection failed!")
        return

    print("✓ Connected successfully!")
    
    commands = ['FORWARD', 'LEFT', 'RIGHT', 'STOP']
    
    try:
        for cmd in commands:
            print(f"Sending command: {cmd}")
            robot.send_command(cmd)
            time.sleep(2)
            
        # Stop at the end
        robot.send_command('STOP')
        
    except KeyboardInterrupt:
        print("Interrupted")
    finally:
        robot.disconnect()
        print("\nTest complete")

if __name__ == "__main__":
    test_robot()

"""
Run live BCI control with BioAmp EXG Pill
"""
import sys
from pathlib import Path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.pipeline.realtime_bci import RealtimeBCIPipeline
from config.settings import Config

def run_live_bci(duration=60, use_duration=False):
    """
    Run live BCI session
    
    Args:
        duration: Session duration in seconds
        use_duration: Use duration-based commands (LEFT/FORWARD/RIGHT)
    """
    print("="*60)
    print("NEUROSENSE AI - LIVE BCI CONTROL (BioAmp Edition)")
    print("="*60)
    
    # Check if model exists
    model_path = Config.MODEL_DIR / 'neurosense_binary_model.pkl'
    norm_path = Config.MODEL_DIR / 'normalizer.pkl'
    
    if not model_path.exists():
        print("No trained model found!")
        print("Train model first: python scripts/3_train_model.py")
        return
    
    print(f"\nControl mode: {'Duration-based (LEFT/FORWARD/RIGHT)' if use_duration else 'Binary (ACTIVE/STOP)'}")
    
    # Initialize pipeline
    pipeline = RealtimeBCIPipeline(
        model_path=str(model_path),
        normalizer_path=str(norm_path),
        use_duration=use_duration
    )
    
    # Connect hardware
    try:
        pipeline.connect_hardware()
    except ConnectionError as e:
        print(f"Hardware connection failed: {e}")
        return
    
    input("\nPress ENTER to start BCI control...")
    
    # Run BCI loop
    try:
        pipeline.run(duration=duration)
    except Exception as e:
        print(f"\nError during BCI: {e}")
        import traceback
        traceback.print_exc()
    finally:
        pipeline.disconnect_hardware()

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Run live BCI with BioAmp')
    parser.add_argument('duration', type=int, nargs='?', default=60,
                       help='Session duration in seconds')
    parser.add_argument('--duration-mode', action='store_true',
                       help='Use duration-based commands (LEFT/FORWARD/RIGHT)')
    
    args = parser.parse_args()
    
    print(f"\nSession duration: {args.duration} seconds")
    run_live_bci(args.duration, use_duration=args.duration_mode)

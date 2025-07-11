"""
CLI entry point for Scale Detective game
"""

import argparse
import sys
from .scale_detector import ScaleDetector

def main():
    """Main CLI function for Scale Detective"""
    parser = argparse.ArgumentParser(
        description="Scale Detective - Detect out-of-tune notes in an A major scale",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python -m hide_and_seek.scale_detector_cli              # Easy mode: 50 cents out of tune
  python -m hide_and_seek.scale_detector_cli -c 30        # Easy mode: 30 cents out of tune
  python -m hide_and_seek.scale_detector_cli --hard       # Hard mode: require direction detection
  python -m hide_and_seek.scale_detector_cli -c 30 --hard # Hard mode: 30 cents out of tune
        """
    )
    
    parser.add_argument(
        '-c', '--cents',
        type=float,
        default=50.0,
        help='Number of cents the out-of-tune note will be off (default: 50.0)'
    )
    
    parser.add_argument(
        '--hard',
        action='store_true',
        help='Hard mode: require direction detection (up/down arrows)'
    )
    
    args = parser.parse_args()
    
    # Validate arguments
    if args.cents <= 0:
        print("Error: Cents must be positive")
        sys.exit(1)
    
    if args.cents > 200:
        print("Warning: {args.cents} cents is very out of tune (more than 2 semitones)")
        response = input("Continue anyway? (y/N): ").strip().lower()
        if response != 'y':
            sys.exit(0)
    
    # Create and run the game
    try:
        game = ScaleDetector(out_of_tune_cents=args.cents, hard_mode=args.hard)
        game.run_game()
    except KeyboardInterrupt:
        print("\n\nGame interrupted. Thanks for playing! 🎵")
    except Exception as e:
        print(f"\nError: {e}")
        print("Make sure your speakers are working properly.")
        sys.exit(1)

if __name__ == '__main__':
    main() 
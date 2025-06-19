"""
Main entry point for the Hide and Seek ear training app
"""

import argparse
import sys
from .game import HideAndSeekGame

def main():
    """Main CLI function"""
    parser = argparse.ArgumentParser(
        description="Hide and Seek - Ear Training for Violin Students",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python -m hide_and_seek              # Play with 3 notes (default)
  python -m hide_and_seek -n 5         # Play with 5 notes
  python -m hide_and_seek --tolerance 30  # Use stricter tolerance (30 cents)
        """
    )
    
    parser.add_argument(
        '-n', '--num-notes',
        type=int,
        default=3,
        help='Number of notes to play (default: 3)'
    )
    
    parser.add_argument(
        '-t', '--tolerance',
        type=float,
        default=50.0,
        help='Tolerance in cents for note matching (default: 50.0)'
    )
    
    parser.add_argument(
        '--list-notes',
        action='store_true',
        help='List all available notes and exit'
    )
    
    parser.add_argument(
        '--debug',
        action='store_true',
        help='Enable debug mode'
    )
    
    args = parser.parse_args()
    
    # List available notes if requested
    if args.list_notes:
        from .notes import get_violin_range_notes
        notes = get_violin_range_notes()
        print("Available notes in violin range:")
        for note_name, freq in notes:
            print(f"  {note_name}: {freq:.1f} Hz")
        return
    
    # Validate arguments
    if args.num_notes < 2:
        print("Error: Number of notes must be at least 2")
        sys.exit(1)
    
    if args.tolerance <= 0:
        print("Error: Tolerance must be positive")
        sys.exit(1)
    
    # Create and run the game
    try:
        game = HideAndSeekGame(tolerance_cents=args.tolerance, debug=args.debug)
        game.run_game(num_notes=args.num_notes)
    except KeyboardInterrupt:
        print("\n\nGame interrupted. Thanks for playing! 🎵")
    except Exception as e:
        print(f"\nError: {e}")
        print("Make sure your microphone and speakers are working properly.")
        sys.exit(1)

if __name__ == '__main__':
    main() 
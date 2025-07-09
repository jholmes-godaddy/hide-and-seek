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
  python -m hide_and_seek                    # 3 distinct notes, 8 total notes
  python -m hide_and_seek -d 4              # 4 distinct notes, 8 total notes
  python -m hide_and_seek -n 10             # 3 distinct notes, 10 total notes
  python -m hide_and_seek -d 4 -n 10        # 4 distinct notes, 10 total notes
  python -m hide_and_seek --tolerance 30    # Use stricter tolerance (30 cents)
        """
    )
    
    parser.add_argument(
        '-n', '--num-notes',
        type=int,
        default=8,
        help='Number of notes to play in sequence (default: 8)'
    )
    
    parser.add_argument(
        '-d', '--distinct-notes',
        type=int,
        default=4,
        help='Number of distinct notes to choose from (default: 4)'
    )
    
    parser.add_argument(
        '-t', '--tolerance',
        type=float,
        default=40.0,
        help='Tolerance in cents for note matching (default: 40.0)'
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
    if args.num_notes < 1:
        print("Error: Number of notes in sequence must be at least 1")
        sys.exit(1)
    
    if args.distinct_notes < 1:
        print("Error: Number of distinct notes must be at least 1")
        sys.exit(1)
    
    if args.distinct_notes > 8:
        print("Error: Number of distinct notes cannot exceed 8 (available A major scale notes)")
        sys.exit(1)
    
    if args.tolerance <= 0:
        print("Error: Tolerance must be positive")
        sys.exit(1)
    
    # Create and run the game
    try:
        game = HideAndSeekGame(tolerance_cents=args.tolerance, debug=args.debug)
        game.run_game(num_distinct_notes=args.distinct_notes, sequence_length=args.num_notes)
    except KeyboardInterrupt:
        print("\n\nGame interrupted. Thanks for playing! 🎵")
    except Exception as e:
        print(f"\nError: {e}")
        print("Make sure your microphone and speakers are working properly.")
        sys.exit(1)

if __name__ == '__main__':
    main() 
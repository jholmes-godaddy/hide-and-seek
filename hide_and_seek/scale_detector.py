"""
Scale Detective - A game to detect out-of-tune notes in an A major scale
"""

import random
import time
import sys
import tty
import termios
from typing import List, Tuple, Optional
from .notes import get_violin_range_notes
from .audio import AudioPlayer

class ScaleDetector:
    """Game to detect out-of-tune notes in an A major scale"""
    
    def __init__(self, out_of_tune_cents: float = 50.0, hard_mode: bool = False):
        self.audio_player = AudioPlayer()
        self.out_of_tune_cents = out_of_tune_cents
        self.hard_mode = hard_mode
        self.a_major_scale = self._get_a_major_scale()
    
    def _get_key_press(self) -> str:
        """Get a single key press without requiring Enter"""
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(sys.stdin.fileno())
            ch = sys.stdin.read(1)
            # Handle arrow keys (they send 3 characters)
            if ch == '\x1b':
                ch2 = sys.stdin.read(1)
                if ch2 == '[':
                    ch3 = sys.stdin.read(1)
                    if ch3 == 'A':
                        return 'up'
                    elif ch3 == 'B':
                        return 'down'
            return ch
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    
    def _get_a_major_scale(self) -> List[Tuple[str, float]]:
        """Get the A major scale notes in order"""
        all_notes = get_violin_range_notes()
        # A major scale: A, B, C#, D, E, F#, G#, A
        scale_notes = []
        for note_name, freq in all_notes:
            if note_name in ['A4', 'B4', 'C#5', 'D5', 'E5', 'F#5', 'G#5', 'A5']:
                scale_notes.append((note_name, freq))
        return scale_notes
    
    def _make_note_out_of_tune(self, frequency: float, cents_off: float) -> float:
        """Make a note out of tune by the specified number of cents"""
        # Calculate the out-of-tune frequency
        # cents = 1200 * log2(f2/f1)
        # f2 = f1 * 2^(cents/1200)
        return frequency * (2 ** (cents_off / 1200))
    
    def _play_scale_with_correction(self, scale_notes: List[Tuple[str, float]], 
                                   out_of_tune_index: int, out_of_tune_freq: float) -> None:
        """Play the scale with the out-of-tune note followed by the correct one"""
        print("\n🎵 Here's the scale with the correction:")
        
        for i, (note_name, correct_freq) in enumerate(scale_notes):
            if i == out_of_tune_index:
                # Play out-of-tune note (normal speed)
                print(f"  {note_name} (out of tune)")
                self.audio_player.play_note(out_of_tune_freq, duration=1.0, volume=0.3)
                time.sleep(0.2)
                # Immediately play correct note (normal speed)
                print(f"  {note_name} (correct)")
                self.audio_player.play_note(correct_freq, duration=1.0, volume=0.3)
                time.sleep(0.2)
            else:
                # Play regular notes twice as fast
                print(f"  {note_name}")
                self.audio_player.play_note(correct_freq, duration=0.5, volume=0.3)
                time.sleep(0.1)
    
    def _play_fast_scale(self, scale_notes: List[Tuple[str, float]]) -> None:
        """Play the scale quickly as a victory celebration"""
        print("\n🎉 Victory! Here's the scale you detected:")
        
        for note_name, freq in scale_notes:
            print(f"  {note_name}")
            self.audio_player.play_note(freq, duration=0.5, volume=0.3)
            time.sleep(0.1)
    
    def _play_victory_sequence(self, scale_notes: List[Tuple[str, float]], 
                              out_of_tune_index: int, out_of_tune_freq: float) -> None:
        """Play the actual sequence that was played, then show the correction"""
        print("\n🎉 Victory! Here's what you heard:")
        
        for i, (note_name, correct_freq) in enumerate(scale_notes):
            if i == out_of_tune_index:
                # Play the out-of-tune note that was actually played (normal speed)
                print(f"  {note_name} (out of tune)")
                self.audio_player.play_note(out_of_tune_freq, duration=0.5, volume=0.3)
                time.sleep(0.1)
                # Immediately play the corrected note (normal speed)
                print(f"  {note_name} (correct)")
                self.audio_player.play_note(correct_freq, duration=0.5, volume=0.3)
                time.sleep(0.1)
            else:
                # Play regular notes twice as fast
                print(f"  {note_name}")
                self.audio_player.play_note(correct_freq, duration=0.25, volume=0.3)
                time.sleep(0.05)
    
    def run_game(self) -> None:
        """Run the scale detection game"""
        print("🎻 Welcome to Scale Detective!")
        print("=" * 40)
        print("I'll play an A major scale, one note at a time.")
        print("One note will be out of tune by", self.out_of_tune_cents, "cents.")
        print("After each note, press:")
        print("  Enter = 'OK' (note sounds in tune)")
        print("  Z = 'Out of tune' (note sounds wrong)")
        print()
        
        # Select which note will be out of tune (not the first A)
        out_of_tune_index = random.randint(1, len(self.a_major_scale) - 1)
        out_of_tune_note, correct_freq = self.a_major_scale[out_of_tune_index]
        
        # Randomly decide if the note will be sharp (high) or flat (low)
        is_sharp = random.choice([True, False])
        cents_off = self.out_of_tune_cents if is_sharp else -self.out_of_tune_cents
        out_of_tune_freq = self._make_note_out_of_tune(correct_freq, cents_off)
        
        input("Press Enter to start...")
        print()
        
        # Play the scale one note at a time
        for i, (note_name, freq) in enumerate(self.a_major_scale):
            # Use out-of-tune frequency if this is the target note
            play_freq = out_of_tune_freq if i == out_of_tune_index else freq
            
            print(f"Note {i + 1}")
            
            # Play note without blocking and check for keypresses
            self.audio_player.play_note_non_blocking(play_freq, duration=1.0, volume=0.3)
            
            # Wait for either the note to finish or a keypress
            start_time = time.time()
            user_input = None
            
            while time.time() - start_time < 1.0 and user_input is None:
                # Check if note is still playing
                if not self.audio_player.is_note_playing():
                    break
                    
                # Check for keypress
                user_input = self.audio_player.check_for_keypress()
                if user_input:
                    # Stop the note immediately
                    self.audio_player.stop_current_note()
                    break
                    
                # Small delay to avoid busy waiting
                time.sleep(0.01)
            
            # If no key was pressed during playback, wait for input after note finishes
            if user_input is None:
                if self.hard_mode:
                    print("Press: ↑ (too high), ↓ (too low), Enter (in tune)")
                    user_input = self._get_key_press()
                else:
                    print("Press: / (out of tune), Enter (in tune)")
                    user_input = self._get_key_press()
            
            # Check the response
            if self.hard_mode:
                # Hard mode: require direction detection
                if user_input in ['up', 'down']:  # User said out of tune
                    if i == out_of_tune_index:  # Correctly identified out-of-tune note
                        # Check if they got the direction right
                        if (user_input == 'up' and is_sharp) or (user_input == 'down' and not is_sharp):
                            print("🎉 Well done! You found the out-of-tune note and got the direction right!")
                            self._play_victory_sequence(self.a_major_scale, out_of_tune_index, out_of_tune_freq)
                            print("\nGreat work! Keep training your ear! 🎵")
                            return
                        else:
                            print("❌ GAME OVER! You found the out-of-tune note but got the direction wrong.")
                            print(f"The {out_of_tune_note} was {'sharp' if is_sharp else 'flat'} by {self.out_of_tune_cents} cents.")
                            self._play_scale_with_correction(self.a_major_scale, out_of_tune_index, out_of_tune_freq)
                            print("\nKeep practicing! Your ear will get stronger! 🎵")
                            return
                    else:  # Incorrectly said in-tune note was out of tune
                        print("❌ Not quite right. That note was actually in tune.")
                        if i < len(self.a_major_scale) - 1:
                            print("Let's continue...")
                            print()
                else:  # User said in tune (Enter)
                    if i == out_of_tune_index:  # Missed the out-of-tune note
                        print("❌ GAME OVER! You missed the out-of-tune note.")
                        print(f"The {out_of_tune_note} was {'sharp' if is_sharp else 'flat'} by {self.out_of_tune_cents} cents.")
                        self._play_scale_with_correction(self.a_major_scale, out_of_tune_index, out_of_tune_freq)
                        print("\nKeep practicing! Your ear will get stronger! 🎵")
                        return
                    else:  # Correctly said in-tune note was OK
                        print("✅ Correct! That note was in tune.")
                        if i < len(self.a_major_scale) - 1:
                            print("Let's continue...")
                            print()
            else:
                # Easy mode: just detect if out of tune
                if user_input == '/':  # User said out of tune
                    if i == out_of_tune_index:  # Correctly identified out-of-tune note
                        print("🎉 Well done! You found the out-of-tune note!")
                        self._play_victory_sequence(self.a_major_scale, out_of_tune_index, out_of_tune_freq)
                        print("\nGreat work! Keep training your ear! 🎵")
                        return
                    else:  # Incorrectly said in-tune note was out of tune
                        print("❌ Not quite right. That note was actually in tune.")
                        if i < len(self.a_major_scale) - 1:
                            print("Let's continue...")
                            print()
                else:  # User said in tune (Enter)
                    if i == out_of_tune_index:  # Missed the out-of-tune note
                        print("❌ GAME OVER! You missed the out-of-tune note.")
                        print(f"The {out_of_tune_note} was {'sharp' if is_sharp else 'flat'} by {self.out_of_tune_cents} cents.")
                        self._play_scale_with_correction(self.a_major_scale, out_of_tune_index, out_of_tune_freq)
                        print("\nKeep practicing! Your ear will get stronger! 🎵")
                        return
                    else:  # Correctly said in-tune note was OK
                        print("✅ Correct! That note was in tune.")
                        if i < len(self.a_major_scale) - 1:
                            print("Let's continue...")
                            print()
        
        # If we get here, they went through the whole scale without finding it
        print("❌ GAME OVER! You went through the whole scale without finding the out-of-tune note.")
        print(f"The {out_of_tune_note} was {'sharp' if is_sharp else 'flat'} by {self.out_of_tune_cents} cents.")
        self._play_scale_with_correction(self.a_major_scale, out_of_tune_index, out_of_tune_freq)
        print("\nKeep practicing! Your ear will get stronger! 🎵") 
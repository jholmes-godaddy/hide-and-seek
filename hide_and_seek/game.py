"""
Main game logic for Hide and Seek ear training
"""

import random
import time
from typing import List, Tuple, Optional
from .notes import get_violin_range_notes
from .audio import AudioPlayer

class HideAndSeekGame:
    """Main game class for the ear training app"""
    
    def __init__(self, tolerance_cents: float = 50.0):
        self.audio_player = AudioPlayer()
        self.tolerance_cents = tolerance_cents
        self.available_notes = get_violin_range_notes()
        self.score = 0
        self.total_attempts = 0
        
    def select_random_notes(self, count: int) -> List[Tuple[str, float]]:
        """
        Select a random set of notes for the game.
        
        Args:
            count: Number of notes to select
            
        Returns:
            List of (note_name, frequency) tuples
        """
        return random.sample(self.available_notes, min(count, len(self.available_notes)))
    
    def play_celebration(self) -> None:
        """Play a celebration sound when the game is completed"""
        print("\n🎉🎉🎉 CONGRATULATIONS! 🎉🎉🎉")
        print("You found all the hidden notes!")
        print("🎵🎵🎵🎵🎵🎵🎵🎵🎵🎵🎵🎵🎵🎵🎵🎵")
        
        # Play a little celebration melody
        celebration_notes = [440.0, 493.9, 523.3, 587.3, 659.3]  # A, B, C, D, E
        for freq in celebration_notes:
            self.audio_player.play_note(freq, duration=0.3, volume=0.2)
            time.sleep(0.1)
        
        # Play the sequence backwards
        for freq in reversed(celebration_notes):
            self.audio_player.play_note(freq, duration=0.3, volume=0.2)
            time.sleep(0.1)
    
    def play_note_sequence(self, notes: List[Tuple[str, float]]) -> None:
        """
        Play a sequence of notes to introduce the game.
        
        Args:
            notes: List of (note_name, frequency) tuples
        """
        print("\n🎵 Let's play Hide and Seek with these notes:")
        for i, (note_name, freq) in enumerate(notes, 1):
            print(f"  {i}. {note_name} ({freq:.1f} Hz)")
            self.audio_player.play_note(freq, duration=1.0, volume=0.2)
            time.sleep(0.5)
        
        print("\nNow I'll hide one note at a time. Listen carefully and try to match it!")
        time.sleep(2)
    
    def play_single_note(self, note_name: str, frequency: float) -> bool:
        """
        Play a single note and listen for the response.
        
        Args:
            note_name: Name of the note
            frequency: Frequency of the note
            
        Returns:
            True if the correct note was played back
        """
        print(f"\n🎵 Playing: {note_name}")
        self.audio_player.play_note(frequency, duration=2.0, volume=0.3)
        
        # Listen for the response
        success, detected_freq = self.audio_player.listen_for_note(
            frequency, duration=3.0, tolerance_cents=self.tolerance_cents
        )
        
        self.total_attempts += 1
        
        if success:
            self.score += 1
            print("✅ Perfect! You found the hidden note!")
        else:
            print("❌ Not quite right. Let me play it again...")
            # Play the note again
            self.audio_player.play_note(frequency, duration=2.0, volume=0.3)
            
            # Give another chance
            print("Try again:")
            success, detected_freq = self.audio_player.listen_for_note(
                frequency, duration=3.0, tolerance_cents=self.tolerance_cents
            )
            
            self.total_attempts += 1
            if success:
                self.score += 1
                print("✅ Great! You got it on the second try!")
            else:
                print("❌ Let's move on to the next note...")
        
        return success
    
    def run_game(self, num_notes: int = 3) -> None:
        """
        Run the complete hide and seek game.
        
        Args:
            num_notes: Number of notes to play in the game
        """
        print("🎻 Welcome to Hide and Seek - Ear Training for Violin!")
        print("=" * 50)
        
        # Select random notes
        selected_notes = self.select_random_notes(num_notes)
        
        # Introduce the notes
        self.play_note_sequence(selected_notes)
        
        # Play the game
        successful_notes = 0
        for note_name, frequency in selected_notes:
            if self.play_single_note(note_name, frequency):
                successful_notes += 1
        
        # Show results
        print(f"\n🎯 Game Results:")
        print(f"   Notes found: {successful_notes}/{num_notes}")
        print(f"   Total attempts: {self.total_attempts}")
        print(f"   Success rate: {(successful_notes/num_notes)*100:.1f}%")
        
        # Celebration if all notes were found
        if successful_notes == num_notes:
            self.play_celebration()
        else:
            print(f"\nGood job! You found {successful_notes} out of {num_notes} notes.")
            print("Keep practicing and you'll get better!")
        
        print("\nThanks for playing Hide and Seek! 🎵") 
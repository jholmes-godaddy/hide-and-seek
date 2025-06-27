"""
Main game logic for Hide and Seek ear training
"""

import random
import time
from typing import List, Tuple, Optional
from .notes import get_violin_range_notes
from .audio import AudioPlayer
import numpy as np
import sounddevice as sd

class HideAndSeekGame:
    """Main game class for the ear training app"""
    
    def __init__(self, tolerance_cents: float = 50.0, debug: bool = False):
        self.audio_player = AudioPlayer()
        self.tolerance_cents = tolerance_cents
        self.debug = debug
        self.available_notes = get_violin_range_notes()
        self.score = 0
        self.total_attempts = 0
        
    def select_random_notes(self, count: int) -> List[Tuple[str, float]]:
        """
        Select a random set of distinct notes for the game.
        
        Args:
            count: Number of distinct notes to select
            
        Returns:
            List of (note_name, frequency) tuples
        """
        return random.sample(self.available_notes, min(count, len(self.available_notes)))
    
    def generate_note_sequence(self, distinct_notes: List[Tuple[str, float]], sequence_length: int) -> List[Tuple[str, float]]:
        """
        Generate a random sequence of notes that can include repetition but never the same note twice in a row.
        
        Args:
            distinct_notes: List of available distinct notes
            sequence_length: Length of the sequence to generate
            
        Returns:
            List of (note_name, frequency) tuples for the sequence
        """
        if sequence_length == 0:
            return []
        
        if len(distinct_notes) == 1:
            # If only one distinct note, we can't avoid repetition
            return [distinct_notes[0]] * sequence_length
        
        sequence = []
        last_note = None
        
        for _ in range(sequence_length):
            # Filter out the last note to avoid consecutive repeats
            available_notes = [note for note in distinct_notes if note != last_note]
            selected_note = random.choice(available_notes)
            sequence.append(selected_note)
            last_note = selected_note
        
        return sequence
    
    def play_celebration(self) -> None:
        """Play a celebration sound when the game is completed"""
        print("\n🎉🎉🎉 CONGRATULATIONS! 🎉🎉🎉")
        print("You found all the hidden notes!")
        print("🎵🎵🎵🎵🎵🎵🎵🎵🎵🎵🎵🎵🎵🎵🎵🎵")
        
        # Play the celebration melody: A B C# D E E E E F# D A(high) F# E(long)
        celebration_notes = [
            (440.0, 0.1),    # A4
            (493.9, 0.1),    # B4
            (554.4, 0.1),    # C#5
            (587.3, 0.1),    # D5
            (659.3, 0.1),    # E5
            (659.3, 0.1),    # E5
            (659.3, 0.1),    # E5
            (659.3, 0.1),    # E5
            (740.0, 0.1),    # F#5
            (587.3, 0.1),    # D5
            (880.0, 0.1),    # A5 (high)
            (740.0, 0.1),    # F#5
            (659.3, 0.5),    # E5 (long)
        ]
        
        for freq, duration in celebration_notes:
            self.audio_player.play_note(freq, duration=duration, volume=0.2)
            time.sleep(0.1)
        
        print("\n🎵 You've mastered the A major scale! 🎵")
        time.sleep(1)
        
        # Play cheering/applause sound
        print("👏👏👏👏👏👏👏👏👏👏👏👏👏👏👏👏")
        self.play_cheering_sound()
    
    def play_cheering_sound(self) -> None:
        """Play a cheering/applause sound effect"""
        # Create a cheering sound using multiple overlapping frequencies
        # that simulate the sound of many people clapping
        cheering_frequencies = [
            800, 1200, 1600, 2000, 2400, 2800, 3200, 3600, 4000
        ]
        
        duration = 2.0
        sample_rate = self.audio_player.sample_rate
        
        # Generate cheering sound with random variations
        # Create the base cheering sound
        t = np.linspace(0, duration, int(sample_rate * duration), False)
        cheering_sound = np.zeros_like(t)
        
        # Add multiple frequencies with random phases and amplitudes
        for freq in cheering_frequencies:
            # Random phase
            phase = np.random.random() * 2 * np.pi
            # Random amplitude (stronger for lower frequencies)
            amplitude = np.random.random() * 0.1 * (4000 / freq)
            # Add this frequency component
            cheering_sound += amplitude * np.sin(2 * np.pi * freq * t + phase)
        
        # Add some noise to make it sound more realistic
        noise = np.random.normal(0, 0.05, len(cheering_sound))
        cheering_sound += noise
        
        # Apply envelope to make it fade in and out
        envelope = np.ones_like(cheering_sound)
        fade_samples = int(0.1 * sample_rate)  # 0.1 second fade
        envelope[:fade_samples] = np.linspace(0, 1, fade_samples)
        envelope[-fade_samples:] = np.linspace(1, 0, fade_samples)
        
        cheering_sound *= envelope
        
        # Normalize and play
        cheering_sound = cheering_sound * 0.3  # Reduce volume
        sd.play(cheering_sound, sample_rate)
        sd.wait()
    
    def play_note_sequence(self, notes: List[Tuple[str, float]]) -> None:
        """
        Play a sequence of notes to introduce the game.
        
        Args:
            notes: List of (note_name, frequency) tuples
        """
        print("\n🎵 Let's learn these notes:")
        for i, (note_name, freq) in enumerate(notes, 1):
            print(f"  {i}. {note_name} ({freq:.1f} Hz)")
            self.audio_player.play_note(freq, duration=1.0, volume=0.2)
            time.sleep(0.5)
        
        print("\nNow I'll play them one at a time. Get ready!")
        input("Press Enter when you're ready to hear the notes...")
        
        for i, (note_name, freq) in enumerate(notes, 1):
            print(f"\nPlaying note {i}: {note_name}")
            self.audio_player.play_note(freq, duration=2.0, volume=0.3)
            if i < len(notes):  # Don't wait after the last note
                input("Press Enter for the next note...")
        
        print("\nNow I'll hide one note at a time. Listen carefully and try to match it!")
        time.sleep(2)
    
    def play_single_note(self, note_name: str, frequency: float) -> bool:
        """
        Play a single note and listen for the response.
        Keep trying until the correct note is played.
        
        Args:
            note_name: Name of the note
            frequency: Frequency of the note
            
        Returns:
            True when the correct note was played back
        """
        attempts = 0
        
        while True:
            attempts += 1
            print(f"\n🎵 Playing: {note_name} (attempt {attempts})")
            self.audio_player.play_note(frequency, duration=2.0, volume=0.3)
            
            # Listen for the response
            success, detected_freq = self.audio_player.listen_for_note(
                frequency, duration=3.0, tolerance_cents=self.tolerance_cents, debug=self.debug
            )
            
            self.total_attempts += 1
            
            if success:
                self.score += 1
                if attempts == 1:
                    print("✅ Perfect! You found the hidden note!")
                else:
                    print(f"✅ Great! You found the hidden note after {attempts} attempts!")
                
                # Play water drop sound for correct pitch
                self.audio_player.play_water_drop_sound()
                
                return True
            else:
                print("❌ Not quite right. Let me play it again...")
                # The note will be played again in the next iteration of the loop
    
    def run_game(self, num_distinct_notes: int = 3, sequence_length: int = 8) -> None:
        """
        Run the complete hide and seek game.
        
        Args:
            num_distinct_notes: Number of distinct notes to choose from
            sequence_length: Number of notes to play in the sequence (can repeat)
        """
        print("🎻 Welcome to Hide and Seek - Ear Training for Violin!")
        print("=" * 50)
        
        # Select random distinct notes
        distinct_notes = self.select_random_notes(num_distinct_notes)
        
        # Generate the sequence (can include repetition)
        note_sequence = self.generate_note_sequence(distinct_notes, sequence_length)
        
        # Introduce the distinct notes
        self.play_note_sequence(distinct_notes)
        
        print(f"\nNow I'll play {sequence_length} notes in random order (some may repeat)!")
        input("Press Enter when you're ready to start...")
        
        # Play the game
        successful_notes = 0
        for note_name, frequency in note_sequence:
            if self.play_single_note(note_name, frequency):
                successful_notes += 1
        
        # Show results
        print(f"\n🎯 Game Results:")
        print(f"   Notes found: {successful_notes}/{sequence_length}")
        print(f"   Total attempts: {self.total_attempts}")
        print(f"   Success rate: {(successful_notes/sequence_length)*100:.1f}%")
        
        # Celebration if all notes were found
        if successful_notes == sequence_length:
            self.play_celebration()
        else:
            print(f"\nGood job! You found {successful_notes} out of {sequence_length} notes.")
            print("Keep practicing and you'll get better!")
        
        print("\nThanks for playing Hide and Seek! 🎵") 
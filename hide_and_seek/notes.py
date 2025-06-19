"""
Violin note definitions and utilities
"""

from typing import List, Dict, Tuple
import numpy as np

# Violin string frequencies (open strings)
VIOLIN_STRINGS = {
    'G': 196.0,  # G3
    'D': 293.7,  # D4
    'A': 440.0,  # A4
    'E': 659.3,  # E5
}

# Note names in order
NOTE_NAMES = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']

def get_note_frequency(note_name: str, octave: int = 4) -> float:
    """
    Calculate frequency for a given note name and octave.
    
    Args:
        note_name: Note name (e.g., 'A', 'C#')
        octave: Octave number (4 is middle C)
    
    Returns:
        Frequency in Hz
    """
    # Find the note index (0-11)
    note_index = NOTE_NAMES.index(note_name)
    
    # Calculate frequency using A4 = 440Hz as reference
    # A4 is at index 9 in our note array
    semitones_from_a4 = note_index - 9 + (octave - 4) * 12
    
    # Calculate frequency using the formula: f = f0 * 2^(n/12)
    frequency = 440.0 * (2 ** (semitones_from_a4 / 12))
    
    return frequency

def get_violin_range_notes() -> List[Tuple[str, float]]:
    """
    Get notes from A major scale between 440 Hz (A4) and 880 Hz (A5).
    
    A major scale: A, B, C#, D, E, F#, G#
    
    Returns:
        List of (note_name, frequency) tuples
    """
    notes = []
    
    # A major scale notes - only those 440 Hz and above
    a_major_scale_notes = [
        ('A4', 440.0),      # A4 - 440 Hz
        ('B4', get_note_frequency('B', 4)),      # B4 - ~493.9 Hz
        ('C#5', get_note_frequency('C#', 5)),    # C#5 - ~554.4 Hz
        ('D5', get_note_frequency('D', 5)),      # D5 - ~587.3 Hz
        ('E5', get_note_frequency('E', 5)),      # E5 - ~659.3 Hz
        ('F#5', get_note_frequency('F#', 5)),    # F#5 - ~740.0 Hz
        ('G#5', get_note_frequency('G#', 5)),    # G#5 - ~830.6 Hz
        ('A5', get_note_frequency('A', 5)),      # A5 - 880 Hz
    ]
    
    # Add all notes
    notes.extend(a_major_scale_notes)
    
    return notes

def generate_sine_wave(frequency: float, duration: float, sample_rate: int = 44100) -> np.ndarray:
    """
    Generate a sine wave for a given frequency and duration.
    
    Args:
        frequency: Frequency in Hz
        duration: Duration in seconds
        sample_rate: Sample rate in Hz
    
    Returns:
        Audio samples as numpy array
    """
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    return np.sin(2 * np.pi * frequency * t)

def is_note_close(frequency1: float, frequency2: float, tolerance_cents: float = 50.0) -> bool:
    """
    Check if two frequencies are close enough (within tolerance in cents).
    
    Args:
        frequency1: First frequency in Hz
        frequency2: Second frequency in Hz
        tolerance_cents: Tolerance in cents (1 semitone = 100 cents)
    
    Returns:
        True if frequencies are within tolerance
    """
    if frequency1 <= 0 or frequency2 <= 0:
        return False
    
    # Calculate cents difference
    cents_diff = 1200 * np.log2(frequency2 / frequency1)
    return abs(cents_diff) <= tolerance_cents 
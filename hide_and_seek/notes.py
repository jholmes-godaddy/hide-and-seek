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
    Get all notes in violin range from open A to A on E string.
    
    Returns:
        List of (note_name, frequency) tuples
    """
    notes = []
    
    # Open A string (A4)
    notes.append(('A4', 440.0))
    
    # Notes on A string
    notes.append(('A#4', get_note_frequency('A#', 4)))
    notes.append(('B4', get_note_frequency('B', 4)))
    
    # Notes on D string
    notes.append(('D4', 293.7))
    notes.append(('D#4', get_note_frequency('D#', 4)))
    notes.append(('E4', 329.6))
    notes.append(('F4', get_note_frequency('F', 4)))
    notes.append(('F#4', get_note_frequency('F#', 4)))
    notes.append(('G4', 392.0))
    notes.append(('G#4', get_note_frequency('G#', 4)))
    notes.append(('A4', 440.0))  # Already added, but for completeness
    
    # Notes on E string
    notes.append(('E5', 659.3))
    notes.append(('F5', get_note_frequency('F', 5)))
    notes.append(('F#5', get_note_frequency('F#', 5)))
    notes.append(('G5', get_note_frequency('G', 5)))
    notes.append(('G#5', get_note_frequency('G#', 5)))
    notes.append(('A5', get_note_frequency('A', 5)))
    
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
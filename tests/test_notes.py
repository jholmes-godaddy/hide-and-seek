"""
Tests for the notes module
"""

import pytest
import numpy as np
from hide_and_seek.notes import (
    get_note_frequency,
    get_violin_range_notes,
    generate_sine_wave,
    is_note_close
)

def test_get_note_frequency():
    """Test frequency calculation for various notes"""
    # Test A4 (should be 440 Hz)
    assert abs(get_note_frequency('A', 4) - 440.0) < 0.1
    
    # Test C4 (middle C)
    assert abs(get_note_frequency('C', 4) - 261.6) < 0.1
    
    # Test E5 (should be 659.3 Hz)
    assert abs(get_note_frequency('E', 5) - 659.3) < 0.1

def test_get_violin_range_notes():
    """Test that violin range notes are returned"""
    notes = get_violin_range_notes()
    
    # Should have multiple notes
    assert len(notes) > 0
    
    # Should be tuples of (note_name, frequency)
    for note_name, frequency in notes:
        assert isinstance(note_name, str)
        assert isinstance(frequency, float)
        assert frequency > 0

def test_generate_sine_wave():
    """Test sine wave generation"""
    freq = 440.0
    duration = 1.0
    sample_rate = 44100
    
    wave = generate_sine_wave(freq, duration, sample_rate)
    
    # Should have correct length
    expected_length = int(sample_rate * duration)
    assert len(wave) == expected_length
    
    # Should be numpy array
    assert isinstance(wave, np.ndarray)
    
    # Should have reasonable amplitude
    assert np.max(np.abs(wave)) <= 1.0

def test_is_note_close():
    """Test note closeness detection"""
    # Same frequency should be close
    assert is_note_close(440.0, 440.0)
    
    # Very close frequencies should be close
    assert is_note_close(440.0, 441.0)
    
    # Different frequencies should not be close
    assert not is_note_close(440.0, 880.0)
    
    # Test with custom tolerance
    assert is_note_close(440.0, 450.0, tolerance_cents=100.0)
    assert not is_note_close(440.0, 450.0, tolerance_cents=10.0)
    
    # Invalid frequencies should return False
    assert not is_note_close(0.0, 440.0)
    assert not is_note_close(440.0, -1.0) 
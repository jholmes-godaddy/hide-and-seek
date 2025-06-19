"""
Audio playback and recording utilities
"""

import numpy as np
import sounddevice as sd
import soundfile as sf
from typing import Optional, Tuple
import librosa
from .notes import is_note_close

class AudioPlayer:
    """Handles audio playback and recording"""
    
    def __init__(self, sample_rate: int = 44100):
        self.sample_rate = sample_rate
        
    def play_note(self, frequency: float, duration: float = 2.0, volume: float = 0.3) -> None:
        """
        Play a note at the given frequency.
        
        Args:
            frequency: Frequency in Hz
            duration: Duration in seconds
            volume: Volume level (0.0 to 1.0)
        """
        from .notes import generate_sine_wave
        
        # Generate the sine wave
        audio = generate_sine_wave(frequency, duration, self.sample_rate)
        
        # Apply volume
        audio = audio * volume
        
        # Play the audio
        sd.play(audio, self.sample_rate)
        sd.wait()  # Wait until audio is finished playing
        
    def record_audio(self, duration: float = 3.0) -> np.ndarray:
        """
        Record audio for the specified duration.
        
        Args:
            duration: Recording duration in seconds
            
        Returns:
            Recorded audio as numpy array
        """
        print(f"Recording for {duration} seconds... Speak or play now!")
        
        # Record audio
        audio = sd.rec(int(duration * self.sample_rate), 
                      samplerate=self.sample_rate, 
                      channels=1)
        sd.wait()  # Wait until recording is finished
        
        return audio.flatten()
    
    def detect_pitch(self, audio: np.ndarray, min_freq: float = 200.0, max_freq: float = 800.0) -> Optional[float]:
        """
        Detect the fundamental frequency (pitch) of the recorded audio.
        
        Args:
            audio: Audio samples as numpy array
            min_freq: Minimum frequency to detect (Hz)
            max_freq: Maximum frequency to detect (Hz)
            
        Returns:
            Detected frequency in Hz, or None if no clear pitch detected
        """
        if len(audio) == 0:
            return None
            
        # Use librosa to detect pitch
        try:
            # Extract pitch using librosa
            pitches, magnitudes = librosa.piptrack(y=audio, sr=self.sample_rate, 
                                                 fmin=min_freq, fmax=max_freq)
            
            # Find the pitch with the highest magnitude
            max_magnitude_idx = np.argmax(magnitudes)
            pitch = pitches[max_magnitude_idx // magnitudes.shape[1], max_magnitude_idx % magnitudes.shape[1]]
            
            # Only return if we have a valid pitch
            if pitch > 0 and min_freq <= pitch <= max_freq:
                return float(pitch)
            else:
                return None
                
        except Exception as e:
            print(f"Error detecting pitch: {e}")
            return None
    
    def listen_for_note(self, target_frequency: float, duration: float = 3.0, 
                       tolerance_cents: float = 50.0) -> Tuple[bool, Optional[float]]:
        """
        Listen for a note and check if it matches the target frequency.
        
        Args:
            target_frequency: Expected frequency in Hz
            duration: Recording duration in seconds
            tolerance_cents: Tolerance in cents
            
        Returns:
            Tuple of (success, detected_frequency)
        """
        # Record audio
        audio = self.record_audio(duration)
        
        # Detect pitch
        detected_freq = self.detect_pitch(audio)
        
        if detected_freq is None:
            print("No clear pitch detected. Please try again!")
            return False, None
        
        # Check if the detected frequency is close enough
        is_close = is_note_close(target_frequency, detected_freq, tolerance_cents)
        
        if is_close:
            print(f"Great! Detected {detected_freq:.1f} Hz (target: {target_frequency:.1f} Hz)")
        else:
            print(f"Detected {detected_freq:.1f} Hz, but target was {target_frequency:.1f} Hz")
            
        return is_close, detected_freq 
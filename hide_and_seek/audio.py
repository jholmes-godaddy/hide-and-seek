"""
Audio playback and recording utilities
"""

import numpy as np
import sounddevice as sd
import soundfile as sf
import threading
import time
from typing import Optional, Tuple
from scipy import signal
from .notes import is_note_close

class AudioPlayer:
    """Handles audio playback and recording"""
    
    def __init__(self, sample_rate: int = 44100):
        self.sample_rate = sample_rate
        self._current_stream = None
        self._is_playing = False
        
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
        
    def play_note_non_blocking(self, frequency: float, duration: float = 2.0, volume: float = 0.3) -> None:
        """
        Play a note without blocking. Can be stopped with stop_current_note().
        
        Args:
            frequency: Frequency in Hz
            duration: Duration in seconds
            volume: Volume level (0.0 to 1.0)
        """
        from .notes import generate_sine_wave
        
        # Stop any currently playing note
        self.stop_current_note()
        
        # Generate the sine wave
        audio = generate_sine_wave(frequency, duration, self.sample_rate)
        
        # Apply volume
        audio = audio * volume
        
        # Play the audio without waiting
        self._current_stream = sd.play(audio, self.sample_rate)
        self._is_playing = True
        
    def stop_current_note(self) -> None:
        """Stop the currently playing note if any"""
        if self._is_playing and self._current_stream is not None:
            sd.stop()
            self._is_playing = False
            self._current_stream = None
            
    def is_note_playing(self) -> bool:
        """Check if a note is currently playing"""
        return self._is_playing
        
    def check_for_keypress(self) -> Optional[str]:
        """
        Check for a keypress without blocking. Returns the key if pressed, None otherwise.
        This is a non-blocking version of _get_key_press.
        """
        import sys
        import tty
        import termios
        import select
        
        # Check if there's input available
        if select.select([sys.stdin], [], [], 0)[0]:
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
        return None

    def record_audio(self, duration: float = 3.0) -> np.ndarray:
        """
        Record audio for the specified duration.
        
        Args:
            duration: Recording duration in seconds
            
        Returns:
            Recorded audio as numpy array
        """
        print(f"Recording for {duration} seconds... Speak or play now!")
        
        # Play click sound to indicate recording start
        self.play_click_sound()
        
        # Record audio
        audio = sd.rec(int(duration * self.sample_rate), 
                      samplerate=self.sample_rate, 
                      channels=1)
        sd.wait()  # Wait until recording is finished
        
        return audio.flatten()
    
    def detect_pitch(self, audio: np.ndarray, min_freq: float = 200.0, max_freq: float = 900.0, debug: bool = False) -> Optional[float]:
        """
        Detect the fundamental frequency (pitch) using FFT-based analysis.
        Optimized for violin notes with harmonic correction.
        
        Args:
            audio: Audio samples as numpy array
            min_freq: Minimum frequency to detect (Hz)
            max_freq: Maximum frequency to detect (Hz)
            debug: If True, print debug information
            
        Returns:
            Detected frequency in Hz, or None if no clear pitch detected
        """
        if len(audio) == 0:
            return None
            
        try:
            # Use a larger window for better frequency resolution
            # Pad the audio to ensure we have enough samples
            target_length = 8192  # Larger FFT for better resolution
            if len(audio) < target_length:
                # Pad with zeros if audio is too short
                padded_audio = np.pad(audio, (0, target_length - len(audio)), 'constant')
            else:
                # Take the middle portion if audio is longer
                start = len(audio) // 2 - target_length // 2
                padded_audio = audio[start:start + target_length]
            
            # Apply a window function to reduce spectral leakage
            window = signal.windows.hann(len(padded_audio))
            audio_windowed = padded_audio * window
            
            # Compute FFT
            fft = np.fft.rfft(audio_windowed)
            freqs = np.fft.rfftfreq(len(padded_audio), 1.0 / self.sample_rate)
            
            # Get magnitude spectrum
            magnitude = np.abs(fft)
            
            # Find frequency range of interest (extend range for harmonic detection)
            extended_min_freq = min_freq * 0.5  # Allow detection of lower harmonics
            extended_max_freq = max_freq * 2.0   # Allow detection of higher harmonics
            freq_mask = (freqs >= extended_min_freq) & (freqs <= extended_max_freq)
            freqs_of_interest = freqs[freq_mask]
            magnitude_of_interest = magnitude[freq_mask]
            
            if debug:
                print(f"Debug: Audio length: {len(audio)}, Padded length: {len(padded_audio)}")
                print(f"Debug: Frequency range: {extended_min_freq:.1f} - {extended_max_freq:.1f} Hz")
                print(f"Debug: Max magnitude: {np.max(magnitude_of_interest):.2f}")
            
            if len(freqs_of_interest) == 0:
                return None
            
            # Find peaks in the magnitude spectrum with more lenient threshold
            peaks, properties = signal.find_peaks(
                magnitude_of_interest, 
                height=np.max(magnitude_of_interest) * 0.05,  # Lower threshold
                distance=10  # Minimum distance between peaks
            )
            
            if debug:
                print(f"Debug: Found {len(peaks)} peaks")
                for i, peak_idx in enumerate(peaks[:5]):  # Show top 5 peaks
                    freq = freqs_of_interest[peak_idx]
                    mag = magnitude_of_interest[peak_idx]
                    print(f"Debug: Peak {i+1}: {freq:.1f} Hz, magnitude: {mag:.2f}")
            
            if len(peaks) == 0:
                return None
            
            # Sort peaks by magnitude (highest first)
            peak_magnitudes = magnitude_of_interest[peaks]
            sorted_indices = np.argsort(peak_magnitudes)[::-1]
            sorted_peaks = peaks[sorted_indices]
            
            # Check each peak, starting with the strongest
            for peak_idx in sorted_peaks:
                detected_freq = freqs_of_interest[peak_idx]
                peak_magnitude = magnitude_of_interest[peak_idx]
                avg_magnitude = np.mean(magnitude_of_interest)
                
                if debug:
                    print(f"Debug: Checking peak at {detected_freq:.1f} Hz, magnitude: {peak_magnitude:.2f}, avg: {avg_magnitude:.2f}")
                
                # Only consider peaks significantly above the average
                if peak_magnitude < avg_magnitude * 1.5:
                    if debug:
                        print(f"Debug: Peak too weak, skipping")
                    continue
                
                # Check if this frequency is in our target range
                if min_freq <= detected_freq <= max_freq:
                    if debug:
                        print(f"Debug: Found valid frequency: {detected_freq:.1f} Hz")
                    return float(detected_freq)
                
                # Harmonic correction: check if this is half the target frequency
                # This handles cases where the fundamental is weak but the first harmonic is strong
                for target_freq in [440.0, 493.9, 554.4, 587.3, 659.3, 740.0, 830.6, 880.0]:  # Our A major scale
                    if abs(detected_freq - target_freq/2) < 10:  # Within 10 Hz of half frequency
                        # Check if the second harmonic (target_freq) is also present
                        harmonic_idx = np.argmin(np.abs(freqs_of_interest - target_freq))
                        if harmonic_idx < len(magnitude_of_interest):
                            harmonic_magnitude = magnitude_of_interest[harmonic_idx]
                            if debug:
                                print(f"Debug: Potential harmonic: {detected_freq:.1f} Hz -> {target_freq:.1f} Hz, harmonic magnitude: {harmonic_magnitude:.2f}")
                            # If the harmonic is also strong, return the target frequency
                            if harmonic_magnitude > avg_magnitude * 1.0:
                                if debug:
                                    print(f"Debug: Harmonic correction applied: {target_freq:.1f} Hz")
                                return float(target_freq)
                
                # If we're looking for high notes (like A5 = 880 Hz) and detect a lower frequency
                # that's close to half the target, it might be an octave error
                if detected_freq < max_freq * 0.6:  # If detected frequency is much lower
                    for target_freq in [740.0, 830.6, 880.0]:  # High notes in our scale
                        if abs(detected_freq - target_freq/2) < 20:  # Within 20 Hz of half
                            # Check if the target frequency has a strong peak
                            target_idx = np.argmin(np.abs(freqs_of_interest - target_freq))
                            if target_idx < len(magnitude_of_interest):
                                target_magnitude = magnitude_of_interest[target_idx]
                                if debug:
                                    print(f"Debug: Octave error check: {detected_freq:.1f} Hz -> {target_freq:.1f} Hz, target magnitude: {target_magnitude:.2f}")
                                if target_magnitude > avg_magnitude * 0.8:
                                    if debug:
                                        print(f"Debug: Octave error correction applied: {target_freq:.1f} Hz")
                                    return float(target_freq)
            
            if debug:
                print("Debug: No valid pitch found")
            return None
                
        except Exception as e:
            print(f"Error detecting pitch: {e}")
            return None
    
    def listen_for_note(self, target_frequency: float, duration: float = 3.0, 
                       tolerance_cents: float = 50.0, debug: bool = False) -> Tuple[bool, Optional[float]]:
        """
        Listen for a note and check if it matches the target frequency.
        
        Args:
            target_frequency: Expected frequency in Hz
            duration: Recording duration in seconds
            tolerance_cents: Tolerance in cents
            debug: If True, show detailed pitch detection info
            
        Returns:
            Tuple of (success, detected_frequency)
        """
        # Record audio
        audio = self.record_audio(duration)
        
        # Detect pitch
        detected_freq = self.detect_pitch(audio, debug=debug)
        
        if debug:
            print(f"Debug: Target frequency: {target_frequency:.1f} Hz")
            print(f"Debug: Detected frequency: {detected_freq:.1f} Hz" if detected_freq else "Debug: No pitch detected")
            if detected_freq:
                cents_diff = 1200 * np.log2(detected_freq / target_frequency)
                print(f"Debug: Cents difference: {cents_diff:.1f}")
                print(f"Debug: Within tolerance ({tolerance_cents} cents): {abs(cents_diff) <= tolerance_cents}")
        
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
    
    def play_water_drop_sound(self) -> None:
        """Play a water drop rising and decaying sound for correct pitches"""
        # Create a water drop sound with rising frequency that decays quickly
        duration = 0.4  # Reduced from 0.8 to 0.4 seconds
        sample_rate = self.sample_rate
        
        t = np.linspace(0, duration, int(sample_rate * duration), False)
        
        # Start at a low frequency and rise to a higher frequency
        start_freq = 400  # Hz
        end_freq = 1200   # Hz
        
        # Create a frequency sweep (rising)
        freq_sweep = np.linspace(start_freq, end_freq, len(t))
        
        # Generate the rising tone
        rising_tone = np.sin(2 * np.pi * freq_sweep * t)
        
        # Apply envelope: quick attack, very fast decay
        envelope = np.ones_like(t)
        attack_samples = int(0.05 * sample_rate)  # 0.05 second attack (reduced)
        decay_samples = int(0.35 * sample_rate)   # 0.35 second decay (reduced)
        
        # Quick attack
        envelope[:attack_samples] = np.linspace(0, 1, attack_samples)
        # Very fast decay
        envelope[attack_samples:] = np.exp(-8 * (t[attack_samples:] - t[attack_samples]) / (t[-1] - t[attack_samples]))  # Increased decay rate
        
        # Apply envelope and add some harmonics for richness
        water_drop = rising_tone * envelope
        water_drop += 0.3 * np.sin(2 * np.pi * freq_sweep * 2 * t) * envelope  # Second harmonic
        water_drop += 0.1 * np.sin(2 * np.pi * freq_sweep * 3 * t) * envelope  # Third harmonic
        
        # Normalize and play
        water_drop = water_drop * 0.2  # Reduce volume
        sd.play(water_drop, sample_rate)
        sd.wait()
    
    def play_click_sound(self) -> None:
        """Play a click sound when recording starts"""
        # Create a short click sound using noise
        duration = 0.05  # Very short click
        sample_rate = self.sample_rate
        
        t = np.linspace(0, duration, int(sample_rate * duration), False)
        
        # Create a click using white noise instead of a pitched tone
        click = np.random.normal(0, 1, len(t))
        
        # Apply envelope: very quick attack and decay
        envelope = np.ones_like(t)
        attack_samples = int(0.005 * sample_rate)  # 0.005 second attack
        decay_samples = int(0.045 * sample_rate)   # 0.045 second decay
        
        # Quick attack
        envelope[:attack_samples] = np.linspace(0, 1, attack_samples)
        # Quick decay
        envelope[attack_samples:] = np.exp(-15 * (t[attack_samples:] - t[attack_samples]) / (t[-1] - t[attack_samples]))
        
        # Apply envelope
        click = click * envelope
        
        # Normalize and play
        click = click * 0.1  # Reduce volume
        sd.play(click, sample_rate)
        sd.wait() 
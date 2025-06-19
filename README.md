# Hide and Seek - Ear Training for Violin

A fun ear training app designed for violin students to practice pitch recognition and matching. The app plays notes and listens for your daughter to play them back on her violin!

## Features

- 🎻 **Violin-focused**: Notes are selected from the violin range (open A to A on E string)
- 🎵 **Interactive**: Plays notes and listens for your response
- 🎯 **Adaptive**: Gives second chances and provides feedback
- 🎉 **Celebration**: Special celebration when all notes are found correctly
- 📊 **Progress tracking**: Shows success rate and total attempts

## Requirements

- Python 3.8 or higher
- Microphone for recording violin sounds
- Speakers or headphones for listening to notes
- Poetry (for dependency management)

## Installation

1. **Install Poetry** (if not already installed):
   ```bash
   curl -sSL https://install.python-poetry.org | python3 -
   ```

2. **Clone and install dependencies**:
   ```bash
   cd hide-and-seek
   poetry install
   ```

## Usage

### Basic Game
```bash
poetry run python -m hide_and_seek
```
This starts a game with 3 random notes from the violin range.

### Customize the Game
```bash
# Play with 5 notes
poetry run python -m hide_and_seek -n 5

# Use stricter tolerance (30 cents instead of 50)
poetry run python -m hide_and_seek --tolerance 30

# List all available notes
poetry run python -m hide_and_seek --list-notes
```

### Game Flow

1. **Introduction**: The app plays all the notes you'll need to match
2. **Hide and Seek**: One by one, the app plays a note and waits for you to play it back
3. **Feedback**: You get immediate feedback on whether you matched the note
4. **Second Chance**: If you miss, the app plays the note again and gives you another try
5. **Celebration**: When you find all the notes, you get a special celebration!

## How It Works

### Note Detection
The app uses advanced audio processing to:
- Record your violin playing
- Detect the fundamental frequency (pitch)
- Compare it to the target note
- Allow for some tolerance (default 50 cents, about half a semitone)

### Available Notes
The app includes notes from the violin range:
- **A string**: A4, A#4, B4
- **D string**: D4, D#4, E4, F4, F#4, G4, G#4, A4
- **E string**: E5, F5, F#5, G5, G#5, A5

### Tolerance Settings
- **50 cents** (default): About half a semitone - good for beginners
- **30 cents**: More precise - for intermediate players
- **20 cents**: Very precise - for advanced players

## Tips for Best Results

1. **Good microphone**: Use a decent microphone for better pitch detection
2. **Quiet environment**: Reduce background noise for clearer recording
3. **Clear playing**: Play each note clearly and hold it for a moment
4. **Proper tuning**: Make sure your violin is in tune
5. **Volume**: Speak or play at a good volume level

## Troubleshooting

### "No clear pitch detected"
- Make sure your microphone is working
- Try playing the note more clearly
- Check that your violin is in tune
- Reduce background noise

### Audio not playing
- Check your speakers/headphones
- Make sure your system volume is up
- Try a different audio output device

### Poor pitch detection
- Use a better microphone
- Play in a quieter environment
- Make sure your violin is properly tuned
- Try adjusting the tolerance setting

## Development

### Project Structure
```
hide-and-seek/
├── hide_and_seek/
│   ├── __init__.py
│   ├── __main__.py      # CLI entry point
│   ├── notes.py         # Note definitions and utilities
│   ├── audio.py         # Audio playback and recording
│   └── game.py          # Main game logic
├── pyproject.toml       # Poetry configuration
└── README.md
```

### Running Tests
```bash
poetry run pytest
```

### Code Formatting
```bash
poetry run black hide_and_seek/
poetry run flake8 hide_and_seek/
```

## Future Enhancements

- [ ] GUI interface
- [ ] Different difficulty levels
- [ ] Melody sequences instead of single notes
- [ ] Progress tracking across sessions
- [ ] Different instrument support
- [ ] Rhythm training
- [ ] Interval recognition

## Contributing

Feel free to contribute improvements! This is a learning project, so all suggestions are welcome.

## License

This project is open source and available under the MIT License. 
# WhisperTranscribe

A Python tool that performs speech segmentation and transcription by combining inaSpeechSegmenter for audio analysis with Whisper.cpp for speech-to-text conversion. This tool analyzes audio files to detect speech segments, classify them by gender (male/female), and transcribe the spoken content.

## Features

- **Speech Segmentation**: Automatically detects speech, music, and noise segments
- **Gender Classification**: Identifies male and female speech segments
- **Speech Transcription**: Converts speech segments to text using Whisper.cpp
- **Multiple Audio Formats**: Supports various audio/video formats via pydub and ffmpeg
- **CSV Output**: Generates structured CSV files with timestamps, labels, and transcripts
- **Voice Activity Detection**: Configurable VAD engines for optimal speech detection
- **Batch Processing**: Process multiple files or use pattern matching

## Prerequisites

Before installing, ensure you have:

1. **Python 3.7+** installed on your system
2. **ffmpeg** installed and accessible in your PATH
3. **Whisper.cpp** compiled and configured (see Setup section)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/ctxzz/WhisperTranscribe.git
cd WhisperTranscribe
```

2. Install Python dependencies:
```bash
pip install -r requirements.txt
```

3. Set up Whisper.cpp:
   - Follow the [whisper.cpp installation guide](https://github.com/ggerganov/whisper.cpp)
   - Place the compiled `main` executable in `./whisper.cpp/main`
   - Download a Whisper model (e.g., `ggml-base.bin`) to `./whisper.cpp/models/`

## Usage

### Basic Usage

```bash
python main.py -i input_audio.wav -o output_directory
```

### Advanced Usage

```bash
python main.py \
    -i "*.wav" "audio_file.mp3" \
    -o ./results \
    -d smn \
    -g true \
    -b /usr/local/bin/ffmpeg
```

### Command Line Arguments

| Argument | Short | Description | Default | Choices |
|----------|-------|-------------|---------|---------|
| `--input` | `-i` | Input media files or patterns (required) | - | File paths, URLs, or glob patterns |
| `--output_directory` | `-o` | Output directory for CSV files (required) | - | Writable directory path |
| `--vad_engine` | `-d` | Voice Activity Detection engine | `smn` | `sm`, `smn` |
| `--detect_gender` | `-g` | Enable gender detection for speech segments | `True` | `true`, `false` |
| `--ffmpeg_binary` | `-b` | Path to ffmpeg binary | `ffmpeg` | Custom ffmpeg path |

### Input Options

- **Local files**: `audio.wav`, `video.mp4`, `recording.m4a`
- **Glob patterns**: `"*.wav"`, `"recordings/*.mp3"`
- **URLs**: `"http://example.com/audio.wav"`
- **Multiple inputs**: `-i file1.wav file2.mp3 "*.m4a"`

## Output Format

The tool generates CSV files with the following structure:

| Column | Description |
|--------|-------------|
| `start` | Segment start time (seconds) |
| `end` | Segment end time (seconds) |
| `label` | Segment classification (`male`, `female`, `speech`) |
| `transcript` | Transcribed text content |

### Example Output

```csv
start,end,label,transcript
0.5,3.2,female,こんにちは、今日はいい天気ですね
3.8,7.1,male,はい、本当にそうですね
8.0,12.5,female,散歩に行きませんか
```

## Configuration

### VAD Engine Options

- **`sm`**: Standard model - faster processing, moderate accuracy
- **`smn`**: Standard model with noise detection - better accuracy, slightly slower

### Language Settings

The tool is currently configured for Japanese transcription (`--language ja`). To modify for other languages, edit the `command` array in the `transcribe_audio_with_whisper()` function in `main.py`.

## Dependencies

### Python Packages

- **pydub**: Audio processing and format conversion
- **inaSpeechSegmenter**: Speech/music/noise segmentation and gender detection
- **subprocess**: System command execution
- **argparse**: Command-line argument parsing
- **csv**: CSV file generation
- **os, glob**: File system operations

### External Tools

- **ffmpeg**: Audio/video processing backend for pydub
- **whisper.cpp**: Fast C++ implementation of OpenAI's Whisper model

## Troubleshooting

### Common Issues

1. **ModuleNotFoundError**: Install requirements with `pip install -r requirements.txt`

2. **ffmpeg not found**: 
   - Install ffmpeg: `sudo apt install ffmpeg` (Ubuntu) or `brew install ffmpeg` (macOS)
   - Or specify custom path: `-b /path/to/ffmpeg`

3. **Whisper.cpp not found**:
   - Ensure `./whisper.cpp/main` exists and is executable
   - Verify model file exists at `./whisper.cpp/models/ggml-base.bin`

4. **Permission denied on output directory**:
   - Check write permissions: `ls -la output_directory`
   - Create directory if needed: `mkdir -p output_directory`

### Performance Tips

- Use `smn` VAD engine for better accuracy with noisy audio
- Disable gender detection (`-g false`) for faster processing when not needed
- Process shorter audio files for faster results
- Use appropriate Whisper model size (base/small/medium/large) based on accuracy needs

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project uses several open-source components. Please check individual license requirements for:
- inaSpeechSegmenter
- Whisper.cpp
- Other dependencies listed in requirements.txt

## Acknowledgments

- [inaSpeechSegmenter](https://github.com/ina-foss/inaSpeechSegmenter) for speech segmentation
- [whisper.cpp](https://github.com/ggerganov/whisper.cpp) for efficient speech recognition
- OpenAI's Whisper model for the underlying speech recognition capability

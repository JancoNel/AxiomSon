# Installation Guide

## System Requirements

- **Python 3.14**
- **pip** (Python package manager)

### Optional for Audio Rendering

- **FluidSynth** (MIDI → WAV synthesis)
- **ffmpeg** (WAV → MP3 conversion)

---

## Quick Setup (Recommended)

### Windows

1. Download and run the project folder.
2. Double-click `start.bat`:

   ```bash
   start.bat
   ```

   This will automatically:
   - Create a Python virtual environment (`.venv`)
   - Install all dependencies from `requirements.txt`
   - Launch `alpha.py` in GUI mode

3. Follow the on-screen prompts to enter equations.

### Linux / macOS

1. Open a terminal in the project folder.
2. Run:

   ```bash
   bash start.sh
   ```

   This will automatically:
   - Create a Python virtual environment (`.venv`)
   - Install all dependencies
   - Launch `alpha.py` in GUI mode

---

## Manual Setup

### 1. Create a Virtual Environment

**Windows (cmd.exe):**

```bash
python -m venv .venv
.venv\Scripts\activate
```

**Linux / macOS:**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

This installs:

- Core: `sympy`, `numpy`, `pyyaml`, `pretty_midi`, `mido`
- Optional audio: `pyfluidsynth`, `pydub`, `music21`, `scipy`, `soundfile`
- Testing: `pytest`

### 3. Verify Installation

```bash
python main.py --example
```

You should see output indicating a config was loaded and MIDI was written to `/output`.

---

## Optional: Audio Rendering Setup

To generate WAV and MP3 files directly (not just MIDI), follow these steps:

### Install FluidSynth

**Windows:**

1. Download FluidSynth from <https://www.fluidsynth.org/download/>
2. Extract to a known location (e.g., `C:\FluidSynth`)
3. Add to PATH:
   - Open "Environment Variables" (search in Start menu)
   - Add `C:\FluidSynth\bin` to your `PATH`
4. Verify: Open cmd and run `fluidsynth --version`

**Linux (Ubuntu/Debian):**

```bash
sudo apt-get install fluidsynth
```

**macOS:**

```bash
brew install fluid-synth
```

### Download a SoundFont

1. Get a free GM SoundFont:
   - [FluidR3 GM](https://packages.debian.org/sid/fonts/fluid-soundfont-gs)
   - [Timbres of Heaven](http://www.timbresofheaven.org/download.html)

2. Place the `.sf2` file in a known location, e.g., `./soundfonts/FluidR3_GM.sf2`

3. Reference in your config:

   ```yaml
   soundfont: ./soundfonts/FluidR3_GM.sf2
   ```

### Install ffmpeg (for MP3 conversion)

**Windows:**

1. Download from <https://ffmpeg.org/download.html>
2. Extract and add to PATH (same as FluidSynth above)

**Linux (Ubuntu/Debian):**

```bash
sudo apt-get install ffmpeg
```

**macOS:**

```bash
brew install ffmpeg
```

### Test Audio Rendering

```bash
python main.py --example --output test_song
```

This should generate:

- `/output/test_song.mid`
- `/output/test_song.wav` (if FluidSynth + soundfont configured)
- `/output/test_song.mp3` (if ffmpeg available)

---

## Docker Setup (Advanced)

If you prefer containerization:

```bash
docker build -t AxiomSon .
docker run -it -v $(pwd)/output:/app/output AxiomSon python main.py
```

(Requires a Dockerfile in the repo; contact maintainers if needed.)

---

## Troubleshooting

### "Python not found"

- Ensure Python 3.8+ is installed and in PATH.
- Use `python --version` (or `python3 --version` on macOS/Linux).

### "No module named 'sympy'"

- Activate your virtual environment: `.venv\Scripts\activate` (Windows) or `source .venv/bin/activate` (Linux/macOS).
- Run `pip install -r requirements.txt` again.

### "FluidSynth not found"

- Verify installation with `fluidsynth --version`.
- Check PATH configuration.
- If not installing, audio rendering will be skipped; MIDI files will still be generated.

### Tests fail

```bash
pytest -v
```

This will show which tests are failing. Common issues:

- Missing `pretty_midi` or `sympy`.
- Install via `pip install -r requirements.txt`.

### Permission denied (macOS/Linux)

```bash
chmod +x start.sh
bash start.sh
```

---

## Virtual Environment Management

### Activate (every time you use the project)

**Windows:** `.venv\Scripts\activate`
**Linux/macOS:** `source .venv/bin/activate`

### Deactivate

```bash
deactivate
```

### Remove (if you want to start fresh)

**Windows:** `rmdir /s .venv`
**Linux/macOS:** `rm -rf .venv`

---

## Next Steps

1. Run `python main.py` to start the interactive mode.
2. See `README.md` for usage and example equations.
3. Check `design.md` for technical architecture.

Happy composing!

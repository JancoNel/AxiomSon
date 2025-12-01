# AxiomSon

Turn mathematical equations into music. Define up to 3 concurrent equations using variables `x`, `y`, `z` and evaluate them over time to generate MIDI, sheet music, and audio.

# This was part of an informal CodeJam between me and my one friend, lot of it was rushed. Please dont get mad at quality.

## Features

- **Math-driven composition**: Write equations like `sin(x) + 0.5*cos(y*z)` to generate melodies.
- **Variable updates**: Apply per-timestep updates (e.g., `x = x + 1`, `y = y * 0.99`) to evolve the sound.
- **Limits & resets**: Set thresholds for variables—when `x >= 10`, reset to 0 (or any value).
- **Scale quantization**: Map output to musical scales (A_minor, major, pentatonic).
- **Polyphony**: Generate multi-note chords from a single equation.
- **Rhythmic control**: Snap notes to a grid (`rhythm_quant`) and tempo-aware evaluation (`eval_rate`).
- **Velocity curves**: Linear or exponential velocity mapping.
- **Interactive mode**: CLI-driven workflow—enter equations one by one, queue up to 3 concurrent, save config.
- **MIDI + Audio**: Render to MIDI (for further editing) or directly to WAV/MP3 (via FluidSynth).
- **Sheet music export**: Convert MIDI to MusicXML (via `music21`).
- **Open utuau export**: With Kaseno Teto support!

## Quick Start

### Option 1: Automated Setup (Windows/Linux/Mac)

```bash
# Windows
start.bat

# Linux/Mac
bash start.sh
```

### Option 2: Manual Setup

See [installation.md](./installation.md) for detailed steps.

### Option 3: Docker (if available)

```bash
docker build -t AxiomSon .
docker run -it -v $(pwd)/output:/app/output AxiomSon python main.py
```

## Usage

It is important to note that both main.py and alpha.py works but main.py has way less features because it
was my original base, alpha.py was a more comprehensive rewrite and includes a GUI.

You can use either one but we recommend alpha.py because it is less buggy and has more features/

### GUI mode

```bash
python alpha.py --gui
```

A web GUI will start , fill out the forms and then your set!

### Interactive Mode

```bash
python alpha.py
```

Follow the prompts:

- **Equation name**: e.g., `lead`, `bass`, or type `save` to finish.
- **Expression**: e.g., `sin(x) + 0.1*y`
- **Initial vars (x,y,z)**: comma-separated floats, e.g., `0,0,0`
- **Update rules**: semicolon-separated, e.g., `x = x + 1; y = y*0.99`
- **eval_rate**: beats per evaluation, e.g., `1/8` (eighth note)
- **Duration**: seconds (for simulation display)
- **Active window**: `MM:SS,MM:SS` format, e.g., `00:00,02:00`
- **Mapping options**: scale, octave_range, instrument (piano/synth), polyphony, rhythm_quant, velocity_curve.
- **Variable limits**: Thresholds and reset values, e.g., `10,0` (if x >= 10, reset to 0).

When done entering equations, type `save` to save the config to `/configs` and wait for rendering.

### Config File Mode

```bash
python main.py --config ./my_config.yaml
```

### Example Mode (quick test)

```bash
python main.py --example
```

### Run Tests

```bash
python main.py --test
```

### Specify Output Filename

```bash
python main.py --config myconfig.yaml --output my_song.mid
```

(Outputs MIDI and auto-generates WAV/MP3 if soundfont configured.)

## Config Format

See `design.md` for the full specification. Example:

```yaml
tempo: 120
ticks_per_beat: 24
soundfont: /path/to/FluidR3_GM.sf2  # optional; if set, WAV/MP3 generated

equations:
  - name: lead
    expr: "sin(x) + 0.5*cos(y*z)"
    vars: {x: 0, y: 0, z: 1}
    updates:
      - "x = x + 0.1"
      - "y = y + 0.05"
    eval_rate: "1/8"
    duration: 10
    active_window: [0, 120]  # seconds, or "00:00,02:00"
    limits: {x: [10, 0], y: [1, -1]}  # threshold,reset
    mapping:
      instrument: piano
      scale: A_minor
      base_midi: 60
      octave_range: 2
      polyphony: 1
      rhythm_quant: 0.0625  # 1/16 beat
      velocity_curve: linear

output:
  midi: ./output/song.mid
  wav: ./output/song.wav
  mp3: ./output/song.mp3
```

## Files & Architecture

- **main.py** — CLI entry point (argparse-based).
- **mods/parser.py** — Parse math expressions safely using `sympy` → `numpy` lambdify.
- **mods/engine.py** — Core evaluation: iterate timesteps, apply updates/limits, map to MIDI notes with scale quantization, polyphony, rhythm quantization.
- **mods/runner.py** — Interactive mode and config save/load.
- **design.md** — Detailed design notes, roadmap, and algorithm pseudocode.
- **tests/** — Unit tests (parser, end-to-end MIDI generation).

## Dependencies

Core:

- `sympy`, `numpy` — expression parsing and numeric evaluation.
- `pretty_midi`, `mido` — MIDI generation.
- `pyyaml` — config parsing.

Optional (for audio rendering):

- `pyfluidsynth` — MIDI → WAV via FluidSynth.
- `pydub` — WAV → MP3 conversion.
- `music21` — MIDI → MusicXML (sheet music export).

See `requirements.txt` for full list.

## Examples

### Example 1: Simple Sine Wave

```py
Equation name: sine
Expression: sin(x)
Initial vars: 0,0,0
Updates: x = x + 0.2
Active window: 00:00,01:00
Mapping: scale=A_minor, base_midi=60, octave_range=1
```

### Example 2: Arpeggiator

```py
Equation name: arp
Expression: sin(x) * cos(y)
Initial vars: 0,0,1
Updates: x = x + 1; y = y + 0.5
Active window: 00:00,02:00
Mapping: polyphony=3, scale=major, base_midi=48
```

### Example 3: Drone with Modulation

```py
Equation name: drone
Expression: 0.5*sin(x) + 0.3*sin(y*2)
Initial vars: 1,0,0
Updates: y = y + 0.01
Active window: 00:00,03:00
Limits: y -> [6.28, 0]
Mapping: base_midi=36, instrument=piano
```

## Rendering & Output

- **MIDI** (.mid): Always generated, saved to `/output/song_<timestamp>.mid`. Can be imported into any DAW.
- **WAV** (.wav): Generated if FluidSynth and a soundfont are available. Use `soundfont` key in config.
- **MP3** (.mp3): Auto-generated from WAV using ffmpeg/pydub (if installed).

## Performance Tips

- For long durations (> 5 minutes), use lower `eval_rate` (e.g., `1/16` instead of `1/4`) to reduce sample density.
- Use simple expressions (e.g., polynomial ops, trig) rather than complex nested functions for faster evaluation.
- Limit concurrent equations to 3 for interactive queueing; rendering is serial per equation.

## Troubleshooting

**"pretty_midi is required..."**
→ Run `pip install -r requirements.txt`

**"sympy and numpy are required..."**
→ Same as above.

**Expression parse errors**
→ Ensure expression uses only `x`, `y`, `z` and supported functions: `sin`, `cos`, `tan`, `exp`, `log`, `sqrt`, etc. (via sympy).

**No audio output (WAV/MP3)**
→ Install `pyfluidsynth` and provide a soundfont file path in config under `soundfont`.

**MIDI is silent in DAW**
→ Ensure instrument program (0 = piano, 80 = lead synth) matches your soundfont. Adjust `mapping.instrument`.

## Contributing

PRs welcome! Areas for contribution:

- Additional scale definitions and key transpose logic.
- More sophisticated mapping presets (e.g., harmonic voicing, dynamics).
- Visualization of equation output over time.
- VST plugin wrapper.

## License

MIT (or your preferred license).

---

**Questions?** See `design.md` and `Plan.md` for architecture and roadmap notes.


1. Front end / UI (optional)

CLI for rapid development + optional web UI (NiceGUI)

2. Parser

Parse user-supplied expressions for each equation, and parse variable update rules & timing expressions.

3. Engine / Iterator

Iterates time steps (or event-based times) and evaluates f(x,y,z) for each equation across samples/ticks.

4. Mapper

Converts raw numeric outputs into musical events (note on/off, pitch, velocity, duration, control changes).

5. Sequencer / Scheduler

Handles timing equations (start/stop, triggers), polyphony, and multiple concurrent equations.

6. Synth / Renderer

Convert MIDI events to audio (WAV → MP3) using a soundfont/softsynth (FluidSynth / sf2) or software synth library.

7. Sheet export

Convert event stream to MusicXML (or MIDI → MusicXML) for piano sheet (music21 or lilypond export).

8. Optional extras

Lyrics injector, additional instruments, graphical visuals / music video generation.

2 — Libraries & tools (Python)

Core math / parsing: numpy, sympy (for safe parsing and supporting trig functions), or asteval for secure eval (but prefer sympy parsing to a lambdified function).

MIDI: mido or python-rtmidi for event creation; pretty_midi for easier note handling & MIDI→audio.

Sheet music: music21 (MIDI <-> MusicXML, notation rendering), or produce LilyPond files for high-quality engraving.

Synthesis / audio rendering: fluidsynth (via pyfluidsynth), or pretty_midi + sounddevice for playback. For MP3: render to WAV then convert to MP3 via pydub (which uses ffmpeg) or lame.

Audio I/O: scipy.io.wavfile, soundfile, pydub.

GUI / Web: PyQt6, FastAPI + lightweight React.

Packaging: pyinstaller for an exe, or Docker for consistent env.

> Quick note: MusicXML support and piano engraving is easiest via music21 (export to MusicXML) or via generating LilyPond and rendering to PDF.

3 — Priority roadmap (what to implement, in order)

MVP (must have to be competitive)

1. CLI app (fast to iterate)

2. Parse / evaluate mathematical expressions safely (x,y,z; all trig functions)

3. Single equation → generate monophonic MIDI for piano

4. Export MIDI and render to MP3 (use FluidSynth + a decent GM soundfont)

5. Support variable updates (x, y, z) per equation (linear, arithmetic ops)

6. Timing equation support (tempo mapping + schedule start/stop)

7. Support 3 simultaneous equations (mix voices into single MIDI)

8. Basic mapping presets (Scale quantization, octave range, velocity mapping)

9. Export MusicXML or create basic sheet via music21 (piano-only)

Strong second wave (features that stand out)

1. Polyphonic mapping (harmonies / chords)

2. Multiple instruments (after piano)

3. Envelope/dynamics mapping, CC controls (pedal, reverb)

4. Configurable per-equation mapping profiles (scale, quantize, rhythm template)

5. GUI/web UI with live preview and parameter sliders

6. Advanced pattern generators (LFO-like variable patterns, stochastic patterns)

7. Lyrics injection pipeline (syllabify text & map to note durations)

8. Visualizer / music video generation (audio-reactive visuals or score-to-video)

Stretch / show-stoppers

1. Realtime mode (play as it generates)

2. User-defined mapping language / DSL for melodic/harmonic rules

3. AI-assisted mapping presets (generate best-sounding mapping automatically)

4. Export high-quality WAV + MP3 with mastering effects

5. Integration with VSTs (if aiming for highest audio quality)

4 — Parsing & safe evaluation

Use sympy.sympify for parsing strings into symbolic expressions, then lambdify into numpy functions with sin, cos, tan, asin, etc. This avoids eval and supports trig functions, exponentials, logs, etc.

Example: parse sin(x) + cos(y*z) => lambdified function f(x,y,z) that accepts numpy arrays or floats.

5 — Iteration & Timing model (concrete)

Two modes:

Tick-based: discrete steps t = 0..N-1 with dt set by tempo and ticks_per_beat.

Event-based: evaluate at arbitrary time points driven by timing equations (e.g., run f at times listed by another equation).

Design:

Engine maintains global time in beats or seconds.

Each equation has:

initial_vars: x0,y0,z0

update_rules: e.g. x = x + 1, y = y * 0.99, or z = sin(t)

eval_rate: how often to evaluate (e.g., every tick, every 0.25 beat)

active_window: start & end times from timing equations

mapping_profile: how to convert output to notes

6 — Mapping strategies (VERY important — concrete algorithms)

You want reproducible, musical output. Provide a suite of mapping strategies and presets.

Basic flow

1. Evaluate v = f(x,y,z) → a float (can be scalar or vector).

2. Normalize or scale v to a given numeric domain (e.g., [-1,1] → [0,1]).

3. Map normalized v to pitch (via scale quantization), velocity, duration, channel.

4. Generate MIDI note events (note_on with velocity, note_off after duration).

Pitch mapping (examples)

Linear pitch: pitch = base_midi + round(v_norm * pitch_range) then quantize to scale.

Scale-quantized pitch: map to a scale degrees array (e.g., major pentatonic). Example:

scale_degrees = [0,2,4,5,7,9,11]

degree = int(v_norm *len(scale_degrees)* octaves)

pitch = base_midi + scale_degrees[degree % len(scale_degrees)] + 12*(degree//len(scale_degrees))

Harmonic/chord mapping: Use v to select chord root and provide voicing across simultaneous notes (polyphony).

Stochastic mapping: interpret v as a probability distribution to pick from candidate notes.

Rhythm / duration mapping

Map v to a rhythmic grid: e.g., duration = base_note *2**(round(v_norm* max_power)) → yields whole/half/quarter/eighth etc.

Use eval_rate as an onset grid and allow repeat or sustain.

Velocity & articulation

Map v2 (or f's derivative) to MIDI velocity.

Map variable deltas (Δv) to accent/attack.

Dynamics & expressivity

Generate CC64 for sustain pedal when overlapping notes required.

Map an extra function or variable to CCs for reverb/dampening.

Example mapping presets (fast implement)

Monophonic melody preset: f -> pitch (scale A minor) ; velocity = clipping(abs(f)*127) ; duration = 1/8 note.

Arpeggio preset: f -> selects chord degree; play triad arpeggio with configurable arpeggio pattern.

Drone preset: f -> low pitch sustained; amplitude mapped to filter cutoff.

7 — Handling three equations concurrently

Each equation gets its own MIDI track / channel. Piano required: they can all be mapped to piano (channel 0), or split into left/right hand ranges (lower/higher octaves) to produce piano sheet that reads well.

For sheet music: you’ll want to convert separate voices into two staves (left/right hands) for piano; use music21’s Part and Score abstractions.

8 — Sheet music pipeline (piano)

1. Build a music21.stream.Score.

2. Convert event timeline into music21.note.Note objects with offsets and durations.

3. Assign notes to Part objects (left/right hand) based on pitch range.

4. Export to MusicXML or directly to PDF via music21’s show methods (or produce LilyPond and render).

5. Consider quantization heuristics (snap note ons/off to nearest 16th/8th depending on tempo).

9 — MP3 rendering pipeline

1. Create MIDI file using mido or pretty_midi.

2. Use fluidsynth with a high-quality .sf2 soundfont to render MIDI -> WAV.

pyfluidsynth or call fluidsynth binary.

3. Optionally apply simple mastering (normalize) with pydub or scipy.

4. Convert WAV -> MP3 using pydub (ffmpeg) or lame.

10 — Lyrics (optional) — quick plan

Accept text input (Teto lyrics).

Syllabify (naive: split on spaces; better: use syllapy or a simple heuristic).

Map syllables to notes by onset mapping (one syllable per note or stretched syllables over durations).

Export lyrics in MusicXML using music21 (it supports lyrics on notes).

11 — Graphics / music video (optional)

Option A: generate audio-reactive visuals using the envelope of the MIDI output. Tools: matplotlib + moviepy to create frames and combine into MP4. Or use processing.py-style visuals.

Option B: map functions to shapes/colors (f -> hue; derivative -> brightness) and render frames per beat → assemble into video.

12 — CLI / config example

A YAML/JSON config per run. Example skeleton:

tempo: 100
ticks_per_beat: 24
soundfont: /path/to/FluidR3_GM.sf2
equations:

- name: lead
    expr: "sin(x) + 0.5*cos(y*z)"
    vars: {x:0, y:0, z:1}
    updates:
  - "x = x + 0.1"
  - "y = y + 0.05"
    eval_rate: "1/8"    # every 1/8 note
    mapping:
      instrument: "piano"
      scale: "A_minor"
      base_midi: 60
      octave_range: 2
- name: bass
    expr: "sin(z*x)*10"
    ...
output:
  midi: "./out.mid"
  mp3: "./out.mp3"
  musicxml: "./out.musicxml"

13 — Example algorithm (pseudocode)

# assume sympy-lambdified function f(x,y,z)

for beat_idx in range(total_ticks):
    t = beat_idx * resolution  # in beats
    for eq in equations:
        if not eq.is_active(t): continue
        if eq.should_eval(t):
            v = eq.f(eq.x, eq.y, eq.z)
            # normalize v to [0,1]
            v_norm = (v - eq.vmin)/(eq.vmax - eq.vmin)
            pitch = eq.map_to_pitch(v_norm)
            vel = eq.map_to_velocity(v_norm)
            dur = eq.map_to_duration(v_norm)
            schedule_note(track=eq.track, pitch=pitch, vel=vel, start=t, dur=dur)
            eq.apply_updates()  # e.g. x = x + 1

# After loop, write midi, render with FluidSynth to wav, convert to mp3, export musicxml via music21

14 — Testing, tuning & quality control

Unit tests for parser and mapping functions.

Golden tests: for a fixed seed and config, assert MIDI note sequence equals expected.

Perceptual tests: quick listening sessions to tune mapping presets.

Edge cases: clamp extremely large outputs, handle NaN/inf gracefully.

Performance: profiling for long renders (use numpy vectorization where possible).

15 — Performance & production tips

Vectorize evaluation when doing many time steps: lambdified sympy functions with numpy arrays can evaluate entire timeline at once and let you derive events faster.

Use chunked rendering to avoid huge memory usage.

Precompute quantization tables (scales, pitch maps) for speed.

16 — UX and presentation (how to win)

Provide presets: “Ambient drone”, “Arpeggiator”, “Classical piano”, “8-bit chiptune”.

Add a clean demo with 3-4 short examples and a README + a 30–60s demo video — presentation matters hugely.

Provide an interactive web demo where you can tweak variables live and hear the result (even a tiny demo wins judges’ hearts).

Provide automatic sheet music export and a nice-looking PDF in the deliverables.

Make it easy to reproduce: include sample configs and the exact soundfont used.

17 — Example minimal stack to get working fast

sympy, numpy, pretty_midi, mido, pyfluidsynth, pydub, music21

Build CLI first. Generate one pretty-sounding example per mapping preset.

18 — Sample presets & judging differentiators (how you’ll beat the friend)

Expressivity: map derivatives and delta-values to dynamics/pedal so music breathes — most entrants will have static velocities.

Readable sheet music: algorithmically allocate notes between two staves, keep left hand for bass ranges — many exports will be messy.

Live tweak UI: small but real-time parameter control (sliders) shows polish.

Polished audio: use a high-quality soundfont + subtle reverb/mastering rather than raw synth output.

Meaningful presets: curated presets (ambient/chiptune/classical) that actually sound good.

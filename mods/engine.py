"""Engine: separates evaluation from rendering.

Provides `render_config(config, out_dir='output') -> Path` which evaluates equations,
applies update rules and limits, maps values to musical events (scale quantization,
polyphony, rhythmic quantization, velocity curves), and returns the path to the written MIDI file.

This implementation aims for clarity and modest vectorization where possible; evaluation
supports per-step updates and limit resets (iterative), mapping uses numpy operations
for arrays when possible.
"""

from music21 import converter
from typing import Any, Dict, List, Optional
from pathlib import Path
import time


def _get_scale_degrees(name: str) -> List[int]:
    # semitone offsets for common scales relative to scale root
    scales = {
        'major': [0, 2, 4, 5, 7, 9, 11],
        'minor': [0, 2, 3, 5, 7, 8, 10],
        'pentatonic': [0, 2, 4, 7, 9],
        'a_minor': [0, 2, 3, 5, 7, 8, 10],
        'b_minor': [0, 2, 3, 5, 7, 9, 11],
        'c_minor': [0, 2, 3, 5, 7, 8, 10],
        'c_major': [0, 2, 4, 5, 7, 9, 11], # C major best fr
        'd_minor': [0, 2, 3, 5, 7, 8, 10],
        'd_major': [0, 2, 4, 5, 7, 9, 11],
        'e_minor': [0, 2, 3, 5, 7, 8, 10],
        'e_major': [0, 2, 4, 5, 7, 9, 11],
        'f_minor': [0, 2, 3, 5, 7, 8, 10],
        'f_major': [0, 2, 4, 5, 7, 9, 11],
        'g_minor': [0, 2, 3, 5, 7, 8, 10],
        'g_major': [0, 2, 4, 5, 7, 9, 11],
    }
    key = name.lower().replace('-', '_') if name else ''
    return scales.get(key, scales['minor'])


def _quantize_time(t: float, quant: float, beat_seconds: float) -> float:
    # quant is a fraction of a beat (e.g. 1/16 -> 1/16)
    if quant <= 0:
        return t
    grid = beat_seconds * quant
    return round(t / grid) * grid


def render_to_wav(midi_path: Path, soundfont: Optional[str] = None, wav_path: Optional[Path] = None) -> Optional[Path]:
    """Convert MIDI file to WAV using FluidSynth CLI.

    Returns path to WAV file if successful, None if skipped (no soundfont or FluidSynth unavailable).
    """
    if not soundfont:
        return None
    
    if not Path(soundfont).exists():
        print(f"Soundfont not found: {soundfont}")
        return None
    
    try:
        import subprocess
        import shutil
    except Exception:
        print("subprocess module not available")
        return None

    if wav_path is None:
        wav_path = midi_path.with_suffix('.wav')

    try:
        # Use fluidsynth command-line tool
        if shutil.which('fluidsynth') is None:
            print("FluidSynth executable not found in PATH; skipping WAV rendering.")
            return None
        
        # FIX: Remove the -T raw flag and use proper WAV output
        result = subprocess.run([
            'fluidsynth', '-ni', 
            '-F', str(wav_path), 
            str(soundfont), 
            str(midi_path)
        ], capture_output=True, timeout=300)

        if result.returncode == 0 and wav_path.exists():
            return wav_path
        else:
            print(f"FluidSynth failed: {result.stderr.decode() if result.stderr else 'unknown error'}")
            return None
    except FileNotFoundError:
        print("fluidsynth command not found; install FluidSynth to enable WAV rendering.")
        return None
    except Exception as e:
        print(f"FluidSynth rendering failed: {e}")
        return None


def render_to_mp3(wav_path: Path, mp3_path: Optional[Path] = None) -> Optional[Path]:
    """Convert WAV to MP3 using pydub + ffmpeg.

    Returns path to MP3 file if successful, None if skipped.
    """
    if not wav_path.exists():
        return None
    
    if mp3_path is None:
        mp3_path = wav_path.with_suffix('.mp3')

    try:
        from pydub import AudioSegment
    except Exception:
        print("pydub not available; skipping MP3 conversion. Install pydub to enable.")
        return None

    try:
        audio = AudioSegment.from_wav(str(wav_path))
        audio.export(str(mp3_path), format='mp3', bitrate='192k')
        return mp3_path
    except Exception as e:
        print(f"MP3 conversion failed: {e}")
        return None


def render_config(config: Dict[str, Any], out_dir: Optional[str] = 'output', output_file: Optional[str] = None) -> Path:
    """Render the provided config to MIDI (and optionally WAV/MP3).

    Args:
        config: Configuration dictionary
        out_dir: Output directory for MIDI, WAV, MP3
        output_file: Explicit output filename (without extension); if None, uses timestamp

    Returns:
        Path to the generated MIDI file
    """
    try:
        import pretty_midi
    except Exception:
        raise RuntimeError('pretty_midi is required to render MIDI')
    try:
        from .parser import parse_expr
    except Exception:
        raise
    try:
        import numpy as np
        import sympy as sp
    except Exception:
        raise RuntimeError('numpy and sympy required for engine')

    tempo = float(config.get('tempo', 120))
    beat_seconds = 60.0 / tempo
    out_path_dir = Path(out_dir or 'output')
    out_path_dir.mkdir(parents=True, exist_ok=True)

    pm = pretty_midi.PrettyMIDI(initial_tempo=tempo)

    ts = int(time.time())
    if output_file is None:
        output_file = f"song_{ts}"

    equations = config.get('equations', []) or []

    for i, e in enumerate(equations, start=1):
        name = e.get('name') or f'eq{i}'
        expr = e.get('expr', 'sin(x)')
        vars_ = e.get('vars', {'x': 0.0, 'y': 0.0, 'z': 0.0})
        updates = e.get('updates', [])
        eval_rate = e.get('eval_rate', '1/8')
        mapping = e.get('mapping', {})
        aw = e.get('active_window') or e.get('activeWindow') or [0.0, float(e.get('duration', 5.0))]

        # parse window formats mm:ss,mm:ss
        if isinstance(aw, str):
            try:
                a_str, b_str = (s.strip() for s in aw.split(',', 1))
                def mmss_to_s(s):
                    if ':' in s:
                        m, sec = s.split(':', 1)
                        return int(m) * 60 + float(sec)
                    return float(s)
                aw = [mmss_to_s(a_str), mmss_to_s(b_str)]
            except Exception:
                aw = [0.0, float(e.get('duration', 5.0))]

        start_t, end_t = float(aw[0]), float(aw[1])

        # parse eval_rate to seconds
        if '/' in eval_rate:
            try:
                a, b = (float(s) for s in eval_rate.split('/', 1))
                frac = a / b
            except Exception:
                frac = 1.0 / 8.0
        else:
            try:
                frac = float(eval_rate)
            except Exception:
                frac = 1.0 / 8.0
        dt = beat_seconds * frac
        if dt <= 0:
            dt = beat_seconds * 0.125

        # mapping options ig
        base_midi = int(mapping.get('base_midi', 60))
        scale_name = (mapping.get('scale') or 'a_minor')
        scale_degrees = _get_scale_degrees(scale_name)
        octaves = int(mapping.get('octave_range', 2))
        poly = int(mapping.get('polyphony', mapping.get('poly', 1)))

        rhythm_quant_raw = mapping.get('rhythm_quant', 1/16)
        if isinstance(rhythm_quant_raw, str) and '/' in rhythm_quant_raw:
            try:
                num, denom = rhythm_quant_raw.split('/')
                rhythm_quant = float(num) / float(denom)
            except (ValueError, ZeroDivisionError):
                rhythm_quant = 1/16
        else:
            rhythm_quant = float(rhythm_quant_raw)

        vel_curve = mapping.get('velocity_curve', 'linear')

        # parse limits per variable, expecting mapping 'limits': {'x': [threshold, reset_to], ...}
        limits = e.get('limits', {}) or {}

        # prepare function
        fn, meta = parse_expr(expr)

        # prepare updates (sympy lambdify)
        update_fns = []
        try:
            x_sym, y_sym, z_sym, t_sym = sp.symbols('x y z t')
            for upd in updates:
                if '=' not in upd:
                    continue
                left, right = (s.strip() for s in upd.split('=', 1))
                if left not in ('x', 'y', 'z'):
                    continue
                expr_rhs = sp.sympify(right)
                f_rhs = sp.lambdify((x_sym, y_sym, z_sym, t_sym), expr_rhs, modules=['numpy'])
                update_fns.append((left, f_rhs))
        except Exception:
            update_fns = []

        # create instrument
        instr_name = (mapping.get('instrument') or 'piano').lower()
        program = 0 if instr_name == 'piano' else 80
        instrument = pretty_midi.Instrument(program=program, name=name)

        # iterate time steps (iterative because of updates and limits)
        t = start_t
        vars_local = {k: float(v) for k, v in vars_.items()}

        # collect notes for possible polyphony per step
        while t <= end_t + 1e-9:
            # evaluate
            try:
                v = float(fn(vars_local.get('x', 0.0), vars_local.get('y', 0.0), vars_local.get('z', 0.0)))
            except Exception:
                try:
                    v = float(fn(t, t, t))
                except Exception:
                    v = 0.0

            # normalization
            try:
                v_norm = float(np.tanh(v))
            except Exception:
                # fallback
                v_norm = max(-1.0, min(1.0, v))
            v_scaled = (v_norm + 1.0) / 2.0

            # choose degrees across polyphony
            total_steps = len(scale_degrees) * octaves
            if total_steps <= 0:
                total_steps = len(scale_degrees)
            deg_index = int(v_scaled * total_steps)
            deg_index = max(0, min(total_steps - 1, deg_index))

            chosen = []
            for p in range(poly):
                d = deg_index + p
                scale_idx = d % len(scale_degrees)
                octave_shift = d // len(scale_degrees)
                pitch = base_midi + scale_degrees[scale_idx] + 12 * octave_shift
                pitch = max(0, min(127, int(pitch)))
                chosen.append(pitch)

            # velocity curve
            if vel_curve == 'exp':
                vel = int(max(1, min(127, 1 + (v_scaled ** 2) * 126)))
            else:
                vel = int(max(1, min(127, 1 + v_scaled * 126)))

            # set note start/end and apply rhythm quantization
            start_q = _quantize_time(t, rhythm_quant, beat_seconds)
            end_q = _quantize_time(min(end_t, t + dt), rhythm_quant, beat_seconds)
            if end_q <= start_q:
                end_q = start_q + max(0.01, dt)

            # add notes (polyphony creates multiple notes at same time)
            for pitch in chosen:
                note = pretty_midi.Note(velocity=vel, pitch=pitch, start=float(start_q), end=float(end_q))
                instrument.notes.append(note)

            # apply updates sequentially to avoid issues
            if update_fns:
                for (varname, f_rhs) in update_fns:
                    try:
                        newval = float(f_rhs(vars_local.get('x', 0.0), vars_local.get('y', 0.0), vars_local.get('z', 0.0), t))
                        vars_local[varname] = newval
                    except Exception:
                        pass

            # apply limits lol
            for varname, lim in (limits or {}).items():
                try:
                    threshold = float(lim[0])
                    reset_to = float(lim[1])
                    if vars_local.get(varname, 0.0) >= threshold:
                        vars_local[varname] = reset_to
                except Exception:
                    pass

            t += dt # My body is in so much pain rn

        pm.instruments.append(instrument)

    out_path = out_path_dir / f"{output_file}.mid"
    pm.write(str(out_path))
    print(f"[engine] Wrote MIDI to {out_path}")

    # Writes sheet music in xml format for other software to read.
    sheet_path = Path('sheets')
    sheet_path.mkdir(parents=True, exist_ok=True)  
    sheet_path = sheet_path / f"{output_file}.xml"
    score = converter.parse(str(out_path))
    score.write('musicxml', fp=str(sheet_path)) 
    print(f'Wrote sheet music to ' + str(sheet_path))

    # attempt audio rendering: prefer explicit soundfont from config, otherwise try to locate one
    def _find_soundfont() -> Optional[str]:
        # 1) respect explicit config
        sf = config.get('soundfont')
        if sf:
            if Path(sf).exists():
                return str(Path(sf))
            else:
                print(f"Configured soundfont not found: {sf}")

        # 2) look for .sf2 files in project, output, and user home directories (shallow)
        candidates = []
        search_dirs = [Path('.'), out_path_dir, Path.home()]
        for d in search_dirs:
            try:
                for p in d.glob('**/*.sf2'):
                    candidates.append(str(p))
                    # stop early on first match
                    return candidates[0]
            except Exception:
                continue

        # 3) no soundfont found
        return None

    soundfont = _find_soundfont()
    if soundfont is None:
        print("[engine] No soundfont specified or found; skipping WAV/MP3 rendering.")
    else:
        print(f"[engine] Using soundfont: {soundfont}")
        wav_path = render_to_wav(out_path, soundfont, out_path_dir / f"{output_file}.wav")
        if wav_path:
            print(f"[engine] Wrote WAV to {wav_path}")
            # attempt MP3 conversion
            mp3_path = render_to_mp3(wav_path, out_path_dir / f"{output_file}.mp3")
            if mp3_path:
                print(f"[engine] Wrote MP3 to {mp3_path}")

    return out_path

def render_config_with_notes(config: Dict[str, Any], out_dir: Optional[str] = 'output', output_file: Optional[str] = None) -> tuple[Path, List[Dict]]:
    """Render config and return both MIDI path and note data for UTAU export"""
    midi_path = render_config(config, out_dir, output_file)
    
    # Extract note data from the PrettyMIDI object that was created
    # You'll need to modify render_config to return or store the note data
    # For now, let's create a simple version:
    
    notes_data = []
    # This would need access to the PrettyMIDI object created in render_config
    # You might need to refactor render_config to return the note data
    
    return midi_path, notes_data
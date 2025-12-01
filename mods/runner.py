"""Interactive runner for Sound codewar.

This module provides two entry points used by `main.py`:
- `run(config)` — accepts a config dictionary and performs a minimal summary run (placeholder).
- `interactive()` — interactive prompt loop that collects equations from the user, manages
  up to 3 concurrent active equations and an arbitrary queue, and saves the config when the user
  types `save` (or `save=true`) as the equation name.

The interactive loop is intentionally lightweight: it collects the essential fields for an
equation, then either starts it (if fewer than 3 active) or places it in the queue. Each active
equation is simulated by a background timer that marks it finished after the user-provided
`duration` in seconds. When an active slot frees up a queued equation is started.

When the user finishes entering equations they should type `save` (or `save=true`) to persist the
collected config to `saved_config.yaml`. This satisfies the workflow where the prompt loop
continues until a `save` equation is given.
"""

from typing import Any, Dict, List, Optional
import threading
import time
from pathlib import Path
import json

try:
    import yaml
except Exception:
    yaml = None


class Equation:
    def __init__(self, name: str, expr: str, vars: Dict[str, Any], updates: List[str], eval_rate: str, duration: float, mapping: Dict[str, Any], active_window: List[float] = None, save_flag: bool = False):
        self.name = name
        self.expr = expr
        self.vars = vars
        self.updates = updates
        self.eval_rate = eval_rate
        self.duration = duration
        self.mapping = mapping
        self.active_window = active_window
        self.save_flag = save_flag

    def to_dict(self):
        return {
            "name": self.name,
            "expr": self.expr,
            "vars": self.vars,
            "updates": self.updates,
            "eval_rate": self.eval_rate,
            "duration": self.duration,
            "mapping": self.mapping,
            "active_window": self.active_window,
            "save": self.save_flag,
        }


_active: List[Equation] = []
_queue: List[Equation] = []
_lock = threading.Lock()


def _start_equation(eq: Equation):
    with _lock:
        _active.append(eq)
    print(f"[runner] Starting equation '{eq.name}' for {eq.duration} second(s)")

    def _finish():
        with _lock:
            try:
                _active.remove(eq)
            except ValueError:
                pass
        print(f"[runner] Equation '{eq.name}' finished")
        # start next queued equation if any
        with _lock:
            if _queue and len(_active) < 3:
                next_eq = _queue.pop(0)
                threading.Thread(target=_start_equation, args=(next_eq,), daemon=True).start()

    # Use a timer to simulate the running equation
    t = threading.Timer(eq.duration, _finish)
    t.daemon = True
    t.start()


def _maybe_start_or_queue(eq: Equation):
    with _lock:
        if len(_active) < 3:
            # start immediately in background
            threading.Thread(target=_start_equation, args=(eq,), daemon=True).start()
        else:
            _queue.append(eq)
            print(f"[runner] Queued equation '{eq.name}' (position {len(_queue)})")


def interactive(config_only: bool = False):
    """Interactive prompt loop for adding equations.

    Commands supported in the `name` prompt:
    - `save` or `save=true`: finish input loop and write `saved_config.yaml`
    - `status`: print current active and queued equations
    - `help`: show brief usage

    Args:
        config_only: If True, save config without triggering render. Useful for testing.
    """
    print("Sound codewar interactive mode — enter equations. Type 'help' for commands.")
    collected: List[Equation] = []

    while True:
        name = input("Equation name (or 'save' to finish, 'status', 'help'): ").strip()
        if not name:
            continue
        if name.lower() in ("help", "h"):
            print("Enter equation fields when prompted. Special names: 'save' to end and save, 'status' to view queue.")
            continue
        if name.lower() in ("status", "s"):
            with _lock:
                print(f"Active ({len(_active)}): {[e.name for e in _active]}")
                print(f"Queued ({len(_queue)}): {[e.name for e in _queue]}")
            continue
        if name.lower().startswith("save"):
            # finish and save collected config
            if not collected:
                print("No equations collected — exiting without saving.")
                print("Interactive session ended.")
                return
            cfg = {"equations": [e.to_dict() for e in collected]}
            cfg_dir = Path("configs")
            cfg_dir.mkdir(parents=True, exist_ok=True)
            out = cfg_dir / "saved_config.yaml"
            if yaml:
                out.write_text(yaml.safe_dump(cfg), encoding="utf-8")
                print(f"Saved config to {out}")
            else:
                out.write_text(json.dumps(cfg, indent=2), encoding="utf-8")
                print(f"Saved config (JSON) to {out}")

            if config_only:
                print("Config saved. Exiting (config_only mode).")
                return

            # Block until active jobs and queue finish, then optionally render
            print("Waiting for active and queued equations to finish...")
            try:
                while True:
                    with _lock:
                        active_len = len(_active)
                        queue_len = len(_queue)
                        if active_len == 0 and queue_len == 0:
                            break
                    time.sleep(0.3)
                print("All jobs finished. Interactive session ended.")
            except KeyboardInterrupt:
                print("Interrupted while waiting. Exiting; background jobs may still be running.")
            return

        # otherwise collect fields for an equation
        expr = input("  expression (e.g. sin(x) + 0.1*y): ").strip() or "sin(x)"
        # vars prompt: x,y,z as comma-separated floats
        vars_raw = input("  initial vars x,y,z (comma-separated) [0,0,0]: ").strip() or "0,0,0"
        try:
            x_str, y_str, z_str = (v.strip() for v in vars_raw.split(",", 2))
            vars_dict = {"x": float(x_str), "y": float(y_str), "z": float(z_str)}
        except Exception:
            vars_dict = {"x": 0.0, "y": 0.0, "z": 0.0}

        updates_raw = input("  update rules (semicolon-separated, e.g. 'x = x + 1; y = y*0.99') [none]: ").strip()
        updates = [u.strip() for u in updates_raw.split(";") if u.strip()] if updates_raw else []

        eval_rate = input("  eval_rate (e.g. 1/8) [1/8]: ").strip() or "1/8"
        dur_raw = input("  duration in seconds (simulation) [5]: ").strip() or "5"
        try:
            duration = max(0.1, float(dur_raw))
        except Exception:
            duration = 5.0

        mapping_base_raw = input("  mapping.base_midi (int) [60]: ").strip() or "60"
        try:
            base_midi = int(mapping_base_raw)
        except Exception:
            base_midi = 60

        mapping_scale = input("  mapping.scale (e.g. A_minor) [A_minor]: ").strip() or "A_minor"
        mapping_octaves_raw = input("  mapping.octave_range (int) [2]: ").strip() or "2"
        try:
            mapping_octaves = int(mapping_octaves_raw)
        except Exception:
            mapping_octaves = 2
        mapping_instrument = input("  mapping.instrument (piano/synth) [piano]: ").strip() or "piano"
        mapping_poly_raw = input("  mapping.polyphony (int) [1]: ").strip() or "1"
        try:
            mapping_poly = int(mapping_poly_raw)
        except Exception:
            mapping_poly = 1
        mapping_rhythm_raw = input("  mapping.rhythm_quant (fraction of beat, e.g. 1/16) [1/16]: ").strip() or "1/16"
        try:
            if '/' in mapping_rhythm_raw:
                a,b = mapping_rhythm_raw.split('/',1)
                mapping_rhythm = float(a)/float(b)
            else:
                mapping_rhythm = float(mapping_rhythm_raw)
        except Exception:
            mapping_rhythm = 1.0/16.0
        mapping_velcurve = input("  mapping.velocity_curve (linear/exp) [linear]: ").strip() or "linear"
        # optional active window for the equation (start,end) in mm:ss or seconds
        active_window = None
        aw_raw = input("  active_window (start,end) in mm:ss or seconds [none]: ").strip()
        if aw_raw:
            try:
                # allow comma-separated or space-separated
                if "," in aw_raw:
                    a_str, b_str = (s.strip() for s in aw_raw.split(",", 1))
                else:
                    parts = aw_raw.split()
                    a_str = parts[0]
                    b_str = parts[1] if len(parts) > 1 else parts[0]

                def _mmss_to_s(s):
                    if ":" in s:
                        m, sec = s.split(":", 1)
                        return int(m) * 60 + float(sec)
                    return float(s)

                active_window = [ _mmss_to_s(a_str), _mmss_to_s(b_str) ]
            except Exception:
                active_window = None

        # limits per variable (threshold,reset_to) e.g. for x enter: 10,0 (or leave blank)
        limits = {}
        for var in ('x','y','z'):
            lr = input(f"  limit for {var} (threshold,reset_to) [none]: ").strip()
            if lr:
                try:
                    th, rv = (s.strip() for s in lr.split(',',1))
                    limits[var] = [float(th), float(rv)]
                except Exception:
                    pass

        # save flag if user set name like 'save=true' or provided explicit yes/no
        save_flag = False
        if "=" in name:
            # support 'save=true' or 'mysave=true' style
            k, v = (s.strip() for s in name.split("=", 1))
            if k.lower() == "save" and v.lower() in ("true", "1", "y", "yes"):
                save_flag = True
                # normalize name
                name = "save"

        eq = Equation(
            name=name,
            expr=expr,
            vars=vars_dict,
            updates=updates,
            eval_rate=eval_rate,
            duration=duration,
            mapping={
                "base_midi": base_midi,
                "scale": mapping_scale,
                "octave_range": mapping_octaves,
                "instrument": mapping_instrument,
                "polyphony": mapping_poly,
                "rhythm_quant": mapping_rhythm,
                "velocity_curve": mapping_velcurve,
            },
            active_window=active_window,
            save_flag=save_flag,
        )
        collected.append(eq)

        # start or queue
        _maybe_start_or_queue(eq)


def run(config: Dict[str, Any], output_file: Optional[str] = None) -> int:
    """Run the provided config: save to /configs, render to /output via engine.

    Args:
        config: Configuration dictionary
        output_file: Optional explicit output filename (without extension)

    Returns:
        Exit code (0 for success)
    """
    print("[mods.runner] Starting run() with provided config")
    eqs = config.get("equations", []) or []
    # build Equation instances and start them respecting concurrency
    print("[mods.runner] Starting run() with provided config")

    # Ensure output and configs directories exist
    out_dir = Path("output")
    cfg_dir = Path("configs")
    out_dir.mkdir(parents=True, exist_ok=True)
    cfg_dir.mkdir(parents=True, exist_ok=True)

    # Save a copy of the provided config
    ts = int(time.time())
    cfg_path = cfg_dir / f"config_{ts}.yaml"
    try:
        if yaml:
            cfg_path.write_text(yaml.safe_dump(config), encoding="utf-8")
        else:
            cfg_path.write_text(json.dumps(config, indent=2), encoding="utf-8")
        print(f"Saved runtime config to {cfg_path}")
    except Exception as exc:
        print("Failed to save config:", exc)

    # Prepare tempo and mapping defaults
    tempo = float(config.get("tempo", 120))
    ticks_per_beat = int(config.get("ticks_per_beat", 24))

    try:
        import pretty_midi
    except Exception:
        print("pretty_midi is required to render MIDI. Install the requirements and retry.")
        return 4

    pm = pretty_midi.PrettyMIDI(initial_tempo=tempo)

    eqs = config.get("equations", []) or []

    # Helper to parse active_window values (supports mm:ss or list)
    def parse_window(v):
        if v is None:
            return None
        if isinstance(v, list) or isinstance(v, tuple):
            try:
                return [float(v[0]), float(v[1])]
            except Exception:
                return None
        if isinstance(v, str):
            try:
                a_str, b_str = (s.strip() for s in v.split(",", 1))
                def mmss_to_s(s):
                    if ":" in s:
                        m, sec = s.split(":", 1)
                        return int(m) * 60 + float(sec)
                    return float(s)
                return [mmss_to_s(a_str), mmss_to_s(b_str)]
            except Exception:
                return None
        return None

    beat_seconds = 60.0 / tempo

    # Delegate to engine for rendering
    try:
        from .engine import render_config
    except Exception as exc:
        print("Engine module not available:", exc)
        return 6

    try:
        out_path = render_config(config, out_dir=str(out_dir), output_file=output_file)
        print(f"Wrote MIDI to {out_path}")
    except Exception as exc:
        print("Engine rendering failed:", exc)
        import traceback
        traceback.print_exc()
        return 5

    print("[mods.runner] Run complete")
    return 0

    # legacy wait loop (kept for reference)
    print("[mods.runner] All equations scheduled. Waiting for active jobs to finish...")
    try:
        while True:
            with _lock:
                if not _active and not _queue:
                    break
            time.sleep(0.3)
    except KeyboardInterrupt:
        print("[mods.runner] Interrupted by user.")
        return 2

    print("[mods.runner] Run complete")
    return 0

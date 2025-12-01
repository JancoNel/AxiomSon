# mods/utau_integration.py
"""Simple integration between engine and UTAU exporter"""
from mods.engine import render_config
from mods.utau_exporter import UTAUExporter
import pretty_midi
from pathlib import Path

def render_to_utau(config: dict, lyrics: str = "", output_name: str = None) -> Path:
    """Render config to both MIDI and UTAU UST"""
    
    # Step 1: Generate MIDI normally
    midi_path = render_config(config, output_file=output_name)
    
    # Step 2: Parse the MIDI to extract note data
    pm = pretty_midi.PrettyMIDI(str(midi_path))
    
    notes_data = []
    for instrument in pm.instruments:
        for note in instrument.notes:
            notes_data.append({
                'pitch': note.pitch,
                'duration': note.end - note.start,
                'start': note.start,
                'velocity': note.velocity,
                'lyric': 'a'  # Placeholder - you'll need lyric mapping
            })
    
    # Step 3: Generate UST from note data
    exporter = UTAUExporter()
    exporter.tempo = config.get('tempo', 120)
    
    ust_path = exporter.generate_ust(notes_data, lyrics)
    return ust_path
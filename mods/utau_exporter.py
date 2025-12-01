# mods/utau_exporter.py --- shamelessly stolen from somewhere on github

"""UTAU export support for Kasane Teto English"""
import re
from pathlib import Path
from typing import List, Dict, Any

class UTAUExporter:
    def __init__(self):
        self.tempo = 120
        self.project_name = "AxiomSon_UTAU"
        
    def midi_note_to_utau_pitch(self, midi_note: int) -> str:
        """Convert MIDI note to UTAU note number"""
        # UTAU uses C4=48, MIDI uses C4=60
        return str(midi_note - 12)
    
    def text_to_lyrics(self, text: str, note_duration: float) -> List[Dict]:
        """Convert English text to UTAU phonemes for Teto English"""
        # Basic English to CV mapping
        phoneme_map = {
            'a': ['a'], 'e': ['e'], 'i': ['i'], 'o': ['o'], 'u': ['u'],
            'ka': ['k','a'], 'ke': ['k','e'], 'ki': ['k','i'], 'ko': ['k','o'], 'ku': ['k','u'],
            'sa': ['s','a'], 'se': ['s','e'], 'si': ['s','i'], 'so': ['s','o'], 'su': ['s','u'],
            'ta': ['t','a'], 'te': ['t','e'], 'ti': ['t','i'], 'to': ['t','o'], 'tu': ['t','u'],
            'na': ['n','a'], 'ne': ['n','e'], 'ni': ['n','i'], 'no': ['n','o'], 'nu': ['n','u'],
            'ha': ['h','a'], 'he': ['h','e'], 'hi': ['h','i'], 'ho': ['h','o'], 'hu': ['h','u'],
            'ma': ['m','a'], 'me': ['m','e'], 'mi': ['m','i'], 'mo': ['m','o'], 'mu': ['m','u'],
            'ra': ['r','a'], 're': ['r','e'], 'ri': ['r','i'], 'ro': ['r','o'], 'ru': ['r','u']
        }
        
        # Simple word splitting - you'd want a proper lyric→phoneme converter
        words = text.lower().split()
        notes = []
        
        for word in words:
            # Distribute word across notes (simplistic)
            for phoneme in word:
                if phoneme in phoneme_map:
                    notes.append({
                        'lyric': phoneme,
                        'length': int(note_duration * 480),  # UTAU uses ticks
                        'note_num': 60,  # Default pitch
                        'flags': "B50"  # Breathiness for Teto
                    })
        
        return notes
    
    def generate_ust(self, midi_notes: List, lyrics: str = "", output_path: Path = None) -> Path:
        """Generate UTAU project file from MIDI data"""
        if output_path is None:
            output_path = Path("output") / "utau_project.ust"
            
        ust_content = [
            "[#SETTING]",
            f"Tempo={self.tempo}",
            "Tracks=1",
            f"ProjectName={self.project_name}",
            "VoiceDir=%VOICE%Teto_English\\",
            "CacheDir=%VOICE%Teto_English\\cache\\",
            "Mode2=True",
            "",
            "[#0000]",
            "Length=480",
            "Lyric=R",
            "NoteNum=60",
            "",
        ]
        
        # Convert MIDI notes to UTAU notes
        for i, note in enumerate(midi_notes, 1):
            ust_content.extend([
                f"[#{i:04d}]",
                f"Length={int(note['duration'] * 480)}",
                f"Lyric={note.get('lyric', 'a')}",
                f"NoteNum={self.midi_note_to_utau_pitch(note['pitch'])}",
                "Flags=B50",  # Teto English vocal characteristics
                "",
            ])
        
        # Add end marker
        ust_content.extend([
            f"[#{len(midi_notes)+1:04d}]",
            "Length=480",
            "Lyric=R",
            "NoteNum=60",
            "",
        ])
        
        output_path.write_text('\n'.join(ust_content), encoding='utf-8')
        return output_path

def export_to_utau(config: Dict, lyrics: str = "", output_name: str = None) -> Path:
    """Main export function to integrate with your engine"""
    # First generate MIDI using existing engine
    from mods.engine import render_config
    midi_path = render_config(config, output_file=output_name)
    
    # Convert MIDI to UST (you'd need to parse MIDI or store note data)
    exporter = UTAUExporter()
    
    # This would require storing note data from render_config
    # For now, placeholder implementation
    mock_notes = [
        {'pitch': 60, 'duration': 0.5, 'lyric': 'a'},
        {'pitch': 62, 'duration': 0.5, 'lyric': 'e'},
    ]
    
    ust_path = exporter.generate_ust(mock_notes, lyrics)
    return ust_path
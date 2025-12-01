# gui.py
"""Main GUI for AxiomSon - Unified generation approach"""
from nicegui import ui, app
from pathlib import Path
import logging
from typing import Dict, List, Optional, Any

from mods.ui_helpers import UIHelpers, EquationBuilder
from mods.ui_components import StatusDisplay, ConfigurationPanel

# Global constants
gh = 'GH2025'

class AxiomSonUI:
    """Main UI controller with unified generation"""
    
    def __init__(self):
        self.equation_list: List[Dict[str, Any]] = []
        self.status_timer: Optional[ui.timer] = None
        self._ui_components: Dict[str, Any] = {}
        
        # Initialize components
        self.status_display = StatusDisplay()
        self.config_panel = ConfigurationPanel(self._ui_components)
        
        # License verification (simplified)
        self._verify_license()
    
    def _verify_license(self) -> None:
        """Simple license verification"""
        try:
            with open("LICENSE", "r") as f:
                license_text = f.read()
                if gh not in license_text:
                    logging.warning("License verification failed")
        except FileNotFoundError:
            logging.warning("LICENSE file not found")
    
    def create_header(self) -> None:
        """Create main header with unified generate button"""
        with ui.row().classes('w-full items-center justify-between'):
            ui.label('🎵 AxiomSon').classes('text-3xl font-bold text-purple-400')
            
            # SINGLE universal generate button
            ui.button('🎵 Generate Music', on_click=self.generate_all_outputs, 
                     icon='music_note').props('color=green size=lg')
    
    def create_output_options(self) -> None:
        """Create output format options"""
        with ui.expansion('Output Options', icon='tune').classes('w-full'):
            with ui.grid(columns=2).classes('w-full gap-4'):
                # Output filename
                self._ui_components['config_output'] = ui.input(
                    'Output Name', 
                    placeholder='my_song'
                ).classes('w-full').props('clearable')
                
                # Output formats selection
                self._ui_components['output_midi'] = ui.checkbox('MIDI', value=True)
                self._ui_components['output_sheet'] = ui.checkbox('Sheet Music', value=True)
                self._ui_components['output_audio'] = ui.checkbox('Audio (WAV/MP3)', value=True)
                self._ui_components['output_utau'] = ui.checkbox('UTAU Project', value=False)
            
            # UTAU-specific options (only show if UTAU is selected)
            with ui.card().bind_visibility_from(self._ui_components['output_utau'], 'value'):
                ui.label('UTAU Settings').classes('font-bold')
                with ui.grid(columns=2).classes('w-full gap-2'):
                    # FIXED: Proper string handling
                    placeholder_text = "Enter lyrics for vocal synthesis"
                    self._ui_components['utau_lyrics'] = ui.textarea('Lyrics').classes('w-full col-span-2')
                    self._ui_components['utau_lyrics'].props(f'placeholder="{placeholder_text}"')
                    
                    self._ui_components['utau_voicebank'] = ui.select([
                        'Teto_English', 
                        'Teto_Japanese',
                        'Custom Voicebank'
                    ], value='Teto_English').classes('w-full')
                    self._ui_components['utau_flags'] = ui.input('Vocal Flags', value='B50').classes('w-full')
    
    def generate_all_outputs(self) -> None:
        """Generate ALL selected output formats with one click"""
        if not self.equation_list:
            ui.notify('No equations to generate music from', type='warning')
            return
        
        # Build config
        config = {
            'tempo': float(self._ui_components['config_tempo'].value),
            'ticks_per_beat': int(self._ui_components['config_ticks'].value),
            'equations': self.equation_list
        }
        
        output_file = self._ui_components['config_output'].value or None
        
        try:
            from mods.runner import run
            
            # Generate base MIDI (required for all other formats)
            result = run(config, output_file=output_file)
            
            if result == 0:
                successes = []
                
                # Generate additional formats based on selections
                if self._ui_components['output_utau'].value:
                    utau_success = self._generate_utau_output(config, output_file)
                    if utau_success:
                        successes.append("UTAU")
                
                if self._ui_components['output_audio'].value:
                    audio_success = self._generate_audio_output(output_file)
                    if audio_success:
                        successes.append("Audio")
                
                # Sheet music is generated automatically by engine.py
                if self._ui_components['output_sheet'].value:
                    successes.append("Sheet Music")
                
                # MIDI is always generated
                successes.append("MIDI")
                
                success_msg = f"Generated: {', '.join(successes)}"
                ui.notify(success_msg)
                
            else:
                ui.notify(f'Generation failed with code: {result}', type='warning')
                
        except Exception as e:
            ui.notify(f'Generation error: {e}', type='negative')
    
    def _generate_utau_output(self, config: Dict, output_file: str = None) -> bool:
        """Generate UTAU output if lyrics provided"""
        lyrics = self._ui_components['utau_lyrics'].value
        if not lyrics:
            ui.notify('Skipping UTAU: No lyrics provided', type='warning')
            return False
        
        try:
            from mods.utau_integration import render_to_utau
            ust_path = render_to_utau(config, lyrics, output_file)
            ui.notify(f'UTAU project: {ust_path.name}')
            return True
        except Exception as e:
            ui.notify(f'UTAU export failed: {e}', type='warning')
            return False
    
    def _generate_audio_output(self, output_file: str = None) -> bool:
        """Generate audio output (WAV/MP3)"""
        try:
            # This would use your existing audio rendering logic
            # For now, just notify that it would happen
            ui.notify('Audio rendering would happen here')
            return True
        except Exception as e:
            ui.notify(f'Audio rendering failed: {e}', type='warning')
            return False
    
    def create_equation_form(self) -> None:
        """Create equation form using helper"""
        EquationBuilder.create_equation_form(self._ui_components)
    
    def create_equations_display(self) -> None:
        """Create equations list display"""
        self._ui_components['equations_display'] = ui.card().classes('w-full')
        self.refresh_equations_display()
    
    def refresh_equations_display(self) -> None:
        """Refresh equations list"""
        display = self._ui_components.get('equations_display')
        if not display:
            return
            
        display.clear()
        with display:
            ui.label('Equations List').classes('text-xl font-bold')
            
            if not self.equation_list:
                ui.label('No equations added').classes('text-gray-500')
                return
                
            for i, eq in enumerate(self.equation_list):
                with ui.card().classes('w-full mb-2'):
                    with ui.row().classes('w-full justify-between items-center'):
                        with ui.column():
                            ui.label(f'{eq["name"]}').classes('font-bold')
                            ui.label(f'Expression: {eq["expr"]}').classes('text-sm')
                            ui.label(f'Duration: {eq["duration"]}s').classes('text-sm')
                        
                        ui.button(icon='delete', on_click=lambda _, idx=i: self.delete_equation(idx)).props('flat color=red')
    
    def delete_equation(self, index: int) -> None:
        """Delete equation"""
        if 0 <= index < len(self.equation_list):
            del self.equation_list[index]
            self.refresh_equations_display()
            ui.notify('Equation deleted')
    
    def clear_all(self) -> None:
        """Clear all equations"""
        self.equation_list.clear()
        self.refresh_equations_display()
        ui.notify('All equations cleared')
    
    def create_ui(self) -> None:
        """Create main UI with unified workflow"""
        logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')
        
        ui.dark_mode().enable()
        
        with ui.column().classes('w-full max-w-6xl mx-auto p-4 gap-4'):
            self.create_header()
            self.status_display.create()
            
            with ui.tabs().classes('w-full') as tabs:
                eq_tab = ui.tab('Equations', icon='functions')
                config_tab = ui.tab('Settings', icon='settings')
            
            with ui.tab_panels(tabs, value=eq_tab).classes('w-full'):
                with ui.tab_panel(eq_tab):
                    self.create_equation_form()
                    self.create_equations_display()
                
                with ui.tab_panel(config_tab):
                    # Configuration
                    with ui.card().classes('w-full'):
                        ui.label('Music Settings').classes('text-xl font-bold')
                        with ui.grid(columns=2).classes('w-full gap-4'):
                            self._ui_components['config_tempo'] = ui.number('Tempo', value=120, min=1).classes('w-full')
                            self._ui_components['config_ticks'] = ui.number('Ticks per Beat', value=24, min=1).classes('w-full')
                    
                    # ADDED BACK: Config file path input
                    with ui.card().classes('w-full'):
                        ui.label('Configuration Files').classes('text-xl font-bold')
                        self._ui_components['config_file_path'] = ui.input(
                            'Config File Path', 
                            placeholder='configs/my_config.yaml'
                        ).classes('w-full')
                    
                    # Output options
                    self.create_output_options()
                    
                    # Utility buttons
                    with ui.card().classes('w-full'):
                        ui.label('Utilities').classes('text-xl font-bold')
                        with ui.row().classes('w-full justify-between'):
                            ui.button('Load Config', on_click=self.load_config, icon='folder_open')
                            ui.button('Save Config', on_click=self.save_config, icon='save')
                            ui.button('Clear All', on_click=self.clear_all, icon='clear').props('color=red')
                            ui.button('Run Example', on_click=self.run_example, icon='play_arrow')
            
            ui.label('Music is just math that got drunk and started feeling things').classes('text-sm text-gray-500 text-center w-full')
    
    def load_config(self) -> None:
        """Load config from file"""
        path_input = self._ui_components['config_file_path']
        if not path_input.value:
            ui.notify('Config file path required', type='warning')
            return
        
        try:
            config_path = Path(path_input.value)
            if not config_path.exists():
                ui.notify(f'Config file not found: {config_path}', type='negative')
                return
            
            # Use your existing load_config logic here
            config = UIHelpers.load_config(config_path)
            
            # Process equations from config
            equations = config.get('equations', [])
            if isinstance(equations, dict):
                equations = list(equations.values())
            
            self.equation_list = []
            for eq in equations:
                processed_eq = {
                    'name': eq.get('name', 'unnamed'),
                    'expr': eq.get('expr', 'sin(x)'),
                    'vars': {k: float(v) for k, v in eq.get('vars', {}).items()},
                    'updates': eq.get('updates', []),
                    'eval_rate': eq.get('eval_rate', '1/8'),
                    'duration': float(eq.get('duration', 5.0)),
                    'mapping': {
                        'base_midi': int(eq.get('mapping', {}).get('base_midi', 60)),
                        'scale': eq.get('mapping', {}).get('scale', 'C_major'),
                        'octave_range': int(eq.get('mapping', {}).get('octave_range', 2)),
                        'instrument': eq.get('mapping', {}).get('instrument', 'piano'),
                        'polyphony': int(eq.get('mapping', {}).get('polyphony', 1)),
                        'rhythm_quant': UIHelpers._parse_rhythm_quant(eq.get('mapping', {}).get('rhythm_quant')),
                        'velocity_curve': eq.get('mapping', {}).get('velocity_curve', 'linear')
                    },
                    'active_window': eq.get('active_window', [0.0, 60.0])
                }
                self.equation_list.append(processed_eq)
            
            # Update global config values
            if 'tempo' in config:
                self._ui_components['config_tempo'].value = float(config['tempo'])
            if 'ticks_per_beat' in config:
                self._ui_components['config_ticks'].value = int(config['ticks_per_beat'])
            
            self.refresh_equations_display()
            ui.notify(f'Config loaded from {config_path}')
            
        except Exception as e:
            ui.notify(f'Config load error: {e}', type='negative')
    
    def save_config(self) -> None:
        """Save current configuration"""
        if not self.equation_list:
            ui.notify('No equations to save', type='warning')
            return
        
        config = {
            'tempo': float(self._ui_components['config_tempo'].value),
            'ticks_per_beat': int(self._ui_components['config_ticks'].value),
            'equations': self.equation_list
        }
        
        try:
            out_path = UIHelpers.save_config(config)
            ui.notify(f'Config saved to {out_path}')
        except Exception as e:
            ui.notify(f'Config save error: {e}', type='negative')
    
    def run_example(self) -> None:
        """Run example configuration"""
        ui.notify('Example would run here')

def launch_ui():
    """Launch the UI"""
    app = AxiomSonUI()
    app.create_ui()
    ui.run(title="AxiomSon - Mathematical Music Generator", port=8080, reload=False)
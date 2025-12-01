# mods/ui_helpers.py
"""UI helper functions and components for AxiomSon"""
from nicegui import ui
from pathlib import Path
import time
import json
import logging
from typing import Dict, List, Optional, Any, Union

# Conditional imports
try:
    import yaml 
except ImportError:
    yaml = None

class UIHelpers:
    """Helper methods for UI components"""
    
    # Default constants
    _DEFAULT_RHYTHM_QUANT = 0.0625
    _DEFAULT_DURATION = 5.0
    _DEFAULT_BASE_MIDI = 60
    _DEFAULT_TEMPO = 120
    _DEFAULT_TICKS_PER_BEAT = 24
    
    @staticmethod
    def _parse_time_string(time_str: str) -> float:
        """Parse time string to seconds"""
        if not time_str:
            return 0.0
        try:
            if ':' in time_str:
                minutes, seconds = time_str.split(':', 1)
                return float(minutes) * 60 + float(seconds)
            return float(time_str)
        except ValueError:
            return 0.0
    
    @staticmethod
    def _parse_rhythm_quant(quant: Union[str, float, int]) -> float:
        """Parse rhythm quant with type checking"""
        if isinstance(quant, (int, float)):
            return float(quant)
        if not quant:
            return UIHelpers._DEFAULT_RHYTHM_QUANT
        if isinstance(quant, str) and '/' in quant:
            try:
                num, denom = quant.split('/')
                return float(num) / float(denom)
            except (ValueError, ZeroDivisionError):
                return UIHelpers._DEFAULT_RHYTHM_QUANT
        try:
            return float(quant)
        except ValueError:
            return UIHelpers._DEFAULT_RHYTHM_QUANT
    
    @staticmethod
    def load_config(path: Path) -> Dict[str, Any]:
        """Load YAML or JSON config"""
        try:
            text = path.read_text(encoding='utf-8')
            return yaml.safe_load(text) if yaml else json.loads(text)
        except (OSError, json.JSONDecodeError, yaml.YAMLError) as e:
            logging.error(f"Config load failed: {e}")
            raise
    
    @staticmethod
    def save_config(config: Dict, filename: str = None) -> Path:
        """Save configuration to file"""
        if filename is None:
            ts = int(time.time())
            filename = f"ui_config_{ts}.yaml"
        
        cfg_dir = Path("configs")
        cfg_dir.mkdir(parents=True, exist_ok=True)
        out_path = cfg_dir / filename
        
        if yaml:
            out_path.write_text(yaml.safe_dump(config, default_flow_style=False, indent=2), encoding="utf-8")
        else:
            out_path.write_text(json.dumps(config, indent=2), encoding="utf-8")
        
        return out_path

class EquationBuilder:
    """Helper class for building equation forms and data"""
    
    @staticmethod
    def create_equation_form(ui_components: Dict) -> None:
        """Create the equation input form"""
        with ui.card().classes('w-full'):
            ui.label('Add New Equation').classes('text-xl font-bold')
            
            with ui.grid(columns=2).classes('w-full gap-4'):
                # Core equation parameters
                ui_components['eq_name'] = ui.input('Equation Name').classes('w-full')
                ui_components['eq_expr'] = ui.input('Expression', placeholder='sin(x) + 0.1*y').classes('w-full')
                ui_components['eq_eval_rate'] = ui.input('Evaluation Rate', value='1/8').classes('w-full')
                ui_components['eq_duration'] = ui.number('Duration (seconds)', value=UIHelpers._DEFAULT_DURATION, min=0.1).classes('w-full')
                
                # Variable inputs
                with ui.expansion('Variables', icon='settings').classes('w-full col-span-2'):
                    with ui.grid(columns=3).classes('w-full gap-2'):
                        ui_components['eq_x'] = ui.number('X', value=0.0).classes('w-full')
                        ui_components['eq_y'] = ui.number('Y', value=0.0).classes('w-full') 
                        ui_components['eq_z'] = ui.number('Z', value=0.0).classes('w-full')
                
                # Mapping settings
                with ui.expansion('Mapping Settings', icon='tune').classes('w-full col-span-2'):
                    with ui.grid(columns=2).classes('w-full gap-2'):
                        ui_components['eq_base_midi'] = ui.number('Base MIDI', value=UIHelpers._DEFAULT_BASE_MIDI).classes('w-full')
                        ui_components['eq_scale'] = ui.select([
                            'A_minor', 'B_minor', 'C_minor', 'C_major', 'D_minor', 'D_major',
                            'E_minor', 'E_major', 'F_minor', 'F_major', 'G_minor', 'G_major',
                            'major', 'minor', 'pentatonic'
                        ], value='C_major').classes('w-full')
                        ui_components['eq_octave_range'] = ui.number('Octave Range', value=2).classes('w-full')
                        ui_components['eq_instrument'] = ui.select(['piano', 'synth'], value='piano').classes('w-full')
                        ui_components['eq_polyphony'] = ui.number('Polyphony', value=1).classes('w-full')
                        ui_components['eq_rhythm_quant'] = ui.input('Rhythm Quant', value='0.0625').classes('w-full')
                        ui_components['eq_velocity_curve'] = ui.select(['linear', 'exp'], value='linear').classes('w-full')
                
                # Update rules
                with ui.expansion('Update Rules', icon='update').classes('w-full col-span-2'):
                    ui_components['eq_updates'] = ui.textarea('Update Rules').classes('w-full').props('placeholder="x = x + 1; y = y * 0.99"')
                
                # Time window constraints
                with ui.expansion('Active Window (Optional)', icon='schedule').classes('w-full col-span-2'):
                    with ui.grid(columns=2).classes('w-full gap-2'):
                        ui_components['eq_window_start'] = ui.input('Start (seconds or mm:ss)', value='0.0').classes('w-full')
                        ui_components['eq_window_end'] = ui.input('End (seconds or mm:ss)', value='60.0').classes('w-full')
            
            ui.button('Add Equation', on_click=lambda: EquationBuilder.add_equation(ui_components)).classes('col-span-2')
    
    @staticmethod
    def add_equation(ui_components: Dict) -> Dict:
        """Build equation data from form inputs"""
        name_input = ui_components['eq_name']
        if not name_input.value:
            ui.notify('Equation name required', type='negative')
            return None
        
        active_window = [
            UIHelpers._parse_time_string(ui_components['eq_window_start'].value),
            UIHelpers._parse_time_string(ui_components['eq_window_end'].value)
        ]
        
        eq_data = {
            'name': name_input.value,
            'expr': ui_components['eq_expr'].value or 'sin(x)',
            'vars': {
                'x': float(ui_components['eq_x'].value),
                'y': float(ui_components['eq_y'].value), 
                'z': float(ui_components['eq_z'].value)
            },
            'updates': [u.strip() for u in ui_components['eq_updates'].value.split(';')] if ui_components['eq_updates'].value else [],
            'eval_rate': ui_components['eq_eval_rate'].value,
            'duration': float(ui_components['eq_duration'].value),
            'mapping': {
                'base_midi': int(ui_components['eq_base_midi'].value),
                'scale': ui_components['eq_scale'].value,
                'octave_range': int(ui_components['eq_octave_range'].value),
                'instrument': ui_components['eq_instrument'].value,
                'polyphony': int(ui_components['eq_polyphony'].value),
                'rhythm_quant': UIHelpers._parse_rhythm_quant(ui_components['eq_rhythm_quant'].value),
                'velocity_curve': ui_components['eq_velocity_curve'].value
            },
            'active_window': active_window
        }
        
        # Reset form
        name_input.value = ''
        ui_components['eq_expr'].value = ''
        ui_components['eq_updates'].value = ''
        ui_components['eq_window_start'].value = '0.0'
        ui_components['eq_window_end'].value = '60.0'
        
        return eq_data
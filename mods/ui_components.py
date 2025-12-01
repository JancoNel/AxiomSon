# mods/ui_components.py
"""UI component classes for AxiomSon"""
from nicegui import ui
from pathlib import Path
from typing import Dict, List, Optional, Any
from mods.ui_helpers import UIHelpers, EquationBuilder

class StatusDisplay:
    """Status display component"""
    
    def __init__(self):
        self._ui_components = {}
        self._last_status = ""
    
    def create(self) -> None:
        """Create status display"""
        self._ui_components['status_card'] = ui.card().classes('w-full')
        self.update()
    
    def update(self) -> None:
        """Update status display"""
        # This would integrate with your runner status
        active_names, queued_names = self._get_runner_status()
        
        current_content = f"{sorted(active_names)}|{sorted(queued_names)}"
        if self._last_status == current_content:
            return
            
        self._last_status = current_content
        self._render(active_names, queued_names)
    
    def _get_runner_status(self) -> tuple[List[str], List[str]]:
        """Get runner status - placeholder for now"""
        return [], []  # Would integrate with your runner module
    
    def _render(self, active_names: List[str], queued_names: List[str]) -> None:
        """Render status UI"""
        card = self._ui_components.get('status_card')
        if not card:
            return
            
        card.clear()
        with card:
            ui.label('Current Status').classes('text-xl font-bold')
            with ui.grid(columns=2).classes('w-full gap-4'):
                # Active equations panel
                with ui.card().classes('bg-blue-100'):
                    ui.label('Active Equations').classes('font-bold')
                    if active_names:
                        for name in active_names:
                            ui.label(f'• {name}')
                    else:
                        ui.label('None').classes('text-gray-500')
                
                # Queued equations panel  
                with ui.card().classes('bg-yellow-100'):
                    ui.label('Queued Equations').classes('font-bold')
                    if queued_names:
                        for i, name in enumerate(queued_names, 1):
                            ui.label(f'{i}. {name}')
                    else:
                        ui.label('None').classes('text-gray-500')

class ConfigurationPanel:
    """Configuration panel component"""
    
    def __init__(self, ui_components: Dict):
        self._ui_components = ui_components
    
    def create(self) -> None:
        """Create configuration section"""
        with ui.card().classes('w-full'):
            ui.label('Configuration').classes('text-xl font-bold')
            
            with ui.grid(columns=2).classes('w-full gap-4'):
                self._ui_components['config_tempo'] = ui.number('Tempo', value=120, min=1).classes('w-full')
                self._ui_components['config_ticks'] = ui.number('Ticks per Beat', value=24, min=1).classes('w-full')
                self._ui_components['config_output'] = ui.input('Output Filename', placeholder='my_song').classes('w-full')
                self._ui_components['config_file_path'] = ui.input('Config File Path', placeholder='configs/my_config.yaml').classes('w-full col-span-2')
        
            with ui.row().classes('w-full justify-between'):
                ui.button('Load Config', on_click=self.load_config, icon='folder_open')
                ui.button('Save Config', on_click=self.save_config, icon='save')
    
    def load_config(self) -> None:
        """Load config from file"""
        # Implementation would go here
        pass
    
    def save_config(self) -> None:
        """Save current configuration"""
        # Implementation would go here  
        pass

class UTAUPanel:
    """UTAU export panel component"""
    
    def __init__(self, ui_components: Dict):
        self._ui_components = ui_components
    
    def create(self) -> None:
        """Create UTAU export section"""
        with ui.expansion('UTAU Export (Beta)', icon='record_voice_over').classes('w-full'):
            with ui.grid(columns=2).classes('w-full gap-2'):
                stemp = "Enter English lyrics for Teto...\nEach line will be mapped to musical phrases"
                self._ui_components['utau_lyrics'] = ui.textarea('Lyrics').classes('w-full col-span-2').props(
                    f'placeholder={stemp}'
                )
                self._ui_components['utau_voicebank'] = ui.select([
                    'Teto_English', 
                    'Teto_Japanese',
                    'Custom Voicebank'
                ], value='Teto_English').classes('w-full')
                self._ui_components['utau_flags'] = ui.input('Vocal Flags', value='B50').classes('w-full')
        
            ui.button('Export to UTAU', on_click=self.export_utau, icon='voice_over').props('color=purple')
    
    def export_utau(self) -> None:
        """Handle UTAU export"""
        try:
            from mods.utau_integration import render_to_utau
        except ImportError as e:
            ui.notify(f'UTAU export module not available: {e}', type='warning')
            return
        
        lyrics = self._ui_components['utau_lyrics'].value
        if not lyrics:
            ui.notify('Please enter lyrics for UTAU export', type='warning')
            return
        
        # Build config and export
        # Implementation would integrate with your main app
        ui.notify('UTAU export would be processed here')
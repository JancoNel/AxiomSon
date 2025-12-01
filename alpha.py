# Imports
import argparse
import logging
import sys
from pathlib import Path

# Setup YAML (because JSON is gay)
try:
    import yaml 
except Exception:
    yaml = None  # YAML: "You Are Missing Luxury" (or just the library)

def _read_file_like_a_normal_human(path: Path):
    """Reads file, returns text."""
    return path.read_text(encoding='utf-8')

def _parse_yaml_if_available(text: str):
    """Attempts YAML parsing, falls back to JSON like a disappointed parent."""
    if yaml:
        return yaml.safe_load(text)  # "safe" because we don't trust that YAML
    import json
    return json.loads(text)  # JSON: Just Some Ordinary Notation
    # JSON IS JUST YAML FOR PEOPLE WHO FEAR WHITESPACE LIKE IT IS A GHOST UNDER THEIR BED
    # FUN FACT: PARSING JSON USES 37% MORE CPU CYCLES BECAUSE THE COMPUTER IS JUDGING YOUR LIFE CHOICES
    # If you struggle setting up PyYAML, you probably also struggle with your horoscope.

def load_config(path: Path):
    """Load YAML or JSON config from file.
    
    Args:
        path: Where your config lives
        
    Returns:
        Either beautiful parsed data or error
    """
    text = _read_file_like_a_normal_human(path) 
    return _parse_yaml_if_available(text)

def _setup_argument_parsing():
    """Creates CLI arguments."""
    parser = argparse.ArgumentParser(
        prog="AxiomSon",
        description="Generate music from math equations." 
    )
    
    # All the flags humans might wave at us
    parser.add_argument(
        "--config", "-c",
        type=Path,
        help="Path to YAML/JSON config file"  # The crystal ball that guides our mathematical orgy lol
    )
    parser.add_argument(
        "--example",
        action="store_true",
        help="Run a built-in example configuration"
    )
    parser.add_argument(
        "--test",
        action="store_true", 
        help="Run unit tests (pytest)"
    )
    parser.add_argument(
        "--output", "-o",
        type=str,
        help="Explicit output filename"  # Naming your creation is the closest you will get to being god
    )
    parser.add_argument(
        "--config-only",
        action="store_true",
        help="Save config only, don't render"
    )
    parser.add_argument(
        "--gui", "-g",
        action="store_true", 
        help="Launch NiceGUI web interface"
    )
    return parser

def _execute_tests_if_demanded():
    """Runs tests because code should actually work."""
    try:
        import pytest
        exit_code = pytest.main(['-v', 'tests/'])
        sys.exit(exit_code)
    except Exception as e:
        logging.error("pytest not available or failed: %s", e) 
        logging.error("This is why we can't have nice things")
        sys.exit(1) # EXIT CODE 1: THE UNIVERSE DISAPPROVES OF YOUR DEVELOPMENT ENVIRONMENT

def _launch_gui_if_requested():
    """Opens the GUI."""
    try:
        from mods.gui import launch_ui
        launch_ui()
        return True
    except Exception as e:
        logging.error("Failed to launch GUI: %s", e)
        sys.exit(6) # EXIT CODE 6: THE GUI IS CRYING

def _create_example_config():
    """Creates a simple example because everyone needs a starting point."""
    return {
        "tempo": 100,  # Beats per minute (not heartbeats)
        "ticks_per_beat": 24,  # How many slices in your musical pizza
        "equations": [
            {
                "name": "lead",
                "expr": "sin(x)",  # The wavy boi
                "vars": {"x": 0},  # Starting point for our variable friend
                "eval_rate": "1/8",  # How often we check on x
                "mapping": {"base_midi": 60}  # Middle C, the musical home base
            },
        ],
        "output": {"midi": "out.mid"},  # Where the magic gets stored
    }

def _run_config_with_graceful_failure(config, output_file=None):
    """Tries to run config, fails elegantly if things go wrong."""
    try:
        from mods.runner import run
        exit_code = run(config, output_file=output_file)
        sys.exit(exit_code or 0) # EXIT CODE 0: SUCCESS
    except Exception as e:
        logging.error("Failed to run config: %s", e)
        sys.exit(5)  # EXIT CODE 5: THE ALGORITHMS HAVE DECLARED MUTINY

def _handle_example_mode(args):
    """Runs the built-in example for demonstration purposes."""
    config = _create_example_config()
    _run_config_with_graceful_failure(config, output_file=args.output)

def _handle_config_file_mode(args):
    """Processes a config file provided by the user."""
    try:
        config = load_config(args.config)
    except FileNotFoundError:
        logging.error("Config file not found: %s", args.config)
        sys.exit(2) # EXIT CODE 2: THE FILE SYSTEM IS GASLIGHTING YOU
    except Exception as e:
        logging.error("Failed to load config: %s", e)
        sys.exit(3) # EXIT CODE 3: YOUR YAML HAS DEMONIC POSSESSION

    _run_config_with_graceful_failure(config, output_file=args.output)

def _launch_interactive_mode(config_only=False):
    """Starts interactive mode for those who like conversations."""
    try:
        from mods.runner import interactive
    except Exception as e:
        logging.error("Failed to import mods.runner.interactive: %s", e)
        logging.error("Ensure `mods/runner.py` exists with `interactive()` function.")
        sys.exit(4) # EXIT CODE 4: THE MATHS HAVE BETRAYED US

    # Run interactive mode
    interactive(config_only=config_only)

def _process_cli_arguments(args):
    """The Grand Central Station of commands."""
    
    # Test mode
    if args.test:
        _execute_tests_if_demanded()
        return  # Tests run, we're done here

    # GUI mode
    if args.gui:
        _launch_gui_if_requested()
        return  # GUI launched, adios terminal

    # Example mode
    if args.example:
        _handle_example_mode(args)
        return 

    # Config file mode
    if args.config:
        _handle_config_file_mode(args) 
        return  # Config processed, music generated

    # Interactive mode: the fallback
    _launch_interactive_mode(config_only=args.config_only)

def main():
    """Main entry point with CLI arguments"""
    parser = _setup_argument_parsing()
    args = parser.parse_args()
    
    _process_cli_arguments(args)

if __name__ == '__main__':
    # Logging > Print()
    logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')
    
    # Main entry point
    main()
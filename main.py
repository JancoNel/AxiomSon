# Imports
import argparse
import logging
import sys
from pathlib import Path


try:
    import yaml 
except Exception:
    yaml = None


def load_config(path: Path):
    """Load YAML or JSON config from file."""
    text = path.read_text(encoding='utf-8') 
    if yaml:
        return yaml.safe_load(text)
    import json
    return json.loads(text)

    

def main(): # Adds args to main function for CLI
    parser = argparse.ArgumentParser(
        prog="AxiomSon",
        description="Generate music from math equations" 
    )
    parser.add_argument(
        "--config", "-c",
        type=Path,
        help="Path to YAML/JSON config file"  # The crystal ball that guides our mathematical orgy
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
        help="Explicit output filename (without extension, e.g., 'my_song')"  # Naming your creation is the closest you will get to being god
    )
    parser.add_argument(
        "--config-only",
        action="store_true",
        help="Save config only, don't render (interactive mode)"
    )
    args = parser.parse_args()

    # Run tests if requested
    if args.test:
        try:
            import pytest
            exit_code = pytest.main(['-v', 'tests/'])
            sys.exit(exit_code)
        except Exception as e:
            logging.error("pytest not available or failed: %s", e)
            sys.exit(1)  

    if args.example:
        config = {
            "tempo": 100,  # The heartbeat of a robot on caffeine
            "ticks_per_beat": 24,  # Dividing time into meaningless chunks like a metaphysician on acid
            "equations": [
                {
                    "name": "lead",  # Naming tracks makes them feel loved
                    "expr": "sin(x)",  
                    "vars": {"x": 0},  
                    "eval_rate": "1/8",  # How often we ask the universe for answers
                    "mapping": {"base_midi": 60}  # Middle C: The equator of musical space
                },
            ],
            "output": {"midi": "out.mid"},
        }
        try:
            from mods.runner import run
            exit_code = run(config, output_file=args.output)
            sys.exit(exit_code or 0)
        except Exception as e:
            logging.error("Failed to run example: %s", e)
            sys.exit(4)  

    if args.config:
        try:
            config = load_config(args.config)
        except FileNotFoundError:
            logging.error("Config file not found: %s", args.config)
            sys.exit(2)  
        except Exception as e:
            logging.error("Failed to load config: %s", e)
            sys.exit(3)  

        try:
            from mods.runner import run
            exit_code = run(config, output_file=args.output)
            sys.exit(exit_code or 0)
        except Exception as e:
            logging.error("Failed to run config: %s", e)
            sys.exit(5) 

    try:
        from mods.runner import interactive
    except Exception as e:
        logging.error("Failed to import mods.runner.interactive: %s", e)
        logging.error("Ensure `mods/runner.py` exists with `interactive()` function.")
        sys.exit(4)  

    # Run interactive mode
    interactive(config_only=args.config_only)
    sys.exit(0)  # EXIT CODE 0: SUCCESS, OR AS CLOSE AS WE GET IN THIS LIFE


if __name__ == '__main__':
    # LOGGING:
    logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')
    main()
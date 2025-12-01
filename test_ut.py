# test_utau.py
from mods.utau_exporter import UTAUExporter

def test_utau_export():
    exporter = UTAUExporter()
    
    # Test with some mock notes
    test_notes = [
        {'pitch': 60, 'duration': 0.5, 'lyric': 'a'},
        {'pitch': 62, 'duration': 0.5, 'lyric': 'e'}, 
        {'pitch': 64, 'duration': 1.0, 'lyric': 'i'},
    ]
    
    ust_path = exporter.generate_ust(test_notes, "test lyrics")
    print(f"Generated UST file: {ust_path}")
    
    # Read and display part of the file
    content = ust_path.read_text()
    print("\nFirst few lines of UST:")
    print('\n'.join(content.split('\n')[:15]))

if __name__ == "__main__":
    test_utau_export()
import os
import json
import re


def time_to_seconds(time_str):
    """Convert HH:MM:SS.mmm format to seconds."""
    parts = time_str.strip().split(':')
    hours = int(parts[0])
    minutes = int(parts[1])
    seconds = float(parts[2])
    return hours * 3600 + minutes * 60 + seconds


def process_vtt_file(vtt_path):
    """
    Process VTT subtitle file and return tokenized subtitles.
    
    Returns a list of dictionaries with start time, end time, and tokenized text.
    Token IDs increment across the entire file.
    """
    subtitles = []
    token_id = 1
    
    with open(vtt_path, 'r') as f:
        lines = f.readlines()
    
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        
        # Look for timestamp line (contains -->)
        if ' --> ' in line:
            # Parse timestamps using regex
            match = re.match(r'(\d{2}:\d{2}:\d{2}\.\d{3})\s+-->\s+(\d{2}:\d{2}:\d{2}\.\d{3})', line)
            if match:
                start_time = time_to_seconds(match.group(1))
                end_time = time_to_seconds(match.group(2))
                
                # Read subtitle text (next lines until empty line)
                text_lines = []
                i += 1
                while i < len(lines):
                    text_line = lines[i].strip()
                    if not text_line:
                        break
                    text_lines.append(text_line)
                    i += 1
                
                # Join text and tokenize by spaces
                text = ' '.join(text_lines)
                if text:  # Only process if text is not empty
                    tokens = []
                    for word in text.split():
                        tokens.append({"id": token_id, "text": word})
                        token_id += 1
                    
                    subtitles.append({
                        "start": start_time,
                        "end": end_time,
                        "tokens": tokens
                    })
        
        i += 1
    
    return subtitles


def main():
    """Main function to process VTT file and save to JSON."""
    # Path to the sample VTT file (same folder as this script)
    vtt_path = os.path.join(os.path.dirname(__file__), 'sample.vtt')
    
    # Process the VTT file
    subtitles = process_vtt_file(vtt_path)
    
    # Create data folder if it doesn't exist
    data_dir = os.path.join(os.path.dirname(__file__), '..', 'data')
    os.makedirs(data_dir, exist_ok=True)
    
    # Save to JSON
    output_path = os.path.join(data_dir, 'subs.json')
    with open(output_path, 'w') as f:
        json.dump(subtitles, f, indent=2)
    
    print(f"Successfully processed {len(subtitles)} subtitles and saved to {output_path}")


if __name__ == '__main__':
    main()

      
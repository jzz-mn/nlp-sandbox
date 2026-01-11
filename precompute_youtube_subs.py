"""
Preprocess raw YouTube subtitles for word-level lookup.

This script loads the raw YouTube subtitle JSON and extracts individual words
with their precise timing information. Useful for building word-level search
and synchronization without runtime API calls.

Not for production use.
"""

import os
import json


def load_raw_subtitles(input_path):
    """
    Load raw YouTube subtitles from JSON file.
    
    Args:
        input_path: path to data/raw_youtube.json
    
    Returns:
        dict: Parsed JSON data from YouTube API, or None if file doesn't exist
    """
    if not os.path.exists(input_path):
        print(f"Error: File not found at {input_path}")
        return None
    
    try:
        with open(input_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON in {input_path}")
        return None


def ms_to_seconds(milliseconds):
    """Convert milliseconds to seconds."""
    return milliseconds / 1000.0


def extract_text_from_segments(segs):
    """
    Extract text from YouTube subtitle segment array.
    
    Args:
        segs: list of segment objects, each with 'utf8' field
    
    Returns:
        str: Concatenated text from all segments with spaces between words
    """
    if not segs:
        return ""
    
    text_parts = []
    for seg in segs:
        if isinstance(seg, dict) and "utf8" in seg:
            text_parts.append(seg["utf8"])
    
    # Join with spaces instead of concatenating directly
    return " ".join(text_parts).strip()


def precompute_subtitles(raw_data):
    """
    Extract word-level timing from raw YouTube subtitle data.
    
    Args:
        raw_data: dict with 'events' array from YouTube API
    
    Returns:
        dict: Words array with word_id, word, start, end, sentence_id
    """
    words = []
    word_id = 1
    sentence_id = 0
    
    # Check if events array exists
    if not raw_data or "events" not in raw_data:
        print("Warning: No events found in subtitle data")
        return {"words": words}
    
    events = raw_data["events"]
    
    # Iterate through each subtitle event (sentence)
    for event in events:
        # Skip events without timing information
        if "tStartMs" not in event or "dDurationMs" not in event:
            continue
        
        # Skip events without segments
        if "segs" not in event or not event["segs"]:
            continue
        
        # Extract timing information
        start_ms = int(event["tStartMs"])
        duration_ms = int(event["dDurationMs"])
        
        start_seconds = ms_to_seconds(start_ms)
        end_seconds = ms_to_seconds(start_ms + duration_ms)
        
        # Extract text from all segments in this event
        text = extract_text_from_segments(event["segs"])
        
        # Skip empty text
        if not text:
            continue
        
        # Tokenize text by whitespace
        word_tokens = text.split()
        
        # Create word entry for each token
        for word in word_tokens:
            if word:  # Skip empty tokens
                word_entry = {
                    "word_id": word_id,
                    "word": word,
                    "start": start_seconds,
                    "end": end_seconds,
                    "sentence_id": sentence_id
                }
                words.append(word_entry)
                word_id += 1
        
        # Increment sentence ID for next event
        sentence_id += 1
    
    return {"words": words}


def save_precomputed_subtitles(data, output_path):
    """
    Save precomputed word-level subtitles to JSON file.
    
    Args:
        data: dict containing words array
        output_path: path where to save the JSON file
    """
    # Create data directory if it doesn't exist
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # Write JSON to file with indentation for readability
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print(f"Saved precomputed subtitles to {output_path}")


def print_summary(precomputed_data):
    """
    Print summary of precomputed subtitles.
    
    Args:
        precomputed_data: dict with words array
    """
    words_list = precomputed_data.get("words", [])
    num_words = len(words_list)
    
    print("\n" + "="*50)
    print("Subtitle Precomputation Summary")
    print("="*50)
    print(f"Total words extracted: {num_words}")
    
    if words_list:
        print(f"First word: {words_list[0]['word']}")
        print(f"Last word: {words_list[-1]['word']}")
        max_sentence_id = max(w.get("sentence_id", 0) for w in words_list)
        print(f"Total sentences: {max_sentence_id + 1}")
    
    print("="*50 + "\n")


def main():
    """Main function to preprocess YouTube subtitles."""
    # Define input and output paths (relative to this script's directory)
    script_dir = os.path.dirname(__file__)
    input_path = os.path.join(script_dir, "data", "raw_youtube.json")
    output_path = os.path.join(script_dir, "data", "subs_precomputed.json")
    
    print("Loading raw YouTube subtitles...")
    
    # Load raw subtitle data
    raw_data = load_raw_subtitles(input_path)
    if raw_data is None:
        print("Failed to load raw subtitles. Exiting.")
        return
    
    # Precompute word-level timing
    precomputed_data = precompute_subtitles(raw_data)
    
    # Save precomputed subtitles
    save_precomputed_subtitles(precomputed_data, output_path)
    
    # Print summary
    print_summary(precomputed_data)


if __name__ == "__main__":
    main()

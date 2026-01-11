"""
Fetch YouTube subtitles using yt-dlp (more reliable than YouTube API).

This script uses yt-dlp to download subtitles and converts them to the
YouTube API json3 format for compatibility with precompute_youtube_subs.py

Not for production use.
"""

import os
import json
import subprocess
import re
import glob


# Hardcoded YouTube video ID to fetch subtitles for
VIDEO_ID = "inNYQUC6dFs"


def get_available_languages(video_id):
    """Check what subtitle languages are available for a video."""
    url = f"https://www.youtube.com/watch?v={video_id}"
    
    try:
        result = subprocess.run(
            ["yt-dlp", "--list-subs", "--no-warnings", url],
            capture_output=True,
            text=True,
            timeout=15
        )
        
        print("Available subtitles:")
        print(result.stdout)
        return result.stdout
    
    except Exception as e:
        print(f"Error checking available languages: {e}")
        return None


def fetch_subtitles_with_ytdlp(video_id, lang="en", auto_generated=False):
    """Fetch YouTube subtitles using yt-dlp."""
    url = f"https://www.youtube.com/watch?v={video_id}"
    
    try:
        caption_type = "auto-generated" if auto_generated else "manual"
        print(f"Fetching {caption_type} {lang} subtitles using yt-dlp for {video_id}...")
        
        # Use yt-dlp to fetch subtitles in VTT format
        args = [
            "yt-dlp",
            "--skip-download",
            "-o", "/tmp/yt_subtitle",
            url
        ]
        
        # Add appropriate subtitle flag
        if auto_generated:
            args.insert(1, "--write-auto-subs")
        else:
            args.insert(1, "--write-subs")
        
        # Add language selection
        args.insert(2, "--sub-langs")
        args.insert(3, lang)
        
        result = subprocess.run(
            args,
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if "no subtitles" in result.stdout.lower() or "no subtitles" in result.stderr.lower():
            print(f"No {caption_type} captions available in {lang}")
            return None
        
        # Check what files exist in /tmp
        tmp_files = glob.glob("/tmp/yt_subtitle*")
        print(f"Files created: {tmp_files}")
        
        if not tmp_files:
            print(f"No subtitle files created")
            return None
        
        # Read the first subtitle file found
        subtitle_file = tmp_files[0]
        print(f"Reading from: {subtitle_file}")
        
        with open(subtitle_file, 'r', encoding='utf-8') as f:
            subtitle_data = f.read()
        
        # Clean up all temp files
        for tmp_file in tmp_files:
            try:
                os.remove(tmp_file)
            except:
                pass
        
        return subtitle_data
    
    except Exception as e:
        print(f"Error fetching subtitles: {e}")
        return None


def parse_vtt_to_youtube_format(vtt_text):
    """Convert VTT subtitle format to YouTube API json3 format."""
    events = []
    lines = vtt_text.strip().split('\n')
    
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        
        # Look for timestamp line (contains -->)
        if ' --> ' in line:
            # Parse VTT timestamp format: HH:MM:SS.mmm --> HH:MM:SS.mmm
            match = re.match(r'(\d{2}):(\d{2}):(\d{2})\.(\d{3})\s+-->\s+(\d{2}):(\d{2}):(\d{2})\.(\d{3})', line)
            
            if match:
                # Convert to milliseconds
                start_h, start_m, start_s, start_ms = int(match.group(1)), int(match.group(2)), int(match.group(3)), int(match.group(4))
                end_h, end_m, end_s, end_ms = int(match.group(5)), int(match.group(6)), int(match.group(7)), int(match.group(8))
                
                start_ms_total = (start_h * 3600 + start_m * 60 + start_s) * 1000 + start_ms
                end_ms_total = (end_h * 3600 + end_m * 60 + end_s) * 1000 + end_ms
                duration_ms = end_ms_total - start_ms_total
                
                # Read subtitle text (next non-empty lines until empty line)
                text_parts = []
                i += 1
                while i < len(lines):
                    text_line = lines[i].strip()
                    if not text_line:
                        break
                    # Add each line as a separate text part
                    if text_line:
                        text_parts.append(text_line)
                    i += 1
                
                # Join all text parts with space
                full_text = ' '.join(text_parts)
                
                # Clean up VTT formatting codes (e.g., <c>, </c>, <00:00:11.440>)
                # Remove color/styling tags
                full_text = re.sub(r'<c[^>]*>', '', full_text)
                full_text = re.sub(r'</c>', '', full_text)
                # Remove timestamp codes
                full_text = re.sub(r'<\d{2}:\d{2}:\d{2}\.\d{3}>', '', full_text)
                # Remove any other XML-like tags
                full_text = re.sub(r'<[^>]+>', '', full_text)
                
                if full_text:
                    # Tokenize by whitespace, preserving all words
                    words = full_text.split()
                    
                    # Create YouTube API format event with individual words
                    segs = [{"utf8": word} for word in words if word]
                    
                    if segs:  # Only add event if it has words
                        event = {
                            "tStartMs": str(int(start_ms_total)),
                            "dDurationMs": str(int(duration_ms)),
                            "segs": segs
                        }
                        events.append(event)
        
        i += 1
    
    return {
        "responseContext": {
            "serviceTrackingParams": []
        },
        "events": events
    }


def save_subtitles(data, output_path):
    """Save subtitle JSON to file."""
    # Create directory if it doesn't exist
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # Write JSON to file with indentation for readability
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print(f"Saved subtitles to {output_path}")


def print_summary(video_id, subtitle_data, lang="en"):
    """Print a summary of fetched subtitles."""
    print("\n" + "="*50)
    print("YouTube Subtitle Fetch Summary (yt-dlp)")
    print("="*50)
    print(f"Video ID: {video_id}")
    print(f"Language: {lang}")
    
    # Count subtitle events from the JSON response
    if subtitle_data and "events" in subtitle_data:
        num_events = len(subtitle_data["events"])
        print(f"Number of subtitle events: {num_events}")
    else:
        print("Number of subtitle events: 0 (no subtitle data)")
    
    print("="*50 + "\n")


def main():
    """Main function to orchestrate subtitle fetching."""
    print(f"Checking subtitles available for video: {VIDEO_ID}\n")
    
    # First, check what languages are available
    get_available_languages(VIDEO_ID)
    
    print("\n" + "="*50)
    print("Fetching Korean subtitles...")
    print("="*50 + "\n")
    
    # Fetch subtitles using yt-dlp (try manual Korean first)
    vtt_text = fetch_subtitles_with_ytdlp(VIDEO_ID, lang="ko", auto_generated=False)
    
    # If manual Korean not available, try auto-generated Korean
    if vtt_text is None:
        print("\nManual Korean not available, trying auto-generated Korean...")
        vtt_text = fetch_subtitles_with_ytdlp(VIDEO_ID, lang="ko", auto_generated=True)
    
    # If Korean not available, try auto-generated English
    if vtt_text is None:
        print("\nKorean not available, trying auto-generated English...")
        vtt_text = fetch_subtitles_with_ytdlp(VIDEO_ID, lang="en", auto_generated=True)
    
    # If fetch was unsuccessful, exit
    if vtt_text is None:
        print("Failed to fetch subtitles. Exiting.")
        return
    
    # Convert VTT format to YouTube API format
    subtitle_data = parse_vtt_to_youtube_format(vtt_text)
    
    # Define output path (relative to this script's directory)
    output_path = os.path.join(
        os.path.dirname(__file__),
        "data",
        "raw_youtube.json"
    )
    
    # Save the converted JSON response
    save_subtitles(subtitle_data, output_path)
    
    # Print summary
    print_summary(VIDEO_ID, subtitle_data, lang="en")


if __name__ == "__main__":
    main()

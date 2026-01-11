"""
Process any YouTube video URL and generate interactive subtitles.

Usage:
    python process_video.py "https://www.youtube.com/watch?v=VIDEO_ID"
    python process_video.py "youtu.be/VIDEO_ID"

This script:
1. Extracts the video ID from the URL
2. Fetches subtitles using yt-dlp
3. Preprocesses into word-level timing data
4. Generates interactive HTML ready to view

Not for production use.
"""

import os
import sys
import re
import subprocess


def extract_video_id(url):
    """Extract YouTube video ID from various URL formats."""
    patterns = [
        r'youtu\.be/([a-zA-Z0-9_-]{11})',
        r'youtube\.com/watch\?v=([a-zA-Z0-9_-]{11})',
        r'youtube\.com/embed/([a-zA-Z0-9_-]{11})',
        r'^([a-zA-Z0-9_-]{11})$'  # Just the ID
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    
    return None


def update_script_variable(script_path, variable_name, new_value):
    """Update a variable in a Python script."""
    with open(script_path, 'r') as f:
        content = f.read()
    
    # Replace the variable assignment
    pattern = f'{variable_name} = ".*?"'
    replacement = f'{variable_name} = "{new_value}"'
    new_content = re.sub(pattern, replacement, content)
    
    with open(script_path, 'w') as f:
        f.write(new_content)


def run_command(cmd, description):
    """Run a shell command and report status."""
    print(f"\n{'='*60}")
    print(f"📍 {description}")
    print(f"{'='*60}")
    
    result = subprocess.run(cmd, shell=True)
    
    if result.returncode != 0:
        print(f"❌ Failed: {description}")
        return False
    
    print(f"✅ Success: {description}")
    return True


def main():
    """Main workflow."""
    print("\n" + "="*60)
    print("🎬 YouTube Subtitle Processor")
    print("="*60)
    
    # Get video URL from command line or prompt
    if len(sys.argv) > 1:
        video_url = sys.argv[1]
    else:
        video_url = input("\n🎥 Enter YouTube URL or video ID: ").strip()
    
    if not video_url:
        print("❌ No URL provided. Exiting.")
        return
    
    # Extract video ID
    video_id = extract_video_id(video_url)
    
    if not video_id:
        print("❌ Invalid YouTube URL. Please use formats like:")
        print("   - https://www.youtube.com/watch?v=...")
        print("   - https://youtu.be/...")
        print("   - Just the video ID (11 characters)")
        return
    
    print(f"\n✨ Extracted video ID: {video_id}")
    
    # Get script directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    fetch_script = os.path.join(script_dir, 'fetch_youtube_subs_ytdlp.py')
    precompute_script = os.path.join(script_dir, 'precompute_youtube_subs.py')
    
    # Update VIDEO_ID in fetch script
    print(f"\n🔧 Updating fetch script with video ID...")
    try:
        update_script_variable(fetch_script, 'VIDEO_ID', video_id)
        print("✅ Updated fetch_youtube_subs_ytdlp.py")
    except Exception as e:
        print(f"❌ Failed to update script: {e}")
        return
    
    # Fetch subtitles
    if not run_command(f'cd "{script_dir}" && python fetch_youtube_subs_ytdlp.py', 
                      'Fetching subtitles from YouTube'):
        return
    
    # Precompute word-level data
    if not run_command(f'cd "{script_dir}" && python precompute_youtube_subs.py',
                      'Preprocessing subtitles'):
        return
    
    # Success!
    print("\n" + "="*60)
    print("✅ COMPLETE!")
    print("="*60)
    print(f"\n📺 Video ID: {video_id}")
    print(f"📁 Data saved to: data/subs_precomputed.json")
    print(f"🌐 Open index.html in your browser to view interactive subtitles")
    print("\n" + "="*60 + "\n")


if __name__ == "__main__":
    main()

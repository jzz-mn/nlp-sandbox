"""
Fetch YouTube subtitles for reverse-engineering and learning.

This script fetches raw subtitles from YouTube's API without any processing.
It's for understanding how subtitles are structured before tokenization.

Not for production use.
"""

import os
import json
import requests


# Hardcoded YouTube video ID to fetch subtitles for
# Using a popular video that reliably has Korean subtitles
VIDEO_ID = "5HemFxI89q8"  # Korean vlog with Korean CC


def fetch_youtube_subtitles(video_id, lang="ko"):
    """
    Fetch raw YouTube subtitles using the timedtext API.
    
    Args:
        video_id: YouTube video ID (string)
        lang: Language code (default: 'ko' for Korean)
    
    Returns:
        dict: Raw JSON response from YouTube API, or None if unavailable
    """
    # YouTube's timedtext endpoint for fetching subtitles
    url = "https://www.youtube.com/api/timedtext"
    
    # Parameters required by YouTube API
    params = {
        "v": video_id,
        "lang": lang,
        "fmt": "json3"
    }
    
    # Headers to mimic a browser request (required by YouTube)
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    
    try:
        # Make the request to YouTube's API with headers
        response = requests.get(url, params=params, headers=headers, timeout=10)
        
        # Check if request was successful
        if response.status_code == 200:
            # Check if response has content
            if not response.text:
                print(f"Error: YouTube returned empty response")
                print("This video may not have subtitles available in Korean.")
                print(f"Response content length: {len(response.text)}")
                return None
            
            # Parse and return the JSON response
            data = response.json()
            return data
        else:
            print(f"Error: YouTube returned status code {response.status_code}")
            print("Subtitles may not be available for this video in the requested language.")
            return None
    
    except requests.exceptions.RequestException as e:
        print(f"Error fetching subtitles: {e}")
        return None
    except ValueError as e:
        print(f"Error parsing JSON response: {e}")
        print("This video may not have subtitles available in the requested language.")
        return None


def save_subtitles(data, output_path):
    """
    Save raw subtitle JSON to file.
    
    Args:
        data: dict containing subtitle data
        output_path: path where to save the JSON file
    """
    # Create directory if it doesn't exist
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # Write JSON to file with indentation for readability
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print(f"Saved raw subtitles to {output_path}")


def print_summary(video_id, subtitle_data):
    """
    Print a summary of fetched subtitles.
    
    Args:
        video_id: YouTube video ID
        subtitle_data: dict containing the raw subtitle JSON
    """
    print("\n" + "="*50)
    print("YouTube Subtitle Fetch Summary")
    print("="*50)
    print(f"Video ID: {video_id}")
    
    # Count subtitle events from the JSON response
    if subtitle_data and "events" in subtitle_data:
        num_events = len(subtitle_data["events"])
        print(f"Number of subtitle events: {num_events}")
    else:
        print("Number of subtitle events: 0 (no subtitle data)")
    
    print("="*50 + "\n")


def main():
    """Main function to orchestrate subtitle fetching."""
    print(f"Fetching subtitles for video: {VIDEO_ID}")
    
    # Fetch subtitles from YouTube (try Korean first)
    subtitle_data = fetch_youtube_subtitles(VIDEO_ID, lang="ko")
    
    # If fetch was unsuccessful, exit
    if subtitle_data is None:
        print("Failed to fetch subtitles. Exiting.")
        return
    
    # Define output path (relative to this script's directory)
    output_path = os.path.join(
        os.path.dirname(__file__),
        "data",
        "raw_youtube.json"
    )
    
    # Save the raw JSON response
    save_subtitles(subtitle_data, output_path)
    
    # Print summary
    print_summary(VIDEO_ID, subtitle_data)


if __name__ == "__main__":
    main()

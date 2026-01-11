# 🧪 Local DASH + Dictionary Test Guide

> **Netflix-style subtitle + dictionary integration, safely tested with local resources**

## Table of Contents

1. [Quick Start](#quick-start)
2. [Setup Instructions](#setup-instructions)
3. [Test Scenarios](#test-scenarios)
4. [Verification Checklist](#verification-checklist)
5. [Troubleshooting](#troubleshooting)

---

## Quick Start

### Option A: Minimal Setup (HTML + Subtitles Only)

```bash
# 1. Files already exist:
ls data/local_subs_ko.json    # Korean subtitles (11 words)
ls data/local_subs_en.json    # English subtitles (11 words)

# 2. Open dash-test-player.html in browser
open dash-test-player.html

# 3. Enter video file: sample.mp4
# 4. Select subtitle: Korean (local_subs_ko.json)
# 5. Click "Load & Play"
```

### Option B: Full DASH Setup (Advanced)

Requires ffmpeg to create DASH manifest:

```bash
# 1. Install ffmpeg (if needed)
brew install ffmpeg

# 2. Create DASH manifest from sample video
ffmpeg -i sample.mp4 -map 0:v -map 0:a \
  -f dash -seg_duration 2 \
  -init_seg_name init-\$RepresentationID\$.mp4 \
  -media_seg_name segment-\$RepresentationID\$-\$Number%05d\$.m4s \
  out/manifest.mpd

# 3. Serve files locally
python3 -m http.server 8000

# 4. Load in dash-test-player.html:
#    Video: http://localhost:8000/out/manifest.mpd
```

---

## Setup Instructions

### 1. Verify Files Exist

```bash
# Check all required files
ls -la
```

**Files you should have:**

```
✅ data/local_subs_ko.json      # Korean (11 words, 0-11s)
✅ data/local_subs_en.json      # English (11 words, 0-11s)
✅ data/subs_precomputed.json   # YouTube example
✅ subtitle-dictionary.js        # Core module (501 lines)
✅ dash-test-player.html        # Test interface (THIS FILE)
✅ player-simple.html            # Simple example
✅ sample.mp4                    # Your sample video (optional)
```

### 2. Choose Video Source

**Option A: MP4 File (Simplest)**
- Use any `.mp4` or `.webm` file
- No conversion needed
- Supports playback in modern browsers

**Option B: DASH Manifest (Netflix-like)**
- Requires ffmpeg for initial setup
- Creates streaming segments
- More realistic testing

**Option C: YouTube URL (via embed)**
- Use in `player-simple.html`
- Limited subtitle access

### 3. Serve Files Locally

```bash
# Start simple HTTP server
python3 -m http.server 8000

# Or using Node.js
npx http-server -p 8000

# Or using Python 2
python -m SimpleHTTPServer 8000
```

Access at: `http://localhost:8000/dash-test-player.html`

### 4. Load Player

In the test interface:

```
1. Video Source: sample.mp4 (or your video)
2. Subtitle Source: Korean (local_subs_ko.json)
3. Click "Load & Play"
```

---

## Test Scenarios

### Test 1: Video Loading ✅

**Purpose:** Verify video playback works

**Steps:**
1. Click "Test MP4" button
2. See video metadata loaded
3. Confirm duration displays

**Expected Result:**
```
✅ MP4 file loaded successfully
Duration: [X] seconds
```

---

### Test 2: Subtitle Loading ✅

**Purpose:** Verify subtitle parsing

**Steps:**
1. Click "Korean", "English", or "YouTube" buttons
2. View parsed subtitle data

**Expected Result:**
```
✅ Successfully loaded 11 words
Format: Precomputed
Size: [X] KB
Words:안녕하세요, 반갑습니다, ...
```

---

### Test 3: Dictionary Integration ✅

**Purpose:** Verify word lookup works

**Steps:**
1. Enter word: `안녕`
2. Click "Lookup Word"
3. View definition from API

**Expected Result:**
```
✅ Found 3 definitions in 250ms
안녕 → Hello, Hi, Goodbye
```

**Test Multiple Words:**
- `날씨` (weather)
- `음식` (food)
- `문화` (culture)
- `한국` (Korea)

---

### Test 4: Cache Performance ⚡

**Purpose:** Verify smart caching (sub-1ms lookups)

**Steps:**
1. Click "Run Benchmark"
2. View timing comparison

**Expected Result:**
```
✅ Benchmark Complete
First Lookup: 250ms
Cached Lookup: <1ms
Speedup: ~250x
```

**Cache Features:**
- LRU eviction (max 500 words)
- Automatic on repeat access
- Manual clear available

---

### Test 5: Video/Subtitle Sync ⏱️

**Purpose:** Verify words update in real-time with playback

**Steps:**
1. Click "Load & Play"
2. Watch video play
3. Observe subtitle words changing
4. Click "Test Sync"

**Expected Result:**
```
✅ Timing sync verified
Words updating in real-time
No lag detected
```

**Manual Verification:**
```
- Word 1: 0.0s - 1.0s  (안녕하세요)
- Word 2: 1.0s - 2.0s  (반갑습니다)
- Word 3: 2.0s - 3.0s  (오늘)
... etc
```

---

### Test 6: Error Handling ⚠️

**Purpose:** Verify graceful error handling

**Steps:**

1. **Missing File:**
   - Click "Missing File"
   - See proper error message

2. **Invalid JSON:**
   - Click "Invalid JSON"
   - See JSON parse error

3. **Network Error:**
   - Click "Network Error"
   - See connection error

**Expected Result:**
```
✅ All errors handled gracefully
No crashes
Helpful error messages
```

---

## Verification Checklist

### Core Features

- [ ] Video loads and plays
- [ ] Subtitles load (11 words)
- [ ] Video/subtitle timing syncs
- [ ] Words display in real-time

### Dictionary Integration

- [ ] Dictionary lookups work
- [ ] Multiple words can be tested
- [ ] Results display correctly
- [ ] API responds with definitions

### Caching

- [ ] First lookup: ~250ms
- [ ] Cached lookups: <1ms
- [ ] Cache can be cleared
- [ ] Cache shows correct size

### Performance

- [ ] No lag during playback
- [ ] Smooth tooltip animations
- [ ] Responsive UI
- [ ] Quick word highlighting

### Error Handling

- [ ] Missing files handled
- [ ] Invalid JSON handled
- [ ] Network errors handled
- [ ] Graceful fallbacks

### Cross-Language

- [ ] Korean subtitles work
- [ ] English subtitles work
- [ ] Language auto-detection
- [ ] Dual-language display (if enabled)

---

## Troubleshooting

### Video Won't Load

**Problem:** "Error loading video"

**Solutions:**
```bash
# 1. Check file path
ls sample.mp4

# 2. Verify format
file sample.mp4

# 3. Test with MP4 codec
ffprobe sample.mp4

# 4. Convert if needed
ffmpeg -i input.webm -c:v libx264 sample.mp4
```

### Subtitles Not Displaying

**Problem:** "Subtitles loaded but not visible"

**Solutions:**
1. Check browser console (F12)
2. Verify subtitle file path
3. Confirm JSON format:
   ```json
   [
     {"word_id": 0, "word": "텍스트", "start": 0.0, "end": 1.0, "sentence_id": 0}
   ]
   ```
4. Load player again

### Dictionary Lookups Failing

**Problem:** "API Error" or "Network Error"

**Solutions:**
```bash
# 1. Test API directly
curl "https://api-cdn-plus.dioco.io/base_dict_getHoverDict_8?form=안녕&sl=ko&tl=en"

# 2. Check internet connection
ping 8.8.8.8

# 3. Clear browser cache
# Cmd+Shift+Delete (or Ctrl+Shift+Delete)

# 4. Try different word
# Some words may return empty results
```

### Cache Not Working

**Problem:** "All lookups taking 250ms"

**Solutions:**
1. Click "Clear Cache" button
2. Try same word twice
3. Check browser DevTools → Application → Cache Storage
4. Verify cache max size: 500 words

### DASH Manifest Issues

**Problem:** "Invalid manifest file"

**Solutions:**
```bash
# 1. Check manifest validity
xmllint out/manifest.mpd

# 2. Verify segments exist
ls -la out/*.m4s

# 3. Regenerate if needed
ffmpeg -i sample.mp4 -f dash out/manifest.mpd

# 4. Use absolute paths in manifest
# Or serve from web server
python3 -m http.server 8000
```

### Browser Compatibility

**Supported Browsers:**
- Chrome/Edge 60+
- Firefox 55+
- Safari 11+
- Opera 47+

**Not Supported:**
- IE 11 (no ES6 support)

---

## Advanced: Creating DASH Manifest

### Full DASH Setup

```bash
# 1. Create output directory
mkdir -p out

# 2. Generate DASH manifest with multiple bitrates (optional)
ffmpeg -i sample.mp4 \
  -filter:v scale=1920:1080 \
  -b:v 5000k -maxrate 5000k -bufsize 10000k \
  -c:v libx264 -preset medium \
  -map 0:a -c:a aac -b:a 128k \
  -f dash -seg_duration 2 \
  out/manifest.mpd

# 3. Verify manifest created
cat out/manifest.mpd

# 4. Serve locally
cd out && python3 -m http.server 9000
```

### Test with DASH

```
Video URL: http://localhost:9000/manifest.mpd
Subtitle: data/local_subs_ko.json
Click "Load & Play"
```

---

## Example Test Flow

### Complete Test Sequence (5 minutes)

```
1. Load Player (30s)
   - Open dash-test-player.html
   - Load sample.mp4 + Korean subtitles
   
2. Test Video Loading (30s)
   - Click "Test MP4"
   - Verify file loaded

3. Test Subtitles (30s)
   - Click "Korean"
   - See 11 words loaded
   - Duration: 0-11 seconds

4. Test Dictionary (60s)
   - Enter word: 안녕
   - Click "Lookup Word"
   - See definition
   - Try 3-4 different words

5. Test Cache (60s)
   - Click "Run Benchmark"
   - See 250ms → <1ms improvement
   - Click "Test Cache Size"

6. Test Sync (60s)
   - Click "Load & Play"
   - Play video for ~3 seconds
   - Watch words highlight in real-time
   - Pause and observe sync

7. Error Handling (30s)
   - Click "Missing File"
   - Click "Invalid JSON"
   - Click "Network Error"
   - See error messages

Total Time: ~5 minutes
```

---

## Success Criteria

### All Tests Pass ✅

When these conditions are met, your setup is working:

```
✅ Video loads and plays
✅ All 11 subtitle words display
✅ Dictionary lookups return results
✅ Words sync with video timing
✅ Cache provides <1ms lookups
✅ Errors handled gracefully
✅ No console errors (F12)
```

### Ready for Production

If all above are satisfied:

1. **Module is production-ready** ✅
2. **Dictionary API is functional** ✅
3. **Caching system works** ✅
4. **Error handling is robust** ✅
5. **Performance meets targets** ✅

---

## Next Steps

### After Successful Testing

1. **Deploy to server:**
   ```bash
   git add dash-test-player.html
   git commit -m "Add comprehensive DASH + dictionary test suite"
   git push
   ```

2. **Integrate into main player:**
   ```javascript
   // Use SubtitleDictionary module in any player
   const dict = new SubtitleDictionary({
     videoSelector: '#my-video',
     subtitleSource: 'my-subtitles.json',
     language: 'ko',
     targetLanguage: 'en'
   });
   await dict.init();
   ```

3. **Add more videos:**
   - Create DASH manifests for multiple videos
   - Add multi-language subtitle tracks
   - Test with longer videos (10+ minutes)

4. **Optimize performance:**
   - Benchmark with large subtitle files
   - Test mobile performance
   - Profile cache hit rates

---

## Support

**For issues:**
1. Check troubleshooting section
2. Review browser console (F12)
3. Test individual components
4. Verify file paths and formats

**Files to check:**
- `subtitle-dictionary.js` - Core module
- `data/local_subs_ko.json` - Test data
- `dash-test-player.html` - Test interface

---

**Happy Testing! 🚀**

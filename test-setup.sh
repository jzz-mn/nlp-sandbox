#!/bin/bash

# 🧪 DASH + Dictionary Test Setup Script
# ========================================
# 
# This script verifies your local DASH + dictionary testing environment
# and shows you how to start testing.

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🧪 Local DASH + Dictionary Test Environment"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Check required files
echo "📋 Checking required files..."
echo ""

files=(
  "subtitle-dictionary.js:Core module"
  "dash-test-player.html:Test interface"
  "DASH_TEST_GUIDE.md:Testing guide"
  "data/local_subs_ko.json:Korean subtitles"
  "data/local_subs_en.json:English subtitles"
  "data/subs_precomputed.json:YouTube example"
)

for file_desc in "${files[@]}"; do
  IFS=':' read -r file desc <<< "$file_desc"
  if [ -f "$file" ]; then
    size=$(ls -lh "$file" | awk '{print $5}')
    echo "  ✅ $file ($size) - $desc"
  else
    echo "  ❌ $file - MISSING"
  fi
done

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🚀 Quick Start"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

echo "Option 1: Open directly in browser"
echo "  → Open dash-test-player.html in your web browser"
echo "  → Load sample.mp4 + Korean subtitles"
echo "  → Click 'Load & Play'"
echo ""

echo "Option 2: Start local web server"
echo "  → Run: python3 -m http.server 8000"
echo "  → Open: http://localhost:8000/dash-test-player.html"
echo "  → Load sample.mp4 + Korean subtitles"
echo ""

echo "Option 3: Full DASH setup"
echo "  → Install ffmpeg: brew install ffmpeg"
echo "  → Create manifest: ffmpeg -i sample.mp4 -f dash out/manifest.mpd"
echo "  → Start server: python3 -m http.server 8000"
echo "  → Load: http://localhost:8000/out/manifest.mpd"
echo ""

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ Test Plan (6 Modules)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

tests=(
  "🎥 Test 1: Video Loading|Load MP4, DASH, HLS streams"
  "📖 Test 2: Subtitle Loading|Parse Korean, English, YouTube"
  "📚 Test 3: Dictionary|Live API lookups (dioco.io)"
  "⚡ Test 4: Cache Performance|Benchmark cache speedup"
  "⏱️ Test 5: Timing Sync|Video/subtitle alignment"
  "⚠️ Test 6: Error Handling|Missing files, invalid JSON"
)

counter=1
for test_desc in "${tests[@]}"; do
  IFS='|' read -r header desc <<< "$test_desc"
  echo "$header"
  echo "   $desc"
  echo ""
done

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📚 Subtitle Data"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

echo "Korean Subtitles (11 words, 0-11 seconds):"
echo "  1. 안녕하세요 (Hello) - 0.0-1.0s"
echo "  2. 반갑습니다 (Nice to meet) - 1.0-2.0s"
echo "  3. 오늘 (Today) - 2.0-3.0s"
echo "  4. 날씨 (Weather) - 3.0-4.0s"
echo "  5. 좋네요 (It's nice) - 4.0-5.0s"
echo "  6. 맛있는 (Delicious) - 5.0-6.0s"
echo "  7. 음식 (Food) - 6.0-7.0s"
echo "  8. 먹었어요 (I ate) - 7.0-8.0s"
echo "  9. 한국 (Korea) - 8.0-9.0s"
echo "  10. 문화 (Culture) - 9.0-10.0s"
echo "  11. 흥미로워요 (It's interesting) - 10.0-11.0s"
echo ""

echo "English Subtitles (parallel, same timing)"
echo "  1. Hello - 0.0-1.0s"
echo "  2. Nice - 1.0-2.0s"
echo "  3. to - 2.0-3.0s"
echo "  ... etc"
echo ""

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🎯 Success Criteria"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

criteria=(
  "✅ Video loads and plays"
  "✅ All 11 subtitle words display"
  "✅ Dictionary lookups work (dioco.io API)"
  "✅ Words sync with video timing"
  "✅ Cache provides <1ms lookups"
  "✅ Errors handled gracefully"
  "✅ No console errors (F12)"
)

for criterion in "${criteria[@]}"; do
  echo "  $criterion"
done

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📖 Documentation"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Read DASH_TEST_GUIDE.md for:"
echo "  • Detailed setup instructions"
echo "  • Step-by-step test procedures"
echo "  • Verification checklist"
echo "  • Troubleshooting guide"
echo "  • DASH manifest creation"
echo "  • Complete test flow"
echo ""

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "💡 Next Steps"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "1. Open dash-test-player.html in browser"
echo "2. Click 'Load & Play' (uses sample.mp4 + Korean subtitles)"
echo "3. Run through all 6 test modules"
echo "4. Verify all success criteria"
echo "5. Check GitHub: https://github.com/jzz-mn/nlp-sandbox"
echo ""

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✨ Ready to test! Start with dash-test-player.html"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

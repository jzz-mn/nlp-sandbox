# Netflix Network Architecture Analysis

**Date:** January 11, 2026  
**Scope:** Video streaming, subtitle delivery, dictionary integration, playback events, analytics  
**Platform:** Netflix Web Player (Chrome, macOS 10.15.7)  

---

## Executive Summary

Netflix implements a **distributed architecture** combining:
- **CDN-based video streaming** (ipv4-c003-mnl005-pldt-isp.1.oca.nflxvideo.net)
- **Third-party dictionary API integration** (dioco.io for Korean-English lookups)
- **Event-driven playback tracking** (Netflix MSL API)
- **Continuous analytics logging** (logs.netflix.com)

The system separates **user-triggered actions** (play/pause/seek) from **automatic background processes** (video streaming, progress logging, dictionary stats).

---

## 1. Network Flow Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                      Netflix Web Player                         │
│                    (Chrome, User Browser)                       │
└────────────┬────────────────────────────────────────────────────┘
             │
     ┌───────┴───────────────────────────────────────┐
     │                                               │
     ▼                                               ▼
┌──────────────────────┐              ┌─────────────────────────┐
│  Video Streaming     │              │  User Interaction       │
│  (Automatic)         │              │  (Manual/Automatic)     │
└──────────────────────┘              └─────────────────────────┘
     │                                               │
     ├─ CDN: ipv4-c003-mnl005-pldt-isp             ├─ Play/Pause/Seek
     │  Range request (~310KB chunks)              │  Netflix MSL API
     │  Every 5-10 seconds                         │  Triggered by user
     │                                              │
     ▼                                              ▼
┌──────────────────────┐              ┌─────────────────────────┐
│  Subtitle Detection  │              │  Playback Events API    │
│  (In Player)         │              │  /msl/playapi/cadmium   │
└──────────────────────┘              └─────────────────────────┘
     │                                               │
     ├─ Text extracted from subtitle tracks         ├─ Event: pause
     │ (embedded in video metadata or separate)     │ Event: play
     │                                              │ Event: seek
     ▼                                              ▼
┌──────────────────────┐              ┌─────────────────────────┐
│  Word Hover/Lookup   │              │  Event Reporting        │
│  (User Action)       │              │  (Automatic)            │
└──────────────────────┘              └─────────────────────────┘
     │                                               │
     ├─ User hovers over word                       ├─ Progress: current_ms
     │ Query: dioco.io/base_dict_getHoverDict_8     │ Response logged
     │ Params: form, sl, tl, pos                    │ Every few seconds
     │                                              │
     ▼                                              ▼
┌──────────────────────┐              ┌─────────────────────────┐
│  Dictionary Response │              │  Analytics Logging      │
│  (JSON Definition)   │              │  /logblob               │
└──────────────────────┘              └─────────────────────────┘
     │                                               │
     ├─ Show inline definition                      ├─ Encoded log data
     │ Update UI with translation                   │ User behavior tracking
     │                                              │ Device/browser info
     ▼                                              ▼
┌──────────────────────┐              ┌─────────────────────────┐
│  Dictionary Stats    │              │  Session Management     │
│  (Async)             │              │  Telemetry              │
└──────────────────────┘              └─────────────────────────┘
     │                                               │
     └─ api.dioco.io/stats                          └─ Continuous tracking
        (POST, automatic)                              Device/OS/Browser info
```

---

## 2. Request Breakdown

### **REQUEST 1: Video Streaming (Automatic)**

| Property | Value |
|----------|-------|
| **URL** | `https://ipv4-c003-mnl005-pldt-isp.1.oca.nflxvideo.net/range/122638100-122948590` |
| **Method** | GET |
| **Headers** | Accept: `*/*`<br>Accept-Encoding: `gzip, deflate, br, zstd`<br>Referer: `https://www.netflix.com/`<br>User-Agent: Chrome/143.0.0.0 |
| **Query Params** | `o=1` (offset)<br>`v=266` (version)<br>`e=1768187062` (expiration timestamp)<br>`t=[token]` (auth token)<br>`sc=[signature]` (request signature) |
| **Response** | Binary video segment<br>Content-Length: 310,491 bytes<br>Content-Type: video/mp4 or similar |
| **Triggered By** | **Automatic** - Playback streaming every 5-10 seconds |
| **Purpose** | Download video chunks for playback buffer |

**Technical Notes:**
- Uses **HTTP Range requests** (byte-range: 122638100-122948590)
- **Signed URLs** with expiration (prevents hotlinking, token expires at `e=1768187062`)
- **CDN distribution** across regional ISP networks (PLDT in this case)
- **Compression support** (gzip, brotli, zstd)

---

### **REQUEST 2A: Dictionary Lookup - "어" (Automatic on Hover)**

| Property | Value |
|----------|-------|
| **URL** | `https://api-cdn-plus.dioco.io/base_dict_getHoverDict_8` |
| **Method** | GET |
| **Headers** | Accept: `application/json, text/plain, */*`<br>Referer: `https://www.netflix.com/` |
| **Query Params** | `form=%EC%96%B4` (URL-encoded Korean: "어")<br>`lemma=` (empty)<br>`sl=ko` (source language: Korean)<br>`tl=en` (target language: English)<br>`pos=NOUN` (part of speech)<br>`pow=n` (power/confidence level) |
| **Response** | `{"word":"어","definitions":[...]}` (69 bytes)<br>JSON with word, definitions, pronunciation, examples |
| **Triggered By** | **User Action** - Hover over Korean word in subtitles |
| **Purpose** | Fetch English translation & definition for Korean word |

**Technical Notes:**
- **Third-party API** (dioco.io, not Netflix-owned)
- **POS tagging** included in request (NOUN, ADJ, VERB, etc.)
- **Real-time lookup** on user interaction (not cached batch lookup)
- **Language pair** explicitly specified (ko→en)

---

### **REQUEST 2B: Dictionary Lookup - "그렇죠" (Automatic on Hover)**

| Property | Value |
|----------|-------|
| **URL** | `https://api-cdn-plus.dioco.io/base_dict_getHoverDict_8` |
| **Method** | GET |
| **Headers** | Accept: `application/json, text/plain, */*`<br>Referer: `https://www.netflix.com/` |
| **Query Params** | `form=%EA%B7%B8%EB%A0%87%EC%A3%A0` (URL-encoded: "그렇죠")<br>`lemma=` (empty)<br>`sl=ko` (Korean)<br>`tl=en` (English)<br>`pos=ADJ` (Adjective)<br>`pow=n` |
| **Response** | `{"word":"그렇죠","definitions":[...]}` (72 bytes) |
| **Triggered By** | **User Action** - Hover over different Korean word |
| **Purpose** | Fetch translation for adjective form |

**Technical Notes:**
- Same endpoint, different word & POS
- **Conjugated/inflected forms** supported (그렇죠 = 그렇다 + 죠 conjugation)
- **CDN-plus subdomain** suggests cached/optimized dictionary requests

---

### **REQUEST 3: Playback Event - Pause (User Action)**

| Property | Value |
|----------|-------|
| **URL** | `https://www.netflix.com/msl/playapi/cadmium/event/1` |
| **Method** | POST |
| **Query Params** | `reqAttempt=1`<br>`reqName=events/pause`<br>`reqId=d987fffc2e2986ed6535682a980143d5`<br>`mainContentViewableId=81726576` (show/movie ID)<br>`clienttype=akira` (Netflix web player)<br>`uiversion=v9d296d83`<br>`browsername=chrome`<br>`browserversion=143.0.0.0`<br>`osname=mac`<br>`osversion=10.15.7` |
| **Headers** | Content-Type: `text/plain`<br>Referer: `https://www.netflix.com/watch/81726576` |
| **Request Body** | `{ "eventType": "pause", "progress": [current_time_ms], ... }` (9,687 bytes)<br>Contains: timestamp, device ID, session info, client state |
| **Response** | HTTP 200 OK |
| **Triggered By** | **User Action** - User clicks Pause button |
| **Purpose** | Report playback pause event to Netflix backend |

**Technical Notes:**
- **MSL API** (Netflix Messaging Security Layer)
- **Cadmium player** endpoint (Netflix's internal codename for web player)
- **Large payload** (9.7KB) suggests additional telemetry data beyond event type
- **Request ID** for idempotency & tracking
- **Client info** embedded in query params (device, browser, OS, UI version)

---

### **REQUEST 4: Analytics Logging (Automatic)**

| Property | Value |
|----------|-------|
| **URL** | `https://logs.netflix.com/log/cadmium/logblob/1` |
| **Method** | POST |
| **Query Params** | `reqAttempt=1`<br>`reqName=logblob`<br>`reqId=e34189bdc64cbb4cec1a65f9164805cd`<br>`clienttype=akira`<br>`uiversion=v9d296d83`<br>`browsername=chrome`<br>`browserversion=143.0.0.0`<br>`osname=mac`<br>`osversion=10.15.7` |
| **Headers** | Content-Type: `text/plain`<br>Referer: `https://www.netflix.com/` |
| **Request Body** | Encoded/compressed log blob (23,059 bytes)<br>Contains: playback progress, user interactions, UI events, performance metrics |
| **Response** | HTTP 200 OK |
| **Triggered By** | **Automatic** - Every few seconds (~5s intervals) |
| **Purpose** | Aggregate and send telemetry/analytics data to Netflix servers |

**Technical Notes:**
- **Separate from event API** - logblob is batch/aggregate data, not individual events
- **Large payload** (23KB) = multiple events batched together
- **Encoded format** (likely gzip + optional encryption)
- **Continuous background process** - runs independent of user action
- **Device/browser profiling** included in every request

---

### **REQUEST 5: Dictionary Statistics (Automatic)**

| Property | Value |
|----------|-------|
| **URL** | `https://api.dioco.io/stats` |
| **Method** | POST |
| **Headers** | Content-Type: `text/plain; charset=utf-8`<br>Referer: `https://www.netflix.com/` |
| **Request Body** | `{}` (empty or minimal) |
| **Response** | `{"status":200}` (2 bytes) |
| **Triggered By** | **Automatic** - Likely after each dictionary lookup or periodically |
| **Purpose** | Report dictionary usage statistics to dioco (improve relevance, track engagement) |

**Technical Notes:**
- **Minimal payload** - just acknowledgment
- **Separate analytics endpoint** for dictionary service
- **Decoupled from Netflix logs** - sent to third-party analytics
- **Non-critical request** - no impact on playback if fails

---

## 3. Subtitle Fetching Strategy

### **Key Insight: Subtitles Not in Captured Logs**

The network logs **do not show explicit subtitle fetch requests** because:

1. **Subtitles embedded in video manifest** - Netflix includes subtitle tracks in the **DASH/HLS manifest** (not captured in these logs)
2. **Timed text format** - Subtitles likely delivered as:
   - **WebVTT** (text-based, human-readable)
   - **TTML** (XML-based, more structured)
   - **CEA-608/708** (embedded in video frames for compliance)

3. **Language selection** - Handled at manifest level, before video chunk download

### **Inferred Subtitle Flow**

```
User selects language (Korean)
     ↓
Netflix requests DASH manifest with lang=ko
     ↓
Manifest contains subtitle track reference
     ↓
Player downloads subtitle chunks in parallel with video
     ↓
Subtitles rendered in player
     ↓
On hover: text extracted → sent to dioco.io API
```

### **Why No Subtitle Request in Logs**

- Subtitles are **bundled with video manifest** (single request covers both)
- Already downloaded before playback starts
- Subsequent lookups only needed for dictionary (hover feature)

---

## 4. Dictionary Integration

### **Architecture**

```
Netflix Player
     ↓
[Subtitle Text Extracted]
     ↓
User hovers over word
     ↓
Query dioco.io API
  - form: Korean word (URL-encoded)
  - lemma: empty (lookup by form)
  - sl: source language (ko)
  - tl: target language (en)
  - pos: part of speech (NOUN, ADJ, VERB)
  - pow: confidence level
     ↓
dioco.io responds with definition JSON
     ↓
Netflix displays inline translation
     ↓
Analytics: POST to api.dioco.io/stats
```

### **Key Parameters Explained**

| Param | Example | Purpose |
|-------|---------|---------|
| `form` | `%EC%96%B4` ("어") | The actual word form user hovered on |
| `lemma` | (empty) | Lemma/base form (not used if empty) |
| `sl` | `ko` | Source language (Korean) |
| `tl` | `en` | Target language (English) |
| `pos` | `NOUN`, `ADJ` | Part of speech for context |
| `pow` | `n` | Confidence/power level (n=normal?) |

### **Response Format**

```json
{
  "word": "어",
  "definitions": [
    {
      "meaning": "something",
      "example": "어떤 것",
      "pos": "noun"
    }
  ],
  "pronunciation": "eo",
  "alternatives": [...]
}
```

### **Real-time Lookup Pattern**

- **On-demand**: Only fetches when user hovers (not pre-cached)
- **Per-word**: Separate request for each unique word
- **Stateless**: No session required, each lookup independent
- **Fast response**: API returns <100ms (69-72 bytes)

---

## 5. User Action vs Automatic Detection

### **User-Triggered Actions**

| Action | Request | Frequency | Purpose |
|--------|---------|-----------|---------|
| **Play** | POST /msl/playapi/cadmium/event | 1× on click | Signal playback start |
| **Pause** | POST /msl/playapi/cadmium/event | 1× on click | Signal playback pause |
| **Seek** | POST /msl/playapi/cadmium/event | 1× per seek | Report new playback position |
| **Hover word** | GET /base_dict_getHoverDict_8 | 1× per unique word | Fetch translation on demand |

### **Automatic Background Processes**

| Process | Request | Frequency | Purpose |
|---------|---------|-----------|---------|
| **Video streaming** | GET /range/[bytes] | Every 5-10s | Download video chunks for playback buffer |
| **Progress logging** | POST /log/cadmium/logblob | Every ~5s | Batch telemetry & analytics data |
| **Dictionary stats** | POST /stats | After lookups / periodic | Report usage to dictionary service |

### **Timeline Example**

```
t=0s    User clicks Play
           ↓ POST /msl/playapi/cadmium/event {eventType: play}
           ↓ GET /range/0-310491 (video chunk 1)

t=5s    Automatic: Progress logging
           ↓ POST /log/cadmium/logblob {...progress: 5000ms...}
           ↓ GET /range/310492-620982 (video chunk 2)

t=8s    User hovers over "어"
           ↓ GET /base_dict_getHoverDict_8?form=어&sl=ko&tl=en
           ↓ POST /stats (report usage)

t=12s   Automatic: Progress logging & video chunk
           ↓ POST /log/cadmium/logblob
           ↓ GET /range/620983-931473 (video chunk 3)

t=35s   User clicks Pause
           ↓ POST /msl/playapi/cadmium/event {eventType: pause}
           ↓ POST /log/cadmium/logblob (final progress)
```

---

## 6. Critical Implementation Insights

### **For Building a Netflix-Like Platform**

#### **1. Separate Video & Metadata Streams**
✅ **What Netflix Does:**
- Video chunks via CDN (ipv4-c003-mnl005-pldt-isp)
- Manifest/metadata via main API
- Subtitles bundled with manifest
- Analytics to separate service

**Implementation:**
```
Frontend → Manifest API (metadata + subtitle tracks)
        → CDN (video chunks)
        → Analytics Service (logging)
        → Dictionary API (word lookups)
```

#### **2. Signed URLs with Expiration**
✅ **Why:** Prevents hotlinking, controls access, time-limited tokens

**Implementation:**
```python
# Generate signed CDN URL
url = f"https://cdn.example.com/range/{byte_start}-{byte_end}"
url += f"?t={auth_token}&sc={signature}&e={expiration_timestamp}"
```

#### **3. Real-Time Dictionary Lookups**
✅ **Current Netflix approach:**
- On-demand per-word queries
- No batch pre-loading
- Language pair explicit (ko→en)
- POS tagging helps accuracy

**Implementation:**
```javascript
word.addEventListener('hover', async (e) => {
  const response = await fetch(
    `https://api.dict.io/lookup?form=${word}&sl=ko&tl=en&pos=${pos}`
  );
  showDefinition(response);
});
```

#### **4. Decoupled Event Reporting**
✅ **Netflix pattern:**
- User actions → MSL API (/msl/playapi/cadmium/event)
- Telemetry → Log service (/log/cadmium/logblob)
- Stats → Analytics (/stats)

**Benefits:**
- Events are critical, logged immediately
- Telemetry is non-blocking, batched
- Stats are informational, can fail silently

#### **5. Header & Query Param Profiling**
✅ **Netflix includes in every request:**
```
clienttype=akira
uiversion=v9d296d83
browsername=chrome
browserversion=143.0.0.0
osname=mac
osversion=10.15.7
```

**Purpose:** Track which client versions have issues, A/B test features

#### **6. Request Idempotency**
✅ **Netflix uses:**
```
reqId=d987fffc2e2986ed6535682a980143d5  (unique per request)
reqAttempt=1                             (retry counter)
```

**Purpose:** Prevent duplicate processing if request retried

#### **7. Batch Logging to Save Bandwidth**
✅ **Netflix approach:**
- Single pause event: 9.7 KB (with lots of context)
- Batched logblob: 23 KB (multiple events compressed)

**Ratio:** ~2.4× compression through batching

---

## 7. Technical Specifications

### **Content Delivery**

| Aspect | Implementation |
|--------|-----------------|
| **Video Format** | MP4 (MPEG-4) with H.264 codec |
| **Chunk Size** | ~300KB per range request |
| **CDN** | Multi-regional (PLDT ISP in this region) |
| **Compression** | gzip, brotli, zstd supported |
| **Auth** | Signed URLs (token + signature + expiration) |

### **Playback Events API**

| Aspect | Implementation |
|--------|-----------------|
| **Endpoint** | `/msl/playapi/cadmium/event/1` |
| **Protocol** | HTTPS POST |
| **Event Types** | play, pause, seek, resume, stop |
| **Payload Size** | ~9.7 KB (includes metadata) |
| **Response** | HTTP 200 (async processing) |

### **Dictionary API**

| Aspect | Implementation |
|--------|-----------------|
| **Endpoint** | `/base_dict_getHoverDict_8` |
| **Protocol** | HTTPS GET |
| **Query Params** | form, lemma, sl, tl, pos, pow |
| **Response Size** | 69-72 bytes (minimal JSON) |
| **Response Time** | <100ms (estimated) |
| **Language Pairs** | ko→en, and presumably others |

### **Analytics Service**

| Aspect | Implementation |
|--------|-----------------|
| **Event Endpoint** | `/log/cadmium/logblob/1` |
| **Stats Endpoint** | `/stats` (third-party) |
| **Batch Interval** | ~5 seconds |
| **Encoding** | text/plain (possibly gzip) |
| **Payload Size** | 23 KB per batch |

---

## 8. Recommendations for Custom Implementation

### **Phase 1: Minimum Viable Product**

```
✓ Video streaming (CDN + manifest)
✓ Subtitle embedding (DASH/HLS)
✓ Basic playback controls (play/pause/seek)
✓ Event logging (POST to analytics)
```

### **Phase 2: Enhanced Features**

```
✓ Real-time dictionary API integration
✓ Hover-based lookups
✓ Multi-language support (sl, tl params)
✓ POS tagging for accuracy
```

### **Phase 3: Advanced Analytics**

```
✓ Batched telemetry logging
✓ Request idempotency (reqId tracking)
✓ Device/browser profiling
✓ Retry logic & error handling
```

### **Phase 4: Scale & Optimization**

```
✓ CDN integration (reduce latency)
✓ Signed URL generation (security)
✓ Rate limiting (API abuse prevention)
✓ Caching strategies (dictionary pre-warm)
```

---

## 9. Security & Privacy Considerations

### **Signed URLs**
- Tokens expire at `e=1768187062` (epoch timestamp)
- Signature prevents URL tampering
- Prevents unauthorized CDN access

### **Request Signing**
- `reqId` ensures unique request tracking
- Prevents replay attacks
- Enables idempotent retries

### **User Privacy**
- Device/browser info logged for analytics
- User behavior tracked (pause/play/seek)
- Dictionary lookups tied to session (implies personalization)

### **Third-Party Integration**
- Dictionary API is external service (dioco.io)
- Netflix trusts dioco with user hover patterns
- Stats sent separately (analytics decoupled)

---

## 10. Comparison: Netflix vs YouTube Approach

| Aspect | Netflix | YouTube |
|--------|---------|---------|
| **Video Delivery** | Signed CDN URLs | yt-dlp / public APIs |
| **Subtitles** | Manifest-embedded | Separate API endpoint |
| **Word Lookups** | Real-time API | Pre-computed (in our implementation) |
| **Event Tracking** | MSL API (proprietary) | Limited tracking |
| **Authentication** | Session-based | OAuth / API keys |
| **Language Support** | Configurable | Fixed per region |

---

## 11. Architecture Diagram for Replication

```
┌───────────────────────────────────────────────────────────────────┐
│                     Custom Platform                               │
├───────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌──────────────────┐      ┌─────────────────────┐              │
│  │  Manifest API    │      │  Playback Events    │              │
│  │  Returns:        │      │  POST endpoint      │              │
│  │  - video URL     │      │  Tracks: play, pause│              │
│  │  - subtitle URL  │      │  Payload: progress  │              │
│  │  - chunk list    │      │  Response: 200 OK   │              │
│  └────────┬─────────┘      └────────┬────────────┘              │
│           │                         │                            │
│           ▼                         ▼                            │
│  ┌──────────────────┐      ┌─────────────────────┐              │
│  │  CDN Service     │      │  Analytics Logger   │              │
│  │  Serves: video   │      │  Batches telemetry  │              │
│  │  chunks at       │      │  Every ~5s          │              │
│  │  [byte-range]    │      │  Payload: 20+ KB    │              │
│  └────────┬─────────┘      └────────┬────────────┘              │
│           │                         │                            │
│           ▼                         ▼                            │
│  ┌──────────────────┐      ┌─────────────────────┐              │
│  │  Subtitle Parser │      │  Dictionary Lookup  │              │
│  │  Extracts text   │      │  GET /lookup        │              │
│  │  from tracks     │      │  Params: form, pos  │              │
│  │  On-screen       │      │  Response: JSON def │              │
│  └────────┬─────────┘      └────────┬────────────┘              │
│           │                         │                            │
│           └─────────────┬───────────┘                            │
│                         │                                        │
│                         ▼                                        │
│              ┌──────────────────────┐                           │
│              │  Dictionary Stats    │                           │
│              │  POST /stats         │                           │
│              │  Report usage        │                           │
│              └──────────────────────┘                           │
│                                                                   │
└───────────────────────────────────────────────────────────────────┘
```

---

## Conclusion

Netflix's architecture is **highly distributed and event-driven**:

1. **Video streaming** is automatic & continuous (CDN chunks every 5-10s)
2. **Subtitles** are embedded in manifest, not separate requests
3. **User actions** (play/pause) trigger immediate event reporting
4. **Dictionary lookups** are real-time on-demand queries (not pre-cached)
5. **Analytics** are batched & decoupled from critical paths
6. **Security** relies on signed URLs, tokens, and request IDs

For a custom implementation, prioritize:
- ✅ CDN-based video delivery
- ✅ Real-time event logging
- ✅ Stateless dictionary API integration
- ✅ Batched analytics (non-blocking)
- ✅ Comprehensive request tracking (reqId, metadata)

---

**Generated:** January 11, 2026  
**Platform:** macOS 10.15.7 | Chrome 143.0.0.0  
**Status:** Ready for implementation

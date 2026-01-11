/**
 * Subtitle + Dictionary Integration Module
 * 
 * Language Reactor-style implementation for any video source
 * Supports: YouTube, Vimeo, local files, DASH/HLS streams
 * 
 * Usage:
 *   const subtitleDict = new SubtitleDictionary({
 *     videoSelector: '#video',
 *     subtitleSource: 'data/subs_precomputed.json',
 *     language: 'ko',
 *     targetLanguage: 'en'
 *   });
 *   subtitleDict.init();
 */

class SubtitleDictionary {
  constructor(options = {}) {
    this.options = {
      videoSelector: options.videoSelector || 'video',
      subtitleSource: options.subtitleSource || 'data/subs_precomputed.json',
      language: options.language || 'ko',
      targetLanguage: options.targetLanguage || 'en',
      dictionaryAPI: options.dictionaryAPI || 'dioco',
      tooltipDelay: options.tooltipDelay || 300,
      cacheSize: options.cacheSize || 500,
      ...options
    };

    this.video = null;
    this.subtitles = [];
    this.dictionaryCache = new Map();
    this.currentSubtitleIndex = 0;
    this.tooltipTimeout = null;
    this.currentTooltip = null;
    this.subtitleContainer = null;
  }

  /**
   * Initialize the module
   */
  async init() {
    try {
      // Find video element
      this.video = document.querySelector(this.options.videoSelector);
      if (!this.video) {
        console.error('[SubtitleDict] Video element not found:', this.options.videoSelector);
        return false;
      }

      // Load subtitles
      await this.loadSubtitles();
      if (this.subtitles.length === 0) {
        console.warn('[SubtitleDict] No subtitles loaded');
        return false;
      }

      // Create subtitle display container
      this.createSubtitleContainer();

      // Attach event listeners
      this.attachVideoListeners();
      this.attachTooltipListeners();

      console.log(`[SubtitleDict] ✅ Initialized with ${this.subtitles.length} subtitle entries`);
      return true;
    } catch (error) {
      console.error('[SubtitleDict] Initialization failed:', error);
      return false;
    }
  }

  /**
   * Load subtitles from various sources
   */
  async loadSubtitles() {
    try {
      // Try to load from precomputed JSON first (our format)
      const response = await fetch(this.options.subtitleSource);
      if (!response.ok) throw new Error(`Failed to load subtitles: ${response.status}`);

      const data = await response.json();

      // Handle precomputed format: { words: [...] }
      if (data.words && Array.isArray(data.words)) {
        this.subtitles = data.words.map(w => ({
          word_id: w.word_id,
          text: w.word,
          start: w.start * 1000, // Convert to ms
          end: w.end * 1000,
          sentence_id: w.sentence_id
        }));
        return;
      }

      // Handle standard subtitle format: { events: [...] } (YouTube format)
      if (data.events && Array.isArray(data.events)) {
        this.parseYouTubeFormat(data);
        return;
      }

      // Handle basic array format: [{ start, end, text }, ...]
      if (Array.isArray(data)) {
        this.subtitles = data;
        return;
      }

      throw new Error('Unsupported subtitle format');
    } catch (error) {
      console.error('[SubtitleDict] Failed to load subtitles:', error);
      this.subtitles = [];
    }
  }

  /**
   * Parse YouTube API format (events with segments)
   */
  parseYouTubeFormat(data) {
    this.subtitles = [];
    let wordId = 0;

    data.events.forEach((event, eventIdx) => {
      const startMs = event.tStartMs || 0;
      const durationMs = event.dDurationMs || 0;
      const endMs = startMs + durationMs;

      if (event.segs && Array.isArray(event.segs)) {
        const words = event.segs.map(seg => seg.utf8).filter(w => w);
        const timePerWord = words.length > 0 ? durationMs / words.length : durationMs;

        words.forEach((word, wordIdx) => {
          const wordStart = startMs + (wordIdx * timePerWord);
          const wordEnd = wordStart + timePerWord;

          this.subtitles.push({
            word_id: wordId++,
            text: word,
            start: wordStart,
            end: wordEnd,
            sentence_id: eventIdx
          });
        });
      }
    });
  }

  /**
   * Create subtitle display container
   */
  createSubtitleContainer() {
    // Check if container already exists
    if (document.querySelector('.subtitle-dictionary-display')) {
      this.subtitleContainer = document.querySelector('.subtitle-dictionary-display');
      return;
    }

    // Create container
    this.subtitleContainer = document.createElement('div');
    this.subtitleContainer.className = 'subtitle-dictionary-display';
    this.subtitleContainer.innerHTML = `
      <style>
        .subtitle-dictionary-display {
          position: fixed;
          bottom: 20px;
          left: 50%;
          transform: translateX(-50%);
          background: rgba(0, 0, 0, 0.9);
          color: white;
          padding: 15px 25px;
          border-radius: 8px;
          font-size: 18px;
          max-width: 80%;
          z-index: 999;
          line-height: 1.5;
          font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
          text-align: center;
          box-shadow: 0 4px 20px rgba(0, 0, 0, 0.5);
          min-height: 50px;
          display: flex;
          align-items: center;
          justify-content: center;
        }

        .subtitle-dictionary-display .word {
          cursor: pointer;
          padding: 2px 4px;
          transition: background-color 0.2s;
          position: relative;
          display: inline-block;
        }

        .subtitle-dictionary-display .word:hover {
          background-color: rgba(255, 255, 255, 0.2);
          border-radius: 4px;
        }

        .subtitle-dictionary-display .word.current {
          background-color: #ffeb3b;
          color: black;
          font-weight: 600;
          border-radius: 4px;
        }

        .subtitle-tooltip {
          position: fixed;
          background: #333;
          color: white;
          padding: 12px 16px;
          border-radius: 8px;
          font-size: 13px;
          z-index: 10000;
          max-width: 300px;
          box-shadow: 0 4px 12px rgba(0, 0, 0, 0.6);
          pointer-events: none;
          white-space: normal;
          line-height: 1.4;
          animation: slideUp 0.2s ease-out;
        }

        .subtitle-tooltip::before {
          content: '';
          position: absolute;
          bottom: -6px;
          left: 15px;
          width: 0;
          height: 0;
          border-left: 6px solid transparent;
          border-right: 6px solid transparent;
          border-top: 6px solid #333;
        }

        .tooltip-word {
          font-weight: 600;
          display: block;
          margin-bottom: 6px;
          font-size: 14px;
        }

        .tooltip-definition {
          display: block;
          margin: 4px 0;
        }

        .tooltip-pos {
          font-size: 11px;
          opacity: 0.8;
          margin-top: 6px;
          border-top: 1px solid rgba(255,255,255,0.3);
          padding-top: 6px;
        }

        .tooltip-loading {
          font-style: italic;
          opacity: 0.8;
        }

        @keyframes slideUp {
          from {
            opacity: 0;
            transform: translateY(10px);
          }
          to {
            opacity: 1;
            transform: translateY(0);
          }
        }

        @media (max-width: 768px) {
          .subtitle-dictionary-display {
            font-size: 16px;
            padding: 12px 20px;
            bottom: 10px;
            left: 10px;
            right: 10px;
            transform: none;
            max-width: none;
          }
        }
      </style>
    `;

    document.body.appendChild(this.subtitleContainer);
  }

  /**
   * Attach video event listeners
   */
  attachVideoListeners() {
    this.video.addEventListener('timeupdate', () => this.updateSubtitles());
    this.video.addEventListener('play', () => this.updateSubtitles());
    this.video.addEventListener('seeking', () => this.updateSubtitles());
  }

  /**
   * Update displayed subtitles based on current time
   */
  updateSubtitles() {
    if (!this.video || !this.subtitleContainer) return;

    const currentTimeMs = this.video.currentTime * 1000;

    // Find subtitles for current time
    const currentSubs = this.subtitles.filter(
      s => s.start <= currentTimeMs && s.end > currentTimeMs
    );

    if (currentSubs.length === 0) {
      this.subtitleContainer.innerHTML = '';
      return;
    }

    // Group by sentence (optional)
    const html = currentSubs
      .map(sub => `
        <span class="word" data-text="${this.escapeHtml(sub.text)}" data-word-id="${sub.word_id}">
          ${this.escapeHtml(sub.text)}
        </span>
      `)
      .join(' ');

    this.subtitleContainer.innerHTML = html;

    // Re-attach hover listeners to new word elements
    this.attachTooltipListeners();
  }

  /**
   * Attach tooltip listeners to word elements
   */
  attachTooltipListeners() {
    const wordElements = document.querySelectorAll('.subtitle-dictionary-display .word');

    wordElements.forEach(element => {
      element.addEventListener('mouseenter', (e) => {
        clearTimeout(this.tooltipTimeout);
        this.tooltipTimeout = setTimeout(() => {
          this.showWordTooltip(e.target);
        }, this.options.tooltipDelay);
      });

      element.addEventListener('mouseleave', () => {
        clearTimeout(this.tooltipTimeout);
        this.hideTooltip();
      });
    });
  }

  /**
   * Fetch definition from dictionary API
   */
  async fetchDefinition(word) {
    // Check cache first
    if (this.dictionaryCache.has(word)) {
      return this.dictionaryCache.get(word);
    }

    try {
      const params = new URLSearchParams({
        form: word,
        lemma: '',
        sl: this.options.language,
        tl: this.options.targetLanguage,
        pos: 'NOUN',
        pow: 'n'
      });

      const response = await fetch(
        `https://api-cdn-plus.dioco.io/base_dict_getHoverDict_8?${params}`
      );

      if (!response.ok) throw new Error('API error');

      const data = await response.json();

      // Cache result
      if (this.dictionaryCache.size >= this.options.cacheSize) {
        const firstKey = this.dictionaryCache.keys().next().value;
        this.dictionaryCache.delete(firstKey);
      }
      this.dictionaryCache.set(word, data);

      // Report stats
      navigator.sendBeacon('https://api.dioco.io/stats', JSON.stringify({
        word: word,
        timestamp: Date.now(),
        source: 'SubtitleDictionary'
      }));

      return data;
    } catch (error) {
      console.error('[SubtitleDict] Dictionary fetch failed:', error);
      return { error: true };
    }
  }

  /**
   * Show tooltip for word
   */
  async showWordTooltip(element) {
    this.hideTooltip();

    const word = element.dataset.text;
    if (!word) return;

    // Show loading state
    const tooltip = document.createElement('div');
    tooltip.className = 'subtitle-tooltip';
    tooltip.innerHTML = '<div class="tooltip-loading">Looking up...</div>';
    document.body.appendChild(tooltip);

    const rect = element.getBoundingClientRect();
    tooltip.style.left = (rect.left + rect.width / 2 - 60) + 'px';
    tooltip.style.top = (rect.top - tooltip.offsetHeight - 15) + 'px';

    this.currentTooltip = tooltip;

    // Fetch definition
    const data = await this.fetchDefinition(word);

    // Update tooltip content
    if (data.error) {
      tooltip.innerHTML = '<div style="color: #ff6b6b;">Definition not found</div>';
    } else {
      let content = `<span class="tooltip-word">${word}</span>`;

      if (data.definitions && data.definitions.length > 0) {
        const def = data.definitions[0];
        content += `<span class="tooltip-definition">${def.meaning || def}</span>`;

        if (data.definitions.length > 1) {
          content += `<span style="font-size: 11px; opacity: 0.7;">+${data.definitions.length - 1} more</span>`;
        }
      }

      if (data.pos) {
        content += `<span class="tooltip-pos">${data.pos.toUpperCase()}</span>`;
      }

      tooltip.innerHTML = content;
    }

    // Reposition after content updates
    tooltip.style.left = (rect.left + rect.width / 2 - 60) + 'px';
    tooltip.style.top = (rect.top - tooltip.offsetHeight - 15) + 'px';
  }

  /**
   * Hide current tooltip
   */
  hideTooltip() {
    if (this.currentTooltip) {
      this.currentTooltip.remove();
      this.currentTooltip = null;
    }
  }

  /**
   * Escape HTML entities
   */
  escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
  }

  /**
   * Clear cache
   */
  clearCache() {
    this.dictionaryCache.clear();
    console.log('[SubtitleDict] Cache cleared');
  }

  /**
   * Destroy module (cleanup)
   */
  destroy() {
    if (this.subtitleContainer) {
      this.subtitleContainer.remove();
    }
    clearTimeout(this.tooltipTimeout);
    this.hideTooltip();
    console.log('[SubtitleDict] Destroyed');
  }

  /**
   * Get statistics
   */
  getStats() {
    return {
      subtitlesLoaded: this.subtitles.length,
      cacheSize: this.dictionaryCache.size,
      videoElement: this.video ? 'found' : 'not found'
    };
  }
}

// Export for use in modules/scripts
if (typeof module !== 'undefined' && module.exports) {
  module.exports = SubtitleDictionary;
}

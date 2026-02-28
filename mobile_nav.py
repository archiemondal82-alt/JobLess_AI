"""
mobile_nav.py — JobLess AI Mobile Experience Layer
====================================================
Injects into Streamlit:
  • Bottom navigation bar (replaces tab bar on mobile)
  • Full-screen modal system (replaces toasts/alerts)
  • Viewport lock (no zoom, no horizontal scroll)
  • Pull-to-refresh with haptic feedback indicator
  • 120fps-class page transitions using Web Animations API
  • Safe-area insets for notched phones
"""

import streamlit.components.v1 as components

# ─── Tab manifest — must match order in main() st.tabs() call ────────────────
_TABS = [
    {"icon": "📊", "label": "Career",    "short": "Career"},
    {"icon": "📜", "label": "History",   "short": "History"},
    {"icon": "⚖️",  "label": "Compare",  "short": "Compare"},
    {"icon": "📚", "label": "Resources", "short": "Learn"},
    {"icon": "📝", "label": "Resume",    "short": "Resume"},
    {"icon": "🎤", "label": "Interview", "short": "Interview"},
    {"icon": "📂", "label": "PYQ Hub",   "short": "PYQ"},
]

_MOBILE_CSS = """
<style>
/* ═══════════════════════════════════════════════════
   1. VIEWPORT & BASE RESET — no zoom, no h-scroll
═══════════════════════════════════════════════════ */
html, body {
  overflow-x: hidden !important;
  overscroll-behavior-x: none !important;
  touch-action: pan-y !important;
  -webkit-text-size-adjust: 100% !important;
  -ms-text-size-adjust: 100% !important;
  scroll-behavior: smooth;
}

/* Ensure main content doesn't overflow */
[data-testid="stAppViewContainer"],
[data-testid="stMain"],
[data-testid="block-container"] {
  overflow-x: hidden !important;
  max-width: 100vw !important;
}

/* ═══════════════════════════════════════════════════
   2. MOBILE-ONLY STYLES  (≤ 768px)
═══════════════════════════════════════════════════ */
@media screen and (max-width: 768px) {

  /* Hide the Streamlit tab bar — replaced by bottom nav */
  [data-testid="stTabs"] > div:first-child,
  .stTabs [data-baseweb="tab-list"] {
    display: none !important;
  }

  /* Sidebar — hide completely on mobile */
  [data-testid="stSidebar"] {
    display: none !important;
  }

  /* Sidebar toggle button — hide */
  [data-testid="collapsedControl"],
  button[kind="header"] {
    display: none !important;
  }

  /* Main content — full width, bottom padding for nav bar */
  [data-testid="block-container"] {
    padding-left: 12px !important;
    padding-right: 12px !important;
    padding-bottom: calc(80px + env(safe-area-inset-bottom)) !important;
    padding-top: 8px !important;
    max-width: 100% !important;
    width: 100% !important;
  }

  /* Tab panels — add slide transition target */
  [data-testid="stTabsContent"] {
    animation: jl-page-in 0.32s cubic-bezier(0.22, 1, 0.36, 1) both;
  }

  /* Hide Streamlit header/toolbar */
  [data-testid="stHeader"],
  [data-testid="stToolbar"],
  .stDeployButton {
    display: none !important;
  }

  /* Prevent table/code overflow */
  pre, code, table {
    overflow-x: auto;
    max-width: 100%;
    font-size: 12px !important;
  }

  /* Column stacking */
  [data-testid="column"] {
    min-width: 100% !important;
    flex: 1 1 100% !important;
  }

  /* Better button sizing for thumbs */
  .stButton > button {
    min-height: 48px !important;
    font-size: 0.9rem !important;
  }

  /* Text inputs — prevent iOS zoom on focus */
  input, textarea, select {
    font-size: 16px !important;
  }

  /* Remove horizontal scroll from resource grids */
  .resource-grid {
    grid-template-columns: 1fr !important;
  }

  /* Job link buttons — stack vertically */
  .job-links-row {
    flex-direction: column !important;
  }
  .job-link-btn {
    width: 100% !important;
    justify-content: center !important;
  }

  /* Stats row — 2 col grid on mobile */
  .stats-row {
    display: grid !important;
    grid-template-columns: 1fr 1fr !important;
    gap: 10px !important;
  }

  /* Expanders — full width */
  .stExpander {
    margin-left: 0 !important;
    margin-right: 0 !important;
  }

  /* Match rings — smaller on mobile */
  .match-ring-wrap {
    transform: scale(0.85);
  }
}

/* ═══════════════════════════════════════════════════
   3. PAGE TRANSITION ANIMATION
═══════════════════════════════════════════════════ */
@keyframes jl-page-in {
  0%  { opacity: 0; transform: translateY(18px) scale(0.98); }
  100%{ opacity: 1; transform: translateY(0)    scale(1);    }
}
@keyframes jl-page-out {
  0%  { opacity: 1; transform: translateY(0) scale(1); }
  100%{ opacity: 0; transform: translateY(-10px) scale(0.98); }
}
@keyframes jl-slide-up {
  0%  { transform: translateY(100%); opacity: 0; }
  100%{ transform: translateY(0);    opacity: 1; }
}
@keyframes jl-slide-down {
  0%  { transform: translateY(0);    opacity: 1; }
  100%{ transform: translateY(100%); opacity: 0; }
}
@keyframes jl-fade-in {
  from { opacity: 0; }
  to   { opacity: 1; }
}
@keyframes jl-pop-in {
  0%  { transform: scale(0.88); opacity: 0; }
  70% { transform: scale(1.03); opacity: 1; }
  100%{ transform: scale(1);    opacity: 1; }
}

/* ═══════════════════════════════════════════════════
   4. BOTTOM NAVIGATION BAR
═══════════════════════════════════════════════════ */
#jl-bottom-nav {
  display: none; /* JS shows on mobile */
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  z-index: 99999;
  background: rgba(6, 11, 20, 0.97);
  backdrop-filter: blur(28px) saturate(180%);
  -webkit-backdrop-filter: blur(28px) saturate(180%);
  border-top: 1px solid rgba(0, 210, 255, 0.18);
  box-shadow: 0 -8px 40px rgba(0, 0, 0, 0.6),
              0 -1px 0 rgba(0, 210, 255, 0.08);
  padding-bottom: env(safe-area-inset-bottom);
  height: calc(64px + env(safe-area-inset-bottom));
  animation: jl-slide-up 0.45s cubic-bezier(0.22, 1, 0.36, 1) both;
}

.jl-nav-inner {
  display: flex;
  align-items: stretch;
  height: 64px;
  overflow-x: auto;
  scrollbar-width: none;
  -ms-overflow-style: none;
  scroll-snap-type: x mandatory;
  -webkit-overflow-scrolling: touch;
}
.jl-nav-inner::-webkit-scrollbar { display: none; }

.jl-nav-item {
  flex: 1;
  min-width: 52px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 3px;
  cursor: pointer;
  position: relative;
  transition: background 0.2s ease;
  scroll-snap-align: center;
  -webkit-tap-highlight-color: transparent;
  user-select: none;
  border: none;
  background: transparent;
  padding: 6px 4px;
}

.jl-nav-item:active {
  background: rgba(0, 210, 255, 0.08);
}

.jl-nav-icon {
  font-size: 20px;
  line-height: 1;
  transition: transform 0.25s cubic-bezier(0.34, 1.56, 0.64, 1),
              filter 0.25s ease;
  will-change: transform;
}

.jl-nav-label {
  font-family: 'Space Grotesk', 'SF Pro Display', -apple-system, sans-serif;
  font-size: 9.5px;
  font-weight: 600;
  letter-spacing: 0.03em;
  color: #475569;
  transition: color 0.2s ease;
  white-space: nowrap;
  text-transform: uppercase;
  line-height: 1;
}

/* Active tab indicator */
.jl-nav-item::before {
  content: '';
  position: absolute;
  top: 0;
  left: 50%;
  transform: translateX(-50%) scaleX(0);
  width: 32px;
  height: 2.5px;
  background: linear-gradient(90deg, #00d2ff, #3a7bd5);
  border-radius: 0 0 4px 4px;
  box-shadow: 0 0 12px rgba(0, 210, 255, 0.8);
  transition: transform 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
}

.jl-nav-item.active::before {
  transform: translateX(-50%) scaleX(1);
}

.jl-nav-item.active .jl-nav-icon {
  transform: translateY(-2px) scale(1.18);
  filter: drop-shadow(0 0 6px rgba(0, 210, 255, 0.7));
}

.jl-nav-item.active .jl-nav-label {
  color: #00d2ff;
}

/* Active background glow */
.jl-nav-item.active::after {
  content: '';
  position: absolute;
  inset: 4px;
  background: radial-gradient(ellipse at 50% 100%, rgba(0, 210, 255, 0.12) 0%, transparent 70%);
  border-radius: 8px;
}

/* ═══════════════════════════════════════════════════
   5. SETTINGS FAB (replaces sidebar on mobile)
═══════════════════════════════════════════════════ */
#jl-settings-fab {
  display: none;
  position: fixed;
  top: 12px;
  right: 12px;
  z-index: 99998;
  width: 44px;
  height: 44px;
  border-radius: 50%;
  background: rgba(6, 11, 20, 0.9);
  backdrop-filter: blur(16px);
  border: 1px solid rgba(0, 210, 255, 0.3);
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.5),
              0 0 0 1px rgba(0, 210, 255, 0.1);
  cursor: pointer;
  align-items: center;
  justify-content: center;
  font-size: 18px;
  -webkit-tap-highlight-color: transparent;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
  animation: jl-fade-in 0.5s ease 0.6s both;
}
#jl-settings-fab:active {
  transform: scale(0.9);
}

/* ═══════════════════════════════════════════════════
   6. MODAL SYSTEM (replaces toasts/alerts)
═══════════════════════════════════════════════════ */
#jl-modal-overlay {
  display: none;
  position: fixed;
  inset: 0;
  z-index: 999999;
  background: rgba(0, 0, 0, 0.75);
  backdrop-filter: blur(8px);
  -webkit-backdrop-filter: blur(8px);
  animation: jl-fade-in 0.2s ease;
  align-items: flex-end;
  justify-content: center;
}
#jl-modal-overlay.active {
  display: flex;
}

.jl-modal-sheet {
  width: 100%;
  max-width: 600px;
  background: linear-gradient(180deg, rgba(15, 23, 42, 0.99), rgba(6, 11, 20, 1));
  border-radius: 24px 24px 0 0;
  border-top: 1px solid rgba(0, 210, 255, 0.2);
  box-shadow: 0 -20px 80px rgba(0, 0, 0, 0.8);
  animation: jl-slide-up 0.38s cubic-bezier(0.22, 1, 0.36, 1) both;
  max-height: 85vh;
  overflow-y: auto;
  overscroll-behavior: contain;
  padding-bottom: env(safe-area-inset-bottom);
}

.jl-modal-handle {
  width: 36px;
  height: 4px;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 2px;
  margin: 12px auto 0;
}

.jl-modal-header {
  padding: 16px 20px 0;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.jl-modal-title {
  font-family: 'Space Grotesk', sans-serif;
  font-size: 1.1rem;
  font-weight: 700;
  color: #e2e8f0;
}

.jl-modal-close {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.08);
  border: none;
  color: #94a3b8;
  font-size: 16px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  -webkit-tap-highlight-color: transparent;
}

.jl-modal-body {
  padding: 16px 20px 24px;
}

/* Alert variants inside modal */
.jl-alert {
  border-radius: 14px;
  padding: 16px 18px;
  margin: 8px 0;
  display: flex;
  gap: 12px;
  align-items: flex-start;
  animation: jl-pop-in 0.35s cubic-bezier(0.34, 1.56, 0.64, 1) both;
}
.jl-alert-icon { font-size: 1.4rem; flex-shrink: 0; margin-top: 2px; }
.jl-alert-text { flex: 1; }
.jl-alert-heading {
  font-family: 'Space Grotesk', sans-serif;
  font-weight: 700;
  font-size: 0.95rem;
  margin-bottom: 4px;
}
.jl-alert-body {
  font-family: 'Space Grotesk', sans-serif;
  font-size: 0.85rem;
  line-height: 1.5;
  opacity: 0.8;
}
.jl-alert-success { background: rgba(34,197,94,0.12); border: 1px solid rgba(34,197,94,0.3); color: #86efac; }
.jl-alert-error   { background: rgba(239,68,68,0.12);  border: 1px solid rgba(239,68,68,0.3);  color: #fca5a5; }
.jl-alert-info    { background: rgba(0,210,255,0.10);  border: 1px solid rgba(0,210,255,0.25); color: #7dd3fc; }
.jl-alert-warn    { background: rgba(245,158,11,0.10); border: 1px solid rgba(245,158,11,0.25);color: #fcd34d; }

/* Settings panel inside modal */
.jl-settings-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 14px 0;
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
}
.jl-settings-label {
  font-family: 'Space Grotesk', sans-serif;
  font-size: 0.9rem;
  color: #94a3b8;
}
.jl-settings-value {
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.8rem;
  color: #00d2ff;
  background: rgba(0, 210, 255, 0.08);
  border: 1px solid rgba(0, 210, 255, 0.2);
  border-radius: 6px;
  padding: 3px 10px;
}

/* ═══════════════════════════════════════════════════
   7. PULL TO REFRESH INDICATOR
═══════════════════════════════════════════════════ */
#jl-ptr {
  position: fixed;
  top: 0;
  left: 50%;
  transform: translateX(-50%) translateY(-80px);
  z-index: 99997;
  width: 48px;
  height: 48px;
  border-radius: 50%;
  background: linear-gradient(135deg, rgba(0, 210, 255, 0.2), rgba(58, 123, 213, 0.2));
  backdrop-filter: blur(12px);
  border: 1px solid rgba(0, 210, 255, 0.4);
  box-shadow: 0 4px 30px rgba(0, 210, 255, 0.3);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
  transition: transform 0.15s ease;
  pointer-events: none;
}

#jl-ptr.ptr-visible {
  transform: translateX(-50%) translateY(12px);
}

#jl-ptr.ptr-spinning {
  animation: jl-ptr-spin 0.8s linear infinite;
}

@keyframes jl-ptr-spin {
  from { transform: translateX(-50%) translateY(12px) rotate(0deg); }
  to   { transform: translateX(-50%) translateY(12px) rotate(360deg); }
}

/* ═══════════════════════════════════════════════════
   8. PAGE TRANSITION OVERLAY
═══════════════════════════════════════════════════ */
#jl-transition-overlay {
  position: fixed;
  inset: 0;
  z-index: 999998;
  pointer-events: none;
  background: radial-gradient(ellipse at center, rgba(0, 210, 255, 0.06) 0%, transparent 70%);
  opacity: 0;
  transition: opacity 0.18s ease;
}
#jl-transition-overlay.flash {
  opacity: 1;
}

/* ═══════════════════════════════════════════════════
   9. SMOOTH SCROLLING & MOMENTUM
═══════════════════════════════════════════════════ */
* {
  -webkit-overflow-scrolling: touch;
}

/* Scrollbar hidden on mobile */
@media screen and (max-width: 768px) {
  *::-webkit-scrollbar { width: 0 !important; display: none !important; }
  * { scrollbar-width: none !important; }
}
</style>
"""

_MOBILE_HTML = """
<!-- Pull-to-refresh indicator -->
<div id="jl-ptr">🔄</div>

<!-- Page transition flash overlay -->
<div id="jl-transition-overlay"></div>

<!-- Bottom Navigation Bar -->
<nav id="jl-bottom-nav" role="navigation" aria-label="Main navigation">
  <div class="jl-nav-inner">
    {NAV_ITEMS}
  </div>
</nav>

<!-- Settings FAB -->
<button id="jl-settings-fab" aria-label="Settings" title="Settings">⚙️</button>

<!-- Modal Overlay -->
<div id="jl-modal-overlay" role="dialog" aria-modal="true" aria-label="Panel">
  <div class="jl-modal-sheet" id="jl-modal-sheet">
    <div class="jl-modal-handle"></div>
    <div class="jl-modal-header">
      <div class="jl-modal-title" id="jl-modal-title">Settings</div>
      <button class="jl-modal-close" id="jl-modal-close" aria-label="Close">✕</button>
    </div>
    <div class="jl-modal-body" id="jl-modal-body"></div>
  </div>
</div>
"""

_MOBILE_JS = r"""
<script>
(function() {
'use strict';

// ── Viewport meta — inject no-zoom, no-scale ──────────────────────────────
(function injectViewport() {
  var existing = document.querySelector('meta[name="viewport"]');
  var content = 'width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no, viewport-fit=cover';
  if (existing) {
    existing.setAttribute('content', content);
  } else {
    var m = document.createElement('meta');
    m.name = 'viewport';
    m.content = content;
    document.head.appendChild(m);
  }
})();

// ── Device detection ──────────────────────────────────────────────────────
var isMobile = window.innerWidth <= 768 || /Android|iPhone|iPad|iPod|Mobile/i.test(navigator.userAgent);

if (!isMobile) return; // Desktop: do nothing

// ── Show mobile-only elements ─────────────────────────────────────────────
var bottomNav = document.getElementById('jl-bottom-nav');
var fab       = document.getElementById('jl-settings-fab');
if (bottomNav) bottomNav.style.display = 'block';
if (fab)       fab.style.display = 'flex';

// ── State ─────────────────────────────────────────────────────────────────
var currentTab = 0;
var isTransitioning = false;
var navItems = document.querySelectorAll('.jl-nav-item');
var overlay = document.getElementById('jl-transition-overlay');
var ptr = document.getElementById('jl-ptr');
var modal = document.getElementById('jl-modal-overlay');
var modalTitle = document.getElementById('jl-modal-title');
var modalBody = document.getElementById('jl-modal-body');

// ── Tab switching via click on Streamlit's real tab buttons ───────────────
function getStreamlitTabs() {
  // Try multiple selectors since Streamlit updates its class names
  var selectors = [
    '[data-testid="stTabs"] [data-baseweb="tab"]',
    '.stTabs [role="tab"]',
    '[data-testid="stTabsTabList"] button',
    '[role="tablist"] [role="tab"]'
  ];
  for (var i = 0; i < selectors.length; i++) {
    var tabs = document.querySelectorAll(selectors[i]);
    if (tabs && tabs.length > 0) return tabs;
  }
  return [];
}

function switchTab(index) {
  if (isTransitioning) return;
  isTransitioning = true;

  // Visual transition flash
  if (overlay) {
    overlay.classList.add('flash');
    setTimeout(function() { overlay.classList.remove('flash'); }, 220);
  }

  // Update bottom nav active states
  navItems.forEach(function(item, i) {
    item.classList.toggle('active', i === index);
  });

  // Haptic feedback (supported on modern Android/iOS)
  try {
    if (navigator.vibrate) navigator.vibrate(8);
  } catch(e) {}

  // Click the real Streamlit tab
  setTimeout(function() {
    var stTabs = getStreamlitTabs();
    if (stTabs && stTabs[index]) {
      stTabs[index].click();
      // Scroll to top after tab switch
      setTimeout(function() {
        var mainContent = document.querySelector('[data-testid="stMain"]') ||
                          document.querySelector('[data-testid="block-container"]') ||
                          document.documentElement;
        mainContent.scrollTo({ top: 0, behavior: 'smooth' });
        isTransitioning = false;
      }, 200);
    } else {
      isTransitioning = false;
    }
    currentTab = index;
  }, 80);
}

// ── Attach nav item listeners ─────────────────────────────────────────────
navItems.forEach(function(item, index) {
  item.addEventListener('click', function(e) {
    e.preventDefault();
    e.stopPropagation();
    switchTab(index);
  }, { passive: false });

  // Touch ripple effect
  item.addEventListener('touchstart', function() {
    this.style.background = 'rgba(0, 210, 255, 0.1)';
  }, { passive: true });
  item.addEventListener('touchend', function() {
    var el = this;
    setTimeout(function() { el.style.background = ''; }, 150);
  }, { passive: true });
});

// ── Settings FAB → Modal ──────────────────────────────────────────────────
if (fab) {
  fab.addEventListener('click', function() {
    openSettingsModal();
  });
}

function openSettingsModal() {
  if (!modalTitle || !modalBody || !modal) return;
  modalTitle.textContent = '⚙️ Settings';

  // Pull current settings from Streamlit's sidebar DOM
  var providerEl = document.querySelector('[data-testid="stSidebar"] [data-baseweb="select"] [data-testid="stMarkdownContainer"]');
  var providerText = providerEl ? providerEl.textContent.trim() : 'Not set';

  modalBody.innerHTML = [
    '<div style="color:#94a3b8;font-size:0.8rem;margin-bottom:16px;">',
    'Configure AI settings via the sidebar on desktop, or use the controls below.',
    '</div>',
    '<div class="jl-settings-row">',
    '  <span class="jl-settings-label">🤖 AI Provider</span>',
    '  <span class="jl-settings-value">Sidebar →</span>',
    '</div>',
    '<div class="jl-settings-row">',
    '  <span class="jl-settings-label">🧠 Model</span>',
    '  <span class="jl-settings-value">Sidebar →</span>',
    '</div>',
    '<div class="jl-settings-row">',
    '  <span class="jl-settings-label">📱 Screen</span>',
    '  <span class="jl-settings-value">' + window.innerWidth + '×' + window.innerHeight + '</span>',
    '</div>',
    '<div style="margin-top:20px;padding:14px 16px;background:rgba(0,210,255,0.06);',
    'border:1px solid rgba(0,210,255,0.2);border-radius:12px;">',
    '  <div style="color:#00d2ff;font-weight:700;font-size:0.85rem;margin-bottom:6px;">💡 Tip</div>',
    '  <div style="color:#94a3b8;font-size:0.82rem;line-height:1.5;">',
    '  To change AI provider & API key, switch to desktop view or rotate to landscape.',
    '  </div>',
    '</div>',
    '<div style="margin-top:12px;">',
    '  <button onclick="window.location.reload()" style="',
    '    width:100%;padding:12px;border-radius:10px;border:1px solid rgba(0,210,255,0.3);',
    '    background:rgba(0,210,255,0.08);color:#00d2ff;font-size:0.9rem;font-weight:700;',
    '    cursor:pointer;font-family:Space Grotesk,sans-serif;">',
    '    🔄 Refresh App',
    '  </button>',
    '</div>'
  ].join('');

  openModal();
}

// ── Modal open/close ──────────────────────────────────────────────────────
function openModal() {
  if (!modal) return;
  modal.classList.add('active');
  document.body.style.overflow = 'hidden';
}

function closeModal() {
  if (!modal) return;
  var sheet = document.getElementById('jl-modal-sheet');
  if (sheet) {
    sheet.style.animation = 'jl-slide-down 0.28s cubic-bezier(0.55, 0, 1, 0.45) both';
    setTimeout(function() {
      modal.classList.remove('active');
      if (sheet) sheet.style.animation = '';
      document.body.style.overflow = '';
    }, 260);
  } else {
    modal.classList.remove('active');
    document.body.style.overflow = '';
  }
}

// Close on overlay click
if (modal) {
  modal.addEventListener('click', function(e) {
    if (e.target === modal) closeModal();
  });
}

// Close button
var closeBtn = document.getElementById('jl-modal-close');
if (closeBtn) {
  closeBtn.addEventListener('click', closeModal);
}

// ── Pull to Refresh ───────────────────────────────────────────────────────
var ptrStartY = 0;
var ptrCurrentY = 0;
var ptrActive = false;
var PTR_THRESHOLD = 72;

document.addEventListener('touchstart', function(e) {
  var scrollEl = document.querySelector('[data-testid="stMain"]') || document.documentElement;
  if (scrollEl.scrollTop <= 0) {
    ptrStartY = e.touches[0].clientY;
    ptrActive = true;
  }
}, { passive: true });

document.addEventListener('touchmove', function(e) {
  if (!ptrActive || !ptr) return;
  ptrCurrentY = e.touches[0].clientY;
  var delta = ptrCurrentY - ptrStartY;

  if (delta > 0 && delta < PTR_THRESHOLD * 2) {
    var progress = Math.min(delta / PTR_THRESHOLD, 1);
    ptr.style.transform = 'translateX(-50%) translateY(' + (-80 + progress * 92) + 'px)';
    ptr.style.opacity = String(progress);

    if (delta > PTR_THRESHOLD) {
      ptr.classList.add('ptr-visible');
      ptr.textContent = '↻';
    }
  }
}, { passive: true });

document.addEventListener('touchend', function(e) {
  if (!ptrActive || !ptr) return;
  var delta = ptrCurrentY - ptrStartY;

  if (delta > PTR_THRESHOLD) {
    // Trigger refresh
    ptr.classList.add('ptr-spinning');
    ptr.textContent = '⟳';
    try { if (navigator.vibrate) navigator.vibrate([10, 50, 10]); } catch(ex) {}

    setTimeout(function() {
      window.location.reload();
    }, 600);
  } else {
    // Reset
    ptr.style.transition = 'transform 0.3s ease, opacity 0.3s ease';
    ptr.style.transform = 'translateX(-50%) translateY(-80px)';
    ptr.style.opacity = '0';
    ptr.classList.remove('ptr-visible');
    setTimeout(function() {
      ptr.style.transition = '';
      ptr.textContent = '🔄';
    }, 300);
  }

  ptrActive = false;
  ptrStartY = 0;
  ptrCurrentY = 0;
}, { passive: true });

// ── Swipe between tabs (horizontal swipe on content area) ────────────────
var swipeStartX = 0;
var swipeStartY = 0;
var swipeStarted = false;
var SWIPE_THRESHOLD = 60;
var SWIPE_ANGLE_MAX = 35; // degrees

document.addEventListener('touchstart', function(e) {
  if (e.touches.length === 1) {
    swipeStartX = e.touches[0].clientX;
    swipeStartY = e.touches[0].clientY;
    swipeStarted = true;
  }
}, { passive: true });

document.addEventListener('touchend', function(e) {
  if (!swipeStarted) return;
  swipeStarted = false;

  var endX = e.changedTouches[0].clientX;
  var endY = e.changedTouches[0].clientY;
  var deltaX = endX - swipeStartX;
  var deltaY = endY - swipeStartY;

  // Only horizontal swipes (angle check)
  if (Math.abs(deltaX) < SWIPE_THRESHOLD) return;
  var angle = Math.abs(Math.atan2(deltaY, deltaX) * 180 / Math.PI);
  if (angle > SWIPE_ANGLE_MAX && angle < (180 - SWIPE_ANGLE_MAX)) return;

  // Don't swipe inside modals
  if (modal && modal.classList.contains('active')) return;

  var totalTabs = navItems.length;
  if (deltaX < 0 && currentTab < totalTabs - 1) {
    switchTab(currentTab + 1);
  } else if (deltaX > 0 && currentTab > 0) {
    switchTab(currentTab - 1);
  }
}, { passive: true });

// ── Intercept Streamlit alerts/toasts → show as modal ────────────────────
function interceptAlerts() {
  // Override window.alert
  var origAlert = window.alert;
  window.alert = function(msg) {
    showJLModal('ℹ️ Notice', msg, 'info');
  };

  // Watch for Streamlit toast elements appearing in DOM
  var alertObserver = new MutationObserver(function(mutations) {
    mutations.forEach(function(mutation) {
      mutation.addedNodes.forEach(function(node) {
        if (!node.querySelector) return;

        // Streamlit toast/notification
        var toast = node.querySelector('[data-testid="stToast"]') ||
                    (node.dataset && node.dataset.testid === 'stToast' ? node : null);

        if (toast) {
          var text = toast.textContent.trim();
          var type = 'info';
          if (text.includes('⚠️') || text.includes('warning')) type = 'warn';
          if (text.includes('✅') || text.includes('success')) type = 'success';
          if (text.includes('❌') || text.includes('error'))   type = 'error';

          // Hide original toast
          toast.style.display = 'none';
          showJLModal(type === 'success' ? '✅ Success' :
                      type === 'error'   ? '❌ Error'   :
                      type === 'warn'    ? '⚠️ Warning' : 'ℹ️ Info',
                      text.replace(/[✅❌⚠️ℹ️]/g, '').trim(), type);
        }
      });
    });
  });

  alertObserver.observe(document.body, { childList: true, subtree: true });
}

function showJLModal(title, message, type) {
  if (!modal || !modalTitle || !modalBody) return;
  modalTitle.textContent = title;
  var cls = 'jl-alert jl-alert-' + type;
  var icons = { success: '✅', error: '❌', warn: '⚠️', info: 'ℹ️' };
  var icon = icons[type] || 'ℹ️';
  modalBody.innerHTML = '<div class="' + cls + '">' +
    '<div class="jl-alert-icon">' + icon + '</div>' +
    '<div class="jl-alert-text">' +
    '  <div class="jl-alert-body">' + message + '</div>' +
    '</div>' +
    '</div>' +
    '<button onclick="document.getElementById(\'jl-modal-overlay\').classList.remove(\'active\');' +
    'document.body.style.overflow=\'\';" style="' +
    'width:100%;margin-top:14px;padding:13px;border-radius:10px;' +
    'background:rgba(255,255,255,0.07);border:1px solid rgba(255,255,255,0.12);' +
    'color:#e2e8f0;font-size:0.92rem;font-weight:700;cursor:pointer;' +
    'font-family:Space Grotesk,sans-serif;">OK</button>';
  openModal();
}

// ── Sync active tab with Streamlit's actual state ─────────────────────────
function syncActiveTab() {
  var stTabs = getStreamlitTabs();
  if (!stTabs || stTabs.length === 0) return;
  stTabs.forEach(function(tab, i) {
    if (tab.getAttribute('aria-selected') === 'true' ||
        tab.classList.contains('active') ||
        tab.getAttribute('data-active') === 'true') {
      if (i !== currentTab) {
        currentTab = i;
        navItems.forEach(function(item, j) {
          item.classList.toggle('active', j === i);
        });
      }
    }
  });
}

// ── Keyboard: physical back button / Escape ───────────────────────────────
document.addEventListener('keydown', function(e) {
  if (e.key === 'Escape') closeModal();
});

// ── Resize handler ────────────────────────────────────────────────────────
window.addEventListener('resize', function() {
  isMobile = window.innerWidth <= 768;
  if (bottomNav) bottomNav.style.display = isMobile ? 'block' : 'none';
  if (fab)       fab.style.display = isMobile ? 'flex' : 'none';
});

// ── Init sequence ─────────────────────────────────────────────────────────
// Set first tab active
if (navItems.length > 0) navItems[0].classList.add('active');

// Start alert interception
interceptAlerts();

// Periodically sync with Streamlit tab state
setInterval(syncActiveTab, 800);

// Prevent double-tap zoom
var lastTouch = 0;
document.addEventListener('touchend', function(e) {
  var now = Date.now();
  if (now - lastTouch < 300) {
    e.preventDefault();
  }
  lastTouch = now;
}, { passive: false });

// Prevent pinch zoom
document.addEventListener('gesturestart', function(e) { e.preventDefault(); }, { passive: false });
document.addEventListener('gesturechange', function(e) { e.preventDefault(); }, { passive: false });
document.addEventListener('gestureend', function(e) { e.preventDefault(); }, { passive: false });

})();
</script>
"""


def _build_nav_items() -> str:
    """Build HTML for nav items."""
    items = []
    for i, tab in enumerate(_TABS):
        items.append(
            f'<button class="jl-nav-item" '
            f'data-index="{i}" '
            f'aria-label="{tab["label"]}" '
            f'title="{tab["label"]}">'
            f'<span class="jl-nav-icon">{tab["icon"]}</span>'
            f'<span class="jl-nav-label">{tab["short"]}</span>'
            f'</button>'
        )
    return "\n    ".join(items)


def inject_mobile_nav():
    """
    Call this once in main() after page config.
    Injects the complete mobile navigation layer.
    """
    nav_html = _MOBILE_HTML.replace("{NAV_ITEMS}", _build_nav_items())
    full_html = _MOBILE_CSS + nav_html + _MOBILE_JS

    components.html(full_html, height=1, scrolling=False)

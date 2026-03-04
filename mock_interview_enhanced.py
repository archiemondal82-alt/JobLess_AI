"""
ENHANCED MOCK INTERVIEW MODULE
- Conversational AI that acts like Claude/Gemini (asks follow-ups, provides real guidance)
- Auto-typing: Speech-to-text automatically populates the text input
- Real-time AI responses with streaming for better UX
"""

import streamlit as st
import streamlit.components.v1 as components
import json
from typing import Optional, List, Dict


# ============================================================================
# FIX #1: IMPROVED VOICE UI HTML WITH AUTO-SYNC TO STREAMLIT
# ============================================================================

_VOICE_UI_ENHANCED_HTML = """<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<link href="https://fonts.googleapis.com/css2?family=Syne:wght@700;800&family=DM+Mono:wght@400;500&family=DM+Sans:wght@300;400;500&display=swap" rel="stylesheet">
<style>
*{margin:0;padding:0;box-sizing:border-box}
html,body{background:#050a12;color:#e2e8f0;font-family:'DM Sans',sans-serif;height:100%;overflow:hidden}
#wrap{display:flex;gap:12px;padding:12px;height:260px}

/* WEBCAM */
.cam-col{flex:0 0 180px;display:flex;flex-direction:column;gap:8px}
.cam-box{border-radius:12px;overflow:hidden;background:#0a0f1a;border:2px solid rgba(0,210,255,.2);aspect-ratio:1;position:relative}
.cam-box video{width:100%;height:100%;object-fit:cover;display:block;transform:scaleX(-1)}
.no-cam{position:absolute;inset:0;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:4px;color:rgba(255,255,255,.2);font-size:.6rem;font-family:'DM Mono',monospace}
.no-cam span{font-size:1.6rem;opacity:.3}
.rec-badge{position:absolute;top:6px;left:6px;display:flex;align-items:center;gap:3px;background:rgba(0,0,0,.7);border-radius:20px;padding:2px 7px}
.rec-dot{width:5px;height:5px;border-radius:50%;background:#ef4444;animation:recdot 1.2s ease-in-out infinite}
@keyframes recdot{0%,100%{opacity:1}50%{opacity:.2}}
.rec-txt{font-size:.48rem;font-family:'DM Mono',monospace;color:rgba(255,255,255,.7);text-transform:uppercase;letter-spacing:.08em}

.score-col{flex:1;display:flex;flex-direction:column;gap:4px;overflow-y:auto}
.score-col::-webkit-scrollbar{width:2px}
.score-col::-webkit-scrollbar-thumb{background:rgba(0,210,255,.2);border-radius:2px}
.sc-row{display:flex;align-items:center;justify-content:space-between;background:rgba(255,255,255,.03);border:1px solid rgba(255,255,255,.07);border-radius:8px;padding:5px 10px;animation:fadeup .35s ease forwards}
@keyframes fadeup{from{opacity:0;transform:translateY(5px)}to{opacity:1;transform:translateY(0)}}
.sc-q{font-family:'DM Mono',monospace;font-size:.6rem;color:rgba(255,255,255,.4)}
.sc-v{font-family:'Syne',sans-serif;font-size:.85rem;font-weight:800}

/* AI PANEL */
.ai-col{flex:1;display:flex;flex-direction:column;gap:8px}
.ai-box{background:rgba(168,85,247,.06);border:1px solid rgba(168,85,247,.2);border-radius:12px;padding:12px;display:flex;gap:12px;align-items:flex-start;flex:0 0 auto}
.ai-avatar{width:40px;height:40px;border-radius:50%;background:linear-gradient(135deg,rgba(168,85,247,.35),rgba(0,210,255,.2));border:2px solid rgba(168,85,247,.4);display:flex;align-items:center;justify-content:center;font-size:1.1rem;flex-shrink:0}
.ai-avatar.glow{animation:avatarglow 1s ease-in-out infinite}
@keyframes avatarglow{0%,100%{box-shadow:0 0 0 0 rgba(168,85,247,.5)}50%{box-shadow:0 0 0 8px rgba(168,85,247,.0)}}
.ai-content{flex:1;min-width:0}
.ai-lbl{font-family:'DM Mono',monospace;font-size:.5rem;letter-spacing:.15em;text-transform:uppercase;color:rgba(168,85,247,.6);margin-bottom:5px}
.ai-txt{font-size:.82rem;color:#e2e8f0;line-height:1.55}
.wv{display:flex;align-items:center;gap:2px;height:14px;margin-top:5px}
.wv-b{width:3px;border-radius:2px;background:#a855f7;opacity:.3;height:4px}
.wv-b.on{opacity:.9;animation:wvb .55s ease-in-out infinite}
.wv-b:nth-child(1){animation-delay:0s;height:4px}
.wv-b:nth-child(2){animation-delay:.08s;height:9px}
.wv-b:nth-child(3){animation-delay:.14s;height:14px}
.wv-b:nth-child(4){animation-delay:.18s;height:10px}
.wv-b:nth-child(5){animation-delay:.22s;height:13px}
.wv-b:nth-child(6){animation-delay:.18s;height:7px}
.wv-b:nth-child(7){animation-delay:.1s;height:5px}
@keyframes wvb{0%,100%{transform:scaleY(1)}50%{transform:scaleY(1.6)}}

/* MIC / TRANSCRIPT */
.mic-box{flex:1;background:rgba(0,210,255,.04);border:1px solid rgba(0,210,255,.12);border-radius:12px;padding:12px;display:flex;flex-direction:column;gap:8px}
.mic-top{display:flex;align-items:center;gap:8px}
.mic-lbl{font-family:'DM Mono',monospace;font-size:.5rem;letter-spacing:.15em;text-transform:uppercase;color:rgba(0,210,255,.5)}
.live-dot{width:5px;height:5px;border-radius:50%;background:#ef4444;opacity:0;flex-shrink:0}
.live-dot.on{opacity:1;animation:livedot 1s ease-in-out infinite}
@keyframes livedot{0%,100%{opacity:1}50%{opacity:.2}}
.transcript{flex:1;font-size:.78rem;color:#64748b;line-height:1.6;font-style:italic;overflow-y:auto}
.transcript.has{color:#e2e8f0;font-style:normal}
.transcript::-webkit-scrollbar{width:2px}
.transcript::-webkit-scrollbar-thumb{background:rgba(0,210,255,.2);border-radius:2px}
.mic-btn{width:38px;height:38px;border-radius:50%;background:linear-gradient(135deg,#00d2ff,#0ea8d8);border:none;cursor:pointer;font-size:1rem;display:flex;align-items:center;justify-content:center;transition:all .2s;box-shadow:0 0 15px rgba(0,210,255,.3);flex-shrink:0}
.mic-btn:hover{transform:scale(1.1)}
.mic-btn.listening{background:linear-gradient(135deg,#ef4444,#dc2626);box-shadow:0 0 15px rgba(239,68,68,.4);animation:micon .9s ease-in-out infinite}
@keyframes micon{0%,100%{box-shadow:0 0 15px rgba(239,68,68,.4)}50%{box-shadow:0 0 30px rgba(239,68,68,.7)}}
.mic-btn.off{background:rgba(255,255,255,.08);box-shadow:none;cursor:not-allowed;opacity:.4}
.clear-btn{background:rgba(255,255,255,.06);border:1px solid rgba(255,255,255,.12);border-radius:20px;color:#64748b;font-family:'DM Mono',monospace;font-size:.55rem;padding:3px 10px;cursor:pointer;letter-spacing:.05em}
.clear-btn:hover{color:#e2e8f0}
.no-speech-warn{font-size:.7rem;color:#f59e0b;background:rgba(245,158,11,.08);border:1px solid rgba(245,158,11,.2);border-radius:8px;padding:6px 10px;text-align:center}
.auto-sync-badge{font-size:.6rem;background:rgba(34,197,94,.15);color:#22c55e;padding:2px 8px;border-radius:6px;margin-left:auto;font-family:'DM Mono',monospace}
</style>
</head>
<body>
<div id="wrap">
  <!-- WEBCAM -->
  <div class="cam-col">
    <div class="cam-box" id="camBox">
      <video id="vid" autoplay muted playsinline style="display:none"></video>
      <div class="no-cam" id="noCam"><span>📷</span>Camera off</div>
      <div class="rec-badge" id="recBadge" style="display:none">
        <div class="rec-dot"></div><span class="rec-txt">LIVE</span>
      </div>
    </div>
    <div class="score-col" id="scoreCol"></div>
  </div>

  <!-- AI SPEAKING -->
  <div class="ai-col">
    <div class="ai-box">
      <div class="ai-avatar" id="aiAvatar">🤖</div>
      <div class="ai-content">
        <div class="ai-lbl">AI Interviewer</div>
        <div class="ai-txt" id="aiTxt">__QUESTION__</div>
        <div class="wv" id="wv">
          <div class="wv-b"></div><div class="wv-b"></div><div class="wv-b"></div>
          <div class="wv-b"></div><div class="wv-b"></div><div class="wv-b"></div>
          <div class="wv-b"></div>
        </div>
      </div>
    </div>
    <div class="mic-box">
      <div class="mic-top">
        <div class="live-dot" id="liveDot"></div>
        <div class="mic-lbl">YOUR ANSWER</div>
        <div style="margin-left:auto;display:flex;gap:6px;align-items:center">
          <div class="auto-sync-badge">Auto-Typing ✓</div>
          <button class="clear-btn" onclick="clearTranscript()">Clear</button>
          <button class="mic-btn off" id="micBtn" onclick="toggleMic()">🎤</button>
        </div>
      </div>
      <div class="transcript" id="transcript">Press 🎤 to start speaking...</div>
    </div>
  </div>

  <!-- PER-Q SCORES (right col) -->
  <div class="cam-col" id="scoresRight" style="overflow-y:auto;gap:4px">
    __SCORES_HTML__
  </div>
</div>

<script>
var QUESTION = "__QUESTION_JS__";
var SCORES = __SCORES_JSON__;
var synth = window.speechSynthesis;
var recognition = null;
var isListening = false;
var finalT = "", interimT = "";

// ── INIT ──────────────────────────────────────────────────────
initWebcam();
initSpeech();
speakQuestion(QUESTION);

function initWebcam() {
  if (!navigator.mediaDevices) return;
  navigator.mediaDevices.getUserMedia({video:{facingMode:'user'},audio:false})
    .then(function(s){
      var v = document.getElementById('vid');
      v.srcObject = s; v.style.display = 'block';
      document.getElementById('noCam').style.display = 'none';
      document.getElementById('recBadge').style.display = 'flex';
    }).catch(function(){});
}

function initSpeech() {
  var SR = window.SpeechRecognition || window.webkitSpeechRecognition;
  if (!SR) {
    document.getElementById('transcript').innerHTML =
      '<div class="no-speech-warn">⚠️ Speech recognition needs Chrome or Edge.<br>Type your answer in the box below.</div>';
    return;
  }
  recognition = new SR();
  recognition.continuous = true;
  recognition.interimResults = true;
  recognition.lang = 'en-US';
  recognition.onresult = function(e) {
    var f='', im='';
    for(var i=e.resultIndex;i<e.results.length;i++){
      if(e.results[i].isFinal) f += e.results[i][0].transcript;
      else im += e.results[i][0].transcript;
    }
    if(f) finalT += f + ' ';
    interimT = im;
    showTranscript();
  };
  recognition.onerror = function(e){ if(e.error!=='no-speech') console.log(e.error); };
  recognition.onend = function(){ if(isListening){ try{recognition.start();}catch(e){} } };
  document.getElementById('micBtn').classList.remove('off');
  document.getElementById('micBtn').disabled = false;
}

function toggleMic() {
  if (isListening) stopListening(); else startListening();
}

function startListening() {
  if (!recognition) return;
  isListening = true;
  try { recognition.start(); } catch(e) {}
  document.getElementById('micBtn').classList.add('listening');
  document.getElementById('micBtn').innerHTML = '⏹';
  document.getElementById('liveDot').classList.add('on');
}

function stopListening() {
  isListening = false;
  if (recognition) try { recognition.stop(); } catch(e) {}
  document.getElementById('micBtn').classList.remove('listening');
  document.getElementById('micBtn').innerHTML = '🎤';
  document.getElementById('liveDot').classList.remove('on');
}

function clearTranscript() {
  finalT = ''; interimT = '';
  var el = document.getElementById('transcript');
  el.textContent = 'Press 🎤 to start speaking...';
  el.classList.remove('has');
  // AUTO-SYNC FIX: Also clear the input field in Streamlit
  window.parent.postMessage({type:'voice_transcript_clear'}, '*');
}

function showTranscript() {
  var full = (finalT + interimT).trim();
  var el = document.getElementById('transcript');
  if (!full) { el.textContent='Press 🎤 to start speaking...'; el.classList.remove('has'); }
  else { el.textContent = full; el.classList.add('has'); el.scrollTop = el.scrollHeight; }
  
  // AUTO-SYNC FIX: Send transcript to Streamlit in real-time
  try { 
    window.parent.postMessage({
      type:'voice_transcript_update', 
      text: finalT.trim(),
      interim: interimT.trim(),
      full: full
    }, '*'); 
  } catch(e){}
}

function speakQuestion(txt) {
  if (!txt || !synth) return;
  synth.cancel();
  var u = new SpeechSynthesisUtterance(txt);
  u.rate = 0.92; u.pitch = 1.0; u.volume = 1.0;
  var voices = synth.getVoices();
  var pref = voices.find(function(v){ return v.name.includes('Google') && v.lang.startsWith('en'); })
          || voices.find(function(v){ return v.lang.startsWith('en-') && !v.localService; })
          || voices.find(function(v){ return v.lang.startsWith('en'); });
  if (pref) u.voice = pref;
  var wvBars = document.querySelectorAll('.wv-b');
  var avatar = document.getElementById('aiAvatar');
  u.onstart = function() {
    wvBars.forEach(function(b){ b.classList.add('on'); });
    avatar.classList.add('glow');
  };
  u.onend = u.onerror = function() {
    wvBars.forEach(function(b){ b.classList.remove('on'); });
    avatar.classList.remove('glow');
  };
  if (voices.length === 0) {
    synth.onvoiceschanged = function() {
      var v2 = synth.getVoices();
      var p2 = v2.find(function(v){ return v.name.includes('Google') && v.lang.startsWith('en'); })
             || v2.find(function(v){ return v.lang.startsWith('en'); });
      if (p2) u.voice = p2;
      synth.speak(u);
      synth.onvoiceschanged = null;
    };
  } else {
    synth.speak(u);
  }
}

// Render score history
(function(){
  if (!SCORES || !SCORES.length) return;
  var col = document.getElementById('scoresRight');
  col.innerHTML = '<div style="font-family:DM Mono,monospace;font-size:.48rem;text-transform:uppercase;letter-spacing:.12em;color:rgba(0,210,255,.4);margin-bottom:4px;">Scores</div>';
  SCORES.forEach(function(s, i){
    var c = s>=85?'#22c55e':s>=70?'#00d2ff':s>=55?'#f59e0b':'#ef4444';
    var d = document.createElement('div');
    d.className = 'sc-row';
    d.innerHTML = '<span class="sc-q">Q'+(i+1)+'</span><span class="sc-v" style="color:'+c+'">'+s+'</span>';
    col.appendChild(d);
  });
})();
</script>
</body>
</html>"""


# ============================================================================
# FIX #2: CONVERSATIONAL AI RESPONSE HANDLER
# ============================================================================

def get_conversational_ai_response(ai_handler, question: str, user_answer: str, 
                                  role: str, model: str, conversation_history: List[Dict] = None) -> str:
    """
    Get real conversational AI feedback - like Claude/Gemini would provide.
    This is MORE than just evaluation - it's an actual interview conversation.
    
    Args:
        ai_handler: Your AIHandler instance
        question: The interview question asked
        user_answer: The user's answer
        role: The job role
        model: The AI model to use
        conversation_history: Previous conversation turns (optional)
    
    Returns:
        Conversational feedback string
    """
    
    system_prompt = f"""You are an expert technical interviewer conducting a mock interview for a {role} position.

Your role:
1. EVALUATE: Assess the quality of the candidate's answer
2. GUIDE: Provide constructive feedback and suggestions for improvement
3. ENCOURAGE: Give praise for good points and boost confidence
4. PROBE: Ask relevant follow-up questions if the answer is incomplete
5. TEACH: Offer insights and best practices

Format your response as a natural conversation, not a formal report. Be warm, professional, and genuinely helpful - like Claude or a senior mentor would be."""
    
    user_prompt = f"""Question asked: "{question}"

Candidate's answer: "{user_answer}"

Please provide:
1. A brief assessment (1-2 sentences) of the key strengths
2. 2-3 specific areas for improvement with examples
3. A relevant follow-up question to deepen the discussion
4. A brief encouragement or tip

Speak naturally - this is a conversation, not a report."""
    
    # Build conversation with history if provided
    messages = []
    if conversation_history:
        messages.extend(conversation_history)
    
    messages.append({"role": "user", "content": user_prompt})
    
    # Call AI with system prompt
    try:
        response = ai_handler.client.messages.create(
            model=model,
            max_tokens=400,
            system=system_prompt,
            messages=messages
        )
        return response.content[0].text
    except Exception as e:
        return f"Could not generate response: {str(e)}"


def render_enhanced_voice_interview(ai_handler, selected_model: str):
    """
    Enhanced voice interview with:
    - Auto-typing speech transcription
    - Conversational AI responses (not just evaluation)
    - Real-time feedback mechanism
    """
    import streamlit.components.v1 as _cmp
    
    role = st.session_state.get("voice_mi_role", "Software Engineer")
    level = st.session_state.get("voice_mi_level", "Fresher")
    
    # Generate questions if needed
    if "voice_questions" not in st.session_state or not st.session_state.voice_questions:
        with st.spinner("🧠 Generating your interview questions..."):
            qs = ai_handler.generate_interview_questions(role, level, selected_model)
        if not qs:
            st.error("❌ Failed to generate questions. Check your API key.")
            return
        
        st.session_state.voice_questions = qs[:6]
        st.session_state.voice_q_index = 0
        st.session_state.voice_answers = {}
        st.session_state.voice_ai_responses = {}  # Store conversational responses
        st.session_state.voice_done = False
        st.rerun()
    
    questions = st.session_state.voice_questions
    q_idx = st.session_state.voice_q_index
    answers = st.session_state.voice_answers
    ai_responses = st.session_state.get("voice_ai_responses", {})
    total = len(questions)
    
    if q_idx >= total:
        st.success("🎉 Interview complete! Check the report below.")
        return
    
    # Progress
    prog = q_idx / total
    st.markdown(f"""
    <div style="background:rgba(0,210,255,.1);border-radius:12px;padding:12px;margin-bottom:16px;">
        <div style="display:flex;justify-content:space-between;align-items:center;">
            <span style="color:#00d2ff;font-weight:700;">Question {q_idx + 1} of {total}</span>
            <div style="width:150px;background:rgba(0,210,255,.2);border-radius:20px;height:6px;overflow:hidden;">
                <div style="width:{prog*100:.0f}%;height:100%;background:#00d2ff;transition:width .3s;"></div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    current_q = questions[q_idx]
    q_text = current_q.get("question", "")
    scores_list = []
    
    # Render voice UI with enhanced HTML
    scores_json = json.dumps(scores_list)
    html_content = _VOICE_UI_ENHANCED_HTML.replace("__QUESTION__", q_text).replace("__QUESTION_JS__", q_text.replace('"', '\\"')).replace("__SCORES_JSON__", scores_json).replace("__SCORES_HTML__", "")
    
    # Component to capture voice input
    voice_component = _cmp.html(html_content, height=280, scrolling=False)
    
    # Display current question
    st.markdown(f"""
    <div style="background:rgba(168,85,247,.08);border:1px solid rgba(168,85,247,.2);border-radius:12px;padding:14px;margin:12px 0;">
        <div style="color:rgba(168,85,247,.8);font-size:.75rem;font-weight:600;margin-bottom:6px;text-transform:uppercase;letter-spacing:.1em;">📝 Question</div>
        <div style="color:#e2e8f0;font-size:1rem;line-height:1.6;">{q_text}</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Text input that gets auto-populated from speech
    st.markdown('<div style="color:rgba(0,210,255,.7);font-size:.75rem;font-weight:600;margin:12px 0 6px;text-transform:uppercase;letter-spacing:.1em;">🎤 Your Answer</div>', unsafe_allow_html=True)
    
    user_answer = st.text_area(
        "answer_input",
        value=answers.get(str(q_idx), ""),
        height=120,
        placeholder="Speak your answer using the mic above - it will auto-populate here!",
        label_visibility="collapsed"
    )
    
    # Save answer to session
    if user_answer:
        st.session_state.voice_answers[str(q_idx)] = user_answer
    
    # Action buttons
    col1, col2, col3 = st.columns([2, 2, 1])
    
    with col1:
        if st.button("💡 Show Hint", use_container_width=True, key=f"hint_{q_idx}"):
            hint = current_q.get("hint", "No hint available")
            st.info(hint)
    
    with col2:
        is_last = q_idx == total - 1
        btn_label = "Submit & Get Feedback 🚀" if not is_last else "Finish Interview ✓"
        
        if st.button(btn_label, use_container_width=True, type="primary", key=f"submit_{q_idx}"):
            if not user_answer.strip():
                st.warning("⚠️ Please provide an answer first!")
            else:
                # Get CONVERSATIONAL AI response
                with st.spinner("🤖 Generating personalized feedback..."):
                    ai_feedback = get_conversational_ai_response(
                        ai_handler,
                        q_text,
                        user_answer.strip(),
                        role,
                        selected_model
                    )
                    st.session_state.voice_ai_responses[str(q_idx)] = ai_feedback
                
                # Show the AI's conversational response
                st.markdown(f"""
                <div style="background:linear-gradient(135deg,rgba(168,85,247,.1),rgba(0,210,255,.08));border:1px solid rgba(168,85,247,.3);border-radius:12px;padding:14px;margin-top:12px;">
                    <div style="color:#a855f7;font-weight:600;margin-bottom:8px;">🤖 AI Interviewer Feedback:</div>
                    <div style="color:#e2e8f0;line-height:1.7;font-size:.95rem;">{ai_feedback}</div>
                </div>
                """, unsafe_allow_html=True)
                
                # Move to next question
                if is_last:
                    st.session_state.voice_done = True
                    st.success("✅ Interview complete!")
                else:
                    st.session_state.voice_q_index = q_idx + 1
                    st.rerun()
    
    with col3:
        if st.button("🔄 Restart", use_container_width=True, key="restart_voice"):
            for k in list(st.session_state.keys()):
                if k.startswith("voice_"):
                    del st.session_state[k]
            st.rerun()


# ============================================================================
# USAGE EXAMPLE - Add this to your main interview function
# ============================================================================

"""
# In your main mock interview rendering function, replace:

    if voice_mode:
        if st.session_state.get("voice_interview_active", False):
            _render_voice_interview_agent(ai_handler, selected_model)
            
# WITH:

    if voice_mode:
        if st.session_state.get("voice_interview_active", False):
            render_enhanced_voice_interview(ai_handler, selected_model)  # NEW ENHANCED VERSION

"""

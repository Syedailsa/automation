import React, { useState, useRef, useEffect } from 'react';
import {
  Home, MessageSquare, FolderOpen, Clock, BarChart3, Settings,
  Plus, Search, Bell, Sun, Moon, Paperclip, Mic, Send, Copy, Check,
  Trash2, X, Menu, FileText, Image as ImageIcon, File, Sparkles, Zap,
  Library, Upload, Type, LogOut,
  Wand2, Headphones, Presentation, Clapperboard, Network, Layers,
  ListChecks, PieChart, Table, Pin, ArrowLeft, ChevronRight, ChevronLeft,
  Play, Pause, RotateCw, Loader2, AlertTriangle,
  Mail, Lock, Eye, EyeOff, User, ArrowRight
} from 'lucide-react';

/* ============================================================
   NovaAI — Intelligent AI Workspace Portal
   One Workspace. Unlimited AI Intelligence.
   ============================================================ */

const uid = () => Math.random().toString(36).slice(2, 10);

/* Password hashing for the offline demo. Uses Web Crypto PBKDF2 when available
   (secure context); otherwise falls back gracefully so the app never crashes.
   Note: real, production hashing (bcrypt) lives in the auth backend. */
const toHex = (buf) => [...new Uint8Array(buf)].map(b => b.toString(16).padStart(2, '0')).join('');
const cryptoOK = () => typeof crypto !== 'undefined' && crypto.subtle && crypto.getRandomValues;
async function pbkdf2(password, saltHex) {
  const enc = new TextEncoder();
  const salt = saltHex
    ? Uint8Array.from(saltHex.match(/.{2}/g).map(b => parseInt(b, 16)))
    : crypto.getRandomValues(new Uint8Array(16));
  const key = await crypto.subtle.importKey('raw', enc.encode(password), 'PBKDF2', false, ['deriveBits']);
  const bits = await crypto.subtle.deriveBits({ name: 'PBKDF2', salt, iterations: 100000, hash: 'SHA-256' }, key, 256);
  return `p:${toHex(salt)}:${toHex(bits)}`;
}
// Tiny non-crypto fallback (demo only) — never throws.
const weakHash = (s) => { let h = 5381; for (let i = 0; i < s.length; i++) h = ((h << 5) + h + s.charCodeAt(i)) >>> 0; return 'w:' + h.toString(16); };
async function hashPw(pw) {
  try { if (cryptoOK()) return await pbkdf2(pw); } catch (e) {}
  return weakHash(pw);
}
async function verifyPw(pw, stored) {
  if (!stored) return false;
  try {
    if (stored.startsWith('w:')) return stored === weakHash(pw);
    if (stored.startsWith('p:')) { const [, saltHex] = stored.split(':'); return (await pbkdf2(pw, saltHex)) === stored; }
    // legacy "saltHex:hashHex" (no prefix) from an earlier version
    if (stored.includes(':')) { const [saltHex] = stored.split(':'); return (await pbkdf2(pw, saltHex)) === ('p:' + stored); }
  } catch (e) {}
  return stored === weakHash(pw);
}

const SYSTEM = `You are NovaAI, an intelligent enterprise AI workspace assistant.
You help professionals with document analysis, summarization, research, question answering,
report writing, code generation, code review, data analysis, and professional writing.
Give clear, well-structured, professional answers. Use markdown (headings, bold, bullet lists,
numbered lists, and code blocks) whenever it makes the answer easier to read. Be concise but complete.`;

const SUGGESTIONS = [
  { icon: Sparkles, title: 'Explain a concept', text: 'Explain quantum computing in simple terms with a real-world analogy.' },
  { icon: FileText, title: 'Write an email', text: 'Write a professional project status update email to my manager.' },
  { icon: Zap, title: 'Generate code', text: 'Write a clean Python function that reads a CSV file and returns the column averages.' },
  { icon: BarChart3, title: 'Plan a task', text: 'Draft a clear 5-point plan for launching a new SaaS product.' },
];

/* ---------- lightweight markdown renderer ---------- */
function escapeHtml(s) {
  return s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
}
function inlineMd(s) {
  return s
    .replace(/`([^`]+)`/g, '<code>$1</code>')
    .replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>')
    .replace(/(^|[^*])\*([^*]+)\*/g, '$1<em>$2</em>');
}
function renderMarkdown(raw) {
  const blocks = [];
  let text = raw.replace(/```(\w*)\n?([\s\S]*?)```/g, (m, lang, code) => {
    blocks.push(escapeHtml(code.replace(/\n$/, '')));
    return `\uE000${blocks.length - 1}\uE000`;
  });
  const lines = text.split('\n');
  let html = '', inUl = false, inOl = false;
  const closeLists = () => {
    if (inUl) { html += '</ul>'; inUl = false; }
    if (inOl) { html += '</ol>'; inOl = false; }
  };
  for (const line of lines) {
    const t = line.trim();
    if (/^\uE000\d+\uE000$/.test(t)) {
      closeLists();
      const i = +t.replace(/\uE000/g, '');
      html += `<pre><code>${blocks[i]}</code></pre>`;
      continue;
    }
    const h = line.match(/^(#{1,3})\s+(.*)$/);
    if (h) { closeLists(); const lvl = Math.min(h[1].length + 2, 6); html += `<h${lvl}>${inlineMd(escapeHtml(h[2]))}</h${lvl}>`; continue; }
    const ul = line.match(/^\s*[-*]\s+(.*)$/);
    if (ul) { if (!inUl) { closeLists(); html += '<ul>'; inUl = true; } html += `<li>${inlineMd(escapeHtml(ul[1]))}</li>`; continue; }
    const ol = line.match(/^\s*\d+\.\s+(.*)$/);
    if (ol) { if (!inOl) { closeLists(); html += '<ol>'; inOl = true; } html += `<li>${inlineMd(escapeHtml(ol[1]))}</li>`; continue; }
    if (t === '') { closeLists(); continue; }
    closeLists();
    html += `<p>${inlineMd(escapeHtml(line))}</p>`;
  }
  closeLists();
  return html;
}

const timeAgo = (ts) => {
  const s = Math.floor((Date.now() - ts) / 1000);
  if (s < 60) return 'just now';
  if (s < 3600) return `${Math.floor(s / 60)}m ago`;
  if (s < 86400) return `${Math.floor(s / 3600)}h ago`;
  return `${Math.floor(s / 86400)}d ago`;
};

/* ---------- logo mark ---------- */
function NovaMark({ size = 26 }) {
  return (
    <svg width={size} height={size} viewBox="0 0 32 32" className="nova-mark" aria-hidden="true">
      <defs>
        <linearGradient id="ng" x1="0" y1="0" x2="1" y2="1">
          <stop offset="0" stopColor="#3B82F6" />
          <stop offset="1" stopColor="#8B5CF6" />
        </linearGradient>
      </defs>
      <circle cx="16" cy="16" r="11" fill="none" stroke="url(#ng)" strokeWidth="2" opacity="0.45" />
      <circle cx="16" cy="16" r="5" fill="url(#ng)" />
      <g className="nova-orbit"><circle cx="27" cy="16" r="2.4" fill="#8B5CF6" /></g>
    </svg>
  );
}

const TOOLS = [
  { kind: 'audio', title: 'Audio Overview', desc: 'A two-host audio summary you can play', icon: Headphones },
  { kind: 'slides', title: 'Slide Deck', desc: 'Presentation-ready slides', icon: Presentation, beta: true },
  { kind: 'video', title: 'Video Overview', desc: 'A narrated scene-by-scene storyboard', icon: Clapperboard },
  { kind: 'mindmap', title: 'Mind Map', desc: 'See how the key ideas connect', icon: Network },
  { kind: 'report', title: 'Reports', desc: 'A structured, professional written report', icon: FileText },
  { kind: 'flashcards', title: 'Flashcards', desc: 'Flip cards to study key concepts', icon: Layers },
  { kind: 'quiz', title: 'Quiz', desc: 'Test your knowledge, get scored', icon: ListChecks },
  { kind: 'infographic', title: 'Infographic', desc: 'Key stats and highlights at a glance', icon: PieChart, beta: true },
  { kind: 'table', title: 'Data Table', desc: 'Organize information into a clean table', icon: Table },
];

const STUDIO_SYSTEM = `You are NovaAI Work Studio. You transform the user's sources and conversation into polished study and work assets. Follow the requested output format exactly. When JSON is requested, output ONLY raw, valid, minified JSON — no surrounding text, no markdown, no code fences. Keep content concise so it fits in a compact output.`;

const TOOL_PROMPTS = {
  audio: 'Create an engaging two-host audio overview (like a short podcast) of the material above. Respond ONLY with JSON: {"title":string,"segments":[{"speaker":"Host A"|"Host B","text":string}]}. Use 6-10 short, natural, conversational segments alternating hosts.',
  slides: 'Create a professional slide deck from the material above. Respond ONLY with JSON: {"title":string,"slides":[{"title":string,"bullets":[string]}]}. Use 5 slides, 3-4 short bullets each.',
  video: 'Create a video overview storyboard from the material above. Respond ONLY with JSON: {"title":string,"scenes":[{"heading":string,"narration":string,"visual":string}]}. Use 5 concise scenes.',
  mindmap: 'Create a mind map of the material above. Respond ONLY with JSON: {"root":string,"branches":[{"label":string,"children":[string]}]}. Use 4-5 branches, 2-3 short children each.',
  report: 'Write a professional, well-structured report on the material above using markdown (## headings, **bold**, and bullet lists). Include a short executive summary, key findings, and a brief conclusion. Keep it focused.',
  flashcards: 'Create study flashcards from the material above. Respond ONLY with JSON: {"cards":[{"front":string,"back":string}]}. Use 6-8 cards with concise fronts and backs.',
  quiz: 'Create a multiple-choice quiz from the material above. Respond ONLY with JSON: {"questions":[{"q":string,"options":[string,string,string,string],"answer":number,"explanation":string}]}. Use 5 questions; "answer" is the 0-based index of the correct option; keep explanations to one sentence.',
  infographic: 'Create an infographic summary of the material above. Respond ONLY with JSON: {"title":string,"stats":[{"value":string,"label":string}],"highlights":[string]}. Use 3 punchy stats and 4-5 short highlights.',
  table: 'Organize the key information from the material above into a data table. Respond ONLY with JSON: {"title":string,"columns":[string],"rows":[[string]]}. Use 3-4 columns and up to 6 rows.',
};

function cleanJSON(raw) {
  let t = String(raw).trim().replace(/^```json/i, '').replace(/^```/, '').replace(/```$/, '').trim();
  const first = t.indexOf('{'); const last = t.lastIndexOf('}');
  if (first !== -1 && last !== -1 && last > first) t = t.slice(first, last + 1);
  t = t.replace(/,\s*([}\]])/g, '$1');
  return JSON.parse(t);
}

const stepLabel = (p) => p < 25 ? 'Reading your sources' : p < 55 ? 'Analyzing the content' : p < 85 ? 'Generating your asset' : 'Formatting the result';
const toolIcon = (kind) => kind === 'image' ? ImageIcon : kind === 'pdf' ? FileText : kind === 'text' ? FileText : File;

/* ---------- Work Studio tool output (renders in main workspace) ---------- */
function ToolView({ tool, status, progress, data, error, onBack, onRetry }) {
  const Icon = tool.icon;
  const [slide, setSlide] = useState(0);
  const [flipIdx, setFlipIdx] = useState(0);
  const [flipped, setFlipped] = useState(false);
  const [answers, setAnswers] = useState({});
  const [submitted, setSubmitted] = useState(false);
  const [playing, setPlaying] = useState(false);
  const [curSeg, setCurSeg] = useState(-1);
  const [copied, setCopied] = useState(false);
  const ttsOK = typeof window !== 'undefined' && 'speechSynthesis' in window;

  useEffect(() => {
    setSlide(0); setFlipIdx(0); setFlipped(false); setAnswers({}); setSubmitted(false); setCurSeg(-1); setPlaying(false);
    return () => { try { window.speechSynthesis && window.speechSynthesis.cancel(); } catch (e) {} };
  }, [data]);

  const playAudio = () => {
    if (!ttsOK || !data?.segments) return;
    window.speechSynthesis.cancel();
    const segs = data.segments;
    const voices = window.speechSynthesis.getVoices();
    let i = 0;
    const next = () => {
      if (i >= segs.length) { setPlaying(false); setCurSeg(-1); return; }
      setCurSeg(i);
      const u = new SpeechSynthesisUtterance(segs[i].text);
      if (voices.length) u.voice = voices[(segs[i].speaker === 'Host B' ? 1 : 0) % voices.length];
      u.rate = 1.03;
      u.onend = () => { i++; next(); };
      window.speechSynthesis.speak(u);
    };
    setPlaying(true); next();
  };
  const stopAudio = () => { try { window.speechSynthesis.cancel(); } catch (e) {} setPlaying(false); setCurSeg(-1); };
  const copyReport = () => { navigator.clipboard?.writeText(data?.markdown || ''); setCopied(true); setTimeout(() => setCopied(false), 1400); };

  const renderResult = () => {
    if (!data) return null;
    switch (tool.kind) {
      case 'audio': {
        const segs = data.segments || [];
        return (
          <div className="tool-result">
            <div className="audio-head">
              <div><div className="res-h">{data.title}</div><div className="ar-meta">{segs.length} segments · AI hosts</div></div>
              {ttsOK
                ? <button className="play-btn" onClick={playing ? stopAudio : playAudio}>{playing ? <Pause size={17} /> : <Play size={17} />}{playing ? 'Stop' : 'Play'}</button>
                : <span className="ar-meta">Read the script below</span>}
            </div>
            <div className="audio-script">
              {segs.map((s, i) => (
                <div key={i} className={`seg ${curSeg === i ? 'on' : ''}`}>
                  <span className={`seg-spk ${s.speaker === 'Host B' ? 'b' : 'a'}`}>{s.speaker}</span>
                  <p>{s.text}</p>
                </div>
              ))}
            </div>
          </div>
        );
      }
      case 'slides': {
        const sl = data.slides || [];
        const cur = sl[slide] || {};
        return (
          <div className="tool-result slides-wrap">
            <div className="slide-view">
              <div className="slide-num">Slide {slide + 1} / {sl.length}</div>
              <h2 className="slide-title">{cur.title}</h2>
              <ul className="slide-bullets">{(cur.bullets || []).map((b, i) => <li key={i}>{b}</li>)}</ul>
            </div>
            <div className="slide-nav">
              <button className="mini-btn" disabled={slide === 0} onClick={() => setSlide(s => s - 1)}><ChevronLeft size={16} /> Prev</button>
              <div className="dots">{sl.map((_, i) => <span key={i} className={i === slide ? 'on' : ''} onClick={() => setSlide(i)} />)}</div>
              <button className="mini-btn" disabled={slide >= sl.length - 1} onClick={() => setSlide(s => s + 1)}>Next <ChevronRight size={16} /></button>
            </div>
          </div>
        );
      }
      case 'video': {
        const scenes = data.scenes || [];
        return (
          <div className="tool-result">
            <h2 className="res-h">{data.title}</h2>
            <div className="storyboard">
              {scenes.map((s, i) => (
                <div key={i} className="scene">
                  <div className="scene-visual"><Clapperboard size={19} /><span>Scene {i + 1}</span></div>
                  <div className="scene-body">
                    <div className="scene-h">{s.heading}</div>
                    <div className="scene-vis">{s.visual}</div>
                    <p className="scene-narr">“{s.narration}”</p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        );
      }
      case 'mindmap': {
        const branches = data.branches || [];
        return (
          <div className="tool-result">
            <div className="mindmap">
              <div className="mm-root">{data.root}</div>
              <div className="mm-branches">
                {branches.map((b, i) => (
                  <div key={i} className="mm-branch" style={{ '--h': `${(i * 57) % 360}` }}>
                    <div className="mm-node">{b.label}</div>
                    <div className="mm-children">{(b.children || []).map((c, j) => <span key={j} className="mm-child">{c}</span>)}</div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        );
      }
      case 'report':
        return (
          <div className="tool-result">
            <div className="res-toolbar">
              <button className="mini-btn" onClick={copyReport}>{copied ? <><Check size={14} /> Copied</> : <><Copy size={14} /> Copy</>}</button>
            </div>
            <div className="report md" dangerouslySetInnerHTML={{ __html: renderMarkdown(data.markdown || '') }} />
          </div>
        );
      case 'flashcards': {
        const cards = data.cards || [];
        const c = cards[flipIdx] || {};
        return (
          <div className="tool-result flash-wrap">
            <div className={`flashcard ${flipped ? 'flipped' : ''}`} onClick={() => setFlipped(f => !f)}>
              <div className="fc-face fc-front"><span className="fc-tag">Question</span><span className="fc-body">{c.front}</span></div>
              <div className="fc-face fc-back"><span className="fc-tag">Answer</span><span className="fc-body">{c.back}</span></div>
            </div>
            <div className="fc-nav">
              <button className="mini-btn" disabled={flipIdx === 0} onClick={() => { setFlipIdx(i => i - 1); setFlipped(false); }}><ChevronLeft size={16} /></button>
              <span>{flipIdx + 1} / {cards.length}</span>
              <button className="mini-btn" disabled={flipIdx >= cards.length - 1} onClick={() => { setFlipIdx(i => i + 1); setFlipped(false); }}><ChevronRight size={16} /></button>
            </div>
            <div className="fc-hint">Tap the card to flip</div>
          </div>
        );
      }
      case 'quiz': {
        const qs = data.questions || [];
        const score = qs.reduce((n, q, i) => n + (answers[i] === q.answer ? 1 : 0), 0);
        return (
          <div className="tool-result quiz-wrap">
            {qs.map((q, i) => (
              <div key={i} className="quiz-q">
                <div className="qq-title">{i + 1}. {q.q}</div>
                <div className="qq-opts">
                  {(q.options || []).map((o, oi) => {
                    const chosen = answers[i] === oi;
                    const correct = submitted && oi === q.answer;
                    const wrong = submitted && chosen && oi !== q.answer;
                    return (
                      <button key={oi} className={`qq-opt ${chosen ? 'chosen' : ''} ${correct ? 'correct' : ''} ${wrong ? 'wrong' : ''}`}
                        disabled={submitted} onClick={() => setAnswers(a => ({ ...a, [i]: oi }))}>{o}</button>
                    );
                  })}
                </div>
                {submitted && q.explanation && <div className="qq-exp">{q.explanation}</div>}
              </div>
            ))}
            {!submitted
              ? <button className="btn-primary" disabled={Object.keys(answers).length < qs.length} onClick={() => setSubmitted(true)}>Submit answers</button>
              : <div className="quiz-score">You scored {score} / {qs.length}</div>}
          </div>
        );
      }
      case 'infographic':
        return (
          <div className="tool-result">
            <h2 className="res-h center">{data.title}</h2>
            <div className="info-stats">{(data.stats || []).map((s, i) => <div key={i} className="info-stat"><span className="is-val">{s.value}</span><span className="is-label">{s.label}</span></div>)}</div>
            <div className="info-highlights">{(data.highlights || []).map((h, i) => <div key={i} className="info-hl"><span className="ih-num">{i + 1}</span><span>{h}</span></div>)}</div>
          </div>
        );
      case 'table':
        return (
          <div className="tool-result">
            <h2 className="res-h">{data.title}</h2>
            <div className="table-scroll">
              <table className="data-table">
                <thead><tr>{(data.columns || []).map((c, i) => <th key={i}>{c}</th>)}</tr></thead>
                <tbody>{(data.rows || []).map((r, ri) => <tr key={ri}>{(r || []).map((c, ci) => <td key={ci}>{c}</td>)}</tr>)}</tbody>
              </table>
            </div>
          </div>
        );
      default: return null;
    }
  };

  return (
    <div className="tool-view">
      <div className="tv-head">
        <button className="tv-back" onClick={onBack}><ArrowLeft size={16} /> Workspace</button>
        <div className="tv-title"><Icon size={16} /> {tool.title}</div>
        <button className="mini-btn" onClick={onRetry} disabled={status === 'loading'}><RotateCw size={14} /> Regenerate</button>
      </div>
      <div className="tv-body">
        {status === 'loading' && (
          <div className="tool-loading">
            <div className="tl-orb"><Icon size={26} /></div>
            <div className="tl-title">Generating your {tool.title.toLowerCase()}…</div>
            <div className="tl-step">{stepLabel(progress)}</div>
            <div className="tl-bar"><div className="tl-fill" style={{ width: progress + '%' }} /></div>
            <div className="tl-pct">{Math.round(progress)}%</div>
          </div>
        )}
        {status === 'nomaterial' && (
          <div className="tool-error">
            <div className="te-ic soft"><Library size={26} /></div>
            <div className="te-title">Add a source first</div>
            <div className="te-msg">Add a document or note in the workspace, then generate your {tool.title.toLowerCase()}.</div>
            <button className="btn-primary" onClick={onBack}>Back to workspace</button>
          </div>
        )}
        {status === 'error' && (
          <div className="tool-error">
            <div className="te-ic"><AlertTriangle size={26} /></div>
            <div className="te-title">Couldn't generate this</div>
            <div className="te-msg">{error}</div>
            <button className="btn-primary" onClick={onRetry}><RotateCw size={15} /> Retry</button>
          </div>
        )}
        {status === 'done' && renderResult()}
      </div>
    </div>
  );
}

/* ---------- Brand marks for social login ---------- */
const BrandGoogle = () => (
  <svg width="16" height="16" viewBox="0 0 48 48" aria-hidden="true">
    <path fill="#FFC107" d="M43.611 20.083H42V20H24v8h11.303c-1.649 4.657-6.08 8-11.303 8-6.627 0-12-5.373-12-12s5.373-12 12-12c3.059 0 5.842 1.154 7.961 3.039l5.657-5.657C34.046 6.053 29.268 4 24 4 12.955 4 4 12.955 4 24s8.955 20 20 20 20-8.955 20-20c0-1.341-.138-2.65-.389-3.917z" />
    <path fill="#FF3D00" d="M6.306 14.691l6.571 4.819C14.655 15.108 18.961 12 24 12c3.059 0 5.842 1.154 7.961 3.039l5.657-5.657C34.046 6.053 29.268 4 24 4 16.318 4 9.656 8.337 6.306 14.691z" />
    <path fill="#4CAF50" d="M24 44c5.166 0 9.86-1.977 13.409-5.192l-6.19-5.238C29.211 35.091 26.715 36 24 36c-5.202 0-9.619-3.317-11.283-7.946l-6.522 5.025C9.505 39.556 16.227 44 24 44z" />
    <path fill="#1976D2" d="M43.611 20.083H42V20H24v8h11.303c-.792 2.237-2.231 4.166-4.087 5.571l6.19 5.238C36.971 39.205 44 34 44 24c0-1.341-.138-2.65-.389-3.917z" />
  </svg>
);
const BrandGithub = () => (
  <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">
    <path d="M12 .5C5.37.5 0 5.87 0 12.5c0 5.3 3.44 9.8 8.21 11.39.6.11.82-.26.82-.58 0-.29-.01-1.04-.02-2.04-3.34.73-4.04-1.61-4.04-1.61-.55-1.39-1.34-1.76-1.34-1.76-1.09-.75.08-.73.08-.73 1.21.09 1.84 1.24 1.84 1.24 1.07 1.83 2.81 1.3 3.5.99.11-.78.42-1.3.76-1.6-2.67-.3-5.47-1.33-5.47-5.93 0-1.31.47-2.38 1.24-3.22-.12-.3-.54-1.52.12-3.18 0 0 1.01-.32 3.3 1.23a11.5 11.5 0 016 0c2.29-1.55 3.3-1.23 3.3-1.23.66 1.66.24 2.88.12 3.18.77.84 1.24 1.91 1.24 3.22 0 4.61-2.81 5.62-5.49 5.92.43.37.81 1.1.81 2.22 0 1.6-.01 2.9-.01 3.29 0 .32.22.7.83.58C20.56 22.29 24 17.8 24 12.5 24 5.87 18.63.5 12 .5z" />
  </svg>
);
const BrandMicrosoft = () => (
  <svg width="15" height="15" viewBox="0 0 24 24" aria-hidden="true">
    <rect width="10" height="10" x="1" y="1" fill="#F25022" /><rect width="10" height="10" x="13" y="1" fill="#7FBA00" />
    <rect width="10" height="10" x="1" y="13" fill="#00A4EF" /><rect width="10" height="10" x="13" y="13" fill="#FFB900" />
  </svg>
);

/* ---------- Login / Signup / Forgot ---------- */
function AuthScreen({ theme, onToggleTheme, onAuthenticated, accounts = [], registerAccount }) {
  const [mode, setMode] = useState('login');
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirm, setConfirm] = useState('');
  const [showPw, setShowPw] = useState(false);
  const [remember, setRemember] = useState(true);
  const [agree, setAgree] = useState(false);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [resetSent, setResetSent] = useState(false);
  const validEmail = /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
  const PROVIDER_LABEL = { google: 'Google', github: 'GitHub', microsoft: 'Microsoft' };

  const finish = (user) => { setLoading(true); setTimeout(() => { setLoading(false); onAuthenticated(user); }, 650); };
  const submitLogin = async () => {
    setError('');
    const em = email.trim().toLowerCase();
    if (!validEmail) return setError('Please enter a valid email address.');
    if (!password) return setError('Please enter your password.');
    setLoading(true);
    const acct = accounts.find(a => a.email.toLowerCase() === em);
    const ok = acct && await verifyPw(password, acct.passwordHash);
    setLoading(false);
    if (!ok) return setError('Invalid email or password.');
    finish({ name: acct.name, email: acct.email });
  };
  const submitSignup = async () => {
    setError('');
    const em = email.trim().toLowerCase();
    if (!name.trim()) return setError('Please enter your name.');
    if (!validEmail) return setError('Please enter a valid email address.');
    if (password.length < 6) return setError('Password must be at least 6 characters.');
    if (password !== confirm) return setError('Passwords do not match.');
    if (!agree) return setError('Please accept the Terms to continue.');
    if (accounts.some(a => a.email.toLowerCase() === em)) return setError('An account with this email already exists. Please log in.');
    setLoading(true);
    const passwordHash = await hashPw(password);
    registerAccount({ name: name.trim(), email: email.trim(), passwordHash });
    setLoading(false);
    finish({ name: name.trim(), email: email.trim() });
  };
  // OAuth is NOT faked: real Google/GitHub/Microsoft sign-in needs the auth backend.
  const social = (provider) => {
    setError(`${PROVIDER_LABEL[provider]} sign-in uses real OAuth 2.0, which requires the NovaAI auth backend (see server/README). It can't run in this frontend-only preview — so it won't sign you in here.`);
  };
  const sendReset = () => { setError(''); if (!validEmail) return setError('Please enter a valid email address.'); setResetSent(true); };
  const fillDemo = () => { setEmail('demo@novaai.app'); setPassword('nova1234'); setError(''); };
  const onEnter = (e) => { if (e.key === 'Enter') { e.preventDefault(); mode === 'login' ? submitLogin() : mode === 'signup' ? submitSignup() : sendReset(); } };
  const switchMode = (m) => { setMode(m); setError(''); setResetSent(false); };

  return (
    <div className="auth">
      <button className="icon-btn auth-theme" onClick={onToggleTheme} title="Toggle theme">
        {theme === 'dark' ? <Sun size={18} /> : <Moon size={18} />}
      </button>

      <div className="auth-brand">
        <div className="ab-glow" />
        <div className="ab-logo"><NovaMark size={30} /> Nova<span className="brand-ai">AI</span></div>
        <h1>One workspace.<br />Unlimited AI intelligence.</h1>
        <p>Add your sources, ask anything, and turn them into reports, slides, quizzes, and mind maps — all in one place.</p>
        <ul className="ab-feats">
          <li><span className="fc"><Check size={14} /></span> Research grounded in your own sources</li>
          <li><span className="fc"><Check size={14} /></span> Reports, slides & quizzes in one click</li>
          <li><span className="fc"><Check size={14} /></span> Works with PDFs, images, and notes</li>
          <li><span className="fc"><Check size={14} /></span> Beautiful dark & light themes</li>
        </ul>
      </div>

      <div className="auth-panel">
        <div className="auth-card">
          <div className="auth-logo-sm"><NovaMark size={26} /> Nova<span className="brand-ai">AI</span></div>

          <div className="auth-form" key={mode}>
          {mode === 'forgot' ? (
            <>
              <h2>Reset password</h2>
              <p className="auth-sub">Enter your email and we'll send a reset link.</p>
              {resetSent ? (
                <div className="auth-success"><Check size={16} /> If an account exists for {email}, a reset link is on its way.</div>
              ) : (
                <>
                  {error && <div className="auth-error">{error}</div>}
                  <label className="auth-field"><Mail size={16} className="af-ic" /><input type="email" placeholder="Email address" value={email} onChange={e => setEmail(e.target.value)} onKeyDown={onEnter} /></label>
                  <button className="auth-submit" onClick={sendReset}>Send reset link <ArrowRight size={16} /></button>
                </>
              )}
              <p className="auth-switch"><button className="link-btn" onClick={() => switchMode('login')}>← Back to log in</button></p>
            </>
          ) : (
            <>
              <h2>{mode === 'login' ? 'Welcome back' : 'Create your account'}</h2>
              <p className="auth-sub">{mode === 'login' ? 'Log in to your NovaAI workspace.' : 'Start your NovaAI workspace in seconds.'}</p>

              <div className="social-row">
                <button className="social-btn" onClick={() => social('google')}><BrandGoogle /><span className="lbl">Google</span></button>
                <button className="social-btn" onClick={() => social('github')}><BrandGithub /><span className="lbl">GitHub</span></button>
                <button className="social-btn" onClick={() => social('microsoft')}><BrandMicrosoft /><span className="lbl">Microsoft</span></button>
              </div>
              <div className="divider"><span>or continue with email</span></div>

              {error && <div className="auth-error">{error}</div>}

              {mode === 'signup' && (
                <label className="auth-field"><User size={16} className="af-ic" /><input type="text" placeholder="Full name" value={name} onChange={e => setName(e.target.value)} onKeyDown={onEnter} /></label>
              )}
              <label className="auth-field"><Mail size={16} className="af-ic" /><input type="email" placeholder="Email address" value={email} onChange={e => setEmail(e.target.value)} onKeyDown={onEnter} /></label>
              <label className="auth-field">
                <Lock size={16} className="af-ic" />
                <input type={showPw ? 'text' : 'password'} placeholder="Password" value={password} onChange={e => setPassword(e.target.value)} onKeyDown={onEnter} />
                <button className="af-eye" onClick={() => setShowPw(s => !s)} tabIndex={-1}>{showPw ? <EyeOff size={16} /> : <Eye size={16} />}</button>
              </label>
              {mode === 'signup' && (
                <label className="auth-field"><Lock size={16} className="af-ic" /><input type={showPw ? 'text' : 'password'} placeholder="Confirm password" value={confirm} onChange={e => setConfirm(e.target.value)} onKeyDown={onEnter} /></label>
              )}

              {mode === 'login' ? (
                <div className="auth-row">
                  <label className="auth-check"><input type="checkbox" checked={remember} onChange={e => setRemember(e.target.checked)} /> Remember me</label>
                  <button className="link-btn" onClick={() => switchMode('forgot')}>Forgot password?</button>
                </div>
              ) : (
                <label className="auth-check terms"><input type="checkbox" checked={agree} onChange={e => setAgree(e.target.checked)} /> I agree to the Terms & Privacy Policy</label>
              )}

              <button className="auth-submit" onClick={mode === 'login' ? submitLogin : submitSignup} disabled={loading}>
                {loading ? <Loader2 size={17} className="spin" /> : <>{mode === 'login' ? 'Log in' : 'Create account'} <ArrowRight size={16} /></>}
              </button>

              <p className="auth-switch">
                {mode === 'login' ? "Don't have an account?" : 'Already have an account?'}
                <button className="link-btn" onClick={() => switchMode(mode === 'login' ? 'signup' : 'login')}>{mode === 'login' ? 'Sign up' : 'Log in'}</button>
              </p>
              {mode === 'login' && <button className="demo-hint" onClick={fillDemo}>Use demo account (demo@novaai.app)</button>}
            </>
          )}
          </div>
        </div>
      </div>
    </div>
  );
}

const NAV = [
  { id: 'home', label: 'Home', icon: Home },
  { id: 'workspace', label: 'AI Workspace', icon: MessageSquare },
  { id: 'documents', label: 'Documents', icon: FolderOpen },
  { id: 'history', label: 'History', icon: Clock },
  { id: 'analytics', label: 'Analytics', icon: BarChart3 },
  { id: 'settings', label: 'Settings', icon: Settings },
];

export default function App() {
  const [theme, setTheme] = useState('dark');
  const [view, setView] = useState('workspace');
  const [chats, setChats] = useState([{ id: uid(), title: 'New chat', messages: [], sources: [], createdAt: Date.now() }]);
  const [activeId, setActiveId] = useState(() => null);
  const [input, setInput] = useState('');
  const [attachments, setAttachments] = useState([]);
  const [loading, setLoading] = useState(false);
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [notifOpen, setNotifOpen] = useState(false);
  const [query, setQuery] = useState('');
  const [copiedId, setCopiedId] = useState(null);
  const [profile, setProfile] = useState({ name: 'Alex Rahman', email: 'alex@novaai.app', org: 'NovaAI Workspace' });
  const [sourceMenu, setSourceMenu] = useState(false);
  const [pasteOpen, setPasteOpen] = useState(false);
  const [pasteText, setPasteText] = useState('');
  const [studioOpen, setStudioOpen] = useState(false);
  const [studioPinned, setStudioPinned] = useState(false);
  const [studioSearch, setStudioSearch] = useState('');
  const [confirmLogout, setConfirmLogout] = useState(false);
  const [isAuthed, setIsAuthed] = useState(false);
  const [accounts, setAccounts] = useState([]);
  const [activeTool, setActiveTool] = useState(null);
  const [tool, setTool] = useState({ status: 'idle', progress: 0, data: null, error: null });

  const scrollRef = useRef(null);
  const taRef = useRef(null);
  const fileRef = useRef(null);
  const sourceFileRef = useRef(null);
  const progTimer = useRef(null);
  useEffect(() => () => clearInterval(progTimer.current), []);

  // Load saved accounts (persist across reloads); seed a demo account if none exist.
  useEffect(() => {
    let alive = true;
    (async () => {
      try {
        try {
          const r = await window.storage.get('nova_accounts_v3');
          if (alive && r && r.value) { setAccounts(JSON.parse(r.value)); return; }
        } catch (e) { /* no storage or first run */ }
        const seed = [{ name: 'Alex Rahman', email: 'demo@novaai.app', passwordHash: await hashPw('nova1234') }];
        if (alive) setAccounts(seed);
        try { await window.storage.set('nova_accounts_v3', JSON.stringify(seed)); } catch (e) {}
      } catch (e) {
        if (alive) setAccounts([{ name: 'Alex Rahman', email: 'demo@novaai.app', passwordHash: weakHash('nova1234') }]);
      }
    })();
    return () => { alive = false; };
  }, []);

  const registerAccount = (acct) => {
    setAccounts(prev => {
      const next = [...prev, acct];
      try { window.storage && window.storage.set('nova_accounts_v3', JSON.stringify(next)); } catch (e) {}
      return next;
    });
  };

  useEffect(() => { if (activeId === null && chats[0]) setActiveId(chats[0].id); }, [activeId, chats]);

  const activeChat = chats.find(c => c.id === activeId) || chats[0];

  useEffect(() => {
    if (scrollRef.current) scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
  }, [activeChat?.messages?.length, loading, view]);

  /* ---------- API ---------- */
  async function callNova(messages) {
    const res = await fetch('https://api.anthropic.com/v1/messages', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ model: 'claude-sonnet-4-6', max_tokens: 1000, system: SYSTEM, messages }),
    });
    if (!res.ok) throw new Error('HTTP ' + res.status);
    const data = await res.json();
    return (data.content || []).filter(b => b.type === 'text').map(b => b.text).join('\n').trim();
  }

  function buildApiMessages(msgs, sources = []) {
    const out = msgs.filter(m => !m.isError).map(m => {
      if (m.role === 'assistant') return { role: 'assistant', content: m.text || '...' };
      const blocks = [];
      let text = m.text || '';
      (m.attachments || []).forEach(a => {
        if (a.kind === 'image') blocks.push({ type: 'image', source: { type: 'base64', media_type: a.mediaType, data: a.data } });
        else if (a.kind === 'pdf') blocks.push({ type: 'document', source: { type: 'base64', media_type: 'application/pdf', data: a.data } });
        else if (a.kind === 'text') text += `\n\n[Attached file: ${a.name}]\n${a.textContent}`;
        else text += `\n\n[Attached file: ${a.name} — content not readable in this prototype]`;
      });
      if (blocks.length) {
        blocks.push({ type: 'text', text: text || 'Please analyze the attached file(s).' });
        return { role: 'user', content: blocks };
      }
      return { role: 'user', content: text };
    });

    // NotebookLM-style: prepend all research sources to the first user turn so
    // every answer is grounded in them for the whole conversation.
    if (sources.length && out.length) {
      const srcBlocks = [];
      let srcNote = 'RESEARCH SOURCES — base your answers on these and cite the source name when you use it:\n';
      sources.forEach(s => {
        if (s.kind === 'image') srcBlocks.push({ type: 'image', source: { type: 'base64', media_type: s.mediaType, data: s.data } });
        else if (s.kind === 'pdf') srcBlocks.push({ type: 'document', source: { type: 'base64', media_type: 'application/pdf', data: s.data } });
        else if (s.kind === 'text') srcNote += `\n--- Source: ${s.name} ---\n${s.textContent}\n`;
        else srcNote += `\n--- Source: ${s.name} (content not readable) ---\n`;
      });
      const idx = out.findIndex(m => m.role === 'user');
      if (idx !== -1) {
        const orig = out[idx].content;
        const origText = typeof orig === 'string' ? orig : '';
        const origBlocks = Array.isArray(orig) ? orig : [];
        out[idx] = {
          role: 'user',
          content: [...srcBlocks, { type: 'text', text: srcNote }, ...origBlocks, ...(origText ? [{ type: 'text', text: origText }] : [])],
        };
      }
    }
    return out;
  }

  /* ---------- files ---------- */
  const toBase64 = (f) => new Promise((res, rej) => {
    const r = new FileReader();
    r.onload = () => res(String(r.result).split(',')[1]);
    r.onerror = rej;
    r.readAsDataURL(f);
  });

  async function handleFiles(list) {
    for (const f of Array.from(list)) {
      const isImg = f.type.startsWith('image/');
      const isPdf = f.type === 'application/pdf';
      const isTxt = f.type.startsWith('text/') || /\.(txt|md|csv|json)$/i.test(f.name);
      try {
        if (isTxt) {
          const textContent = (await f.text()).slice(0, 20000);
          setAttachments(a => [...a, { id: uid(), name: f.name, kind: 'text', textContent }]);
        } else if (isImg) {
          setAttachments(a => [...a, { id: uid(), name: f.name, kind: 'image', mediaType: f.type, data: '' , _p: true}]);
          const data = await toBase64(f);
          setAttachments(a => a.map(x => x._p && x.name === f.name ? { ...x, data, _p: false } : x));
        } else if (isPdf) {
          const data = await toBase64(f);
          setAttachments(a => [...a, { id: uid(), name: f.name, kind: 'pdf', mediaType: 'application/pdf', data }]);
        } else {
          setAttachments(a => [...a, { id: uid(), name: f.name, kind: 'other' }]);
        }
      } catch { /* skip unreadable */ }
    }
  }

  /* ---------- chat actions ---------- */
  const send = async (override) => {
    const text = (override ?? input).trim();
    if ((!text && attachments.length === 0) || loading) return;
    const userMsg = { id: uid(), role: 'user', text, attachments };
    const updatedMsgs = [...(activeChat?.messages || []), userMsg];
    const isFirst = (activeChat?.messages?.length || 0) === 0;
    setChats(prev => prev.map(c =>
      c.id === activeChat.id
        ? { ...c, messages: updatedMsgs, title: isFirst && text ? text.slice(0, 42) : c.title }
        : c
    ));
    setInput(''); setAttachments([]); setLoading(true);
    if (taRef.current) taRef.current.style.height = 'auto';
    try {
      const reply = await callNova(buildApiMessages(updatedMsgs, activeChat?.sources || []));
      const aMsg = { id: uid(), role: 'assistant', text: reply || 'No response was returned.' };
      setChats(prev => prev.map(c => c.id === activeChat.id ? { ...c, messages: [...c.messages, aMsg] } : c));
    } catch {
      const aMsg = { id: uid(), role: 'assistant', isError: true, text: 'Something went wrong while processing this task. Check your connection and try again.' };
      setChats(prev => prev.map(c => c.id === activeChat.id ? { ...c, messages: [...c.messages, aMsg] } : c));
    } finally { setLoading(false); }
  };

  const newChat = () => {
    const c = { id: uid(), title: 'New chat', messages: [], sources: [], createdAt: Date.now() };
    setChats(prev => [c, ...prev]);
    setActiveId(c.id); setView('workspace'); setSidebarOpen(false);
    setInput(''); setAttachments([]); setSourceMenu(false); setActiveTool(null);
  };

  const openChat = (id) => { setActiveId(id); setView('workspace'); setSidebarOpen(false); setActiveTool(null); };

  const deleteChat = (id, e) => {
    e?.stopPropagation();
    setChats(prev => {
      const next = prev.filter(c => c.id !== id);
      if (next.length === 0) { const c = { id: uid(), title: 'New chat', messages: [], sources: [], createdAt: Date.now() }; setActiveId(c.id); return [c]; }
      if (id === activeId) setActiveId(next[0].id);
      return next;
    });
  };

  /* ---------- sources (NotebookLM-style research) ---------- */
  const addSourceToChat = (src) =>
    setChats(prev => prev.map(c => c.id === activeChat.id ? { ...c, sources: [...(c.sources || []), src] } : c));

  const removeSource = (sid) =>
    setChats(prev => prev.map(c => c.id === activeChat.id ? { ...c, sources: (c.sources || []).filter(s => s.id !== sid) } : c));

  async function addSourceFiles(list) {
    for (const f of Array.from(list)) {
      const isImg = f.type.startsWith('image/');
      const isPdf = f.type === 'application/pdf';
      const isTxt = f.type.startsWith('text/') || /\.(txt|md|csv|json)$/i.test(f.name);
      try {
        if (isTxt) addSourceToChat({ id: uid(), name: f.name, kind: 'text', textContent: (await f.text()).slice(0, 30000) });
        else if (isImg) addSourceToChat({ id: uid(), name: f.name, kind: 'image', mediaType: f.type, data: await toBase64(f) });
        else if (isPdf) addSourceToChat({ id: uid(), name: f.name, kind: 'pdf', mediaType: 'application/pdf', data: await toBase64(f) });
        else addSourceToChat({ id: uid(), name: f.name, kind: 'other' });
      } catch { /* skip */ }
    }
  }

  const addPasteSource = () => {
    if (!pasteText.trim()) return;
    addSourceToChat({ id: uid(), name: `Pasted text (${pasteText.trim().slice(0, 22)}…)`, kind: 'text', textContent: pasteText.trim().slice(0, 30000) });
    setPasteText(''); setPasteOpen(false);
  };

  const handleAuth = (user) => {
    setProfile(p => ({ ...p, name: user.name, email: user.email }));
    const c = { id: uid(), title: 'New chat', messages: [], sources: [], createdAt: Date.now() };
    setChats([c]); setActiveId(c.id); setView('home'); setActiveTool(null);
    setStudioOpen(false); setSidebarOpen(false); setIsAuthed(true);
  };

  const doLogout = () => {
    const c = { id: uid(), title: 'New chat', messages: [], sources: [], createdAt: Date.now() };
    setChats([c]); setActiveId(c.id); setView('home');
    setSidebarOpen(false); setActiveTool(null); setStudioOpen(false); setConfirmLogout(false);
    setIsAuthed(false);
  };

  /* ---------- Work Studio ---------- */
  const hasMaterial = () => ((activeChat?.sources?.length || 0) + (activeChat?.messages?.filter(m => !m.isError).length || 0)) > 0;

  const buildToolMaterial = () => {
    const sources = activeChat?.sources || [];
    const blocks = []; let ctx = '';
    sources.forEach(s => {
      if (s.kind === 'image' && s.data) blocks.push({ type: 'image', source: { type: 'base64', media_type: s.mediaType, data: s.data } });
      else if (s.kind === 'pdf' && s.data) blocks.push({ type: 'document', source: { type: 'base64', media_type: 'application/pdf', data: s.data } });
      else if (s.kind === 'text') ctx += `\n--- Source: ${s.name} ---\n${s.textContent}\n`;
    });
    const convo = (activeChat?.messages || []).filter(m => !m.isError).map(m => `${m.role === 'user' ? 'User' : 'NovaAI'}: ${m.text}`).join('\n');
    if (convo) ctx += `\n--- Conversation ---\n${convo}\n`;
    return { blocks, ctx: ctx.slice(0, 8000) };
  };

  const generateTool = async (kind) => {
    setTool({ status: 'loading', progress: 6, data: null, error: null });
    clearInterval(progTimer.current);
    progTimer.current = setInterval(() => {
      setTool(t => (t.status === 'loading' ? { ...t, progress: Math.min(92, t.progress + Math.random() * 8 + 2) } : t));
    }, 300);
    try {
      const { blocks, ctx } = buildToolMaterial();
      const content = [...blocks, { type: 'text', text: `${ctx}\n\n${TOOL_PROMPTS[kind]}` }];
      const res = await fetch('https://api.anthropic.com/v1/messages', {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ model: 'claude-sonnet-4-6', max_tokens: 1000, system: STUDIO_SYSTEM, messages: [{ role: 'user', content }] }),
      });
      if (!res.ok) throw new Error('HTTP ' + res.status);
      const j = await res.json();
      const raw = (j.content || []).filter(b => b.type === 'text').map(b => b.text).join('\n').trim();
      const data = kind === 'report' ? { markdown: raw } : cleanJSON(raw);
      clearInterval(progTimer.current);
      setTool({ status: 'done', progress: 100, data, error: null });
    } catch (e) {
      clearInterval(progTimer.current);
      setTool({ status: 'error', progress: 0, data: null, error: 'NovaAI could not generate this from the current material. Please try again.' });
    }
  };

  const openTool = (kind) => {
    setActiveTool(kind); setView('workspace'); setStudioOpen(false); setSidebarOpen(false);
    if (!hasMaterial()) { setTool({ status: 'nomaterial', progress: 0, data: null, error: null }); return; }
    generateTool(kind);
  };
  const closeTool = () => { clearInterval(progTimer.current); setActiveTool(null); setTool({ status: 'idle', progress: 0, data: null, error: null }); };

  const copyMsg = (id, text) => {
    navigator.clipboard?.writeText(text);
    setCopiedId(id);
    setTimeout(() => setCopiedId(c => (c === id ? null : c)), 1400);
  };

  const onKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); send(); }
  };
  const grow = (e) => {
    setInput(e.target.value);
    e.target.style.height = 'auto';
    e.target.style.height = Math.min(e.target.scrollHeight, 200) + 'px';
  };

  const filteredChats = chats.filter(c => c.title.toLowerCase().includes(query.toLowerCase()));
  const allDocs = chats.flatMap(c => [
    ...(c.sources || []).map(s => ({ ...s, chatTitle: c.title, chatId: c.id, origin: 'Source' })),
    ...c.messages.flatMap(m => (m.attachments || []).map(a => ({ ...a, chatTitle: c.title, chatId: c.id, origin: 'Attachment' }))),
  ]);
  const totalMessages = chats.reduce((n, c) => n + c.messages.length, 0);

  const fileIcon = (kind) => kind === 'image' ? ImageIcon : kind === 'pdf' ? FileText : kind === 'text' ? FileText : File;

  /* ---------- views ---------- */
  const renderWorkspace = () => {
    const empty = !activeChat || activeChat.messages.length === 0;
    const sources = activeChat?.sources || [];
    return (
      <div className="ws">
        <div className="sources-bar">
          <div className="sb-label"><Library size={15} /> <span className="sb-label-txt">Sources</span>{sources.length > 0 && <span className="sb-count">{sources.length}</span>}</div>
          <div className="sb-list">
            {sources.length === 0
              ? <span className="sb-hint">Add PDFs, images, text or notes — NovaAI will research from them</span>
              : sources.map(s => {
                  const Ic = fileIcon(s.kind);
                  return (
                    <span key={s.id} className="src-chip">
                      <Ic size={13} /><span className="src-name">{s.name}</span>
                      <button onClick={() => removeSource(s.id)} title="Remove source"><X size={12} /></button>
                    </span>
                  );
                })}
          </div>
          <div className="sb-add-wrap">
            <button className="sb-add studio" onClick={() => setStudioOpen(true)}><Wand2 size={16} /> Work Studio</button>
          </div>
        </div>
        <div className="ws-scroll" ref={scrollRef}>
          {empty ? (
            <div className="hero">
              <div className="nova-glow" />
              <div className="hero-mark"><NovaMark size={46} /></div>
              <h1 className="hero-title">Hello, {profile.name.split(' ')[0]}.</h1>
              <p className="hero-sub">Add your sources above, then ask anything — NovaAI researches and answers from them. Or just start typing.</p>
              <div className="suggest-grid">
                {SUGGESTIONS.map((s, i) => (
                  <button key={i} className="suggest" onClick={() => send(s.text)}>
                    <span className="suggest-ic"><s.icon size={17} /></span>
                    <span className="suggest-t">{s.title}</span>
                    <span className="suggest-d">{s.text}</span>
                  </button>
                ))}
              </div>
            </div>
          ) : (
            <div className="thread">
              {activeChat.messages.map(m => (
                <div key={m.id} className={`msg ${m.role}`}>
                  <div className="avatar">{m.role === 'user' ? profile.name.slice(0, 1) : <NovaMark size={20} />}</div>
                  <div className="bubble-wrap">
                    <div className="who">{m.role === 'user' ? 'You' : 'NovaAI'}</div>
                    {m.attachments?.length > 0 && (
                      <div className="attach-row">
                        {m.attachments.map(a => {
                          const Ic = fileIcon(a.kind);
                          return <span key={a.id} className="chip mini"><Ic size={13} />{a.name}</span>;
                        })}
                      </div>
                    )}
                    {m.role === 'assistant'
                      ? <div className={`bubble md ${m.isError ? 'err' : ''}`} dangerouslySetInnerHTML={{ __html: renderMarkdown(m.text) }} />
                      : <div className="bubble user-b">{m.text}</div>}
                    {m.role === 'assistant' && !m.isError && (
                      <button className="copy" onClick={() => copyMsg(m.id, m.text)}>
                        {copiedId === m.id ? <><Check size={13} /> Copied</> : <><Copy size={13} /> Copy</>}
                      </button>
                    )}
                  </div>
                </div>
              ))}
              {loading && (
                <div className="msg assistant">
                  <div className="avatar"><NovaMark size={20} /></div>
                  <div className="bubble-wrap">
                    <div className="who">NovaAI</div>
                    <div className="bubble"><span className="dots"><i /><i /><i /></span></div>
                  </div>
                </div>
              )}
            </div>
          )}
        </div>

        {/* composer */}
        <div className="composer-wrap">
          <div className="composer">
            {attachments.length > 0 && (
              <div className="attach-row top">
                {attachments.map(a => {
                  const Ic = fileIcon(a.kind);
                  return (
                    <span key={a.id} className="chip">
                      <Ic size={14} />{a.name}
                      <button onClick={() => setAttachments(x => x.filter(y => y.id !== a.id))}><X size={12} /></button>
                    </span>
                  );
                })}
              </div>
            )}
            <div className="composer-row">
              <button className="icon-btn" title="Attach file" onClick={() => fileRef.current?.click()}><Paperclip size={19} /></button>
              <input ref={fileRef} type="file" multiple hidden
                onChange={(e) => { handleFiles(e.target.files); e.target.value = ''; }} />
              <textarea
                ref={taRef}
                className="composer-input"
                rows={1}
                placeholder="Ask NovaAI anything, or attach a document to analyze…"
                value={input}
                onChange={grow}
                onKeyDown={onKeyDown}
              />
              <button className="icon-btn" title="Voice input (demo)"><Mic size={19} /></button>
              <button className="send" disabled={loading || (!input.trim() && attachments.length === 0)} onClick={() => send()}>
                <Send size={17} />
              </button>
            </div>
          </div>
          <p className="disclaimer">NovaAI can make mistakes. Verify important information.</p>
        </div>
      </div>
    );
  };

  const renderHome = () => (
    <div className="page home-page">
      <div className="page-hero home-hero">
        <div className="nova-glow small" />
        <div className="hero-badge"><NovaMark size={64} /></div>
        <h1>Welcome back, {profile.name.split(' ')[0]}.</h1>
        <p>One workspace. Unlimited AI intelligence. Add your sources, ask anything, and let NovaAI do the heavy lifting.</p>
        <button className="btn-primary lg" onClick={newChat}><Plus size={17} /> Get started</button>
      </div>
    </div>
  );

  const renderDocuments = () => (
    <div className="page">
      <h1 className="page-h1">Documents</h1>
      <p className="page-p">Every source and file you've given NovaAI is saved here.</p>
      {allDocs.length === 0 ? (
        <div className="empty"><FolderOpen size={30} /><p>No documents yet</p><span>Add a source or attach a file in the AI Workspace and it will appear here.</span></div>
      ) : (
        <div className="doc-grid">
          {allDocs.map((d, i) => {
            const Ic = fileIcon(d.kind);
            return (
              <div key={i} className="doc-card">
                <div className="doc-top">
                  <div className="doc-ic"><Ic size={20} /></div>
                  <span className={`doc-tag ${d.origin === 'Source' ? 'src' : ''}`}>{d.origin}</span>
                </div>
                <div className="doc-name">{d.name}</div>
                <div className="doc-meta">{(d.kind || 'file').toUpperCase()} · in “{d.chatTitle}”</div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );

  const renderHistory = () => (
    <div className="page">
      <h1 className="page-h1">History</h1>
      <p className="page-p">Every task is saved and searchable.</p>
      <div className="list">
        {[...chats].sort((a, b) => b.createdAt - a.createdAt).map(c => (
          <div key={c.id} className="list-row static">
            <Clock size={16} className="lr-ic" />
            <button className="lr-title link" onClick={() => openChat(c.id)}>{c.title}</button>
            <span className="lr-meta">{c.messages.length} msgs · {timeAgo(c.createdAt)}</span>
            <button className="lr-del" onClick={() => deleteChat(c.id)}><Trash2 size={15} /></button>
          </div>
        ))}
      </div>
    </div>
  );

  const renderAnalytics = () => {
    const cards = [
      { n: chats.length, l: 'Total conversations', c: 'var(--primary)' },
      { n: totalMessages, l: 'Messages exchanged', c: 'var(--accent)' },
      { n: allDocs.length, l: 'Documents analyzed', c: 'var(--success)' },
      { n: chats.filter(c => c.messages.length > 0).length, l: 'Active tasks', c: 'var(--warning)' },
    ];
    return (
      <div className="page">
        <h1 className="page-h1">Analytics</h1>
        <p className="page-p">A snapshot of your workspace activity.</p>
        <div className="stat-grid big">
          {cards.map((c, i) => (
            <div key={i} className="stat"><span className="stat-n" style={{ color: c.c }}>{c.n}</span><span className="stat-l">{c.l}</span></div>
          ))}
        </div>
        <div className="bars">
          {chats.slice(0, 6).map(c => {
            const w = Math.min(100, 10 + c.messages.length * 18);
            return (
              <div key={c.id} className="bar-row">
                <span className="bar-label">{c.title}</span>
                <div className="bar-track"><div className="bar-fill" style={{ width: w + '%' }} /></div>
                <span className="bar-val">{c.messages.length}</span>
              </div>
            );
          })}
        </div>
      </div>
    );
  };

  const renderSettings = () => (
    <div className="page">
      <h1 className="page-h1">Settings</h1>
      <p className="page-p">Personalize your NovaAI workspace.</p>
      <div className="card">
        <h4>Appearance</h4>
        <div className="theme-pick">
          <button className={`theme-opt ${theme === 'dark' ? 'on' : ''}`} onClick={() => setTheme('dark')}><Moon size={15} /> Dark</button>
          <button className={`theme-opt ${theme === 'light' ? 'on' : ''}`} onClick={() => setTheme('light')}><Sun size={15} /> Light</button>
        </div>
      </div>
      <div className="card">
        <h4>Profile</h4>
        <label className="fld">Name<input value={profile.name} onChange={e => setProfile(p => ({ ...p, name: e.target.value }))} /></label>
        <label className="fld">Email<input value={profile.email} onChange={e => setProfile(p => ({ ...p, email: e.target.value }))} /></label>
        <label className="fld">Organization<input value={profile.org} onChange={e => setProfile(p => ({ ...p, org: e.target.value }))} /></label>
      </div>
      <div className="card">
        <h4>About</h4>
        <p className="muted-p">NovaAI Workspace — prototype. Connected to a live AI model for real document analysis, writing, research, and code generation.</p>
      </div>
    </div>
  );

  const views = {
    home: renderHome, workspace: renderWorkspace, documents: renderDocuments,
    history: renderHistory, analytics: renderAnalytics, settings: renderSettings,
  };

  const viewLabel = NAV.find(n => n.id === view)?.label || 'AI Workspace';

  return (
    <div className="app" data-theme={theme}>
      <style>{CSS}</style>

      {!isAuthed ? (
        <AuthScreen theme={theme} onToggleTheme={() => setTheme(t => (t === 'dark' ? 'light' : 'dark'))} onAuthenticated={handleAuth} accounts={accounts} registerAccount={registerAccount} />
      ) : (
      <>
      {sidebarOpen && <div className="overlay" onClick={() => setSidebarOpen(false)} />}

      {/* Sidebar */}
      <aside className={`sidebar ${sidebarOpen ? 'open' : ''}`}>
        <div className="brand">
          <NovaMark />
          <span className="brand-name">Nova<span className="brand-ai">AI</span></span>
        </div>

        <div className="add-src-wrap">
          <button className="new-chat" onClick={() => { setView('workspace'); setActiveTool(null); setSourceMenu(o => !o); }}>
            <Plus size={17} /> Add source
          </button>
          {sourceMenu && (
            <div className="src-menu side">
              <button onClick={() => { sourceFileRef.current?.click(); setSourceMenu(false); }}><Upload size={15} /> Upload file</button>
              <button onClick={() => { setPasteOpen(true); setSourceMenu(false); }}><Type size={15} /> Paste text</button>
            </div>
          )}
          <input ref={sourceFileRef} type="file" multiple hidden onChange={e => { addSourceFiles(e.target.files); e.target.value = ''; }} />
        </div>

        <div className="search">
          <Search size={15} />
          <input placeholder="Search tasks" value={query} onChange={e => setQuery(e.target.value)} />
        </div>

        <nav className="nav">
          {NAV.map(n => (
            <button key={n.id} className={`nav-item ${view === n.id && !activeTool ? 'on' : ''}`} onClick={() => { setView(n.id); setActiveTool(null); setSidebarOpen(false); }}>
              <n.icon size={17} /> {n.label}
            </button>
          ))}
        </nav>

        <div className="chats-head">Recent</div>
        <div className="chats">
          {filteredChats.map(c => (
            <div key={c.id} className={`chat-row ${c.id === activeId && view === 'workspace' ? 'on' : ''}`} onClick={() => openChat(c.id)}>
              <MessageSquare size={15} />
              <span className="chat-title">{c.title}</span>
              <button className="chat-del" onClick={(e) => deleteChat(c.id, e)}><Trash2 size={13} /></button>
            </div>
          ))}
        </div>

        <button className="profile" onClick={() => { setView('settings'); setSidebarOpen(false); }}>
          <span className="pf-av">{profile.name.slice(0, 1)}</span>
          <span className="pf-info"><span className="pf-name">{profile.name}</span><span className="pf-plan">Pro workspace</span></span>
        </button>
        <button className="logout" onClick={() => setConfirmLogout(true)}><LogOut size={16} /> Log out</button>
      </aside>

      {/* Main */}
      <div className="main">
        <header className="topbar">
          <button className="icon-btn menu" onClick={() => setSidebarOpen(true)}><Menu size={19} /></button>
          <span className="top-title">{viewLabel}</span>
          <div className="top-actions">
            <button className="icon-btn" onClick={() => setTheme(t => (t === 'dark' ? 'light' : 'dark'))} title="Toggle theme">
              {theme === 'dark' ? <Sun size={18} /> : <Moon size={18} />}
            </button>
          </div>
        </header>

        <section className="content">
          <div className="view-anim" key={activeTool ? 'tool-' + activeTool : 'view-' + view}>
            {activeTool
              ? <ToolView tool={TOOLS.find(t => t.kind === activeTool)} status={tool.status} progress={tool.progress}
                  data={tool.data} error={tool.error} onBack={closeTool} onRetry={() => generateTool(activeTool)} />
              : (views[view] || renderWorkspace)()}
          </div>
        </section>
      </div>

      {/* Work Studio */}
      {studioOpen && <div className="overlay studio-overlay" onClick={() => !studioPinned && setStudioOpen(false)} />}
      <aside className={`studio ${studioOpen ? 'open' : ''}`}>
        <div className="studio-inner">
          <div className="studio-head">
            <div className="sh-title"><Wand2 size={17} /> Work Studio</div>
            <div className="sh-actions">
              <button className={`icon-btn sm ${studioPinned ? 'pinned' : ''}`} title={studioPinned ? 'Unpin' : 'Pin open'} onClick={() => setStudioPinned(p => !p)}><Pin size={15} /></button>
              <button className="icon-btn sm" title="Close" onClick={() => setStudioOpen(false)}><X size={16} /></button>
            </div>
          </div>
          <div className="studio-search">
            <Search size={14} />
            <input placeholder="Search tools" value={studioSearch} onChange={e => setStudioSearch(e.target.value)} />
          </div>
          <div className="studio-body">
            <p className="studio-sub">Turn your sources and conversation into polished study & work assets.</p>
            <div className="tool-list" key={studioOpen ? 'open' : 'closed'}>
              {TOOLS.filter(t => t.title.toLowerCase().includes(studioSearch.toLowerCase())).map((t, i) => (
                <button key={t.kind} className={`tool-card ${activeTool === t.kind ? 'active' : ''}`} style={{ animationDelay: (i * 45) + 'ms' }} onClick={() => openTool(t.kind)}>
                  <span className="tc-ic"><t.icon size={18} /></span>
                  <span className="tc-txt">
                    <span className="tc-title">{t.title}{t.beta && <em className="beta">Beta</em>}</span>
                    <span className="tc-desc">{t.desc}</span>
                  </span>
                  {activeTool === t.kind && tool.status === 'loading'
                    ? <Loader2 size={16} className="spin tc-arrow" />
                    : <ChevronRight size={16} className="tc-arrow" />}
                </button>
              ))}
            </div>
          </div>
        </div>
      </aside>

      {pasteOpen && (
        <div className="modal-overlay fixed" onClick={() => setPasteOpen(false)}>
          <div className="modal" onClick={e => e.stopPropagation()}>
            <div className="modal-head"><span><Type size={16} /> Paste text as a source</span><button onClick={() => setPasteOpen(false)}><X size={16} /></button></div>
            <textarea className="modal-ta" placeholder="Paste an article, notes, transcript, or any text you want NovaAI to research from…" value={pasteText} onChange={e => setPasteText(e.target.value)} />
            <div className="modal-actions">
              <button className="btn-ghost" onClick={() => setPasteOpen(false)}>Cancel</button>
              <button className="btn-primary" onClick={addPasteSource} disabled={!pasteText.trim()}>Add source</button>
            </div>
          </div>
        </div>
      )}

      {confirmLogout && (
        <div className="modal-overlay fixed" onClick={() => setConfirmLogout(false)}>
          <div className="modal sm" onClick={e => e.stopPropagation()}>
            <div className="modal-head"><span><LogOut size={16} /> Log out of NovaAI?</span></div>
            <p className="modal-text">You'll be signed out and returned to the log-in screen. Your current session will be cleared.</p>
            <div className="modal-actions">
              <button className="btn-ghost" onClick={() => setConfirmLogout(false)}>Cancel</button>
              <button className="btn-danger" onClick={doLogout}><LogOut size={15} /> Log out</button>
            </div>
          </div>
        </div>
      )}
      </>
      )}
    </div>
  );
}

/* ============================================================ */
const CSS = `
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;600;700&family=Inter:wght@400;450;500;600&display=swap');

.app{--font:'Inter',system-ui,-apple-system,sans-serif;--display:'Space Grotesk','Inter',sans-serif;}
.app[data-theme="dark"]{
  --bg:#0F172A;--bg2:#0B1120;--surface:#1E293B;--surface2:#26364b;--surface3:#2c3e57;
  --border:rgba(148,163,184,.14);--border2:rgba(148,163,184,.22);
  --text:#F8FAFC;--muted:#94A3B8;--faint:#64748B;
  --primary:#3B82F6;--primary-h:#2563EB;--primary-soft:rgba(59,130,246,.16);
  --accent:#8B5CF6;--success:#22C55E;--warning:#F59E0B;--error:#EF4444;
  --glass:rgba(15,23,42,.72);--shadow:0 12px 40px rgba(0,0,0,.45);--code-bg:#0b1220;
}
.app[data-theme="light"]{
  --bg:#F8FAFC;--bg2:#EEF2F7;--surface:#FFFFFF;--surface2:#F1F5F9;--surface3:#E9EEF5;
  --border:rgba(15,23,42,.09);--border2:rgba(15,23,42,.14);
  --text:#0F172A;--muted:#475569;--faint:#94A3B8;
  --primary:#2563EB;--primary-h:#1D4ED8;--primary-soft:rgba(37,99,235,.10);
  --accent:#7C3AED;--success:#16A34A;--warning:#D97706;--error:#DC2626;
  --glass:rgba(255,255,255,.78);--shadow:0 12px 40px rgba(15,23,42,.10);--code-bg:#f1f5f9;
}
*{box-sizing:border-box}
.app{display:flex;height:100vh;width:100%;background:var(--bg);color:var(--text);
  font-family:var(--font);font-size:14.5px;line-height:1.5;overflow:hidden;
  -webkit-font-smoothing:antialiased;letter-spacing:.005em;}
.app button{font-family:inherit;cursor:pointer;color:inherit}
.app input,.app textarea{font-family:inherit}
.app ::-webkit-scrollbar{width:9px;height:9px}
.app ::-webkit-scrollbar-thumb{background:var(--border2);border-radius:8px}
.app ::-webkit-scrollbar-track{background:transparent}

.nova-mark .nova-orbit{transform-origin:16px 16px;animation:orbit 7s linear infinite}
@keyframes orbit{to{transform:rotate(360deg)}}

/* ---------- Sidebar ---------- */
.sidebar{width:266px;flex-shrink:0;background:var(--bg2);border-right:1px solid var(--border);
  display:flex;flex-direction:column;padding:16px 12px;gap:12px;z-index:40}
.brand{display:flex;align-items:center;gap:9px;padding:4px 6px 2px}
.brand-name{font-family:var(--display);font-weight:700;font-size:19px;letter-spacing:-.02em}
.brand-ai{background:linear-gradient(90deg,var(--primary),var(--accent));-webkit-background-clip:text;background-clip:text;color:transparent}
.new-chat{display:flex;align-items:center;justify-content:center;gap:8px;padding:11px;border-radius:12px;
  border:1px solid transparent;font-weight:600;font-size:14px;color:#fff;
  background:linear-gradient(135deg,var(--primary),var(--accent));box-shadow:0 6px 18px var(--primary-soft);
  transition:transform .12s ease,box-shadow .2s}
.new-chat:hover{transform:translateY(-1px);box-shadow:0 10px 26px var(--primary-soft)}
.search{display:flex;align-items:center;gap:8px;padding:9px 11px;border-radius:11px;background:var(--surface);
  border:1px solid var(--border);color:var(--muted)}
.search input{border:none;background:transparent;outline:none;color:var(--text);width:100%;font-size:13.5px}
.search input::placeholder{color:var(--faint)}
.nav{display:flex;flex-direction:column;gap:2px}
.nav-item{display:flex;align-items:center;gap:11px;padding:9px 11px;border-radius:10px;border:none;
  background:transparent;color:var(--muted);font-size:14px;font-weight:500;transition:background .12s,color .12s}
.nav-item:hover{background:var(--surface);color:var(--text)}
.nav-item.on{background:var(--primary-soft);color:var(--primary);font-weight:600}
.chats-head{font-size:11px;text-transform:uppercase;letter-spacing:.08em;color:var(--faint);padding:6px 8px 0;font-weight:600}
.chats{flex:1;overflow-y:auto;display:flex;flex-direction:column;gap:1px;margin:0 -2px;padding:0 2px}
.chat-row{display:flex;align-items:center;gap:9px;padding:8px 10px;border-radius:9px;color:var(--muted);
  font-size:13.5px;position:relative;transition:background .12s}
.chat-row:hover{background:var(--surface);color:var(--text)}
.chat-row.on{background:var(--surface);color:var(--text)}
.chat-title{flex:1;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.chat-del{opacity:0;border:none;background:transparent;color:var(--faint);padding:2px;display:flex;transition:opacity .12s}
.chat-row:hover .chat-del{opacity:1}
.chat-del:hover{color:var(--error)}
.profile{display:flex;align-items:center;gap:10px;padding:9px;border-radius:12px;border:1px solid var(--border);
  background:var(--surface);text-align:left;transition:background .12s}
.profile:hover{background:var(--surface2)}
.pf-av{width:34px;height:34px;border-radius:9px;display:grid;place-items:center;font-weight:700;color:#fff;
  background:linear-gradient(135deg,var(--primary),var(--accent))}
.pf-info{display:flex;flex-direction:column;line-height:1.25}
.pf-name{font-weight:600;font-size:13.5px}
.pf-plan{font-size:11.5px;color:var(--faint)}

/* ---------- Main ---------- */
.main{flex:1;display:flex;flex-direction:column;min-width:0}
.topbar{height:60px;flex-shrink:0;display:flex;align-items:center;gap:12px;padding:0 20px;
  border-bottom:1px solid var(--border);background:var(--glass);backdrop-filter:blur(12px);position:relative;z-index:30}
.top-title{font-family:var(--display);font-weight:600;font-size:16px}
.top-actions{margin-left:auto;display:flex;align-items:center;gap:6px}
.icon-btn{width:38px;height:38px;border-radius:10px;border:none;background:transparent;color:var(--muted);
  display:grid;place-items:center;transition:background .12s,color .12s}
.icon-btn:hover{background:var(--surface);color:var(--text)}
.icon-btn.menu{display:none}
.notif-wrap{position:relative}
.notif-wrap .dot{position:absolute;top:9px;right:10px;width:7px;height:7px;border-radius:50%;background:var(--error);border:2px solid var(--bg)}
.notif-panel{position:absolute;right:0;top:46px;width:288px;background:var(--surface);border:1px solid var(--border);
  border-radius:14px;box-shadow:var(--shadow);padding:8px;z-index:50;animation:pop .16s ease}
@keyframes pop{from{opacity:0;transform:translateY(-6px)}to{opacity:1;transform:none}}
.notif-head{font-weight:600;padding:7px 9px;font-size:13px}
.notif-item{display:flex;gap:10px;padding:9px;border-radius:10px}
.notif-item:hover{background:var(--surface2)}
.notif-item b{display:block;font-size:13px}
.notif-item span{font-size:12px;color:var(--muted)}
.ni-ic{width:26px;height:26px;flex-shrink:0;border-radius:8px;display:grid;place-items:center;background:var(--primary-soft);color:var(--primary)}
.ni-ic.ok{background:rgba(34,197,94,.16);color:var(--success)}
.top-av{width:34px;height:34px;border-radius:10px;display:grid;place-items:center;font-weight:700;color:#fff;
  background:linear-gradient(135deg,var(--primary),var(--accent));margin-left:4px}
.content{flex:1;overflow:hidden;display:flex;min-height:0}

/* ---------- Workspace ---------- */
.ws{flex:1;display:flex;flex-direction:column;min-width:0}
.ws-scroll{flex:1;overflow-y:auto;scroll-behavior:smooth}
.thread{max-width:800px;margin:0 auto;padding:26px 22px 8px;display:flex;flex-direction:column;gap:22px}
.msg{display:flex;gap:14px;animation:rise .3s ease}
@keyframes rise{from{opacity:0;transform:translateY(8px)}to{opacity:1;transform:none}}
.avatar{width:32px;height:32px;flex-shrink:0;border-radius:9px;display:grid;place-items:center;font-weight:700;font-size:13px}
.msg.user .avatar{background:var(--surface3);color:var(--text)}
.msg.assistant .avatar{background:var(--surface);border:1px solid var(--border)}
.bubble-wrap{min-width:0;flex:1}
.who{font-size:12px;font-weight:600;color:var(--faint);margin-bottom:5px;font-family:var(--display)}
.bubble{background:var(--surface);border:1px solid var(--border);border-radius:14px;border-top-left-radius:5px;
  padding:12px 15px;font-size:14.5px;word-wrap:break-word;overflow-wrap:break-word}
.bubble.user-b{background:var(--primary-soft);border-color:transparent;white-space:pre-wrap}
.bubble.err{border-color:var(--error);color:var(--error)}
.bubble.md p{margin:0 0 9px}.bubble.md p:last-child{margin-bottom:0}
.bubble.md h3,.bubble.md h4,.bubble.md h5{font-family:var(--display);margin:12px 0 7px;line-height:1.3}
.bubble.md h3{font-size:16px}.bubble.md h4{font-size:14.5px}
.bubble.md ul,.bubble.md ol{margin:6px 0 10px;padding-left:20px}
.bubble.md li{margin:3px 0}
.bubble.md code{background:var(--code-bg);border-radius:5px;padding:1px 6px;font-size:13px;font-family:ui-monospace,'SF Mono',Menlo,monospace}
.bubble.md pre{background:var(--code-bg);border:1px solid var(--border);border-radius:10px;padding:13px 15px;overflow-x:auto;margin:9px 0}
.bubble.md pre code{background:none;padding:0;font-size:12.8px;line-height:1.6}
.bubble.md strong{font-weight:650}
.copy{margin-top:7px;display:inline-flex;align-items:center;gap:5px;font-size:12px;color:var(--faint);
  background:transparent;border:1px solid var(--border);border-radius:8px;padding:4px 9px;transition:color .12s,border-color .12s}
.copy:hover{color:var(--text);border-color:var(--border2)}
.dots{display:inline-flex;gap:5px;padding:3px 0}
.dots i{width:7px;height:7px;border-radius:50%;background:var(--muted);animation:blink 1.3s infinite}
.dots i:nth-child(2){animation-delay:.2s}.dots i:nth-child(3){animation-delay:.4s}
@keyframes blink{0%,80%,100%{opacity:.25;transform:translateY(0)}40%{opacity:1;transform:translateY(-3px)}}

.attach-row{display:flex;flex-wrap:wrap;gap:7px;margin-bottom:8px}
.attach-row.top{margin:0 0 10px}
.chip{display:inline-flex;align-items:center;gap:6px;padding:6px 10px;border-radius:9px;background:var(--surface2);
  border:1px solid var(--border);font-size:12.5px;color:var(--text);max-width:220px}
.chip.mini{padding:4px 9px;font-size:12px}
.chip span{white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.chip button{border:none;background:transparent;color:var(--faint);display:flex;padding:0}
.chip button:hover{color:var(--error)}

/* Hero */
.hero{max-width:720px;margin:0 auto;padding:64px 22px 20px;text-align:center;position:relative}
.nova-glow{position:absolute;top:-40px;left:50%;transform:translateX(-50%);width:460px;height:460px;
  background:radial-gradient(circle,rgba(59,130,246,.30),rgba(139,92,246,.14) 40%,transparent 68%);
  filter:blur(8px);pointer-events:none;animation:pulse 6s ease-in-out infinite;z-index:0}
.nova-glow.small{width:320px;height:320px;top:-70px}
@keyframes pulse{0%,100%{opacity:.7;transform:translateX(-50%) scale(1)}50%{opacity:1;transform:translateX(-50%) scale(1.08)}}
.hero-mark,.hero-title,.hero-sub,.suggest-grid{position:relative;z-index:1}
.hero-mark{display:inline-flex;margin-bottom:16px}
.hero-title{font-family:var(--display);font-size:34px;font-weight:700;letter-spacing:-.03em;margin:0 0 10px;
  background:linear-gradient(180deg,var(--text),var(--muted));-webkit-background-clip:text;background-clip:text;color:transparent}
.hero-sub{color:var(--muted);font-size:15.5px;max-width:460px;margin:0 auto 30px}
.suggest-grid{display:grid;grid-template-columns:1fr 1fr;gap:12px;max-width:600px;margin:0 auto;text-align:left}
.suggest{background:var(--surface);border:1px solid var(--border);border-radius:14px;padding:15px;display:flex;
  flex-direction:column;gap:6px;transition:transform .14s,border-color .14s,background .14s}
.suggest:hover{transform:translateY(-2px);border-color:var(--border2);background:var(--surface2)}
.suggest-ic{width:32px;height:32px;border-radius:9px;display:grid;place-items:center;color:var(--primary);background:var(--primary-soft)}
.suggest-t{font-weight:600;font-size:13.5px;font-family:var(--display)}
.suggest-d{font-size:12.5px;color:var(--muted);line-height:1.45}

/* Composer */
.composer-wrap{padding:6px 22px 14px;max-width:800px;width:100%;margin:0 auto;flex-shrink:0}
.composer{background:var(--surface);border:1px solid var(--border2);border-radius:18px;padding:8px;
  box-shadow:var(--shadow);transition:border-color .18s,box-shadow .18s}
.composer:focus-within{border-color:var(--primary);box-shadow:0 0 0 4px var(--primary-soft)}
.composer-row{display:flex;align-items:flex-end;gap:4px}
.composer-input{flex:1;border:none;background:transparent;outline:none;resize:none;color:var(--text);
  font-size:15px;line-height:1.5;padding:8px 4px;max-height:200px}
.composer-input::placeholder{color:var(--faint)}
.send{width:38px;height:38px;flex-shrink:0;border:none;border-radius:11px;color:#fff;display:grid;place-items:center;
  background:linear-gradient(135deg,var(--primary),var(--accent));transition:opacity .15s,transform .12s}
.send:hover:not(:disabled){transform:scale(1.05)}
.send:disabled{opacity:.4;cursor:not-allowed}
.disclaimer{text-align:center;font-size:11.5px;color:var(--faint);margin:8px 0 0}

/* ---------- Generic pages ---------- */
.content>.ws{overflow:hidden}
.page{flex:1;overflow-y:auto;padding:28px 26px 40px;max-width:900px;margin:0 auto;width:100%}
.page-h1{font-family:var(--display);font-size:26px;font-weight:700;letter-spacing:-.02em;margin:0 0 4px}
.page-p{color:var(--muted);margin:0 0 22px}
.page-hero{text-align:center;padding:34px 0 26px;position:relative}
.hero-badge{position:relative;z-index:1;width:84px;height:84px;margin:0 auto;border-radius:22px;
  display:grid;place-items:center;background:var(--surface);border:1px solid var(--border);
  box-shadow:var(--shadow)}
.page-hero h1{font-family:var(--display);font-size:28px;font-weight:700;letter-spacing:-.02em;margin:14px 0 8px;position:relative;z-index:1}
.page-hero p{color:var(--muted);margin:0 auto 20px;max-width:420px;position:relative;z-index:1}
.btn-primary{display:inline-flex;align-items:center;gap:8px;border:none;border-radius:12px;font-weight:600;color:#fff;
  padding:10px 18px;background:linear-gradient(135deg,var(--primary),var(--accent));box-shadow:0 8px 22px var(--primary-soft);
  position:relative;z-index:1;transition:transform .12s}
.btn-primary:hover{transform:translateY(-1px)}
.btn-primary.lg{padding:12px 22px;font-size:15px}
.stat-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:14px;margin-bottom:28px}
.stat-grid.big{margin-bottom:32px}
.stat{background:var(--surface);border:1px solid var(--border);border-radius:16px;padding:20px 18px;text-align:left}
.stat-n{display:block;font-family:var(--display);font-size:30px;font-weight:700;letter-spacing:-.02em}
.stat-l{font-size:12.5px;color:var(--muted)}
.sec-title{font-family:var(--display);font-size:15px;margin:0 0 12px}
.list{display:flex;flex-direction:column;gap:6px}
.list-row{display:flex;align-items:center;gap:12px;padding:13px 15px;border-radius:12px;background:var(--surface);
  border:1px solid var(--border);text-align:left;width:100%;transition:border-color .12s,background .12s}
.list-row:hover{border-color:var(--border2)}
button.list-row{cursor:pointer}
.list-row.static{cursor:default}
.lr-ic{color:var(--primary);flex-shrink:0}
.lr-title{flex:1;font-weight:500;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.lr-title.link{background:none;border:none;text-align:left;font-size:14.5px}
.lr-title.link:hover{color:var(--primary)}
.lr-meta{font-size:12px;color:var(--faint);white-space:nowrap}
.lr-del{border:none;background:transparent;color:var(--faint);padding:4px;display:flex}
.lr-del:hover{color:var(--error)}
.empty{text-align:center;padding:60px 20px;color:var(--faint);display:flex;flex-direction:column;align-items:center;gap:8px}
.empty p{font-weight:600;color:var(--text);margin:6px 0 0}
.empty span{font-size:13px}
.doc-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(180px,1fr));gap:14px}
.doc-card{background:var(--surface);border:1px solid var(--border);border-radius:14px;padding:16px}
.doc-ic{width:40px;height:40px;border-radius:11px;display:grid;place-items:center;color:var(--primary);background:var(--primary-soft);margin-bottom:10px}
.doc-name{font-weight:600;font-size:13.5px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.doc-meta{font-size:11.5px;color:var(--faint);margin-top:3px}
.bars{display:flex;flex-direction:column;gap:12px;margin-top:4px}
.bar-row{display:flex;align-items:center;gap:12px}
.bar-label{width:150px;font-size:13px;color:var(--muted);white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.bar-track{flex:1;height:9px;background:var(--surface2);border-radius:6px;overflow:hidden}
.bar-fill{height:100%;border-radius:6px;background:linear-gradient(90deg,var(--primary),var(--accent));transition:width .5s ease}
.bar-val{width:24px;text-align:right;font-size:12px;color:var(--faint)}
.card{background:var(--surface);border:1px solid var(--border);border-radius:16px;padding:20px;margin-bottom:16px}
.card h4{font-family:var(--display);margin:0 0 14px;font-size:15px}
.muted-p{color:var(--muted);margin:0;font-size:13.5px}
.theme-pick{display:flex;gap:10px}
.theme-opt{display:flex;align-items:center;gap:7px;padding:9px 16px;border-radius:11px;border:1px solid var(--border);
  background:var(--surface2);font-size:13.5px;font-weight:500}
.theme-opt.on{border-color:var(--primary);color:var(--primary);background:var(--primary-soft)}
.fld{display:flex;flex-direction:column;gap:6px;margin-bottom:14px;font-size:12.5px;color:var(--muted);font-weight:500}
.fld:last-child{margin-bottom:0}
.fld input{padding:10px 12px;border-radius:10px;border:1px solid var(--border);background:var(--bg);color:var(--text);font-size:14px;outline:none}
.fld input:focus{border-color:var(--primary)}

/* ---------- Sources (research) ---------- */
.ws{position:relative}
.sources-bar{display:flex;align-items:center;gap:12px;padding:10px 16px;border-bottom:1px solid var(--border);
  background:var(--glass);backdrop-filter:blur(8px);flex-shrink:0;min-height:53px;position:relative;z-index:20}
.sb-label{display:flex;align-items:center;gap:7px;font-family:var(--display);font-weight:600;font-size:13px;color:var(--muted);flex-shrink:0}
.sb-count{background:var(--primary-soft);color:var(--primary);border-radius:20px;padding:1px 8px;font-size:12px;margin-left:4px}
.sb-list{flex:1;display:flex;align-items:center;gap:8px;overflow-x:auto;min-width:0;padding:2px 0}
.sb-list::-webkit-scrollbar{height:0}
.sb-hint{font-size:12.5px;color:var(--faint);white-space:nowrap}
.src-chip{display:inline-flex;align-items:center;gap:6px;padding:6px 10px;border-radius:9px;background:var(--surface2);
  border:1px solid var(--border);font-size:12.5px;flex-shrink:0;max-width:210px}
.src-chip .src-name{white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.src-chip button{border:none;background:transparent;color:var(--faint);display:flex;padding:0}
.src-chip button:hover{color:var(--error)}
.sb-add-wrap{position:relative;flex-shrink:0}
.sb-add{display:inline-flex;align-items:center;gap:6px;padding:8px 13px;border-radius:10px;font-size:13px;font-weight:600;
  color:var(--primary);background:var(--primary-soft);border:1px solid transparent;transition:filter .12s}
.sb-add:hover{filter:brightness(1.08)}
.src-menu{position:absolute;right:0;top:44px;background:var(--surface);border:1px solid var(--border);border-radius:12px;
  box-shadow:var(--shadow);padding:6px;display:flex;flex-direction:column;gap:2px;z-index:35;min-width:172px;animation:pop .15s ease}
.src-menu button{display:flex;align-items:center;gap:10px;padding:9px 11px;border-radius:8px;border:none;background:transparent;
  color:var(--text);font-size:13.5px;text-align:left}
.src-menu button:hover{background:var(--surface2)}

/* ---------- Modal ---------- */
.modal-overlay{position:absolute;inset:0;background:rgba(0,0,0,.45);backdrop-filter:blur(2px);display:grid;
  place-items:center;z-index:60;padding:20px;animation:pop .16s ease}
.modal{width:100%;max-width:520px;background:var(--surface);border:1px solid var(--border);border-radius:18px;
  box-shadow:var(--shadow);padding:18px;display:flex;flex-direction:column;gap:14px}
.modal-head{display:flex;align-items:center;justify-content:space-between;font-family:var(--display);font-weight:600;font-size:15px}
.modal-head>span{display:flex;align-items:center;gap:8px}
.modal-head button{border:none;background:transparent;color:var(--muted);display:flex}
.modal-head button:hover{color:var(--text)}
.modal-ta{min-height:180px;resize:vertical;border:1px solid var(--border);border-radius:12px;background:var(--bg);
  color:var(--text);padding:12px 14px;font-size:14px;line-height:1.5;outline:none;font-family:var(--font)}
.modal-ta:focus{border-color:var(--primary)}
.modal-actions{display:flex;justify-content:flex-end;gap:10px}
.btn-ghost{padding:9px 16px;border-radius:11px;border:1px solid var(--border);background:transparent;color:var(--text);font-weight:500;font-size:14px}
.btn-ghost:hover{background:var(--surface2)}
.modal .btn-primary:disabled{opacity:.45;cursor:not-allowed}

/* ---------- Logout ---------- */
.logout{display:flex;align-items:center;justify-content:center;gap:8px;padding:9px;border-radius:11px;margin-top:2px;
  border:1px solid var(--border);background:transparent;color:var(--muted);font-size:13.5px;font-weight:500;
  transition:color .12s,border-color .12s,background .12s}
.logout:hover{color:var(--error);border-color:var(--error);background:rgba(239,68,68,.08)}

/* ---------- Document tags / Home ---------- */
.doc-top{display:flex;align-items:center;justify-content:space-between;margin-bottom:10px}
.doc-card .doc-ic{margin-bottom:0}
.doc-tag{font-size:10px;font-weight:600;text-transform:uppercase;letter-spacing:.04em;padding:3px 8px;border-radius:20px;
  background:var(--surface2);color:var(--muted)}
.doc-tag.src{background:var(--primary-soft);color:var(--primary)}
.home-page{display:flex;flex-direction:column;align-items:center;justify-content:center;min-height:100%}
.home-hero{padding:20px 0;max-width:680px}
.home-hero .hero-badge{width:118px;height:118px;border-radius:30px}
.home-hero h1{font-size:clamp(36px,5.5vw,52px);margin:22px 0 14px}
.home-hero p{font-size:clamp(15px,2.1vw,19px);max-width:600px;line-height:1.6;margin-bottom:30px}
.home-hero .btn-primary.lg{padding:16px 34px;font-size:17px;border-radius:14px}
.home-hero .nova-glow.small{width:560px;height:560px;top:-90px}

@media(max-width:860px){
  .sources-bar{gap:8px;padding:8px 12px}
  .sb-hint{font-size:11.5px}
}

/* ---------- Work Studio panel ---------- */
.studio-btn{display:inline-flex;align-items:center;gap:7px;padding:8px 13px;border-radius:10px;font-size:13px;font-weight:600;
  color:#fff;background:linear-gradient(135deg,var(--primary),var(--accent));border:none;box-shadow:0 6px 16px var(--primary-soft);
  transition:transform .12s,filter .12s}
.studio-btn:hover{transform:translateY(-1px);filter:brightness(1.05)}
.studio-btn.on{filter:brightness(1.08)}
.studio{width:0;flex-shrink:0;overflow:hidden;border-left:1px solid var(--border);background:var(--bg2);
  transition:width .32s cubic-bezier(.4,0,.2,1);z-index:36}
.studio.open{width:404px}
.studio-inner{width:404px;height:100%;display:flex;flex-direction:column}
.studio-head{display:flex;align-items:center;justify-content:space-between;padding:15px 16px 12px}
.sh-title{display:flex;align-items:center;gap:9px;font-family:var(--display);font-weight:700;font-size:16px}
.sh-actions{display:flex;gap:2px}
.icon-btn.sm{width:32px;height:32px;border-radius:9px}
.icon-btn.sm.pinned{color:var(--primary);background:var(--primary-soft)}
.studio-search{display:flex;align-items:center;gap:8px;margin:0 16px;padding:9px 11px;border-radius:11px;
  background:var(--surface);border:1px solid var(--border);color:var(--muted)}
.studio-search input{border:none;background:transparent;outline:none;color:var(--text);width:100%;font-size:13.5px}
.studio-search input::placeholder{color:var(--faint)}
.studio-body{flex:1;overflow-y:auto;padding:14px 16px 20px}
.studio-sub{font-size:13px;color:var(--muted);margin:0 0 14px;line-height:1.5}
.tool-list{display:flex;flex-direction:column;gap:9px}
.tool-card{display:flex;align-items:center;gap:12px;padding:13px;border-radius:14px;background:var(--surface);
  border:1px solid var(--border);text-align:left;transition:transform .13s,border-color .13s,background .13s,box-shadow .13s}
.tool-card:hover{transform:translateY(-2px);border-color:var(--border2);box-shadow:var(--shadow)}
.tool-card.active{border-color:var(--primary);background:var(--primary-soft)}
.tc-ic{width:40px;height:40px;flex-shrink:0;border-radius:11px;display:grid;place-items:center;color:var(--primary);
  background:var(--primary-soft)}
.tool-card:hover .tc-ic{background:linear-gradient(135deg,var(--primary),var(--accent));color:#fff}
.tc-txt{flex:1;min-width:0;display:flex;flex-direction:column;gap:2px}
.tc-title{font-weight:600;font-size:14px;font-family:var(--display);display:flex;align-items:center;gap:7px}
.beta{font-style:normal;font-size:9.5px;font-weight:700;text-transform:uppercase;letter-spacing:.05em;color:var(--accent);
  background:rgba(139,92,246,.14);padding:2px 6px;border-radius:20px}
.tc-desc{font-size:12px;color:var(--muted);white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.tc-arrow{color:var(--faint);flex-shrink:0}
.tool-card:hover .tc-arrow{color:var(--primary)}
.spin{animation:spin 1s linear infinite}
@keyframes spin{to{transform:rotate(360deg)}}

/* ---------- Tool view (in main area) ---------- */
.tool-view{flex:1;display:flex;flex-direction:column;min-width:0;width:100%}
.tv-head{height:56px;flex-shrink:0;display:flex;align-items:center;gap:12px;padding:0 20px;border-bottom:1px solid var(--border)}
.tv-back{display:inline-flex;align-items:center;gap:6px;font-size:13.5px;font-weight:500;color:var(--muted);
  background:transparent;border:none;padding:6px 8px;border-radius:9px}
.tv-back:hover{background:var(--surface);color:var(--text)}
.tv-title{flex:1;display:flex;align-items:center;gap:8px;font-family:var(--display);font-weight:600;font-size:15px;justify-content:center}
.mini-btn{display:inline-flex;align-items:center;gap:6px;font-size:12.5px;font-weight:500;color:var(--muted);
  background:transparent;border:1px solid var(--border);border-radius:9px;padding:7px 11px;transition:color .12s,border-color .12s}
.mini-btn:hover:not(:disabled){color:var(--text);border-color:var(--border2)}
.mini-btn:disabled{opacity:.45;cursor:not-allowed}
.tv-body{flex:1;overflow-y:auto;padding:26px 22px 40px}

/* loading / error */
.tool-loading{max-width:420px;margin:8vh auto 0;text-align:center;display:flex;flex-direction:column;align-items:center;gap:10px}
.tl-orb{width:74px;height:74px;border-radius:22px;display:grid;place-items:center;color:#fff;margin-bottom:6px;
  background:linear-gradient(135deg,var(--primary),var(--accent));box-shadow:0 10px 30px var(--primary-soft);animation:pulseOrb 1.6s ease-in-out infinite}
@keyframes pulseOrb{0%,100%{transform:scale(1);opacity:.92}50%{transform:scale(1.06);opacity:1}}
.tl-title{font-family:var(--display);font-weight:600;font-size:17px}
.tl-step{font-size:13px;color:var(--muted)}
.tl-bar{width:100%;height:8px;border-radius:6px;background:var(--surface2);overflow:hidden;margin-top:8px}
.tl-fill{height:100%;border-radius:6px;background:linear-gradient(90deg,var(--primary),var(--accent));transition:width .35s ease}
.tl-pct{font-size:12px;color:var(--faint);font-variant-numeric:tabular-nums}
.tool-error{max-width:400px;margin:9vh auto 0;text-align:center;display:flex;flex-direction:column;align-items:center;gap:10px}
.te-ic{width:60px;height:60px;border-radius:18px;display:grid;place-items:center;color:var(--error);background:rgba(239,68,68,.12)}
.te-ic.soft{color:var(--primary);background:var(--primary-soft)}
.te-title{font-family:var(--display);font-weight:600;font-size:17px}
.te-msg{font-size:13.5px;color:var(--muted);line-height:1.5}
.te-msg{margin-bottom:6px}

/* result shared */
.tool-result{max-width:760px;margin:0 auto;animation:rise .3s ease}
.res-h{font-family:var(--display);font-size:20px;font-weight:700;letter-spacing:-.02em;margin:0 0 14px}
.res-h.center{text-align:center}
.res-toolbar{display:flex;justify-content:flex-end;margin-bottom:12px}

/* audio */
.audio-head{display:flex;align-items:center;justify-content:space-between;gap:14px;margin-bottom:18px;flex-wrap:wrap}
.audio-head .res-h{margin:0}
.ar-meta{font-size:12.5px;color:var(--faint)}
.play-btn{display:inline-flex;align-items:center;gap:8px;padding:10px 18px;border-radius:12px;border:none;color:#fff;font-weight:600;
  font-size:14px;background:linear-gradient(135deg,var(--primary),var(--accent));box-shadow:0 6px 16px var(--primary-soft);transition:transform .12s}
.play-btn:hover{transform:translateY(-1px)}
.audio-script{display:flex;flex-direction:column;gap:12px}
.seg{display:flex;gap:12px;padding:12px 14px;border-radius:13px;background:var(--surface);border:1px solid var(--border);transition:border-color .2s,background .2s}
.seg.on{border-color:var(--primary);background:var(--primary-soft)}
.seg-spk{flex-shrink:0;font-size:11px;font-weight:700;padding:3px 9px;border-radius:20px;height:fit-content;font-family:var(--display)}
.seg-spk.a{color:var(--primary);background:var(--primary-soft)}
.seg-spk.b{color:var(--accent);background:rgba(139,92,246,.14)}
.seg p{margin:0;font-size:14px;line-height:1.55}

/* slides */
.slides-wrap{display:flex;flex-direction:column;gap:16px}
.slide-view{background:var(--surface);border:1px solid var(--border);border-radius:18px;padding:34px 30px;min-height:300px;
  box-shadow:var(--shadow);position:relative;overflow:hidden}
.slide-view::before{content:'';position:absolute;left:0;top:0;bottom:0;width:5px;background:linear-gradient(180deg,var(--primary),var(--accent))}
.slide-num{font-size:12px;color:var(--faint);font-weight:600;margin-bottom:10px}
.slide-title{font-family:var(--display);font-size:24px;font-weight:700;letter-spacing:-.02em;margin:0 0 18px}
.slide-bullets{margin:0;padding-left:22px;display:flex;flex-direction:column;gap:11px}
.slide-bullets li{font-size:15px;line-height:1.5}
.slide-nav{display:flex;align-items:center;justify-content:space-between;gap:12px}
.dots{display:flex;gap:7px}
.dots span{width:9px;height:9px;border-radius:50%;background:var(--surface3);cursor:pointer;transition:background .15s,transform .15s}
.dots span.on{background:var(--primary);transform:scale(1.15)}

/* video storyboard */
.storyboard{display:flex;flex-direction:column;gap:12px}
.scene{display:flex;gap:0;border:1px solid var(--border);border-radius:14px;overflow:hidden;background:var(--surface)}
.scene-visual{flex-shrink:0;width:120px;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:6px;
  color:#fff;background:linear-gradient(150deg,var(--primary),var(--accent));font-size:12px;font-weight:600}
.scene-body{flex:1;padding:14px 16px;min-width:0}
.scene-h{font-family:var(--display);font-weight:600;font-size:15px;margin-bottom:4px}
.scene-vis{font-size:12px;color:var(--faint);margin-bottom:8px}
.scene-narr{margin:0;font-size:14px;line-height:1.5;color:var(--muted);font-style:italic}

/* mind map */
.mindmap{display:flex;flex-direction:column;align-items:center;gap:4px;padding:10px 0}
.mm-root{font-family:var(--display);font-weight:700;font-size:18px;color:#fff;padding:12px 24px;border-radius:14px;
  background:linear-gradient(135deg,var(--primary),var(--accent));box-shadow:0 8px 22px var(--primary-soft);margin-bottom:8px}
.mm-branches{display:grid;grid-template-columns:1fr 1fr;gap:14px;width:100%}
.mm-branch{border:1px solid var(--border);border-radius:14px;padding:14px;background:var(--surface);
  border-left:4px solid hsl(var(--h) 80% 60%)}
.mm-node{font-family:var(--display);font-weight:600;font-size:14.5px;margin-bottom:10px;color:hsl(var(--h) 70% 55%)}
.mm-children{display:flex;flex-wrap:wrap;gap:7px}
.mm-child{font-size:12.5px;padding:6px 11px;border-radius:9px;background:var(--surface2);border:1px solid var(--border)}

/* report */
.report{font-size:14.5px;line-height:1.6}
.report h3,.report h4,.report h5{font-family:var(--display);margin:18px 0 9px;line-height:1.3}
.report h3{font-size:19px}.report h4{font-size:16px}
.report p{margin:0 0 11px}
.report ul,.report ol{margin:8px 0 13px;padding-left:22px}
.report li{margin:4px 0}
.report strong{font-weight:650}
.report code{background:var(--code-bg);border-radius:5px;padding:1px 6px;font-size:13px;font-family:ui-monospace,Menlo,monospace}
.report pre{background:var(--code-bg);border:1px solid var(--border);border-radius:10px;padding:13px 15px;overflow-x:auto;margin:11px 0}
.report pre code{background:none;padding:0}

/* flashcards */
.flash-wrap{display:flex;flex-direction:column;align-items:center;gap:16px}
.flashcard{width:100%;max-width:460px;height:250px;perspective:1400px;cursor:pointer}
.flashcard .fc-face{position:absolute;inset:0;backface-visibility:hidden;border-radius:18px;border:1px solid var(--border);
  padding:26px;display:flex;flex-direction:column;gap:14px;align-items:center;justify-content:center;text-align:center;
  box-shadow:var(--shadow);transition:transform .55s cubic-bezier(.4,0,.2,1)}
.flashcard{position:relative}
.fc-front{background:var(--surface);transform:rotateY(0)}
.fc-back{background:linear-gradient(160deg,var(--surface),var(--surface2));transform:rotateY(180deg)}
.flashcard.flipped .fc-front{transform:rotateY(-180deg)}
.flashcard.flipped .fc-back{transform:rotateY(0)}
.fc-tag{font-size:10.5px;font-weight:700;text-transform:uppercase;letter-spacing:.06em;color:var(--primary);
  background:var(--primary-soft);padding:4px 11px;border-radius:20px}
.fc-back .fc-tag{color:var(--accent);background:rgba(139,92,246,.14)}
.fc-body{font-size:16px;line-height:1.5;font-weight:500}
.fc-nav{display:flex;align-items:center;gap:16px;font-size:13px;color:var(--muted);font-variant-numeric:tabular-nums}
.fc-hint{font-size:12px;color:var(--faint)}

/* quiz */
.quiz-wrap{display:flex;flex-direction:column;gap:18px}
.quiz-q{background:var(--surface);border:1px solid var(--border);border-radius:15px;padding:17px}
.qq-title{font-weight:600;font-size:15px;margin-bottom:12px;line-height:1.4}
.qq-opts{display:flex;flex-direction:column;gap:8px}
.qq-opt{text-align:left;padding:11px 14px;border-radius:11px;border:1px solid var(--border);background:var(--bg);
  font-size:14px;transition:border-color .12s,background .12s}
.qq-opt:hover:not(:disabled){border-color:var(--primary)}
.qq-opt.chosen{border-color:var(--primary);background:var(--primary-soft)}
.qq-opt.correct{border-color:var(--success);background:rgba(34,197,94,.14);color:var(--success);font-weight:600}
.qq-opt.wrong{border-color:var(--error);background:rgba(239,68,68,.12);color:var(--error)}
.qq-exp{margin-top:11px;font-size:13px;color:var(--muted);padding:10px 12px;border-radius:10px;background:var(--surface2);line-height:1.5}
.quiz-score{text-align:center;font-family:var(--display);font-weight:700;font-size:20px;padding:16px;border-radius:14px;
  color:#fff;background:linear-gradient(135deg,var(--primary),var(--accent))}

/* infographic */
.info-stats{display:grid;grid-template-columns:repeat(3,1fr);gap:14px;margin-bottom:22px}
.info-stat{background:var(--surface);border:1px solid var(--border);border-radius:16px;padding:22px 14px;text-align:center}
.is-val{display:block;font-family:var(--display);font-size:30px;font-weight:700;letter-spacing:-.02em;
  background:linear-gradient(135deg,var(--primary),var(--accent));-webkit-background-clip:text;background-clip:text;color:transparent}
.is-label{font-size:12.5px;color:var(--muted);margin-top:4px}
.info-highlights{display:flex;flex-direction:column;gap:10px}
.info-hl{display:flex;gap:13px;align-items:flex-start;padding:14px 16px;border-radius:13px;background:var(--surface);border:1px solid var(--border);font-size:14px;line-height:1.5}
.ih-num{flex-shrink:0;width:26px;height:26px;border-radius:8px;display:grid;place-items:center;font-size:13px;font-weight:700;
  color:#fff;background:linear-gradient(135deg,var(--primary),var(--accent))}

/* data table */
.table-scroll{overflow-x:auto;border:1px solid var(--border);border-radius:14px}
.data-table{width:100%;border-collapse:collapse;font-size:13.5px}
.data-table th{text-align:left;padding:12px 15px;background:var(--surface2);font-family:var(--display);font-weight:600;
  border-bottom:1px solid var(--border);white-space:nowrap}
.data-table td{padding:11px 15px;border-bottom:1px solid var(--border)}
.data-table tr:last-child td{border-bottom:none}
.data-table tbody tr:hover{background:var(--surface)}

@media(max-width:1100px){ .studio.open{width:360px} .studio-inner{width:360px} }
@media(max-width:860px){
  .studio{position:fixed;top:0;right:0;bottom:0;width:100%!important;transform:translateX(100%);
    transition:transform .3s ease;border-left:none;z-index:45}
  .studio.open{transform:none}
  .studio-inner{width:100%}
  .sb-btn-label{display:none}
  .studio-btn{padding:8px 10px}
  .mm-branches,.info-stats{grid-template-columns:1fr}
  .tv-title{display:none}
  .scene-visual{width:88px}
}

/* ---------- Button relocations & modals ---------- */
.add-src-wrap{position:relative}
.sb-add,.new-chat,.studio-btn{white-space:nowrap}
.sb-add{flex-shrink:0}
.src-menu.side{left:0;right:0;top:48px}
.sb-add.studio{color:#fff;background:linear-gradient(135deg,var(--primary),var(--accent));box-shadow:0 5px 16px var(--primary-soft);
  padding:11px 26px;font-size:14px;border-radius:12px;font-weight:600;white-space:nowrap;flex-shrink:0;width:auto;min-width:max-content}
.sb-add.studio:hover{filter:brightness(1.07);transform:translateY(-1px)}
.sb-add-wrap{flex-shrink:0}
/* On narrow widths, free up room so the Work Studio button always shows in full. */
@media(max-width:680px){
  .sb-label-txt{display:none}
  .sb-hint{display:none}
}
.studio-btn.newtask{background:var(--surface);color:var(--text);border:1px solid var(--border);box-shadow:none}
.studio-btn.newtask:hover{background:var(--surface2);transform:translateY(-1px)}
.modal-overlay.fixed{position:fixed}
.modal.sm{max-width:420px}
.modal-text{margin:0;font-size:13.5px;color:var(--muted);line-height:1.55}
.btn-danger{display:inline-flex;align-items:center;gap:7px;padding:9px 16px;border-radius:11px;border:none;font-weight:600;
  font-size:14px;color:#fff;background:var(--error)}
.btn-danger:hover{filter:brightness(1.06)}

/* ---------- Auth (login / signup) ---------- */
.auth{position:relative;flex:1;display:flex;min-height:100vh;width:100%;background:var(--bg);overflow-y:auto}
.auth-theme{position:absolute;top:16px;right:16px;z-index:6;background:var(--surface);border:1px solid var(--border)}
.auth-brand{flex:1.05;position:relative;display:flex;flex-direction:column;justify-content:center;gap:20px;padding:56px;overflow:hidden;
  background:linear-gradient(160deg,var(--bg2),var(--surface))}
.ab-glow{position:absolute;top:-8%;left:-6%;width:520px;height:520px;pointer-events:none;
  background:radial-gradient(circle,rgba(59,130,246,.30),rgba(139,92,246,.14) 45%,transparent 70%);filter:blur(10px);animation:pulse 7s ease-in-out infinite}
.ab-logo{position:relative;z-index:1;display:flex;align-items:center;gap:10px;font-family:var(--display);font-weight:700;font-size:22px;letter-spacing:-.02em}
.auth-brand h1{position:relative;z-index:1;font-family:var(--display);font-size:40px;font-weight:700;line-height:1.12;letter-spacing:-.03em;margin:6px 0 0;
  background:linear-gradient(180deg,var(--text),var(--muted));-webkit-background-clip:text;background-clip:text;color:transparent}
.auth-brand>p{position:relative;z-index:1;color:var(--muted);font-size:15px;max-width:420px;margin:0;line-height:1.6}
.ab-feats{list-style:none;padding:0;margin:8px 0 0;display:flex;flex-direction:column;gap:13px;position:relative;z-index:1}
.ab-feats li{display:flex;align-items:center;gap:12px;font-size:14px;color:var(--text)}
.ab-feats .fc{width:24px;height:24px;flex-shrink:0;border-radius:8px;display:grid;place-items:center;color:var(--primary);background:var(--primary-soft)}

.auth-panel{flex:1;display:flex;align-items:center;justify-content:center;padding:36px 28px}
.auth-card{width:100%;max-width:392px;display:flex;flex-direction:column;gap:15px}
.auth-logo-sm{display:none;align-items:center;justify-content:center;gap:10px;font-family:var(--display);font-weight:700;font-size:20px;margin-bottom:4px}
.auth-card h2{font-family:var(--display);font-size:26px;font-weight:700;letter-spacing:-.02em;margin:0}
.auth-sub{color:var(--muted);font-size:14px;margin:-9px 0 3px}
.social-row{display:flex;gap:9px}
.social-btn{flex:1;display:flex;align-items:center;justify-content:center;gap:8px;padding:11px 8px;border-radius:11px;
  border:1px solid var(--border);background:var(--surface);font-size:13px;font-weight:500;color:var(--text);transition:background .12s,border-color .12s,transform .12s}
.social-btn:hover{background:var(--surface2);border-color:var(--border2);transform:translateY(-1px)}
.divider{display:flex;align-items:center;gap:12px;color:var(--faint);font-size:12px;margin:1px 0}
.divider::before,.divider::after{content:'';flex:1;height:1px;background:var(--border)}
.auth-error{background:rgba(239,68,68,.1);border:1px solid var(--error);color:var(--error);border-radius:10px;padding:9px 12px;font-size:13px}
.auth-success{background:rgba(34,197,94,.1);border:1px solid var(--success);color:var(--success);border-radius:11px;padding:12px 14px;font-size:13.5px;display:flex;align-items:center;gap:9px;line-height:1.45}
.auth-field{display:flex;align-items:center;gap:10px;padding:0 13px;border-radius:12px;border:1px solid var(--border);background:var(--surface);transition:border-color .14s,box-shadow .14s}
.auth-field:focus-within{border-color:var(--primary);box-shadow:0 0 0 4px var(--primary-soft)}
.af-ic{color:var(--faint);flex-shrink:0}
.auth-field input{flex:1;min-width:0;border:none;background:transparent;outline:none;color:var(--text);font-size:14.5px;padding:12px 0}
.auth-field input::placeholder{color:var(--faint)}
.af-eye{border:none;background:transparent;color:var(--faint);display:flex;padding:4px}
.af-eye:hover{color:var(--text)}
.auth-row{display:flex;align-items:center;justify-content:space-between;font-size:13px;margin:1px 0}
.auth-check{display:flex;align-items:center;gap:8px;color:var(--muted);cursor:pointer;font-size:13px;line-height:1.4}
.auth-check.terms{align-items:flex-start}
.auth-check input{accent-color:var(--primary);width:15px;height:15px;flex-shrink:0;margin-top:1px}
.link-btn{border:none;background:transparent;color:var(--primary);font-weight:600;font-size:13px;padding:0}
.link-btn:hover{text-decoration:underline}
.auth-submit{display:flex;align-items:center;justify-content:center;gap:8px;padding:13px;border-radius:12px;border:none;color:#fff;
  font-weight:600;font-size:15px;background:linear-gradient(135deg,var(--primary),var(--accent));box-shadow:0 8px 22px var(--primary-soft);
  transition:transform .12s,filter .12s;margin-top:3px;min-height:48px}
.auth-submit:hover:not(:disabled){transform:translateY(-1px);filter:brightness(1.05)}
.auth-submit:disabled{opacity:.75;cursor:not-allowed}
.auth-switch{text-align:center;font-size:13.5px;color:var(--muted);margin:5px 0 0}
.auth-switch .link-btn{margin-left:6px}
@media(max-width:900px){
  .auth-brand{display:none}
  .auth-logo-sm{display:flex}
  .auth-panel{padding:26px 20px;align-items:flex-start}
  .auth-card{margin:auto}
}
@media(max-width:440px){ .social-btn .lbl{display:none} .social-btn{padding:12px 8px} }

/* ---------- Smooth transitions & animations ---------- */
@keyframes fadeIn{from{opacity:0}to{opacity:1}}
@keyframes viewIn{from{opacity:0;transform:translateY(12px)}to{opacity:1;transform:none}}
@keyframes appIn{from{opacity:0;transform:translateY(8px) scale(.995)}to{opacity:1;transform:none}}
@keyframes fadeSlide{from{opacity:0;transform:translateX(10px)}to{opacity:1;transform:none}}
@keyframes cardIn{from{opacity:0;transform:translateY(10px)}to{opacity:1;transform:none}}
@keyframes modalIn{from{opacity:0;transform:translateY(14px) scale(.97)}to{opacity:1;transform:none}}

.view-anim{flex:1;display:flex;flex-direction:column;min-width:0;min-height:0;animation:viewIn .34s cubic-bezier(.22,1,.36,1)}
.auth{animation:fadeIn .4s ease}
.main{animation:appIn .5s cubic-bezier(.22,1,.36,1)}
.auth-form{display:flex;flex-direction:column;gap:15px;animation:fadeSlide .28s cubic-bezier(.22,1,.36,1)}
.modal{animation:modalIn .26s cubic-bezier(.22,1,.36,1)}
.tool-card{animation:cardIn .34s cubic-bezier(.22,1,.36,1) both}
.demo-hint{align-self:center;border:none;background:transparent;color:var(--faint);font-size:12.5px;padding:2px;transition:color .15s}
.demo-hint:hover{color:var(--primary);text-decoration:underline}

/* gentle color fade when switching light/dark */
.app,.main,.topbar,.content,.auth,.auth-brand,.auth-panel,.sources-bar,.tv-head,.tv-body,
.bubble,.stat,.card,.doc-card,.quiz-q,.scene,.slide-view,.data-table th,.auth-card h2{
  transition:background-color .35s ease,border-color .35s ease,color .35s ease}

@media(prefers-reduced-motion:reduce){
  .view-anim,.auth,.main,.auth-form,.modal,.tool-card{animation:none!important}
}

/* ---------- Overlay / responsive ---------- */
.overlay{position:fixed;inset:0;background:rgba(0,0,0,.5);z-index:39;display:none}
@media(max-width:860px){
  .sidebar{position:fixed;left:0;top:0;bottom:0;transform:translateX(-100%);transition:transform .22s ease;box-shadow:var(--shadow)}
  .sidebar.open{transform:none}
  .overlay{display:block}
  .icon-btn.menu{display:grid}
  .stat-grid,.stat-grid.big{grid-template-columns:1fr 1fr}
  .suggest-grid{grid-template-columns:1fr}
  .bar-label{width:100px}
}
@media(prefers-reduced-motion:reduce){
  *{animation:none!important;transition:none!important;scroll-behavior:auto!important}
}
`;

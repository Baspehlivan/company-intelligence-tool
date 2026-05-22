"""Shared CIT HTML theme — v3 with gap matrix and scroll animations."""

CIT_CSS_V3 = """
:root {
  --bg: #0b0f17;
  --surface: #141b2b;
  --surface2: #1e293f;
  --text: #e2e8f0;
  --text-dim: #8899b1;
  --accent: #3b82f6;
  --accent-muted: #3b82f622;
  --accent2: #a78bfa;
  --green: #22d3a7;
  --orange: #f59e0b;
  --red: #ef4444;
  --insight-bg: linear-gradient(160deg, #0f2340 0%, #1e1e3a 50%, #120f26 100%);
  --border: #1e2a44;
  --shadow: 0 2px 20px rgba(0,0,0,0.3);
  --radius: 12px;
  --radius-sm: 8px;
  --font: "Inter","DM Sans",system-ui,-apple-system,sans-serif;
}
[data-theme="light"] {
  --bg: #f0f4fa;
  --surface: #ffffff;
  --surface2: #e8edf6;
  --text: #0f172a;
  --text-dim: #6a7a93;
  --insight-bg: linear-gradient(160deg, #dbeafe 0%, #ede9fe 100%);
  --border: #d0d9e8;
  --shadow: 0 2px 16px rgba(15,23,42,0.06);
}
* { box-sizing: border-box; margin: 0; padding: 0; }
html { font-size: 16px; -webkit-font-smoothing: antialiased; scroll-behavior: smooth; }
body {
  font-family: var(--font);
  background: var(--bg);
  color: var(--text);
  line-height: 1.65;
  padding: 0;
}
a { color: var(--accent); text-decoration: none; }
a:hover { text-decoration: underline; }

/* === Layout === */
.wrap {
  max-width: 1100px;
  margin: 0 auto;
  padding: 1.5rem clamp(0.75rem, 3vw, 2.5rem) 3rem;
}

/* === Fade-in animations === */
.fade-in {
  opacity: 0;
  transform: translateY(12px);
  transition: opacity 0.5s ease, transform 0.5s ease;
}
.fade-in.visible {
  opacity: 1;
  transform: translateY(0);
}

/* === Topbar === */
.topbar {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  flex-wrap: wrap;
  gap: 1rem;
  margin-bottom: 0.5rem;
  padding-bottom: 1.25rem;
  border-bottom: 1px solid var(--border);
}
.topbar .brand {
  font-size: 0.65rem;
  text-transform: uppercase;
  letter-spacing: 0.14em;
  color: var(--accent);
  font-weight: 700;
  margin-bottom: 0.2rem;
}
.topbar h1 {
  font-size: 1.75rem;
  font-weight: 700;
  letter-spacing: -0.025em;
  line-height: 1.2;
}
.sub { color: var(--text-dim); font-size: 0.82rem; margin-top: 0.25rem; }
.toolbar { display: flex; gap: 0.35rem; flex-wrap: wrap; }

/* === Buttons === */
.btn {
  background: var(--surface2);
  border: 1px solid var(--border);
  color: var(--text);
  padding: 0.35rem 0.8rem;
  border-radius: var(--radius-sm);
  cursor: pointer;
  font-size: 0.78rem;
  font-family: var(--font);
  transition: all 0.12s;
}
.btn:hover { border-color: var(--accent); background: var(--surface); }
.btn:active { transform: scale(0.97); }
.btn.primary { background: var(--accent); border-color: var(--accent); color: #fff; }
.btn.ok { border-color: var(--green); color: var(--green); transition: none; }

/* === Scorecard === */
.scorecard {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
  gap: 0.75rem;
  margin: 1.25rem 0;
}
.stat {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 0.85rem 1rem;
  box-shadow: var(--shadow);
  text-align: center;
}
.stat label {
  font-size: 0.62rem;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: var(--text-dim);
  display: block;
  margin-bottom: 0.25rem;
}
.stat .val {
  font-size: 1rem;
  font-weight: 700;
  margin-top: 0.15rem;
}
.stat .ring-wrap {
  display: flex;
  justify-content: center;
  margin: 0.35rem 0 0.15rem;
}
.stat .ring {
  width: 36px; height: 36px;
  border-radius: 50%;
  position: relative;
}
.stat .ring svg { width: 36px; height: 36px; transform: rotate(-90deg); }
.stat .ring .bg { fill: none; stroke: var(--surface2); stroke-width: 3; }
.stat .ring .fg { fill: none; stroke-width: 3; stroke-linecap: round; transition: stroke-dashoffset 0.8s ease; }
.stat .ring .pct {
  position: absolute; inset: 0;
  display: flex; align-items: center; justify-content: center;
  font-size: 0.7rem; font-weight: 700;
}

/* === Chips/tags === */
.chips { display: flex; flex-wrap: wrap; gap: 0.3rem; margin-bottom: 1rem; }
.chip {
  font-size: 0.68rem;
  padding: 0.15rem 0.5rem;
  border-radius: 999px;
  background: var(--surface2);
  border: 1px solid var(--border);
  color: var(--text-dim);
  white-space: nowrap;
}
.chip.warn { color: var(--orange); border-color: #f59e0b44; }
.chip.accent { color: var(--accent); border-color: var(--accent); }
.chip.green { color: var(--green); border-color: var(--green); }
.chip.high { color: var(--red); border-color: #ef444444; }

/* === Report overview === */
.report-overview {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 1.25rem 1.5rem;
  margin-bottom: 1.5rem;
  box-shadow: var(--shadow);
}
.report-overview p { font-size: 0.92rem; line-height: 1.6; color: var(--text); }
.report-overview .quick-stat {
  display: inline-block;
  font-size: 0.72rem;
  color: var(--text-dim);
  margin-top: 0.65rem;
  padding: 0.2rem 0.6rem;
  background: var(--surface2);
  border-radius: 999px;
  margin-right: 0.35rem;
}

/* === Sparse report treatment === */
.sparse-notice {
  background: linear-gradient(135deg, #1a1135 0%, #0f1a30 100%);
  border: 1px solid var(--accent);
  border-radius: var(--radius);
  padding: 1.25rem 1.5rem;
  margin-bottom: 1.5rem;
  box-shadow: var(--shadow);
}
.sparse-notice h3 {
  font-size: 0.78rem;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: var(--accent2);
  margin-bottom: 0.5rem;
}
.sparse-notice p { font-size: 0.88rem; color: var(--text); line-height: 1.6; }
.sparse-notice .questions {
  margin-top: 0.75rem;
  background: var(--surface);
  border-radius: var(--radius-sm);
  padding: 0.85rem 1.1rem;
  border: 1px solid var(--border);
}
.sparse-notice .questions li {
  list-style: none;
  padding: 0.35rem 0;
  border-bottom: 1px solid var(--border);
  font-size: 0.85rem;
  display: flex;
  gap: 0.5rem;
  align-items: baseline;
}
.sparse-notice .questions li:last-child { border: none; }
.sparse-notice .questions li::before {
  content: "\2192";
  color: var(--accent2);
  font-weight: 700;
  flex-shrink: 0;
}

/* === Insight box === */
.insight-box {
  background: var(--insight-bg);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 1.5rem 1.75rem;
  margin-bottom: 1.5rem;
  box-shadow: var(--shadow);
}
.insight-box h2 {
  font-size: 0.68rem;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  color: var(--text-dim);
  margin-bottom: 0.5rem;
}
.tension {
  font-size: 1.05rem;
  font-weight: 600;
  margin-bottom: 0.7rem;
  color: var(--accent2);
  line-height: 1.45;
}
.insight-body { font-size: 0.92rem; line-height: 1.7; }

/* === Gap matrix (NEW v3) === */
.gap-matrix {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 1rem 1.25rem;
  margin-bottom: 1rem;
  box-shadow: var(--shadow);
}
.matrix-title {
  font-size: 0.65rem;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: var(--text-dim);
  margin-bottom: 0.6rem;
}
.matrix-body {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}
.matrix-row {
  display: grid;
  grid-template-columns: 7rem 1fr 5rem;
  gap: 0.6rem;
  align-items: center;
}
.matrix-cat {
  font-size: 0.75rem;
  color: var(--text);
  text-transform: capitalize;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.matrix-bar {
  height: 8px;
  background: var(--surface2);
  border-radius: 4px;
  overflow: hidden;
}
.matrix-fill {
  height: 100%;
  border-radius: 4px;
  animation: matrixGrow 0.6s ease forwards;
}
@keyframes matrixGrow {
  from { width: 0 !important; }
}
.matrix-badge {
  font-size: 0.7rem;
  display: flex;
  align-items: center;
  gap: 0.2rem;
}

/* === Reframing bridge === */
.reframe-bridge {
  display: grid;
  grid-template-columns: 1fr 44px 1fr;
  gap: 0.5rem;
  align-items: stretch;
  margin-bottom: 1.75rem;
}
@media (max-width: 680px) { .reframe-bridge { grid-template-columns: 1fr; gap: 0.35rem; } .bridge-arrow { transform: rotate(90deg); justify-self: center; padding: 0.2rem 0; } }
.layer {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 1.1rem 1.25rem;
  box-shadow: var(--shadow);
}
.layer h3 {
  font-size: 0.65rem;
  text-transform: uppercase;
  letter-spacing: 0.07em;
  color: var(--text-dim);
  margin-bottom: 0.5rem;
  display: flex;
  align-items: center;
  gap: 0.4rem;
}
.layer h3 .num {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 18px; height: 18px;
  border-radius: 50%;
  font-size: 0.6rem;
  font-weight: 700;
  color: #fff;
  flex-shrink: 0;
}
.layer.layer1 { border-top: 3px solid var(--accent); }
.layer.layer1 h3 .num { background: var(--accent); }
.layer.layer2 { border-top: 3px solid var(--green); }
.layer.layer2 h3 .num { background: var(--green); }
.layer p { font-size: 0.88rem; line-height: 1.65; }
.bridge-arrow {
  display: flex; align-items: center; justify-content: center;
  color: var(--accent2); font-weight: 700;
  padding: 0 0.1rem;
  font-size: 1.2rem;
  opacity: 0.7;
}

/* === Sections === */
section { margin-bottom: 1.75rem; scroll-margin-top: 0.75rem; }
section > h2 {
  font-size: 0.88rem;
  font-weight: 700;
  margin-bottom: 0.75rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}
section > h2 .count {
  font-weight: 400;
  color: var(--text-dim);
  font-size: 0.78rem;
}

/* === Professional sections === */
.badge-edgar {
  display: inline-block;
  font-size: 0.6rem;
  padding: 0.08rem 0.4rem;
  border-radius: 3px;
  background: #05966922;
  border: 1px solid #05966966;
  color: #34d399;
  letter-spacing: 0.05em;
  text-transform: uppercase;
  vertical-align: middle;
  font-weight: 600;
}
.fin-section {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 1.25rem 1.5rem;
  box-shadow: var(--shadow);
}
.fin-header h2 { font-size: 0.85rem; font-weight: 700; margin-bottom: 0.35rem; }
.fin-note { font-size: 0.78rem; color: var(--text-dim); line-height: 1.5; margin-bottom: 1rem; }
.fin-kpi {
  display: inline-flex;
  flex-direction: column;
  align-items: center;
  background: var(--surface2);
  border-radius: var(--radius-sm);
  padding: 0.5rem 1rem;
  margin-bottom: 1rem;
}
.fin-kpi label { font-size: 0.6rem; text-transform: uppercase; letter-spacing: 0.06em; color: var(--text-dim); }
.fin-kpi .val { font-size: 1.05rem; font-weight: 700; font-family: "JetBrains Mono", monospace; }
.fin-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.82rem;
}
.fin-table thead th {
  text-align: left;
  font-size: 0.62rem;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  color: var(--text-dim);
  padding: 0.45rem 0.5rem;
  border-bottom: 1px solid var(--border);
  font-weight: 600;
}
.fin-table thead th:first-child { padding-left: 0; }
.fin-table tbody td {
  padding: 0.45rem 0.5rem;
  border-bottom: 1px solid var(--border);
  font-family: "JetBrains Mono", monospace;
  font-size: 0.8rem;
}
.fin-table tbody td:first-child { padding-left: 0; color: var(--text-dim); }
.fin-table tbody tr:last-child td { border: none; }
.fin-table tbody tr:hover { background: var(--surface2); }
.num { text-align: right; font-variant-numeric: tabular-nums; }
.num.pos { color: var(--green); }
.num.neg { color: var(--red); }

/* === Market data panel === */
.fin-panels {
  display: grid;
  grid-template-columns: 1fr 240px;
  gap: 1rem;
  align-items: start;
}
@media (max-width: 720px) { .fin-panels { grid-template-columns: 1fr; } }
.fin-panel-main { min-width: 0; }
.mkt-panel {
  background: var(--surface2);
  border-radius: var(--radius-sm);
  padding: 0.85rem 1rem;
}
.mkt-panel h3 {
  font-size: 0.62rem;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  color: var(--text-dim);
  margin-bottom: 0.5rem;
}
.mkt-grid { display: flex; flex-direction: column; gap: 0.4rem; }
.mkt-card {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.3rem 0;
  border-bottom: 1px solid var(--border);
}
.mkt-card:last-child { border: none; }
.mkt-card label {
  font-size: 0.7rem;
  color: var(--text-dim);
}
.mkt-card .val {
  font-size: 0.82rem;
  font-weight: 600;
  font-family: "JetBrains Mono", monospace;
}

/* === Benchmark section === */
.bench-section {
  margin-top: 1rem;
  padding-top: 0.85rem;
  border-top: 1px solid var(--border);
}
.bench-section h3 {
  font-size: 0.62rem;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  color: var(--text-dim);
  margin-bottom: 0.5rem;
}
.bench-list { list-style: none; }
.bench-list li {
  font-size: 0.78rem;
  padding: 0.25rem 0;
  color: var(--text);
  line-height: 1.5;
}
.bench-rank {
  font-size: 0.7rem;
  font-weight: 600;
  padding: 0.05rem 0.3rem;
  border-radius: 3px;
}
.bench-above_q3 { color: var(--green); background: #22d3a722; }
.bench-q2_q3 { color: var(--accent); background: #3b82f622; }
.bench-q1_q2 { color: var(--orange); background: #f59e0b22; }
.bench-below_q1 { color: var(--red); background: #ef444422; }

/* === Executive summary === */
.exec-summary {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 1.25rem 1.5rem;
  box-shadow: var(--shadow);
  border-left: 4px solid var(--accent);
}
.exec-summary h2 {
  font-size: 0.68rem;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: var(--text-dim);
  margin-bottom: 0.6rem;
}
.exec-body {
  font-size: 0.9rem;
  line-height: 1.7;
}
.exec-body p { margin-bottom: 0.5rem; }
.exec-body strong { color: var(--accent2); }
.exec-body ul { margin: 0.5rem 0 0.5rem 1rem; }
.exec-body li { margin-bottom: 0.25rem; }

/* === Peer comparison === */
.peer-wrap {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 1.25rem 1.5rem;
  font-size: 0.85rem;
  line-height: 1.65;
  box-shadow: var(--shadow);
}

/* === Peer table === */
.peer-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.82rem;
}
.peer-table thead th {
  text-align: left;
  font-size: 0.62rem;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  color: var(--text-dim);
  padding: 0.45rem 0.5rem;
  border-bottom: 2px solid var(--accent);
  font-weight: 600;
}
.peer-table thead th:first-child { padding-left: 0; }
.peer-table tbody td {
  padding: 0.4rem 0.5rem;
  border-bottom: 1px solid var(--border);
  font-size: 0.8rem;
}
.peer-table tbody td:first-child { padding-left: 0; color: var(--text-dim); }
.peer-table tbody tr:last-child td { border: none; }
.peer-table tbody tr:hover { background: var(--surface2); }
.peer-table .num { font-family: "JetBrains Mono", monospace; font-variant-numeric: tabular-nums; }

/* === Gap filters === */
.gap-filters { display: flex; gap: 0.3rem; margin-bottom: 0.75rem; flex-wrap: wrap; }
.gap-filters .btn.active { border-color: var(--accent); color: var(--accent); }

/* === Gap radar === */
.radar { display: flex; flex-direction: column; gap: 0.35rem; margin-bottom: 1rem; }
.radar-row { display: flex; align-items: center; gap: 0.5rem; font-size: 0.72rem; }
.radar-label { width: 4rem; color: var(--text-dim); text-transform: capitalize; }
.radar-bar { flex: 1; height: 6px; background: var(--surface2); border-radius: 3px; overflow: hidden; }
.radar-fill { height: 100%; border-radius: 3px; transition: width 0.4s ease; }

/* === Gap cards === */
.gaps-grid { display: grid; gap: 0.65rem; }
.gap-card {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius-sm);
  padding: 0.9rem 1.1rem;
  transition: opacity 0.15s, border-color 0.2s;
}
.gap-card:hover { border-color: var(--accent-muted); }
.gap-card.hidden { display: none; }
.gap-card header {
  display: flex;
  align-items: center;
  gap: 0.35rem;
  margin-bottom: 0.55rem;
}
.severity-dot { width: 8px; height: 8px; border-radius: 50%; flex-shrink: 0; }
.gap-cat {
  font-weight: 600;
  font-size: 0.82rem;
  flex: 1;
  font-family: ui-monospace, monospace;
}
.severity-badge {
  font-size: 0.6rem;
  text-transform: uppercase;
  padding: 0.08rem 0.35rem;
  border: 1px solid var(--border);
  border-radius: 3px;
  letter-spacing: 0.03em;
}
.gap-card .gap-row {
  display: grid;
  grid-template-columns: 3px 1fr;
  gap: 0.4rem;
  margin-top: 0.25rem;
  font-size: 0.84rem;
  line-height: 1.55;
}
.gap-card .gap-row .accent-bar {
  width: 3px;
  border-radius: 2px;
  flex-shrink: 0;
}
.gap-card .gap-row .label {
  font-size: 0.62rem;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  color: var(--text-dim);
  display: block;
  margin-bottom: 0.05rem;
}
.note { color: var(--text-dim); font-size: 0.78rem; font-style: italic; margin-top: 0.4rem; }

/* === Checklist === */
.checklist { list-style: none; background: var(--surface); border: 1px solid var(--border); border-radius: var(--radius); padding: 0.75rem 1rem; }
.checklist li { padding: 0.4rem 0; border-bottom: 1px solid var(--border); }
.checklist li:last-child { border: none; }
.checklist label { display: flex; gap: 0.5rem; cursor: pointer; font-size: 0.84rem; align-items: flex-start; }
.checklist input { accent-color: var(--accent); margin-top: 0.25rem; }

/* === Warnings === */
.warnings {
  background: #42200633;
  border: 1px solid #f59e0b44;
  border-radius: var(--radius-sm);
  padding: 0.85rem 1rem;
  margin-bottom: 1.5rem;
  font-size: 0.84rem;
}
.warnings ul { margin: 0.35rem 0 0 1rem; color: var(--text-dim); font-size: 0.82rem; }

/* === Nav pills === */
.nav-pills { display: flex; gap: 0.35rem; flex-wrap: wrap; margin-bottom: 1.25rem; }
.nav-pills a {
  font-size: 0.75rem;
  color: var(--text-dim);
  text-decoration: none;
  padding: 0.2rem 0.55rem;
  border-radius: 4px;
  border: 1px solid var(--border);
  transition: all 0.12s;
}
.nav-pills a:hover { color: var(--text); border-color: var(--accent); }

/* === Muted === */
.muted { color: var(--text-dim); }

/* === Footer === */
footer {
  margin-top: 2.5rem;
  padding-top: 0.85rem;
  border-top: 1px solid var(--border);
  font-size: 0.72rem;
  color: var(--text-dim);
  display: flex;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 0.5rem;
}

/* === Compare layout === */
.compare-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; }
@media (max-width: 800px) { .compare-grid { grid-template-columns: 1fr; } }
.compare-col { background: var(--surface); border: 1px solid var(--border); border-radius: var(--radius); padding: 1.25rem; }
.compare-col h3 { font-size: 0.95rem; margin-bottom: 0.5rem; }
.compare-col.a { border-top: 3px solid var(--accent); }
.compare-col.b { border-top: 3px solid var(--accent2); }
.index-list { list-style: none; }
.index-list li { margin: 0.4rem 0; }
.index-list a { font-size: 1rem; }

/* === Print styles === */
@media print {
  body { background: white !important; color: #0f172a !important; }
  .toolbar, .nav-pills, .gap-filters { display: none !important; }
  .wrap { max-width: 100%; padding: 0.75in; }
  .topbar h1 { font-size: 1.4rem; }
  .fade-in { opacity: 1 !important; transform: none !important; }
  .scorecard { grid-template-columns: repeat(4, 1fr); gap: 0.35rem; }
  .stat { box-shadow: none; border: 1px solid #d0d9e8; padding: 0.5rem; }
  .stat .ring { width: 28px; height: 28px; }
  .stat .ring svg { width: 28px; height: 28px; }
  .gap-card { break-inside: avoid; border-color: #d0d9e8; }
  .gap-card:hover { border-color: #d0d9e8; }
  .insight-box { break-inside: avoid; box-shadow: none; border: 1px solid #d0d9e8; background: #f0f4fa !important; }
  .sparse-notice { background: #f0f4fa !important; border: 1px solid #3b82f6; }
  .reframe-bridge { break-inside: avoid; }
  .layer { box-shadow: none; }
  .fin-table tbody td { color: #0f172a !important; }
  .fin-table tbody tr:hover { background: transparent !important; }
  .peer-table tbody td { color: #0f172a !important; }
  .peer-table tbody tr:hover { background: transparent !important; }
  .peer-table thead th { border-bottom-color: #3b82f6; }
  .exec-summary { border-left-color: #3b82f6; }
  .fin-section, .exec-summary, .peer-wrap { box-shadow: none; }
  .num.pos { color: #059669 !important; }
  .num.neg { color: #dc2626 !important; }
  .fin-table { font-size: 0.72rem; }
  .fin-table thead th { color: #475569; }
  .fin-kpi { background: #e8edf6; }
  .fin-kpi .val { font-size: 0.92rem; }
  .mkt-panel { background: #f0f4fa; }
  .mkt-card { border-bottom-color: #d0d9e8; }
  .mkt-card .val { color: #0f172a; }
  .bench-list li { color: #0f172a; }
  .bench-above_q3 { color: #059669 !important; background: transparent !important; }
  .bench-q2_q3 { color: #2563eb !important; background: transparent !important; }
  .bench-q1_q2 { color: #d97706 !important; background: transparent !important; }
  .bench-below_q1 { color: #dc2626 !important; background: transparent !important; }
  .matrix-fill { animation: none !important; }
}
"""

CIT_JS_V3 = """
function toggleTheme() {
  var b = document.body;
  b.dataset.theme = b.dataset.theme === 'dark' ? 'light' : 'dark';
  localStorage.setItem('cit-theme', b.dataset.theme);
}
function copyInsight() {
  var el = document.getElementById('insight-text');
  if (!el) return;
  navigator.clipboard.writeText(el.innerText).then(function() {
    var btn = document.getElementById('copy-btn');
    if (!btn) return;
    btn.textContent = 'Copied!';
    btn.classList.add('ok');
    setTimeout(function() { btn.textContent = 'Copy insight'; btn.classList.remove('ok'); }, 2000);
  });
}
function filterGaps(sev) {
  document.querySelectorAll('.gap-filters .btn').forEach(function(b) {
    b.classList.toggle('active', b.dataset.filter === sev);
  });
  document.querySelectorAll('.gap-card').forEach(function(card) {
    var s = card.dataset.severity || '';
    card.classList.toggle('hidden', sev !== 'all' && s !== sev);
  });
}
(function init() {
  var saved = localStorage.getItem('cit-theme');
  if (saved) document.body.dataset.theme = saved;
  filterGaps('all');
  // Scroll-triggered fade-in
  if ('IntersectionObserver' in window) {
    var els = document.querySelectorAll('.fade-in');
    var observer = new IntersectionObserver(function(entries) {
      entries.forEach(function(e) {
        if (e.isIntersecting) { e.target.classList.add('visible'); observer.unobserve(e.target); }
      });
    }, { threshold: 0.1 });
    els.forEach(function(el) { observer.observe(el); });
    // Manually show elements already in view
    setTimeout(function() { els.forEach(function(el) {
      var rect = el.getBoundingClientRect();
      if (rect.top < window.innerHeight) el.classList.add('visible');
    }); }, 50);
  } else { document.querySelectorAll('.fade-in').forEach(function(e) { e.classList.add('visible'); }); }
})();
"""

SEVERITY_COLORS = {"high": "#ef4444", "medium": "#f59e0b", "low": "#22c55e"}

QUALITY_PCT = {"rich": 90, "moderate": 55, "sparse": 25}
CONFIDENCE_PCT = {"high": 85, "medium": 55, "low": 30}

# Backward-compat aliases
CIT_CSS = CIT_CSS_V3
CIT_JS = CIT_JS_V3

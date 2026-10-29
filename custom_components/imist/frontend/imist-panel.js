// iMist sidebar panel. No dependencies, no build step.
// Home Assistant passes: hass (states, services, websocket), narrow, panel.config.entry_id.

const COLORS = [
  ["white", "#ffffff"], ["red", "#ff2a2a"], ["yellow", "#ffd400"], ["green", "#1fd14b"],
  ["light_blue", "#2cc6ff"], ["dark_blue", "#2b4bff"], ["pink", "#ff3fb4"], ["warm_white", "#ffe9cf"],
];
const MIST = ["off", "continuous", "interval"];
const LIGHT_SWATCH = new Set(["white", "warm_white", "yellow"]);

const TEXT = {
  en: {
    sidebar: "Diffuser", title: "Aroma diffuser", connected: "Connected", disconnected: "Not connected",
    banner_off: "The diffuser is not connected right now{err}. You can still set the timer and schedules.",
    banner_ws: "This page cannot reach the integration: {err}",
    unknown: "Unknown", light_off: "Light off", light: "Light", mist: "Mist",
    mist_state: { off: "Mist off", continuous: "Continuous mist", interval: "Interval mist" },
    mist_label: { off: "Off", continuous: "Continuous", interval: "Interval" },
    colors: { white: "White", red: "Red", yellow: "Yellow", green: "Green", light_blue: "Light blue", dark_blue: "Dark blue", pink: "Pink", warm_white: "Warm white", off: "Off" },
    timer: "Switch off in …", min: "min", h: "h", timer_text: "Switches off at {time} ({rest} min left)", timer_cancel: "Cancel timer",
    schedules: "Schedules", none: "No schedule yet.", add: "+ Add schedule", days: ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
    daily: "Daily", weekdays: "Mon–Fri", weekend: "Sat, Sun", day_label: "Days", on_at: "Switch on", off_at: "Switch off",
    save: "Save schedule", cancel: "Cancel", delete: "Delete schedule", deleted: "Schedule deleted", undo: "Undo",
    edit: "Edit schedule {a} to {b}", active: "active", paused: "paused",
    diag: "Device and diagnostics", signal: "Signal", last: "Last report", since: "Connected since",
    drops: "Disconnects (24 h)", error: "Last error", address: "Address", version: "Integration",
    ago: "{s} s ago", good: "good", fair: "fair", weak: "weak", copy: "Copy diagnostics", copied: "copied",
    copy_fail: "Copying is blocked – download diagnostics from the device page instead",
    failed: "That did not work: {err}", footer: "You can hide this page in the integration options. Timer and schedules keep running.",
  },
  de: {
    sidebar: "Diffusor", title: "Aroma-Diffusor", connected: "Verbunden", disconnected: "Nicht verbunden",
    banner_off: "Das Gerät ist gerade nicht verbunden{err}. Timer und Zeitpläne lassen sich trotzdem einstellen.",
    banner_ws: "Die Seite erreicht die Integration nicht: {err}",
    unknown: "Unbekannt", light_off: "Licht aus", light: "Licht", mist: "Nebel",
    mist_state: { off: "Nebel aus", continuous: "Nebel durchgehend", interval: "Nebel im Intervall" },
    mist_label: { off: "Aus", continuous: "Dauer", interval: "Intervall" },
    colors: { white: "Weiß", red: "Rot", yellow: "Gelb", green: "Grün", light_blue: "Hellblau", dark_blue: "Dunkelblau", pink: "Pink", warm_white: "Warmweiß", off: "Aus" },
    timer: "Ausschalten in …", min: "Min.", h: "Std.", timer_text: "Geht um {time} Uhr aus (noch {rest} Min.)", timer_cancel: "Timer abbrechen",
    schedules: "Zeitpläne", none: "Noch kein Zeitplan.", add: "+ Zeitplan anlegen", days: ["Mo", "Di", "Mi", "Do", "Fr", "Sa", "So"],
    daily: "täglich", weekdays: "Mo–Fr", weekend: "Sa, So", day_label: "Tage", on_at: "Einschalten", off_at: "Ausschalten",
    save: "Zeitplan speichern", cancel: "Abbrechen", delete: "Zeitplan löschen", deleted: "Zeitplan gelöscht", undo: "Rückgängig",
    edit: "Zeitplan {a} bis {b} bearbeiten", active: "aktiv", paused: "pausiert",
    diag: "Gerät und Diagnose", signal: "Signal", last: "Letzte Meldung", since: "Verbunden seit",
    drops: "Abbrüche (24 h)", error: "Letzter Fehler", address: "Adresse", version: "Integration",
    ago: "vor {s} s", good: "gut", fair: "mittel", weak: "schwach", copy: "Diagnose kopieren", copied: "kopiert",
    copy_fail: "Kopieren nicht erlaubt – Diagnose auf der Geräteseite herunterladen",
    failed: "Hat nicht geklappt: {err}", footer: "Diese Seite lässt sich in den Optionen der Integration ausblenden. Timer und Zeitpläne laufen weiter.",
  },
};

const swatch = (key) => (COLORS.find((c) => c[0] === key) || [key, null])[1];
const esc = (s) => String(s).replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));
const fill = (s, v) => s.replace(/\{(\w+)\}/g, (_, k) => (v[k] ?? ""));

const STYLE = `
:host{display:block;min-height:100%;background:var(--primary-background-color);color:var(--primary-text-color);
  --card:var(--card-background-color,#fff);--ink:var(--primary-text-color);--quiet:var(--secondary-text-color);
  --line:var(--divider-color,#e1ddd5);--accent:var(--primary-color);--on-accent:var(--text-primary-color,#fff);
  --warn:var(--warning-color,#8a5a00);--ok:var(--success-color,#1f6b3a);--r:18px;--rs:12px;font-size:17px;line-height:1.45}
*{box-sizing:border-box}
[hidden]{display:none!important}
button,input{font:inherit;color:inherit}
.toolbar{display:flex;align-items:center;gap:4px;height:56px;padding:0 4px;background:var(--app-header-background-color);
  color:var(--app-header-text-color,#fff);font-size:20px}
.page{max-width:1080px;margin:0 auto;padding:16px 16px 48px}
.grid{display:grid;gap:16px;grid-template-columns:minmax(0,1fr)}
@media (min-width:900px){.grid{grid-template-columns:minmax(0,1fr) minmax(0,1fr)}}
.col{display:grid;gap:16px;align-content:start}
.card{background:var(--card);border-radius:var(--r);box-shadow:var(--ha-card-box-shadow,0 2px 10px rgba(0,0,0,.08));padding:18px}
h2{font-size:19px;margin:0 0 14px}
.quiet{color:var(--quiet)}
.head{display:flex;align-items:center;justify-content:space-between;gap:12px;margin:0 0 16px;flex-wrap:wrap}
.head h1{font-size:22px;margin:0}
.conn{display:inline-flex;align-items:center;gap:8px;font-size:16px}
.dot{width:12px;height:12px;border-radius:50%;background:var(--ok);flex:none}
.conn.off .dot{background:transparent;border:2px solid var(--warn)}
.banner{margin:0 0 16px;padding:12px 14px;border-radius:var(--rs);border:2px solid var(--warn)}
.hero{display:grid;grid-template-columns:120px minmax(0,1fr);gap:18px;align-items:center}
.hero svg{width:120px;height:170px;display:block}
.state{font-size:26px;font-weight:650;line-height:1.2;overflow-wrap:anywhere}
.state small{display:block;font-size:17px;font-weight:400;margin-top:6px}
.vapor{opacity:0}
.on .vapor{opacity:.85;animation:rise 3.2s ease-in-out infinite}
.interval .vapor{opacity:.85;animation:rise 3.2s ease-in-out infinite,pause 9s steps(1) infinite}
@keyframes rise{0%{transform:translateY(8px)}50%{transform:translateY(-4px)}100%{transform:translateY(8px)}}
@keyframes pause{0%{opacity:.85}55%{opacity:0}}
@media (prefers-reduced-motion:reduce){.vapor{animation:none!important}}
.colors{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:10px}
.color{display:flex;flex-direction:column;align-items:center;gap:6px;min-height:92px;padding:10px 4px;background:transparent;
  border:2px solid var(--line);border-radius:var(--rs);cursor:pointer;transition:transform .08s}
.color:active,.seg:active,.chip:active,.btn:active,.day:active{transform:scale(.96)}
.color .ball{width:44px;height:44px;border-radius:50%;border:1px solid rgba(0,0,0,.18);display:grid;place-items:center}
.color[aria-pressed="true"]{border-color:var(--ink);border-width:3px;padding:9px 3px}
.color .tick{opacity:0;width:22px;height:22px}
.color[aria-pressed="true"] .tick{opacity:1}
.color .name{font-size:15px;max-width:100%;overflow-wrap:anywhere;hyphens:auto;text-align:center;line-height:1.2}
.segments{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:8px}
.seg{min-height:64px;border-radius:var(--rs);border:2px solid var(--line);background:transparent;display:flex;flex-direction:column;
  align-items:center;justify-content:center;gap:2px;cursor:pointer;transition:transform .08s;overflow-wrap:anywhere;text-align:center;padding:4px}
.seg svg{width:26px;height:22px}
.seg[aria-pressed="true"],.chip[aria-pressed="true"],.day[aria-pressed="true"]{background:var(--accent);color:var(--on-accent);border-color:var(--accent);font-weight:650}
button[disabled]{opacity:.45;cursor:not-allowed}
.chips{display:flex;flex-wrap:wrap;gap:8px}
.chip{min-height:48px;padding:0 18px;border-radius:999px;border:2px solid var(--line);background:transparent;cursor:pointer}
.note{margin:12px 0 0;padding:12px 14px;border-radius:var(--rs);background:color-mix(in srgb,var(--accent) 12%,transparent);
  display:flex;justify-content:space-between;align-items:center;gap:12px;flex-wrap:wrap}
.btn{min-height:48px;padding:0 18px;border-radius:var(--rs);border:2px solid var(--accent);background:var(--accent);color:var(--on-accent);font-weight:600;cursor:pointer}
.btn.alt{background:transparent;color:var(--accent)}
.btn.danger{background:transparent;color:var(--error-color,#b3261e);border-color:var(--error-color,#b3261e)}
.plan{display:grid;grid-template-columns:minmax(0,1fr) auto;gap:6px 12px;align-items:center;padding:14px 0;border-top:1px solid var(--line)}
.plan:first-child{border-top:0;padding-top:0}
.plan .text{background:none;border:0;padding:0;text-align:left;cursor:pointer;min-height:48px}
.plan .time{font-size:20px;font-weight:650;font-variant-numeric:tabular-nums}
.plan .what{display:flex;align-items:center;gap:4px 14px;flex-wrap:wrap}
.pair{display:inline-flex;align-items:center;gap:6px}
.mini{width:16px;height:16px;border-radius:50%;border:1px solid rgba(0,0,0,.2);flex:none}
.switch{position:relative;width:66px;height:48px;border:0;background:transparent;cursor:pointer;padding:0}
.switch::before{content:"";position:absolute;left:4px;top:7px;width:58px;height:34px;border-radius:999px;border:2px solid var(--quiet);box-sizing:border-box}
.switch::after{content:"";position:absolute;top:12px;left:9px;width:24px;height:24px;border-radius:50%;background:var(--quiet);transition:left .15s}
.switch[aria-checked="true"]::before{background:var(--accent);border-color:var(--accent)}
.switch[aria-checked="true"]::after{left:33px;background:var(--on-accent)}
.editor{border-top:1px solid var(--line);margin-top:6px;padding-top:16px;display:grid;gap:14px}
.editor label{display:grid;gap:6px;font-size:16px}
.sub{font-size:16px;margin-bottom:6px}
.days{display:grid;grid-template-columns:repeat(auto-fill,minmax(52px,1fr));gap:6px}
.day{min-height:48px;border-radius:var(--rs);border:2px solid var(--line);background:transparent;cursor:pointer;font-size:15px}
.times{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:10px}
input[type=time]{min-height:48px;border:2px solid var(--line);border-radius:var(--rs);background:var(--card);padding:0 10px;width:100%}
.swatches{display:flex;flex-wrap:wrap;gap:8px}
.swatches button{width:48px;height:48px;border-radius:50%;border:2px solid var(--line);cursor:pointer;padding:0;display:grid;place-items:center}
.swatches button[aria-pressed="true"]{outline:3px solid var(--ink);outline-offset:2px}
.row{display:flex;gap:10px;flex-wrap:wrap}
.err{color:var(--error-color,#b3261e)}
details summary{cursor:pointer;min-height:48px;display:flex;align-items:center;font-size:19px;font-weight:600;list-style:none}
details summary::-webkit-details-marker{display:none}
details summary::after{content:"▸";margin-left:auto;transition:transform .15s}
details[open] summary::after{transform:rotate(90deg)}
dl{display:grid;grid-template-columns:auto minmax(0,1fr);gap:8px 16px;margin:10px 0 16px}
dt{color:var(--quiet)} dd{margin:0;font-variant-numeric:tabular-nums;overflow-wrap:anywhere}
@media (max-width:480px){dl{grid-template-columns:minmax(0,1fr);gap:2px}dd{margin-bottom:10px}}
code{white-space:nowrap;font-family:ui-monospace,SFMono-Regular,Menlo,monospace;font-size:16px}
.toast{position:fixed;left:50%;bottom:calc(16px + env(safe-area-inset-bottom));transform:translateX(-50%);max-width:calc(100% - 32px);
  background:var(--ink);color:var(--card);border-radius:var(--rs);padding:10px 12px 10px 16px;display:flex;gap:12px;align-items:center;
  box-shadow:0 4px 18px rgba(0,0,0,.25);z-index:5}
.toast button{min-height:44px;background:transparent;border:2px solid currentColor;color:inherit;border-radius:10px;padding:0 12px;cursor:pointer;font-weight:600}
.footer{margin-top:20px;font-size:15px}
`;

const TICK = (dark) => `<svg class="tick" viewBox="0 0 24 24" fill="none" stroke="${dark ? "#1d1c1a" : "#fff"}" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12l5 5 9-10"/></svg>`;
const SLASH = '<svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round"><path d="M6 18L18 6"/></svg>';
const ICON = {
  off: '<svg viewBox="0 0 26 22" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round"><circle cx="13" cy="11" r="8"/><path d="M7 17L19 5"/></svg>',
  continuous: '<svg viewBox="0 0 26 22" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round"><path d="M3 6h20M3 11h20M3 16h20"/></svg>',
  interval: '<svg viewBox="0 0 26 22" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round"><path d="M3 6h6M15 6h8M3 11h6M15 11h8M3 16h6M15 16h8"/></svg>',
};

class ImistPanel extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: "open" });
    this._status = null;
    this._editing = null; // index of the schedule in the editor, -1 = new
  }

  set hass(hass) {
    this._hass = hass;
    const lang = (hass.locale && hass.locale.language) || hass.language || "en";
    const t = lang.startsWith("de") ? TEXT.de : TEXT.en;
    if (t !== this._t) { this._t = t; this._lang = lang; this._built = false; }
    if (!this._built) this._build();
    if (!this._status && !this._firstLoad) { this._firstLoad = true; this._load(); }
    const mb = this.shadowRoot.querySelector("ha-menu-button");
    if (mb) { mb.hass = hass; mb.narrow = this.narrow; }
    this._render();
  }
  set narrow(n) { this._narrow = n; const mb = this.shadowRoot.querySelector("ha-menu-button"); if (mb) mb.narrow = n; }
  get narrow() { return this._narrow; }
  set panel(p) { this._panel = p; }
  get _entry() { return this._panel && this._panel.config && this._panel.config.entry_id; }

  connectedCallback() { this._tick = setInterval(() => this._load(), 2000); this._load(); }
  disconnectedCallback() { clearInterval(this._tick); }

  async _load() {
    if (!this._hass || !this._entry) return;
    try { this._status = await this._hass.callWS({ type: "imist/status", entry_id: this._entry }); this._wsError = null; }
    catch (e) { this._wsError = e.message || String(e); }
    this._render();
  }

  _clock(iso) { return new Date(iso).toLocaleTimeString(this._lang, { hour: "2-digit", minute: "2-digit" }); }

  _build() {
    this._built = true; this._schedulesKey = null;
    const t = this._t, r = this.shadowRoot;
    r.innerHTML = `<style>${STYLE}</style>
      <div class="toolbar"><ha-menu-button></ha-menu-button><span>${t.sidebar}</span></div>
      <main class="page">
        <header class="head"><h1>${t.title}</h1><span class="conn" id="conn"><span class="dot"></span><span id="connText">…</span></span></header>
        <p class="banner" id="banner" hidden></p>
        <div class="grid"><div class="col">
          <section class="card hero" id="hero" aria-live="polite">
            <svg viewBox="0 0 120 170" aria-hidden="true">
              <defs><radialGradient id="glow" cx="50%" cy="55%" r="60%">
                <stop offset="0%" id="g1" stop-color="#000" stop-opacity="0"/><stop offset="100%" id="g2" stop-color="#000" stop-opacity="0"/></radialGradient></defs>
              <g class="vapor" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round">
                <path d="M50 30c-6-8 6-12 0-20"/><path d="M62 32c-6-9 7-13 0-24"/><path d="M74 30c-6-8 6-12 0-20"/></g>
              <ellipse cx="60" cy="100" rx="58" ry="62" fill="url(#glow)"/>
              <rect x="30" y="42" width="60" height="98" rx="14" fill="#fbfaf7" opacity=".72" stroke="currentColor" stroke-opacity=".35"/>
              <g stroke="currentColor" stroke-opacity=".18"><path d="M40 46v90M48 44v94M56 43v96M64 43v96M72 44v94M80 46v90"/></g>
              <rect x="30" y="134" width="60" height="18" rx="5" fill="#f2efe9" stroke="currentColor" stroke-opacity=".35"/>
            </svg>
            <div class="state"><span id="sLight">…</span><small class="quiet" id="sMist"></small></div>
          </section>
          <section class="card"><h2>${t.light}</h2><div class="colors" id="colors"></div></section>
          <section class="card"><h2>${t.mist}</h2><div class="segments" id="mist"></div></section>
        </div><div class="col">
          <section class="card"><h2>${t.timer}</h2><div class="chips" id="timer"></div>
            <div class="note" id="timerNote" hidden><span id="timerText"></span><button class="btn alt" id="timerCancel">${t.timer_cancel}</button></div></section>
          <section class="card"><h2>${t.schedules}</h2><div id="plans"></div>
            <p class="quiet" id="noPlans" hidden>${t.none}</p>
            <button class="btn alt" id="planAdd" style="margin-top:12px;width:100%">${t.add}</button>
            <div class="editor" id="editor" hidden></div></section>
          <section class="card"><details><summary>${t.diag}</summary><dl id="diag"></dl>
            <button class="btn alt" id="copy">${t.copy}</button> <span class="quiet" id="copied"></span></details></section>
        </div></div>
        <p class="footer quiet">${t.footer}</p>
      </main>
      <div class="toast" id="toast" hidden><span id="toastText"></span><button id="toastBtn" hidden></button></div>`;

    const colors = r.getElementById("colors");
    for (const [key, hex] of [...COLORS, ["off", null]]) {
      const b = document.createElement("button");
      b.className = "color"; b.dataset.key = key;
      b.innerHTML = hex
        ? `<span class="ball" style="background:${hex}">${TICK(LIGHT_SWATCH.has(key))}</span><span class="name">${t.colors[key]}</span>`
        : `<span class="ball" style="background:transparent;border:2px dashed currentColor">${SLASH}</span><span class="name">${t.colors.off}</span>`;
      b.onclick = () => this._light(key);
      colors.appendChild(b);
    }
    const mist = r.getElementById("mist");
    for (const m of MIST) {
      const b = document.createElement("button");
      b.className = "seg"; b.dataset.key = m; b.innerHTML = ICON[m] + t.mist_label[m];
      b.onclick = () => this._service("select", "select_option", { entity_id: this._status.mist_entity, option: m });
      mist.appendChild(b);
    }
    r.getElementById("timerCancel").onclick = () => this._timer(null);
    r.getElementById("planAdd").onclick = () => this._edit(-1);
    r.getElementById("copy").onclick = () => this._copy();
  }

  _state(eid) { return eid && this._hass && this._hass.states[eid]; }

  _render() {
    if (!this._built) return;
    const t = this._t, r = this.shadowRoot, S = this._status;
    const light = this._state(S && S.light_entity), mist = this._state(S && S.mist_entity);
    const up = S && S.connected && light && light.state !== "unavailable";
    r.getElementById("conn").classList.toggle("off", !up);
    r.getElementById("connText").textContent = up ? t.connected : t.disconnected;
    const banner = r.getElementById("banner");
    banner.hidden = !!up;
    if (!up) banner.textContent = this._wsError ? fill(t.banner_ws, { err: this._wsError })
      : fill(t.banner_off, { err: S && S.last_error ? ` (${S.last_error})` : "" });

    const key = light && light.state === "on" ? light.attributes.effect : light && light.state === "off" ? "off" : null;
    r.querySelectorAll(".color").forEach((b) => { b.setAttribute("aria-pressed", b.dataset.key === key); b.disabled = !up; });
    const m = mist ? mist.state : null;
    r.querySelectorAll(".seg").forEach((b) => { b.setAttribute("aria-pressed", b.dataset.key === m); b.disabled = !up; });
    const hex = key && key !== "off" ? swatch(key) : null;
    r.getElementById("g1").setAttribute("stop-color", hex || "#000"); r.getElementById("g1").setAttribute("stop-opacity", hex ? 0.95 : 0);
    r.getElementById("g2").setAttribute("stop-color", hex || "#000");
    const hero = r.getElementById("hero");
    hero.classList.toggle("on", up && m === "continuous"); hero.classList.toggle("interval", up && m === "interval");
    r.getElementById("sLight").textContent = !up ? t.unknown : key === "off" ? t.light_off : (t.colors[key] || "…");
    r.getElementById("sMist").textContent = up ? t.mist_state[m] || "" : "";

    if (!S) return;
    const timer = r.getElementById("timer");
    if (!timer.childElementCount) for (const min of S.timer_minutes) {
      const b = document.createElement("button");
      b.className = "chip"; b.textContent = min < 60 ? `${min} ${t.min}` : `${min / 60} ${t.h}`;
      b.onclick = () => this._timer(min); timer.appendChild(b);
    }
    const end = S.timer_end;
    r.getElementById("timerNote").hidden = !end;
    if (end) r.getElementById("timerText").textContent = fill(t.timer_text, { time: this._clock(end), rest: Math.max(0, Math.round((new Date(end) - Date.now()) / 60000)) });

    if (this._editing === null) this._renderPlans();
    this._renderDiag();
  }

  _dayText(days) {
    const t = this._t, d = days.join();
    return days.length === 7 ? t.daily : d === "0,1,2,3,4" ? t.weekdays : d === "5,6" ? t.weekend : days.map((i) => t.days[i]).join(", ");
  }

  _renderPlans() {
    const t = this._t, r = this.shadowRoot, list = r.getElementById("plans"), plans = this._status.schedules;
    r.getElementById("noPlans").hidden = plans.length > 0;
    const k = JSON.stringify(plans);
    if (k === this._schedulesKey) return;
    this._schedulesKey = k;
    list.innerHTML = "";
    plans.forEach((p, i) => {
      const row = document.createElement("div"); row.className = "plan";
      const hex = swatch(p.light);
      row.innerHTML = `<button class="text" aria-label="${esc(fill(t.edit, { a: p.start, b: p.end }))}">
          <div class="time">${esc(p.start)} – ${esc(p.end)}</div>
          <div class="what quiet"><span>${esc(this._dayText(p.days))}</span><span class="pair">${hex ? `<span class="mini" style="background:${hex}"></span>` : ""}${esc(p.light === "off" ? t.light_off : t.colors[p.light])}</span><span>${esc(t.mist_state[p.mist])}</span></div></button>
        <button class="switch" role="switch" aria-checked="${p.enabled}" aria-label="${esc(p.start)}–${esc(p.end)} ${p.enabled ? t.active : t.paused}"></button>`;
      row.querySelector(".text").onclick = () => this._edit(i);
      row.querySelector(".switch").onclick = () => this._sendPlans(plans.map((x, j) => (j === i ? { ...x, enabled: !x.enabled } : x)));
      list.appendChild(row);
    });
  }

  _edit(i) {
    const t = this._t, r = this.shadowRoot, ed = r.getElementById("editor");
    this._editing = i;
    const src = i >= 0 ? this._status.schedules[i] : { days: [0, 1, 2, 3, 4], start: "07:00", end: "07:30", light: "dark_blue", mist: "interval", enabled: true };
    const e = { ...src, days: [...src.days] };
    for (const id of ["planAdd", "plans", "noPlans"]) r.getElementById(id).hidden = true;
    ed.hidden = false;
    ed.innerHTML = `
      <div><div class="quiet sub">${t.day_label}</div><div class="days" id="eDays"></div></div>
      <div class="times"><label>${t.on_at}<input type="time" id="eStart" value="${esc(e.start)}"></label>
        <label>${t.off_at}<input type="time" id="eEnd" value="${esc(e.end)}"></label></div>
      <div><div class="quiet sub">${t.light}</div><div class="swatches" id="eColors"></div></div>
      <div><div class="quiet sub">${t.mist}</div><div class="chips" id="eMist"></div></div>
      <p class="err" id="eErr" hidden></p>
      <div class="row"><button class="btn" id="eSave">${t.save}</button><button class="btn alt" id="eCancel">${t.cancel}</button>
        ${i >= 0 ? `<button class="btn danger" id="eDelete">${t.delete}</button>` : ""}</div>`;
    t.days.forEach((label, j) => {
      const b = document.createElement("button"); b.className = "day"; b.textContent = label;
      b.setAttribute("aria-pressed", e.days.includes(j));
      b.onclick = () => { e.days = e.days.includes(j) ? e.days.filter((x) => x !== j) : [...e.days, j].sort(); b.setAttribute("aria-pressed", e.days.includes(j)); };
      ed.querySelector("#eDays").appendChild(b);
    });
    for (const [key, hex] of [...COLORS, ["off", null]]) {
      const b = document.createElement("button");
      const label = key === "off" ? t.light_off : t.colors[key];
      b.setAttribute("aria-label", label); b.title = label;
      b.style.background = hex || "transparent"; if (!hex) b.innerHTML = SLASH;
      b.setAttribute("aria-pressed", e.light === key);
      b.onclick = () => { e.light = key; ed.querySelectorAll("#eColors button").forEach((x) => x.setAttribute("aria-pressed", x === b)); };
      ed.querySelector("#eColors").appendChild(b);
    }
    for (const m of MIST) {
      const b = document.createElement("button"); b.className = "chip"; b.textContent = t.mist_label[m];
      b.setAttribute("aria-pressed", e.mist === m);
      b.onclick = () => { e.mist = m; ed.querySelectorAll("#eMist .chip").forEach((x) => x.setAttribute("aria-pressed", x === b)); };
      ed.querySelector("#eMist").appendChild(b);
    }
    ed.querySelector("#eCancel").onclick = () => this._closeEditor();
    ed.querySelector("#eSave").onclick = async () => {
      e.start = ed.querySelector("#eStart").value; e.end = ed.querySelector("#eEnd").value;
      const plans = [...this._status.schedules];
      if (i >= 0) plans[i] = e; else plans.push(e);
      const err = await this._sendPlans(plans);
      if (err) { const p = ed.querySelector("#eErr"); p.hidden = false; p.textContent = err; } else this._closeEditor();
    };
    const del = ed.querySelector("#eDelete");
    if (del) del.onclick = async () => {
      const before = [...this._status.schedules];
      if (!(await this._sendPlans(before.filter((_, j) => j !== i)))) {
        this._closeEditor();
        this._toast(t.deleted, t.undo, () => this._sendPlans(before));
      }
    };
    ed.querySelector("#eStart").focus();
  }

  _closeEditor() {
    const r = this.shadowRoot;
    this._editing = null; this._schedulesKey = null;
    r.getElementById("editor").hidden = true; r.getElementById("editor").innerHTML = "";
    r.getElementById("planAdd").hidden = false; r.getElementById("plans").hidden = false;
    this._render();
  }

  _renderDiag() {
    const t = this._t, S = this._status, r = this.shadowRoot;
    const rssi = S.rssi == null ? t.unknown : `${String(S.rssi).replace("-", "−")} dBm · ${S.rssi >= -65 ? t.good : S.rssi >= -80 ? t.fair : t.weak}`;
    const last = S.last_report_s == null ? "–" : `${fill(t.ago, { s: S.last_report_s.toLocaleString(this._lang) })} · <code>${esc(S.raw)}</code>`;
    r.getElementById("diag").innerHTML = `
      <dt>${t.signal}</dt><dd>${rssi}</dd><dt>${t.last}</dt><dd>${last}</dd>
      <dt>${t.since}</dt><dd>${S.connected_since ? this._clock(S.connected_since) : "–"}</dd><dt>${t.drops}</dt><dd>${S.disconnects_24h}</dd>
      ${S.last_error ? `<dt>${t.error}</dt><dd>${esc(S.last_error)}</dd>` : ""}
      <dt>${t.address}</dt><dd><code>${esc(S.address)}</code></dd><dt>${t.version}</dt><dd>${esc(S.version)}</dd>`;
  }

  _light(key) {
    if (key === "off") return this._service("light", "turn_off", { entity_id: this._status.light_entity });
    return this._service("light", "turn_on", { entity_id: this._status.light_entity, effect: key });
  }

  async _service(domain, service, data) {
    try { await this._hass.callService(domain, service, data); }
    catch (e) { this._toast(fill(this._t.failed, { err: e.message || e })); }
  }

  async _timer(minutes) {
    try { this._status = await this._hass.callWS({ type: "imist/timer", entry_id: this._entry, minutes }); this._render(); }
    catch (e) { this._toast(fill(this._t.failed, { err: e.message || e })); }
  }

  async _sendPlans(schedules) {
    try {
      this._status = await this._hass.callWS({ type: "imist/schedules", entry_id: this._entry, schedules });
      this._schedulesKey = null; this._render(); return null;
    } catch (e) { return e.message || String(e); }
  }

  _toast(text, button, action) {
    const r = this.shadowRoot, box = r.getElementById("toast"), btn = r.getElementById("toastBtn");
    r.getElementById("toastText").textContent = text;
    btn.hidden = !button; btn.textContent = button || "";
    btn.onclick = () => { box.hidden = true; action && action(); };
    box.hidden = false; clearTimeout(this._toastTimer);
    this._toastTimer = setTimeout(() => (box.hidden = true), button ? 8000 : 5000);
  }

  async _copy() {
    const data = { ...this._status, address: (this._status.address || "").slice(0, 8) + ":xx:xx:xx" };
    const out = this.shadowRoot.getElementById("copied");
    try { await navigator.clipboard.writeText(JSON.stringify(data, null, 2)); out.textContent = this._t.copied; }
    catch { out.textContent = this._t.copy_fail; }
    setTimeout(() => (out.textContent = ""), 4000);
  }
}

customElements.define("imist-panel", ImistPanel);

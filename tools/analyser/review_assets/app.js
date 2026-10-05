// Review page v3 (tools/analyser/review.py). One screen: a top bar, the score
// canvas, a findings rail and an inspector dock that shows one finding at a
// time. Readings are drawn into the score in red; the editor keeps or takes
// one, or edits the lyrics in place, Sibelius-style. Decisions and edits are
// documents in the artifact's db (collection "edits") when the page has one,
// kept in this browser otherwise, and can be copied as JSON for
// `python -m tools.analyser edits apply`. See docs/analyser.md.
(function () {
  "use strict";
  var D = JSON.parse(document.getElementById("data").textContent);
  var SVGNS = "http://www.w3.org/2000/svg";
  var REC = "Claude's recommendation:";
  var $ = function (id) { return document.getElementById(id); };
  var app = $("app"), canvas = $("canvas"), paper = $("paper"), dock = $("dock"), rows = $("rows");
  var pages = paper.querySelectorAll("svg.score-page");
  var reduce = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  var narrow = function () { return window.innerWidth < 1000; };
  var LS = "pol-ren-review:" + D.slug;
  var LETTERS = ["Current", "A", "B", "C", "D"];
  var LEVELS = { "break": 0, warn: 1, look: 2, info: 3 };
  var LAYERS = [
    ["cad", "Cadences", "Rings at the arrivals; a diamond under the system. Hover for type and tone."],
    ["dis", "Dissonance", "Labels above notes: S suspension (arc to its resolution), p passing, n neighbour, c cambiata, a anticipation."],
    ["phr", "Phrases", "A bracket under each staff from a phrase's first note to its last; red where it ends at a cadence."],
    ["imi", "Imitation", "A bracket over each entry's head notes; hover for the point."],
    ["hom", "Homorhythm", "A tint over passages where the voices move together."],
    ["tac", "Against the tactus", "A short line over each note that plays against the tactus."],
    ["kw", "Key words", "A line under the key words' syllables; dashed if only proposed."]
  ];

  function esc(s) {
    return String(s == null ? "" : s).replace(/[&<>"]/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c];
    });
  }
  function each(sel, fn, root) { Array.prototype.forEach.call((root || document).querySelectorAll(sel), fn); }
  function q(t) { return "‘" + String(t || "").replace(/[,.;:!?]+$/, "") + "’"; }

  // ---------------------------------------------------------------- prefs (browser only, a convenience)
  var store = {};
  try { store = JSON.parse(window.localStorage.getItem(LS) || "{}") || {}; } catch (e) { store = {}; }
  function persist() {
    try { window.localStorage.setItem(LS, JSON.stringify(store)); } catch (e) { /* storage off: the page still works */ }
  }
  var prefs = store.prefs || (store.prefs = {});

  // ---------------------------------------------------------------- notes, voices
  var vidx = {};
  D.parts.forEach(function (v) { var m = {}; D.vnotes[v].forEach(function (id, i) { m[id] = i; }); vidx[v] = m; });
  var byNote = {};
  each(".nh", function (g) {
    g.getAttribute("data-n").split(" ").forEach(function (id) { (byNote[id] = byNote[id] || []).push(g); });
  }, paper);
  function voiceOf(id) { return id.split(":")[0]; }
  function verseName(v) { return (D.verseNames && D.verseNames[v]) || (Object.keys(D.verses).some(function (p) { return D.verses[p].length > 1; }) ? "Verse " + v : ""); }

  // ---------------------------------------------------------------- edits and the store
  var edits = store.edits || {};          // id -> doc, this view's
  var saved = {};                         // id -> doc, the db's
  var db = null, me = null, dbState = "local";
  // Claude's recommendations committed with the page: suggestions until decided
  (D.seed || []).forEach(function (d) {
    if (!edits[d.id]) { var c = JSON.parse(JSON.stringify(d)); c._seed = true; edits[d.id] = c; }
  });
  function isSugg(d) { return !!d && d.status !== "declined" && String(d.reason || "").indexOf(REC) === 0; }
  function isMine(d) { return !!d && !isSugg(d); }
  function clean(d) {
    var o = {};
    Object.keys(d).forEach(function (k) { if (k.charAt(0) !== "_") o[k] = d[k]; });
    return JSON.parse(JSON.stringify(o));
  }
  function same(a, b) { return a && b && a.updatedAt === b.updatedAt && JSON.stringify(a.notes) === JSON.stringify(b.notes); }
  function saveLocal() {
    var o = {};
    Object.keys(edits).forEach(function (k) { if (!edits[k]._seed) o[k] = clean(edits[k]); });
    store.edits = o;
    persist();
  }
  function safeId(s) {
    return String(s).normalize("NFD").replace(/[̀-ͯ]/g, "").replace(/[^A-Za-z0-9_\-.~:@+]+/g, "-")
      .replace(/^-+|-+$/g, "").slice(0, 190);
  }
  function findingId(f) { return safeId(D.slug + "__" + f.fingerprint.split("|").slice(1).join("-")); }
  function customId(voice, verse, bar) { return safeId(D.slug + "__" + voice + "-v" + verse + "-b" + bar); }
  function noteRec(id, syl, sb) {
    var e = D.ed[id], n = D.notes[id];
    return { id: id, bar: e[0], pos: e[1], pitch: n[1], where: n[0], syllable: syl || null, syllabic: syl ? (sb || "single") : null };
  }

  function put(doc) {
    doc.updatedAt = new Date().toISOString();
    doc.by = me;
    delete doc._seed;
    edits[doc.id] = doc;
    saveLocal();
    if (db) {
      setSave();
      db.collection("edits").doc(doc.id).set(clean(doc)).then(function () { setSave(); }, function (err) {
        dbState = "error"; setSave((err && err.code) || "error");
      });
    }
    refresh();
  }
  function withdraw(id) {
    delete edits[id];
    saveLocal();
    if (db) db.collection("edits").doc(id).delete().then(function () { setSave(); }, function () { /* already gone */ });
    refresh();
  }
  function pending() {
    return Object.keys(edits).filter(function (k) { return !edits[k]._seed && !same(edits[k], saved[k]); }).length;
  }
  function setSave(err) {
    var el = $("save"), lab = el.querySelector(".save-l");
    var n = Object.keys(edits).filter(function (k) { return !edits[k]._seed; }).length;
    var cls = "", txt = "Local only", tip;
    if (dbState === "on") {
      var p = pending();
      cls = p ? "busy" : "on"; txt = p ? "Saving" : "Saved";
      tip = p ? "Saving " + p + " change" + (p > 1 ? "s" : "") + " to the page's shared store" : "Every decision is saved to the page's shared store, where Claude can read it.";
    } else if (dbState === "error") {
      cls = "err"; txt = "Not saved";
      tip = "The shared store refused (" + (err || "error") + "). Use ⋯ › Copy edits as JSON and paste them into the chat.";
    } else {
      tip = "No shared store here (a local copy, or signed out): " + n + " edit" + (n === 1 ? "" : "s") + " kept in this browser. Use ⋯ › Copy edits as JSON.";
    }
    el.className = "save " + cls; lab.textContent = txt; el.title = tip; el.setAttribute("aria-label", txt + ". " + tip);
  }

  // ---------------------------------------------------------------- findings
  var F = D.findings;
  F.forEach(function (f) { f.vo = D.parts.indexOf(f.voice); });
  function tracked(f) { return f.status === "pending" || f.status === "new"; }
  function docOf(f) {
    var id = findingId(f), d = edits[id];
    if (d && d.finding === f.fingerprint) return d;
    for (var k in edits) if (edits[k].finding === f.fingerprint) return edits[k];
    return null;
  }
  function decision(f) { var d = docOf(f); return isMine(d) ? d : null; }
  function suggestion(f) { var d = docOf(f); return isSugg(d) ? d : null; }
  // custom suggestions (no finding): items of their own in the rail
  function customSuggs() {
    return Object.keys(edits).map(function (k) { return edits[k]; }).filter(function (d) {
      return d.kind === "custom" && !d.finding && (isSugg(d) || d.recommendation) && D.vnotes[d.voice];
    });
  }
  function item(key) {
    if (key == null) return null;
    if (typeof key === "number") return F[key] ? { type: "f", f: F[key], key: key } : null;
    var d = edits[key];
    return d ? { type: "s", d: d, key: key } : null;
  }
  function itemT(it) { return it.type === "f" ? it.f.t : (D.on[it.d.notes[0] && it.d.notes[0].id] || 0); }
  function itemVo(it) { return D.parts.indexOf(it.type === "f" ? it.f.voice : it.d.voice); }
  function decided(it) {
    if (it.type === "f") return !!decision(it.f);
    return !isSugg(it.d);
  }

  var filt = prefs.filt || { voices: {}, levels: { info: false } };
  function shown(f) {
    if (filt.voices[f.voice] === false) return false;
    if (filt.levels[f.level] === false) return false;
    return true;
  }
  function ordered(list) {
    return list.sort(function (a, b) { return (itemT(a) - itemT(b)) || (itemVo(a) - itemVo(b)); });
  }
  function groups() {
    var todo = [], done = [], acc = [];
    F.forEach(function (f, n) {
      if (!shown(f)) return;
      var it = { type: "f", f: f, key: n };
      if (f.status === "accepted") acc.push(it);
      else if (decided(it)) done.push(it);
      else todo.push(it);
    });
    customSuggs().forEach(function (d) {
      if (filt.voices[d.voice] === false) return;
      var it = { type: "s", d: d, key: d.id };
      (decided(it) ? done : todo).push(it);
    });
    return { todo: ordered(todo), done: ordered(done), acc: ordered(acc) };
  }
  function navList() {
    var g = groups();
    var main = g.todo.concat(g.done);
    return main.concat(prefs.accOpen || !main.length ? g.acc : []);
  }

  // ---------------------------------------------------------------- state
  var cur = null;          // active item key: finding index or custom suggestion id
  var tab = 0;             // reading shown for the active item
  var whyOpen = !!prefs.why;
  var reasonOpen = false;
  var E = null;            // edit session
  var sel = null;          // selected note outside edit mode
  var undo = null;

  // ---------------------------------------------------------------- readings
  function baseOf(voice, verse) {
    return D.vnotes[voice].map(function (id) {
      var l = (D.ed[id][2] || {})[verse];
      return l ? [l[0], l[1]] : null;
    });
  }
  function readingsOf(voice, verse, opts) {
    opts = opts || {};
    var r = baseOf(voice, verse);
    var ix = vidx[voice];
    var docs = Object.keys(edits).map(function (k) { return edits[k]; }).filter(function (d) {
      return d.voice === voice && String(d.verse) === String(verse) && isMine(d) && d.status !== "declined";
    });
    function apply(d) {
      (d.notes || []).forEach(function (nt) {
        var i = ix[nt.id];
        if (i != null) r[i] = nt.syllable ? [nt.syllable, nt.syllabic || "single"] : null;
      });
    }
    var byT = function (a, b) { return (a.updatedAt || "") < (b.updatedAt || "") ? -1 : 1; };
    docs.filter(function (d) { return d.kind !== "custom"; }).sort(byT).forEach(apply);
    if (opts.custom !== false) docs.filter(function (d) { return d.kind === "custom"; }).sort(byT).forEach(apply);
    if (opts.preview !== false && !E) {
      var it = item(cur);
      if (it && tab > 0) {
        var pv = previewNotes(it, tab);
        if (pv && pv.voice === voice && String(pv.verse) === String(verse)) pv.notes.forEach(function (nt) {
          var i = ix[nt[0]];
          if (i != null) r[i] = nt[1] ? [nt[1], nt[2] || "single"] : null;
        });
      }
    }
    if (opts.session !== false && E && E.voice === voice && E.verse === verse) {
      Object.keys(E.ch).forEach(function (i) { r[i] = E.ch[i]; });
      if (E.buf) r[E.i] = [E.buf, provisional(r, E.i)];
    }
    return r;
  }
  function prevHy(r, i) {
    for (var j = i - 1; j >= 0; j--) if (r[j]) return r[j][1] === "begin" || r[j][1] === "middle";
    return false;
  }
  function provisional(r, i) { return prevHy(r, i) ? "end" : "single"; }

  // the notes a reading k of an item sets: {voice, verse, notes: [[id, syl, sb]]}
  function previewNotes(it, k) {
    if (it.type === "f") {
      var f = it.f;
      if (!f.pl.length || !f.pl[k]) return null;
      var at = {};
      f.pl[k].forEach(function (p) { at[p[0]] = p; });
      return { voice: f.voice, verse: f.verse, notes: f.span.map(function (id) { var p = at[id]; return p ? [id, p[1], p[2]] : [id, null, null]; }) };
    }
    var d = it.d;
    if (k !== 1) return null;
    return { voice: d.voice, verse: String(d.verse), notes: d.notes.map(function (n) { return [n.id, n.syllable, n.syllabic]; }) };
  }

  // ---------------------------------------------------------------- drawing
  function layerOf(page, cls) {
    var svg = pages[page];
    if (!svg) return null;
    var g = svg.querySelector("g." + cls);
    if (!g) { g = document.createElementNS(SVGNS, "g"); g.setAttribute("class", cls); svg.appendChild(g); }
    return g;
  }
  function el(L, name, attrs, text) {
    if (!L) return null;
    var t = document.createElementNS(SVGNS, name);
    Object.keys(attrs).forEach(function (k) { t.setAttribute(k, attrs[k]); });
    if (text != null) t.textContent = text;
    L.appendChild(t);
    return t;
  }
  function lyBase(id, voice, verse) {
    var s = D.nsys[id];
    var y = D.lyb[s + "|" + voice + "|" + verse];
    if (y != null) return y;
    var y1 = D.lyb[s + "|" + voice + "|1"];
    if (y1 != null) return y1 + 2.9 * (parseInt(verse, 10) - 1);
    var b = D.stb[s + "|" + voice];
    return b != null ? b + 4.4 + 2.9 * (parseInt(verse, 10) - 1) : null;
  }
  function origSyl(id, verse) { return paper.querySelector('.ly[data-n="' + id + '"][data-verse="' + verse + '"]'); }
  function boxOfOrig(id, verse) {
    var o = origSyl(id, verse), p = D.pos[id];
    if (!o || !p) return null;
    try { var bb = o.getBBox(); return { x0: bb.x, x1: bb.x + bb.width, y: bb.y + bb.height * 0.78, page: p[0], sys: D.nsys[id] }; }
    catch (e) { return null; }
  }
  function line(L, x0, x1, y, cls) {
    if (!L || !(x1 > x0)) return;
    el(L, "line", { x1: x0.toFixed(2), x2: x1.toFixed(2), y1: y.toFixed(2), y2: y.toFixed(2), "class": cls });
  }
  function shortNote(id) {
    var d = D.notes[id] && D.notes[id][2];
    if (!d) return "";
    var cut = /cut|¢/i.test(D.mens || "");
    var v = d.replace(".", "");
    if (v === "F" || v === "Sf") return "10.1: never a new syllable on a fusa or shorter";
    if (cut && v === "Sm") return "10.1: a new syllable on a semiminim needs a licence (a)–(c)";
    return "";
  }

  function draw() {
    each(".ed-hide", function (g) { g.classList.remove("ed-hide"); }, paper);
    each("g.ed-layer, g.ui-layer", function (g) { g.textContent = ""; }, paper);
    var keys = {};
    Object.keys(edits).forEach(function (k) { var d = edits[k]; if (isMine(d) && d.voice) keys[d.voice + "|" + d.verse] = 1; });
    var it = item(cur);
    if (it && tab > 0) { var pv = previewNotes(it, tab); if (pv) keys[pv.voice + "|" + pv.verse] = 1; }
    if (E) keys[E.voice + "|" + E.verse] = 1;
    Object.keys(keys).forEach(function (key) {
      var p = key.split("|");
      drawVoice(p[0], p[1]);
    });
    drawFocus();
  }

  function drawVoice(v, verse) {
    if (D.tied[v + "|" + verse] === false) return;
    var ids = D.vnotes[v], base = baseOf(v, verse), r = readingsOf(v, verse), ix = vidx[v];
    var changed = [], isCh = {};
    r.forEach(function (c, i) {
      var b = base[i];
      if ((c ? c.join("|") : "") !== (b ? b.join("|") : "")) { changed.push(i); isCh[i] = true; }
    });
    if (!changed.length) return;
    changed.forEach(function (i) { var o = origSyl(ids[i], verse); if (o) o.classList.add("ed-hide"); });
    each('.lyc[data-verse="' + verse + '"]', function (g) {
      var a = ix[g.getAttribute("data-n")], b = ix[g.getAttribute("data-nx")];
      if (a == null) return;
      if (b == null) b = a + 1;
      for (var i = a; i <= b; i++) if (isCh[i]) { g.classList.add("ed-hide"); return; }
    }, paper);
    var boxes = {};
    changed.forEach(function (i) {
      var c = r[i];
      if (!c) return;
      var id = ids[i], p = D.pos[id];
      if (!p) return;
      var y = lyBase(id, v, verse), L = layerOf(p[0], "ed-layer");
      if (!L || y == null) return;
      var t = el(L, "text", { x: (p[1] + 0.65).toFixed(2), y: y.toFixed(2), "text-anchor": "middle", "class": "ed-syl" }, c[0]);
      var w = 0;
      try { w = t.getComputedTextLength(); } catch (e) { w = 0; }
      if (!w) w = c[0].length * 1.2;
      boxes[i] = { x0: p[1] + 0.65 - w / 2, x1: p[1] + 0.65 + w / 2, y: y, page: p[0], sys: D.nsys[id] };
    });
    var starts = [];
    r.forEach(function (c, i) { if (c) starts.push(i); });
    for (var s = 0; s < starts.length; s++) {
      var a = starts[s], b = s + 1 < starts.length ? starts[s + 1] : null, hit = false;
      for (var i = a; i <= (b == null ? r.length - 1 : b); i++) if (isCh[i]) { hit = true; break; }
      if (!hit) continue;
      var A = boxes[a] || boxOfOrig(ids[a], verse);
      if (!A) continue;
      var L2 = layerOf(A.page, "ed-layer"), sb = r[a][1];
      if (sb === "begin" || sb === "middle") {
        var B = b != null ? (boxes[b] || boxOfOrig(ids[b], verse)) : null;
        var x0 = A.x1, x1 = B && B.sys === A.sys ? B.x0 : A.x1 + 2.4;
        var mid = (x0 + x1) / 2, len = Math.max(0.5, Math.min(0.9, (x1 - x0) * 0.5));
        line(L2, mid - len / 2, mid + len / 2, A.y - 0.52, "ed-hy");
      } else {
        var last = (b == null ? r.length : b) - 1;
        while (last > a && (!D.pos[ids[last]] || D.nsys[ids[last]] !== A.sys)) last--;
        if (last > a) line(L2, A.x1 + 0.3, D.pos[ids[last]][1] + 1.3, A.y + 0.05, "ed-ext");
      }
    }
    // gentle validation: a new syllable on a note too short for one
    var src = {};
    base.forEach(function (b) { if (b) src[normSyl(b[0])] = true; });
    changed.forEach(function (i) {
      var c = r[i], id = ids[i], p = D.pos[id];
      if (!c || !p) return;
      var why = src[normSyl(c[0])] ? shortNote(id) : "text differs from the source text";
      if (!why) return;
      var g = el(layerOf(p[0], "ed-layer"), "g", {});
      el(g, "title", {}, why);
      el(g, "ellipse", { cx: (p[1] + 0.65).toFixed(2), cy: p[2].toFixed(2), rx: "1.6", ry: "1.25", "class": "bad" });
    });
  }

  // the active passage: halo on its notes, a band under its lyrics, other systems dimmed;
  // in edit mode the caret and the word being placed
  function focusIds() {
    if (E) return [D.vnotes[E.voice][E.i]];
    var it = item(cur);
    if (!it) return sel ? [sel] : [];
    if (it.type === "f") return it.f.notes;
    return it.d.notes.map(function (n) { return n.id; });
  }
  function spanIds() {
    var it = item(cur);
    if (!it) return [];
    if (it.type === "f") return it.f.span.length ? it.f.span : it.f.notes;
    return it.d.notes.map(function (n) { return n.id; });
  }
  function drawFocus() {
    each(".nh.hl", function (g) { g.classList.remove("hl"); }, paper);
    var ids = focusIds();
    var it = item(cur);
    var sysOn = {};
    ids.forEach(function (id) {
      var p = D.pos[id];
      if (!p) return;
      sysOn[D.nsys[id]] = true;
      if (!E) {
        (byNote[id] || []).forEach(function (g) { g.classList.add("hl"); });
        el(layerOf(p[0], "ui-layer"), "circle", { cx: (p[1] + 0.65).toFixed(2), cy: p[2].toFixed(2), r: "1.9", "class": "hl-halo" });
      }
    });
    // the voice's lyric span
    if (it && !E) {
      var v = it.type === "f" ? it.f.voice : it.d.voice, verse = String(it.type === "f" ? it.f.verse : it.d.verse);
      var bySys = {};
      spanIds().forEach(function (id) {
        var p = D.pos[id];
        if (!p) return;
        var s = D.nsys[id];
        var b = bySys[s] || (bySys[s] = { page: p[0], x0: p[1], x1: p[1], id: id });
        b.x0 = Math.min(b.x0, p[1]); b.x1 = Math.max(b.x1, p[1]);
      });
      Object.keys(bySys).forEach(function (s) {
        var b = bySys[s], y = lyBase(b.id, v, verse);
        if (y == null) return;
        el(layerOf(b.page, "ui-layer"), "rect", { x: (b.x0 - 1.2).toFixed(2), y: (y - 2.3).toFixed(2), width: (b.x1 - b.x0 + 4).toFixed(2), height: "3.1", rx: "0.6", "class": "hl-band" });
      });
    }
    // dim the other systems
    var on = Object.keys(sysOn).map(Number);
    if (on.length && D.sys && D.sys.length > 1) {
      D.sys.forEach(function (s, k) {
        if (sysOn[k]) return;
        var prev = D.sys[k - 1], next = D.sys[k + 1];
        var top = prev && prev[0] === s[0] ? (prev[2] + s[1]) / 2 : s[1] - 12;
        var bot = next && next[0] === s[0] ? (s[2] + next[1]) / 2 : s[2] + 16;
        var svg = pages[s[0]];
        if (!svg) return;
        var vb = svg.viewBox && svg.viewBox.baseVal;
        el(layerOf(s[0], "ui-layer"), "rect", { x: vb ? vb.x : 0, y: top.toFixed(2), width: vb ? vb.width : 300, height: (bot - top).toFixed(2), "class": "dim" });
      });
    }
    if (E) drawCaret();
    else if (sel && D.pos[sel]) {
      var p2 = D.pos[sel], y2 = lyBase(sel, voiceOf(sel), "1");
      if (y2 != null) el(layerOf(p2[0], "ui-layer"), "rect", { x: (p2[1] - 0.9).toFixed(2), y: (y2 - 2.2).toFixed(2), width: "3.1", height: "2.9", rx: "0.3", "class": "caret idle" });
    }
  }

  function drawCaret() {
    var id = D.vnotes[E.voice][E.i], p = D.pos[id];
    if (!p) return;
    var y = lyBase(id, E.voice, E.verse);
    if (y == null) return;
    var L = layerOf(p[0], "ui-layer");
    var r = readingsOf(E.voice, E.verse);
    var c = r[E.i];
    var w = c ? Math.max(2.6, c[0].length * 1.25 + 0.8) : 2.8;
    el(L, "rect", { x: (p[1] + 0.65 - w / 2).toFixed(2), y: (y - 2.3).toFixed(2), width: w.toFixed(2), height: "3.0", rx: "0.3", "class": "caret" });
    if (!c || E.buf) el(L, "rect", { x: (p[1] + 0.65 + (c ? w / 2 - 0.5 : 0)).toFixed(2), y: (y - 2.0).toFixed(2), width: "0.14", height: "2.4", "class": "caret-bar" });
    (byNote[id] || []).forEach(function (g) { g.classList.add("hl"); });
    // the word being placed, above the caret: placed syllables faint, the next one red
    var h = hint(r);
    if (h) {
      var hy = y - 2.9;   // just above the caret, haloed against the staff
      var t = el(L, "text", { x: (p[1] + 0.65).toFixed(2), y: hy.toFixed(2), "text-anchor": "middle", "class": "hint" });
      h.forEach(function (part, k) {
        var ts = document.createElementNS(SVGNS, "tspan");
        ts.setAttribute("class", part[1]);
        ts.textContent = (k ? "·" : "") + part[0];
        t.appendChild(ts);
      });
    }
  }

  // the base text's syllables, word by word: which word comes next at the caret
  function hint(r) {
    var base = baseOf(E.voice, E.verse).filter(Boolean);
    if (!base.length) return null;
    var k = 0;
    for (var i = 0; i < E.i; i++) if (r[i]) k++;
    if (r[E.i] && E.buf) { /* typing here: this syllable is k */ }
    if (k >= base.length) k = base.length - 1;
    var a = k, b = k;
    while (a > 0 && (base[a - 1][1] === "begin" || base[a - 1][1] === "middle")) a--;
    while (b < base.length - 1 && (base[b][1] === "begin" || base[b][1] === "middle")) b++;
    var out = [];
    for (var j = a; j <= b; j++) out.push([base[j][0], j < k ? "done" : (j === k ? "now" : "")]);
    return out;
  }

  // ---------------------------------------------------------------- scrolling and zoom
  var zoom = prefs.zoom || 0;   // 0: fit
  function fitW() { return Math.max(narrow() ? 720 : 600, canvas.clientWidth - 26); }
  function setZoom(z, keep) {
    zoom = z;
    prefs.zoom = z; persist();
    var w = z ? z : fitW();
    var cx = canvas.scrollLeft + canvas.clientWidth / 2, cy = canvas.scrollTop + canvas.clientHeight / 2;
    var ow = paper.scrollWidth || 1, oh = paper.scrollHeight || 1;
    document.documentElement.style.setProperty("--score-w", Math.round(w) + "px");
    if (keep) {
      canvas.scrollLeft = cx * paper.scrollWidth / ow - canvas.clientWidth / 2;
      canvas.scrollTop = cy * paper.scrollHeight / oh - canvas.clientHeight / 2;
    }
  }
  function zoomBy(f) { var w = zoom || fitW(); setZoom(Math.max(500, Math.min(4000, Math.round(w * f))), true); }

  function centre(ids, smooth) {
    var rect = null;
    ids.forEach(function (id) {
      (byNote[id] || []).forEach(function (g) {
        var b = g.getBoundingClientRect();
        if (!b.width && !b.height) return;
        rect = rect ? { l: Math.min(rect.l, b.left), r: Math.max(rect.r, b.right), t: Math.min(rect.t, b.top), b: Math.max(rect.b, b.bottom) }
          : { l: b.left, r: b.right, t: b.top, b: b.bottom };
      });
    });
    if (!rect) return;
    var cr = canvas.getBoundingClientRect();
    var scale = (pages[0] && pages[0].getBoundingClientRect().width / (pages[0].viewBox.baseVal.width || 1)) || 8;
    rect.b += 6 * scale;   // the lyrics under the notes
    rect.t -= 2 * scale;
    var x = canvas.scrollLeft + (rect.l + rect.r) / 2 - cr.left - canvas.clientWidth / 2;
    var y = canvas.scrollTop + (rect.t + rect.b) / 2 - cr.top - canvas.clientHeight / 2;
    // keep it in view if the passage is taller than the canvas
    if (rect.b - rect.t > canvas.clientHeight) y = canvas.scrollTop + rect.t - cr.top - 8;
    try { canvas.scrollTo({ left: x, top: y, behavior: smooth && !reduce ? "smooth" : "auto" }); }
    catch (e) { canvas.scrollLeft = x; canvas.scrollTop = y; }
  }
  function ensureVisible(id) {
    var g = (byNote[id] || [])[0];
    if (!g) return;
    var b = g.getBoundingClientRect(), cr = canvas.getBoundingClientRect();
    if (b.left < cr.left + 40 || b.right > cr.right - 40 || b.top < cr.top + 40 || b.bottom > cr.bottom - 80) centre([id], true);
  }

  // ---------------------------------------------------------------- rail
  var chips = $("chips");
  function renderChips() {
    var h = D.parts.map(function (v) {
      return '<button type="button" class="chip" data-v="' + esc(v) + '" aria-pressed="' + (filt.voices[v] !== false) + '" title="' + esc(v) + '">' + esc(v.slice(0, 1)) + esc(v.slice(1, 3)) + "</button>";
    }).join("") + '<span class="chip-sep"></span>' + ["break", "warn", "look", "info"].map(function (l) {
      var n = F.filter(function (f) { return f.level === l; }).length;
      if (!n) return "";
      return '<button type="button" class="chip" data-l="' + l + '" aria-pressed="' + (filt.levels[l] !== false) + '"><span class="lv ' + l + '"></span>' + l + "</button>";
    }).join("");
    chips.innerHTML = h;
  }
  chips.addEventListener("click", function (e) {
    var b = e.target.closest(".chip");
    if (!b) return;
    if (b.dataset.v) filt.voices[b.dataset.v] = filt.voices[b.dataset.v] === false;
    if (b.dataset.l) filt.levels[b.dataset.l] = filt.levels[b.dataset.l] === false;
    prefs.filt = filt; persist();
    renderChips(); renderRail();
  });

  function rowHtml(it) {
    var lv, w, right = "", done = decided(it);
    if (it.type === "f") {
      var f = it.f, d = decision(f), s = suggestion(f);
      lv = f.level;
      w = '<b class="tn">' + esc(f.where) + '</b> <span class="vo">' + esc(f.voice) + (f.verse !== "1" && verseName(f.verse) ? " · " + esc(verseName(f.verse).slice(0, 4)) : "") + '</span> <em>' + esc(f.word) + "</em>";
      if (d) right = '<span class="tick" title="' + esc(d.alternative ? "Took " + LETTERS[d.alternative] : (d.edited ? "Edited" : "Kept current")) + '">' + (d.alternative ? LETTERS[d.alternative] + " " : (d.edited ? "ed " : "")) + "✓</span>";
      else if (s) right = '<span class="sg" title="Claude suggests ' + esc(LETTERS[s.alternative] || "") + '">' + esc(LETTERS[s.alternative] || "—") + "</span>";
    } else {
      var dd = it.d;
      lv = "sugg";
      w = '<b class="tn">' + esc(dd.notes[0] ? dd.notes[0].where : "") + '</b> <span class="vo">' + esc(dd.voice) + "</span> <em>" + esc(customWords(dd)) + "</em>";
      right = done ? '<span class="tick">' + (dd.status === "declined" ? "kept " : "") + "✓</span>" : '<span class="sg">edit</span>';
    }
    return '<button type="button" class="row' + (done ? " done" : "") + '" data-k="' + esc(it.key) + '"' + (String(cur) === String(it.key) ? ' aria-current="true"' : "") +
      '><span class="lv ' + lv + '"></span><span class="w">' + w + "</span>" + right + "</button>";
  }
  function customWords(d) {
    return d.notes.filter(function (n) { return n.syllable; }).map(function (n) { return n.syllable; }).join(" ").slice(0, 24);
  }
  function renderRail() {
    var g = groups();
    var h = '<div class="grp-h"><span>To review</span><span class="tn">' + g.todo.length + "</span></div>" +
      (g.todo.map(rowHtml).join("") || '<p class="empty">Nothing left to review here.</p>');
    if (g.done.length) h += '<div class="grp-h"><span>Decided</span><span class="tn">' + g.done.length + "</span></div>" + g.done.map(rowHtml).join("");
    if (g.acc.length) h += '<details class="grp" id="acc"' + (prefs.accOpen ? " open" : "") + '><summary><span>Accepted earlier</span><span class="tn">' + g.acc.length + "</span></summary>" + g.acc.map(rowHtml).join("") + "</details>";
    rows.innerHTML = h;
    var acc = $("acc");
    if (acc) acc.addEventListener("toggle", function () { prefs.accOpen = acc.open; persist(); });
    var c = rows.querySelector('[aria-current="true"]');
    if (c) { var rb = c.getBoundingClientRect(), pb = rows.getBoundingClientRect(); if (rb.top < pb.top || rb.bottom > pb.bottom) c.scrollIntoView({ block: "nearest" }); }
    var tr = F.filter(tracked), dn = tr.filter(function (f) { return !!decision(f); }).length;
    var nAcc = F.filter(function (f) { return f.status === "accepted"; }).length;
    $("prog-n").textContent = !tr.length ? "Nothing to review" + (nAcc ? " · " + nAcc + " accepted earlier" : "")
      : (dn === tr.length ? "All findings decided" : dn + " / " + tr.length);
    $("prog-n").nextElementSibling.hidden = !tr.length || dn === tr.length;
    $("prog-bar").style.width = (tr.length ? 100 * dn / tr.length : 0) + "%";
  }
  rows.addEventListener("click", function (e) {
    var b = e.target.closest(".row");
    if (!b) return;
    var k = b.getAttribute("data-k");
    activate(/^\d+$/.test(k) ? parseInt(k, 10) : k, true);
    if (narrow()) railOpen(false);
  });

  // ---------------------------------------------------------------- dock
  function deltaBadge(alt) {
    if (!alt) return "";
    if (alt.basis === "total") return '<span class="dl up" title="the current reading is not legal">▲</span>';
    if (alt.cost < -0.01) return '<span class="dl up" title="better">' + (alt.cost <= -2 ? "▲▲" : "▲") + "</span>";
    if (alt.cost > 0.01) return '<span class="dl dn" title="worse">▼</span>';
    return '<span class="dl" title="about the same">=</span>';
  }
  function labelOf(it) {
    if (it.type === "f") {
      var f = it.f;
      return "bar " + f.where + " · " + f.voice + (verseName(f.verse) ? " · " + verseName(f.verse) : "") + " · " + f.word;
    }
    var d = it.d;
    return "bar " + (d.notes[0] ? d.notes[0].where : "") + " · " + d.voice + (verseName(String(d.verse)) ? " · " + verseName(String(d.verse)) : "");
  }
  function recReason(d) { return String((d && (isSugg(d) ? d.reason : d.recommendation)) || "").replace(REC, "").trim(); }

  function renderDock() {
    if (E) return renderEditDock();
    var it = item(cur);
    if (!it) { dock.innerHTML = '<p class="one">Nothing selected. Pick a finding on the left.</p>'; return; }
    var nTabs, one, tabs = [], dec, sug, lv;
    if (it.type === "f") {
      var f = it.f;
      dec = decision(f); sug = suggestion(f);
      nTabs = Math.max(1, f.pl.length);
      one = f.plain; lv = f.level;
      for (var k = 0; k < nTabs; k++) {
        var alt = k ? f.alternatives[k - 1] : null;
        var isF = dec && (dec.alternative === k || (k === 0 && dec.alternative === 0));
        var isS = (sug && sug.alternative === k) || (dec && dec.recommendation && dec.recAlternative === k);
        tabs.push('<button type="button" role="tab" class="tab' + (isF ? " firm" : "") + '" data-t="' + k + '" aria-selected="' + (k === tab) + '"' +
          (alt && alt.edit ? ' title="' + (alt.edit === "drop" ? "drops a word (10.13)" : "repeats a word (10.9)") + '"' : "") + ">" +
          LETTERS[k] + (alt && alt.edit ? "*" : "") + deltaBadge(alt) + (isS ? '<span class="sg">Suggested</span>' : "") + '<span class="k">' + (k + 1) + "</span></button>");
      }
      if (!f.pl.length) tabs = ['<span class="lab">No alternative reading here: edit, or keep.</span>'];
    } else {
      var d = it.d;
      dec = isSugg(d) ? null : d; sug = isSugg(d) ? d : null; lv = "sugg";
      one = "Suggested edit: " + d.notes.map(function (n) { return (n.syllable ? q(n.syllable) : "—") + " " + n.where; }).join(", ");
      nTabs = 2;
      tabs.push('<button type="button" role="tab" class="tab' + (d.status === "declined" ? " firm" : "") + '" data-t="0" aria-selected="' + (tab === 0) + '">Current<span class="k">1</span></button>');
      tabs.push('<button type="button" role="tab" class="tab' + (dec && d.status !== "declined" ? " firm" : "") + '" data-t="1" aria-selected="' + (tab === 1) + '">Suggested<span class="k">2</span></button>');
    }
    var takeLab = tab === 0 ? "Keep current" : "Take " + (it.type === "f" ? LETTERS[tab] : "this");
    var st = "";
    if (dec) {
      var what = it.type === "f" ? (dec.alternative ? "Took " + LETTERS[dec.alternative] : (dec.edited ? "Edited" : "Kept current")) : (dec.status === "declined" ? "Kept current" : "Took the edit");
      st = '<span class="st">✓ ' + what + "</span>" + (dec.reason ? " · “" + esc(dec.reason) + "”" : "") +
        (reasonOpen ? '<input class="reason" id="reason" type="text" autocomplete="off" placeholder="Reason (optional), Enter to save" value="' + esc(dec.reason || "") + '">' :
          ' <button type="button" class="linkb" id="add-reason">' + (dec.reason ? "Change reason" : "Add a reason") + "</button>") +
        ' <button type="button" class="linkb" id="undecide">Undo</button>';
    }
    dock.innerHTML =
      '<div class="d1"><span class="lv ' + lv + '" title="' + esc(lv === "sugg" ? "suggested edit" : lv) + '"></span><p class="one">' + esc(one) + '</p><span class="lab">' + esc(labelOf(it)) + "</span>" +
      '<button type="button" class="why-t" id="why-t" aria-expanded="' + whyOpen + '">Why ' + (whyOpen ? "▾" : "▸") + "</button></div>" +
      '<div class="d2"><div class="tabs" role="tablist" aria-label="Readings">' + tabs.join("") + "</div>" +
      '<div class="acts"><button type="button" class="btn" id="a-keep">Keep current <kbd>K</kbd></button>' +
      (tab > 0 ? '<button type="button" class="btn pri" id="a-take">' + esc(takeLab) + " <kbd>↵</kbd></button>" : "") +
      '<button type="button" class="btn" id="a-edit">Edit <kbd>E</kbd></button></div></div>' +
      (st ? '<div class="d3">' + st + "</div>" : "") +
      (whyOpen ? '<div class="why">' + whyHtml(it, sug || dec) + "</div>" : "");
    var r = $("reason");
    if (r) {
      r.focus();
      r.addEventListener("keydown", function (e) {
        if (e.key === "Enter") { e.preventDefault(); setReason(r.value); }
        if (e.key === "Escape") { e.preventDefault(); reasonOpen = false; renderDock(); }
        e.stopPropagation();
      });
      r.addEventListener("blur", function () { if (reasonOpen) setReason(r.value); });
    }
  }
  function whyHtml(it, rec) {
    var out = [];
    var rr = recReason(rec);
    if (it.type === "f") {
      var f = it.f, r = D.rules[f.rule] || {};
      out.push('<p><b>' + esc(f.name.replace(/-/g, " ")) + "</b> · principle " + esc(f.principle) + (r.firm ? " · firm rule" : "") + ' · <span class="k">' + esc(f.rule) + "</span></p>");
      out.push("<p>" + esc(f.message) + "</p>");
      if (rr) out.push('<p class="rec"><b>Claude’s recommendation' + (rec.alternative != null && rec.alternative !== undefined && LETTERS[rec.alternative] && it.type === "f" ? " (" + LETTERS[rec.recAlternative != null ? rec.recAlternative : rec.alternative] + ")" : "") + ":</b> " + esc(rr) + "</p>");
      if (f.alternatives.length) out.push("<ul>" + f.alternatives.map(function (a, k) {
        return "<li><b>" + LETTERS[k + 1] + "</b> " + esc(a.moves.join("; ")) + (a.fixes.length ? ' <span class="k">fixes ' + esc(a.fixes.join(", ")) + "</span>" : "") +
          (a.introduces.length ? ' <span class="k">costs ' + esc(a.introduces.join(", ")) + "</span>" : "") + "</li>";
      }).join("") + "</ul>");
      var gates = f.gates.length ? f.gates.map(function (g) { return g + (D.gates[g] ? " (" + D.gates[g] + ")" : ""); }).join("; ") : "none";
      out.push('<p><span class="k">Gates:</span> ' + esc(gates) + ' · <span class="k">regret</span> ' + (f.regret == null ? "—" : f.regret.toFixed(2)) +
        ' · <span class="k">cost</span> ' + f.cost.toFixed(2) + ' · <span class="k">weight</span> ' + esc(r.weight) + "</p>");
      if (f.breakdown.length) out.push('<p><span class="k">Costs around it:</span> ' + esc(f.breakdown.join("; ")) + "</p>");
      if (r.authority) out.push('<p><span class="k">Authority:</span> ' + esc(r.authority) + "</p>");
      out.push('<p><span class="k">Earlier review:</span> ' + esc(f.baseline ? f.baseline : f.status) + "</p>");
      var pt = D.principles[f.principle];
      if (pt) out.push('<details><summary class="k">Principle ' + esc(f.principle) + '</summary><p class="pr">' + esc(pt) + "</p></details>");
    } else {
      if (rr) out.push('<p class="rec"><b>Claude’s recommendation:</b> ' + esc(rr) + "</p>");
    }
    return out.join("");
  }
  function renderEditDock() {
    var id = D.vnotes[E.voice][E.i], n = D.notes[id];
    var vs = D.verses[E.voice] || ["1"];
    dock.innerHTML =
      '<div class="d1"><span class="mode">Editing lyrics</span><p class="one">' + esc(E.voice) + (verseName(E.verse) ? " · " + esc(verseName(E.verse)) : "") +
      '</p><span class="lab tn">bar ' + esc(n[0]) + " · " + esc(n[1]) + " " + esc(n[2]) + (vs.length > 1 ? " · Tab: " + esc(vs.map(verseName).join(" / ")) : "") + "</span>" +
      '<span class="lab" id="e-st"></span><button type="button" class="btn" id="e-done" style="margin-left:auto">Done <kbd>Esc</kbd></button></div>' +
      '<div class="ekeys"><span>type the syllable</span><span><kbd>Space</kbd> word ends, next note</span><span><kbd>-</kbd> hyphen, next note</span>' +
      '<span><kbd>_</kbd> or <kbd>⇧Space</kbd> hold over the next note</span><span><kbd>⌫</kbd> clear, back</span><span><kbd>Del</kbd> clear</span>' +
      '<span><kbd>←</kbd><kbd>→</kbd> move</span><span><kbd>↑</kbd><kbd>↓</kbd> voice</span></div>' +
      (function () {
        var c = readingsOf(E.voice, E.verse)[E.i];
        if (!c) return "";
        var inSrc = baseOf(E.voice, E.verse).some(function (b) { return b && normSyl(b[0]) === normSyl(c[0]); });
        var w = inSrc ? shortNote(id) : "text differs from the source text";
        return w ? '<div class="warnl">' + esc(w) + "</div>" : "";
      })();
  }

  dock.addEventListener("click", function (e) {
    var b = e.target.closest("button");
    if (!b) return;
    if (b.classList.contains("tab")) { setTab(parseInt(b.dataset.t, 10)); return; }
    switch (b.id) {
      case "why-t": whyOpen = !whyOpen; prefs.why = whyOpen; persist(); renderDock(); recentre(); break;
      case "a-keep": keep(); break;
      case "a-take": take(); break;
      case "a-edit": startEdit(); break;
      case "add-reason": reasonOpen = true; renderDock(); break;
      case "undecide": undecide(); break;
      case "e-done": endEdit(); break;
    }
  });

  // ---------------------------------------------------------------- decisions
  function setTab(k) {
    var it = item(cur);
    if (!it) return;
    var n = it.type === "f" ? Math.max(1, it.f.pl.length) : 2;
    if (k < 0 || k >= n) return;
    tab = k;
    renderDock(); draw();
  }
  function snapshot(id) { return edits[id] ? JSON.parse(JSON.stringify(edits[id])) : null; }
  function decide(k, kind) {
    var it = item(cur);
    if (!it) return;
    var id, prev, doc;
    if (it.type === "f") {
      var f = it.f;
      var old = docOf(f);
      id = old ? old.id : findingId(f);
      prev = snapshot(id);
      var pv = previewNotes(it, k) || { notes: f.span.map(function (x) { return [x, null, null]; }) };
      if (k === 0) pv = previewNotes(it, 0) || pv;
      doc = { id: id, slug: D.slug, kind: "alternative", finding: f.fingerprint, rule: f.rule, voice: f.voice, verse: f.verse,
        alternative: k, notes: (f.pl.length ? pv.notes : []).map(function (p) { return noteRec(p[0], p[1], p[2]); }),
        reason: "", status: "proposed" };
      if (!f.pl.length) doc.notes = f.notes.map(function (x) { var l = (D.ed[x][2] || {})[f.verse]; return noteRec(x, l && l[0], l && l[1]); });
      if (old && (isSugg(old) || old.recommendation)) { doc.recommendation = old.recommendation || old.reason; doc.recAlternative = old.recAlternative != null ? old.recAlternative : old.alternative; }
    } else {
      var d = it.d;
      id = d.id; prev = snapshot(id);
      doc = JSON.parse(JSON.stringify(d));
      doc.recommendation = d.recommendation || d.reason;
      doc.reason = "";
      doc.status = k === 0 ? "declined" : "proposed";
    }
    put(doc);
    undo = { id: id, prev: prev, from: cur };
    toast(k === 0 ? "Kept." : "Taken.");
    advance();
  }
  function keep() { decide(0); }
  function take() { decide(tab); }
  function undecide() {
    var it = item(cur);
    if (!it) return;
    var d = it.type === "f" ? decision(it.f) : it.d;
    if (!d) return;
    var prevId = d.id;
    if (d.recommendation) {
      var back = JSON.parse(JSON.stringify(d));
      back.reason = d.recommendation; back.status = "proposed";
      if (it.type === "f") {
        back.alternative = d.recAlternative != null ? d.recAlternative : back.alternative;
        var pv = previewNotes(it, back.alternative);
        if (pv) back.notes = pv.notes.map(function (p) { return noteRec(p[0], p[1], p[2]); });
      }
      delete back.recommendation; delete back.recAlternative;
      put(back);
    } else withdraw(prevId);
  }
  function setReason(text) {
    var it = item(cur);
    reasonOpen = false;
    if (!it) return;
    var d = it.type === "f" ? decision(it.f) : it.d;
    if (!d) { renderDock(); return; }
    var nd = JSON.parse(JSON.stringify(d));
    nd.reason = String(text || "").trim();
    if (nd.reason.indexOf(REC) === 0) nd.reason = nd.reason.slice(REC.length).trim();
    if (nd.reason !== (d.reason || "")) put(nd); else renderDock();
  }
  function advance() {
    var list = navList(), k = list.map(function (x) { return String(x.key); }).indexOf(String(cur));
    var fs = groups().todo;
    if (!fs.length) { renderAll(); return; }
    // the next undecided one after this, in score order
    var it = item(cur), t = it ? itemT(it) : -1, vo = it ? itemVo(it) : -1;
    var next = fs.filter(function (x) { return itemT(x) > t || (itemT(x) === t && itemVo(x) > vo); })[0] || fs[0];
    activate(next.key, true);
    void k;
  }

  var toastTimer = null;
  function toast(msg) {
    var t = $("toast");
    t.innerHTML = esc(msg) + ' <button type="button" id="t-undo">Undo</button>';
    t.hidden = false;
    clearTimeout(toastTimer);
    toastTimer = setTimeout(function () { t.hidden = true; }, 5000);
    $("t-undo").addEventListener("click", doUndo);
  }
  function doUndo() {
    $("toast").hidden = true;
    if (!undo) return;
    var u = undo; undo = null;
    if (u.prev) { edits[u.id] = u.prev; put(u.prev); } else withdraw(u.id);
    activate(u.from, true);
  }

  // ---------------------------------------------------------------- activation
  function activate(key, scroll) {
    if (E) endEdit();
    var it = item(key);
    if (!it) return;
    cur = key;
    sel = null;
    reasonOpen = false;
    var dec = it.type === "f" ? decision(it.f) : (isSugg(it.d) ? null : it.d);
    var sug = it.type === "f" ? suggestion(it.f) : (isSugg(it.d) ? it.d : null);
    if (it.type === "f") tab = dec ? (dec.alternative || 0) : (sug && sug.alternative ? Math.min(sug.alternative, it.f.pl.length - 1) : 0);
    else tab = dec ? (dec.status === "declined" ? 0 : 1) : 1;
    if (tab < 0) tab = 0;
    prefs.cur = key; persist();
    renderAll();
    if (scroll) requestAnimationFrame(function () { centre(focusIds().concat(spanIds()), true); });
  }
  function recentre() { requestAnimationFrame(function () { centre(focusIds(), false); }); }
  function step(d) {
    var list = navList();
    if (!list.length) return;
    var k = list.map(function (x) { return String(x.key); }).indexOf(String(cur));
    k = k < 0 ? 0 : (k + d + list.length) % list.length;
    activate(list[k].key, true);
  }
  function renderAll() { renderRail(); renderDock(); draw(); setSave(); }
  function refresh() { renderAll(); }

  // ---------------------------------------------------------------- the editor
  function startEdit(id, verse) {
    var it = item(cur);
    var v, i;
    if (id) { v = voiceOf(id); i = vidx[v][id]; }
    else if (it) {
      var ids = it.type === "f" ? it.f.notes : it.d.notes.map(function (n) { return n.id; });
      v = it.type === "f" ? it.f.voice : it.d.voice;
      i = vidx[v][ids[0]];
      verse = String(it.type === "f" ? it.f.verse : it.d.verse);
      // start from the reading on show
      if (tab > 0) {
        var pv = previewNotes(it, tab);
        E = { voice: v, verse: verse, i: i, buf: "", ch: {}, fromF: it.type === "f" ? cur : null, dirty: true };
        if (pv) pv.notes.forEach(function (nt) { var j = vidx[v][nt[0]]; if (j != null) E.ch[j] = nt[1] ? [nt[1], nt[2] || "single"] : null; });
        if (it.type === "f" && it.f.span.length) i = vidx[v][it.f.span[0]];
        E.i = i;
      }
    } else if (sel) { v = voiceOf(sel); i = vidx[v][sel]; }
    if (v == null || i == null) return;
    if (!verse) verse = (D.verses[v] || ["1"])[0];
    if (!E) E = { voice: v, verse: verse, i: i, buf: "", ch: {}, dirty: false,
      fromF: !id && it && it.type === "f" && it.f.voice === v && String(it.f.verse) === String(verse) ? cur : null };
    paper.classList.add("editing");
    renderDock(); draw(); ensureVisible(D.vnotes[v][i]);
  }
  function endEdit() {
    if (!E) return;
    commitBuf("keep");
    flush();
    var from = E.fromF, touched = E.touched;
    E = null;
    tab = 0;
    paper.classList.remove("editing");
    if (from != null && touched && F[from]) markEdited(F[from]);
    renderAll();
  }
  function markEdited(f) {
    var old = docOf(f), id = old ? old.id : findingId(f);
    var r = readingsOf(f.voice, f.verse, { preview: false });
    var doc = { id: id, slug: D.slug, kind: "alternative", finding: f.fingerprint, rule: f.rule, voice: f.voice, verse: f.verse,
      alternative: null, edited: true, notes: (f.span.length ? f.span : f.notes).map(function (x) { var c = r[vidx[f.voice][x]]; return noteRec(x, c && c[0], c && c[1]); }),
      reason: "", status: "proposed" };
    if (old && (isSugg(old) || old.recommendation)) { doc.recommendation = old.recommendation || old.reason; doc.recAlternative = old.recAlternative != null ? old.recAlternative : old.alternative; }
    put(doc);
  }
  function cur_r() { var b = E.buf; E.buf = ""; var r = readingsOf(E.voice, E.verse, { preview: false }); E.buf = b; return r; }
  function setNote(i, val) { E.ch[i] = val; E.dirty = true; E.touched = true; schedule(); }
  // the typed syllable goes onto the caret note; mode: "end" (word ends), "hy" (word goes on), "keep"
  function commitBuf(mode) {
    if (!E) return;
    var typed = E.buf || "";
    E.buf = "";
    var r = cur_r();
    var i = E.i, c = r[i];
    var text = typed || (c ? c[0] : "");
    if (!text) return;
    // the voice's text is fixed: typing a syllable that sits on another note
    // nearby re-places it here (Sibelius-style), the word re-laid from the caret
    if (typed) {
      var m = sourceOf(r, i, typed);
      if (m === i) return;
      if (m != null) {
        var syl = r[m];
        if (m > i) { for (var j = i + 1; j <= m; j++) if (r[j]) setNote(j, null); }
        else setNote(m, null);
        setNote(i, [syl[0], syl[1]]);
        (E.spans = E.spans || []).push([Math.min(i, m), Math.max(i, m)]);
        return;
      }
    }
    // typed without the printed punctuation or capital: keep the text's own
    if (typed) {
      var h = hint(r), now = h && h.filter(function (x) { return x[1] === "now"; })[0];
      if (now && now[0].replace(/[,.;:!?]+$/, "").toLowerCase() === typed.toLowerCase()) text = now[0];
    }
    var ph = prevHy(r, i), sb;
    var goesOn = c ? (c[1] === "begin" || c[1] === "middle") : false;
    if (mode === "hy") goesOn = true;
    else if (mode === "end") goesOn = false;
    else if (!typed) return;
    sb = goesOn ? (ph ? "middle" : "begin") : (ph ? "end" : "single");
    if (!c || c[0] !== text || c[1] !== sb) setNote(i, [text, sb]);
  }
  function normSyl(s) { return String(s || "").replace(/[*,.;:!?]+$/, "").toLowerCase(); }
  // the note of the voice's reading that carries `typed` nearby: the same word
  // or about two words either side (syllable order, not note distance); null if none
  function sourceOf(r, i, typed) {
    var t = normSyl(typed), k = 0, pos = [], best = null;
    r.forEach(function (c, j) { if (c) pos.push(j); if (j < i && c) k++; });
    pos.forEach(function (j, p) {
      if (normSyl(r[j][0]) !== t || Math.abs(p - k) > 6) return;
      if (best == null || Math.abs(j - i) < Math.abs(best - i)) best = j;
    });
    return best;
  }
  function move(d) {
    var n = D.vnotes[E.voice].length;
    E.i = Math.max(0, Math.min(n - 1, E.i + d));
  }
  function moveVoice(d) {
    var id = D.vnotes[E.voice][E.i], t = D.on[id];
    var k = D.parts.indexOf(E.voice) + d;
    if (k < 0 || k >= D.parts.length) return;
    flush();
    var v = D.parts[k], best = 0;
    D.vnotes[v].forEach(function (x, j) { if (D.on[x] <= t + 1e-6) best = j; });
    var vs = D.verses[v] || ["1"];
    E = { voice: v, verse: vs.indexOf(E.verse) >= 0 ? E.verse : vs[0], i: best, buf: "", ch: {}, fromF: null, dirty: false, touched: E.touched };
  }
  var idleT = null;
  function schedule() { clearTimeout(idleT); idleT = setTimeout(function () { if (E) { commitBuf("keep"); flush(); renderAll(); } }, 1500); }

  // group the voice's changed notes (against the reading without custom edits) into runs, one doc each
  function flush() {
    if (!E || !E.dirty) return;
    var v = E.voice, verse = E.verse;
    var plain = readingsOf(v, verse, { custom: false, preview: false, session: false });
    var full = readingsOf(v, verse, { preview: false });
    var ids = D.vnotes[v];
    var old = {}, spans = (E.spans || []).slice();
    Object.keys(edits).forEach(function (k) {
      var d = edits[k];
      if (d.kind === "custom" && isMine(d) && d.status !== "declined" && d.voice === v && String(d.verse) === String(verse)) {
        old[k] = d;
        var xs = (d.notes || []).map(function (n) { return vidx[v][n.id]; }).filter(function (x) { return x != null; });
        if (xs.length) spans.push([Math.min.apply(null, xs), Math.max.apply(null, xs)]);
      }
    });
    function together(a, b) {
      return b - a <= 4 || spans.some(function (sp) { return sp[0] <= a && b <= sp[1]; });
    }
    var runs = [], run = null;
    full.forEach(function (c, i) {
      var b = plain[i];
      var diff = (c ? c.join("|") : "") !== (b ? b.join("|") : "");
      // changes a few notes apart, or one re-placed syllable, are one passage: one document
      if (diff) { if (run && together(run.end, i)) run.end = i; else { run = { start: i, end: i }; runs.push(run); } }
    });
    var seen = {};
    E.ch = {}; E.dirty = false;
    runs.forEach(function (rn) {
      var id = customId(v, verse, D.ed[ids[rn.start]][0]), n = 2;
      while (seen[id]) id = customId(v, verse, D.ed[ids[rn.start]][0]) + "-" + (n++);
      seen[id] = true;
      var notes = [];
      for (var i = rn.start; i <= rn.end; i++) notes.push(noteRec(ids[i], full[i] && full[i][0], full[i] && full[i][1]));
      var prev = edits[id];
      if (prev && isSugg(prev)) { /* the editor's own edit at a suggestion's place replaces it */ }
      if (prev && JSON.stringify(prev.notes) === JSON.stringify(notes) && isMine(prev)) return;
      var doc = { id: id, slug: D.slug, kind: "custom", finding: null, voice: v, verse: verse, alternative: null,
        notes: notes, reason: (prev && isMine(prev) && prev.reason) || "", status: "proposed" };
      if (prev && (prev.recommendation || isSugg(prev))) doc.recommendation = prev.recommendation || prev.reason;
      put(doc);
    });
    Object.keys(old).forEach(function (k) { if (!seen[k]) withdraw(k); });
    var st = $("e-st");
    if (st) st.textContent = "saved";
  }

  function editKey(e) {
    var k = e.key;
    if (e.metaKey || e.ctrlKey || e.altKey) return false;
    var r;
    if (k === "Escape" || k === "Enter") { endEdit(); return true; }
    if (k === "Tab") {
      commitBuf("keep"); flush();
      var vs = D.verses[E.voice] || ["1"];
      E.verse = vs[(vs.indexOf(E.verse) + (e.shiftKey ? vs.length - 1 : 1)) % vs.length];
      E.ch = {}; E.fromF = null;
    } else if (k === " " && e.shiftKey || k === "_") {
      if (E.buf) { commitBuf("keep"); move(1); setNote(E.i, null); move(1); }
      else { if (E.i > 0) setNote(E.i, null); move(1); }
    } else if (k === " ") {
      if (E.buf) commitBuf("end");
      move(1);
    } else if (k === "-") {
      if (E.buf) commitBuf("hy");
      move(1);
    } else if (k === "Backspace") {
      if (E.buf) E.buf = E.buf.slice(0, -1);
      else { if (E.i > 0) setNote(E.i, null); move(-1); }
    } else if (k === "Delete") {
      E.buf = ""; if (E.i > 0) setNote(E.i, null);
    } else if (k === "ArrowLeft" || k === "ArrowRight") {
      commitBuf("keep"); move(k === "ArrowLeft" ? -1 : 1);
    } else if (k === "ArrowUp" || k === "ArrowDown") {
      commitBuf("keep"); moveVoice(k === "ArrowUp" ? -1 : 1);
    } else if (k.length === 1) {
      E.buf += k; schedule();
    } else return false;
    renderDock(); draw(); ensureVisible(D.vnotes[E.voice][E.i]);
    return true;
  }

  // ---------------------------------------------------------------- score clicks
  function noteAt(e) {
    var svg = e.target.closest && e.target.closest("svg.score-page");
    if (!svg) return null;
    var page = parseInt(svg.getAttribute("data-page"), 10);
    var pt = svg.createSVGPoint();
    pt.x = e.clientX; pt.y = e.clientY;
    var m = svg.getScreenCTM();
    if (!m) return null;
    var p = pt.matrixTransform(m.inverse());
    var best = null, bd = 10;
    Object.keys(D.pos).forEach(function (id) {
      var q2 = D.pos[id];
      if (q2[0] !== page) return;
      var dx = p.x - (q2[1] + 0.65), dy = (p.y - q2[2]);
      // a click on the lyric line under a staff picks that voice's note
      var ly = lyBase(id, voiceOf(id), E ? E.verse : "1");
      var dyl = ly != null ? p.y - (ly - 0.8) : 99;
      var d = dx * dx + Math.min(dy * dy, dyl * dyl * 1.5);
      if (d < bd) { bd = d; best = id; }
    });
    return best;
  }
  paper.addEventListener("click", function (e) {
    var id = noteAt(e);
    if (!id) return;
    if (E) {
      commitBuf("keep");
      var v = voiceOf(id);
      if (v !== E.voice) { flush(); var vs = D.verses[v] || ["1"]; E = { voice: v, verse: vs.indexOf(E.verse) >= 0 ? E.verse : vs[0], i: 0, buf: "", ch: {}, fromF: null, dirty: false, touched: E.touched }; }
      E.i = vidx[v][id];
      renderDock(); draw();
      return;
    }
    sel = id;
    draw();
  });
  paper.addEventListener("dblclick", function (e) {
    var id = noteAt(e);
    if (!id) return;
    e.preventDefault();
    var it = item(cur), verse = null;
    if (it && it.type === "f" && it.f.voice === voiceOf(id)) verse = it.f.verse;
    tab = 0;
    startEdit(id, verse);
  });

  // ---------------------------------------------------------------- bar, popovers, about
  function railOpen(on) {
    if (narrow()) { app.classList.toggle("rail-open", on); $("scrim").hidden = !on; }
    else { app.classList.toggle("rail-off", !on); prefs.rail = on; persist(); if (!zoom) setZoom(0); }
    $("b-rail").setAttribute("aria-expanded", String(on));
  }
  function railIsOpen() { return narrow() ? app.classList.contains("rail-open") : !app.classList.contains("rail-off"); }
  $("b-rail").addEventListener("click", function () { railOpen(!railIsOpen()); });
  $("scrim").addEventListener("click", function () { railOpen(false); closePops(); });
  $("b-prev").addEventListener("click", function () { step(-1); });
  $("b-next").addEventListener("click", function () { step(1); });
  $("z-in").addEventListener("click", function () { zoomBy(1.2); });
  $("z-out").addEventListener("click", function () { zoomBy(1 / 1.2); });
  $("z-fit").addEventListener("click", function () { setZoom(0, false); recentre(); });

  var layersOn = prefs.layers || { cad: true };
  $("p-layers").innerHTML = LAYERS.map(function (l) {
    return '<label title="' + esc(l[2]) + '"><input type="checkbox" data-layer="' + l[0] + '"' + (layersOn[l[0]] ? " checked" : "") + '><span class="sw sw-' + l[0] + '"></span>' + esc(l[1]) + "</label>";
  }).join("");
  function applyLayers() { LAYERS.forEach(function (l) { paper.classList.toggle("show-" + l[0], !!layersOn[l[0]]); }); }
  $("p-layers").addEventListener("change", function (e) {
    var b = e.target; layersOn[b.dataset.layer] = b.checked; prefs.layers = layersOn; persist(); applyLayers();
  });
  applyLayers();
  $("p-keys").innerHTML =
    "<h4>Findings</h4><dl><dt><kbd>→</kbd> <kbd>J</kbd></dt><dd>next</dd><dt><kbd>←</kbd> <kbd>⇧J</kbd></dt><dd>previous</dd>" +
    "<dt><kbd>1</kbd>–<kbd>4</kbd></dt><dd>show a reading</dd><dt><kbd>↵</kbd></dt><dd>take it</dd><dt><kbd>K</kbd></dt><dd>keep current</dd>" +
    "<dt><kbd>E</kbd> or double-click</dt><dd>edit the lyrics</dd><dt><kbd>W</kbd></dt><dd>why</dd></dl>" +
    "<h4>Editing</h4><dl><dt>letters</dt><dd>the syllable</dd><dt><kbd>Space</kbd></dt><dd>word ends, next note</dd><dt><kbd>-</kbd></dt><dd>hyphen, next note</dd>" +
    "<dt><kbd>_</kbd> <kbd>⇧Space</kbd></dt><dd>hold over the next note</dd><dt><kbd>⌫</kbd> / <kbd>Del</kbd></dt><dd>clear (and back)</dd>" +
    "<dt><kbd>↑</kbd> <kbd>↓</kbd></dt><dd>voice above, below</dd><dt><kbd>Tab</kbd></dt><dd>other verse</dd><dt><kbd>Esc</kbd></dt><dd>done (saves)</dd></dl>" +
    "<h4>View</h4><dl><dt><kbd>[</kbd></dt><dd>findings list</dd><dt><kbd>L</kbd></dt><dd>layers</dd><dt><kbd>Z</kbd> <kbd>X</kbd> <kbd>F</kbd></dt><dd>zoom out, in, fit</dd><dt><kbd>?</kbd></dt><dd>this list</dd></dl>";

  var POPS = [["b-layers", "p-layers"], ["b-keys", "p-keys"], ["b-menu", "p-menu"]];
  function closePops(except) {
    POPS.forEach(function (p) { if (p[1] !== except) { $(p[1]).hidden = true; $(p[0]).setAttribute("aria-expanded", "false"); } });
  }
  function togglePop(i) {
    var p = POPS[i], open = $(p[1]).hidden;
    closePops(p[1]);
    $(p[1]).hidden = !open; $(p[0]).setAttribute("aria-expanded", String(open));
  }
  POPS.forEach(function (p, i) { $(p[0]).addEventListener("click", function (e) { e.stopPropagation(); togglePop(i); }); });
  document.addEventListener("click", function (e) { if (!e.target.closest(".pop-wrap")) closePops(); });

  function exportJson() {
    return JSON.stringify(Object.keys(edits).sort().filter(function (k) { return !edits[k]._seed; }).map(function (k) { return clean(edits[k]); }), null, 1);
  }
  $("m-copy").addEventListener("click", function () {
    var text = exportJson(), ta = $("m-json"), msg = $("m-msg");
    var n = JSON.parse(text).length;
    function fallback() { ta.value = text; ta.hidden = false; ta.focus(); ta.select(); msg.textContent = "Selected: copy it with your keyboard."; }
    try {
      if (navigator.clipboard && navigator.clipboard.writeText) navigator.clipboard.writeText(text).then(function () { msg.textContent = "Copied " + n + " edits. Paste them into the chat."; }, fallback);
      else fallback();
    } catch (e) { fallback(); }
  });
  function about(on) { $("about").hidden = !on; if (on) $("about-x").focus(); }
  $("b-about").addEventListener("click", function () { about($("about").hidden); });
  $("about-x").addEventListener("click", function () { about(false); });
  each("#about tr.pick", function (tr) {
    tr.addEventListener("click", function () {
      var ids = tr.getAttribute("data-notes").split(" ").filter(Boolean);
      about(false);
      cur = null; renderAll();
      each(".nh.hl", function (g) { g.classList.remove("hl"); }, paper);
      ids.forEach(function (id) { (byNote[id] || []).forEach(function (g) { g.classList.add("hl"); }); });
      centre(ids, true);
    });
  });

  // ---------------------------------------------------------------- keyboard
  document.addEventListener("keydown", function (e) {
    var t = e.target;
    var typing = t && (t.tagName === "INPUT" || t.tagName === "TEXTAREA" || t.tagName === "SELECT" || t.isContentEditable);
    if (E && !typing) { if (editKey(e)) e.preventDefault(); return; }
    if (typing) return;
    if (e.metaKey || e.ctrlKey || e.altKey) return;
    var k = e.key;
    if (k === "Escape") {
      if (!$("about").hidden) about(false);
      else if (narrow() && railIsOpen()) railOpen(false);
      closePops(); return;
    }
    var handled = true;
    if (k === "ArrowRight" || (k === "j" || k === "J") && !e.shiftKey) step(1);
    else if (k === "ArrowLeft" || k === "J" && e.shiftKey) step(-1);
    else if (/^[1-5]$/.test(k)) setTab(parseInt(k, 10) - 1);
    else if (k === "Enter") { if (t && t.tagName === "BUTTON" && t.id !== "a-take") handled = false; else if (tab > 0) take(); else keep(); }
    else if (k === "k" || k === "K") keep();
    else if (k === "e" || k === "E") { if (sel && !item(cur)) startEdit(sel); else startEdit(); }
    else if (k === "w" || k === "W") { whyOpen = !whyOpen; prefs.why = whyOpen; persist(); renderDock(); }
    else if (k === "[") railOpen(!railIsOpen());
    else if (k === "l" || k === "L") togglePop(0);
    else if (k === "?") togglePop(1);
    else if (k === "z" || k === "Z") zoomBy(1 / 1.2);
    else if (k === "x" || k === "X") zoomBy(1.2);
    else if (k === "f" || k === "F") { setZoom(0); recentre(); }
    else if (k === "u" || k === "U") doUndo();
    else handled = false;
    if (handled) e.preventDefault();
  });
  window.addEventListener("resize", function () { if (!zoom) setZoom(0); });

  // ---------------------------------------------------------------- the store
  function noDb() { dbState = "local"; setSave(); }
  var use = window.claude && typeof window.claude.use === "function" ? window.claude.use : null;
  if (use) {
    Promise.all([use.call(window.claude, "db"), use.call(window.claude, "user")]).then(function (r) {
      db = r[0];
      var user = r[1];
      if (!db) { noDb(); return; }
      dbState = "on"; setSave();
      var p = user && user.id ? user.id().then(function (id) { me = id || null; }, function () {}) : Promise.resolve();
      p.then(function () {
        db.collection("edits").onSnapshot(function (qs) {
          var seen = {};
          qs.docs.forEach(function (ds) {
            var d = ds.data();
            if (!d || d.slug !== D.slug) return;
            var id = ds.id;
            seen[id] = true;
            saved[id] = Object.assign({ id: id }, d);
            var mine = edits[id];
            if (!mine || mine._seed || (d.updatedAt || "") >= (mine.updatedAt || "")) edits[id] = Object.assign({}, saved[id]);
          });
          Object.keys(saved).forEach(function (id) { if (!seen[id]) delete saved[id]; });
          // local edits the store has never had: send them
          Object.keys(edits).forEach(function (id) {
            if (!saved[id] && !edits[id]._seed && !edits[id]._sent) {
              edits[id]._sent = true;
              db.collection("edits").doc(id).set(clean(edits[id])).catch(function () {});
            }
          });
          saveLocal();
          renderAll();
        }, function (err) { dbState = "error"; setSave((err && err.code) || "error"); });
      });
    }, noDb);
  }

  // ---------------------------------------------------------------- start
  if (prefs.rail === false && !narrow()) app.classList.add("rail-off");
  if (narrow()) $("b-rail").setAttribute("aria-expanded", "false");
  renderChips();
  setZoom(zoom);
  var start = prefs.cur != null && item(prefs.cur) ? prefs.cur : null;
  if (start == null) { var g0 = groups(); var first = g0.todo[0] || g0.done[0] || g0.acc[0]; start = first ? first.key : null; }
  if (start != null) activate(start, false);
  else renderAll();
  requestAnimationFrame(function () { centre(focusIds().concat(spanIds()), false); });
  window.RV = { D: D, edits: edits, activate: activate, startEdit: function (id, verse) { tab = 0; startEdit(id, verse); } };
})();

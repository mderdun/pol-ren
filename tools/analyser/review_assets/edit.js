// Underlay editing on the review page (tools/analyser/review.py).
//
// A finding's readings (current, alternative 1, 2 ...) are drawn into the
// score in place of the printed syllables, in red; the editor steps through
// them with the buttons or the arrow keys, and may firm one, with a reason.
// In "Edit underlay" mode a click on a note sets the syllable that starts on
// it (or clears it). Edits are kept in the page, saved to the artifact's db
// (collection "edits", one document per finding or per voice, verse and bar)
// when the page is served with it, and can always be copied as JSON for
// `python -m tools.analyser edits apply`. See docs/analyser.md.
(function () {
  "use strict";
  var RV = window.RV;
  if (!RV) return;
  var D = RV.D, esc = RV.esc, pitch = RV.pitch;
  var SVGNS = "http://www.w3.org/2000/svg";
  var paper = document.getElementById("paper");
  var pages = paper.querySelectorAll("svg.score-page");
  var LS = "pol-ren-review-edits:" + D.slug;

  var edits = {};      // id -> doc, as this view has them
  var saved = {};      // id -> doc, as the db has them
  var preview = null;  // {n: finding, k: reading}
  var draft = null;    // {id: note id, verse, syllable} while typing a custom syllable
  var db = null, me = null, dbState = "waiting";
  var editMode = false, selNote = null;

  // ------------------------------------------------------------ storage
  function lsLoad() {
    try { var t = window.localStorage.getItem(LS); if (t) edits = JSON.parse(t) || {}; } catch (e) { edits = {}; }
  }
  function lsSave() {
    try { window.localStorage.setItem(LS, JSON.stringify(edits)); } catch (e) { /* storage off: the page still works */ }
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

  function same(a, b) { return a && b && a.updatedAt === b.updatedAt && JSON.stringify(a.notes) === JSON.stringify(b.notes); }

  function put(doc) {
    doc.updatedAt = new Date().toISOString();
    doc.by = me;
    edits[doc.id] = doc;
    lsSave();
    refresh();
    if (db) {
      var body = clean(doc);
      db.collection("edits").doc(doc.id).set(body).then(function () { refresh(); }, function (err) {
        setDbState("error", err && err.code === "invalid_argument" ? "This view cannot write to the page's store." :
          "Could not save (" + (err && err.code || "error") + "). Copy the edits as JSON instead.");
      });
    }
  }

  function withdraw(id) {
    delete edits[id];
    lsSave();
    if (db) db.collection("edits").doc(id).delete().then(refresh, function () { /* already gone */ });
    refresh();
  }

  // ------------------------------------------------------------ readings
  function baseOf(voice, verse) {
    return D.vnotes[voice].map(function (id) {
      var l = (D.ed[id][2] || {})[verse];
      return l ? [l[0], l[1]] : null;
    });
  }
  function idxOf(voice) {
    var m = {};
    D.vnotes[voice].forEach(function (id, i) { m[id] = i; });
    return m;
  }

  // the reading of each voice and verse that has edits or a preview: [base, new]
  function readings() {
    var out = {};
    function get(v, verse) {
      var key = v + "|" + verse;
      if (!out[key]) { var b = baseOf(v, verse); out[key] = { v: v, verse: verse, base: b, cur: b.slice(), idx: idxOf(v) }; }
      return out[key];
    }
    Object.keys(edits).map(function (k) { return edits[k]; })
      .sort(function (a, b) { return (a.updatedAt || "") < (b.updatedAt || "") ? -1 : 1; })
      .forEach(function (d) {
        if (!D.vnotes[d.voice]) return;
        var r = get(d.voice, String(d.verse));
        if (preview && d.kind === "alternative" && D.findings[preview.n] && d.finding === D.findings[preview.n].fingerprint) return;
        d.notes.forEach(function (nt) {
          var i = r.idx[nt.id];
          if (i != null) r.cur[i] = nt.syllable ? [nt.syllable, nt.syllabic] : null;
        });
      });
    if (preview) {
      var f = D.findings[preview.n];
      if (f && f.pl.length) {
        var r = get(f.voice, f.verse);
        spanNotes(f, preview.k).forEach(function (nt) {
          var i = r.idx[nt[0]];
          if (i != null) r.cur[i] = nt[1] ? [nt[1], nt[2]] : null;
        });
      }
    }
    if (draft) {
      var v = draft.id.split(":")[0];
      var r2 = get(v, draft.verse);
      var i2 = r2.idx[draft.id];
      if (i2 != null) r2.cur[i2] = draft.syllable ? [draft.syllable, draft.syllabic] : null;
    }
    return out;
  }

  // every note of the finding's span with the syllable reading k starts on it, or null
  function spanNotes(f, k) {
    var at = {};
    (f.pl[k] || []).forEach(function (p) { at[p[0]] = p; });
    return f.span.map(function (id) { var p = at[id]; return p ? [id, p[1], p[2]] : [id, null, null]; });
  }

  // ------------------------------------------------------------ drawing
  function layerOf(page) {
    var svg = pages[page];
    if (!svg) return null;
    var g = svg.querySelector("g.ed-layer");
    if (!g) { g = document.createElementNS(SVGNS, "g"); g.setAttribute("class", "ed-layer"); svg.appendChild(g); }
    return g;
  }

  function baseline(id, voice, verse) {
    var s = D.nsys[id];
    var y = D.lyb[s + "|" + voice + "|" + verse];
    if (y != null) return y;
    var y1 = D.lyb[s + "|" + voice + "|1"];
    if (y1 != null) return y1 + 2.9 * (parseInt(verse, 10) - 1);
    var b = D.stb[s + "|" + voice];
    return b != null ? b + 4.4 + 2.9 * (parseInt(verse, 10) - 1) : null;
  }

  function origSyl(id, verse) { return paper.querySelector('.ly[data-n="' + id + '"][data-verse="' + verse + '"]'); }

  function draw() {
    Array.prototype.forEach.call(paper.querySelectorAll(".ed-hide"), function (g) { g.classList.remove("ed-hide"); });
    Array.prototype.forEach.call(paper.querySelectorAll("g.ed-layer"), function (g) { g.textContent = ""; });
    var R = readings();
    Object.keys(R).forEach(function (key) {
      var r = R[key];
      if (D.tied[key] === false) return;
      var ids = D.vnotes[r.v];
      var changed = [];
      r.cur.forEach(function (c, i) {
        var b = r.base[i];
        if ((c ? c.join("|") : "") !== (b ? b.join("|") : "")) changed.push(i);
      });
      if (!changed.length) return;
      var isCh = {};
      changed.forEach(function (i) { isCh[i] = true; });
      // hide the printed syllables that move, and the hyphens and extenders across them
      changed.forEach(function (i) {
        var o = origSyl(ids[i], r.verse);
        if (o) o.classList.add("ed-hide");
      });
      Array.prototype.forEach.call(paper.querySelectorAll('.lyc[data-verse="' + r.verse + '"]'), function (g) {
        var a = r.idx[g.getAttribute("data-n")], b = r.idx[g.getAttribute("data-nx")];
        if (a == null) return;
        if (b == null) b = a + 1;
        for (var i = a; i <= b; i++) if (isCh[i]) { g.classList.add("ed-hide"); return; }
      });
      // draw the new syllables
      var boxes = {};
      changed.forEach(function (i) {
        var c = r.cur[i];
        if (!c) return;
        var id = ids[i], p = D.pos[id];
        if (!p) return;
        var y = baseline(id, r.v, r.verse);
        var L = layerOf(p[0]);
        if (!L || y == null) return;
        var t = document.createElementNS(SVGNS, "text");
        t.setAttribute("x", (p[1] + 0.65).toFixed(2));
        t.setAttribute("y", y.toFixed(2));
        t.setAttribute("text-anchor", "middle");
        t.setAttribute("class", "ed-syl");
        t.textContent = c[0];
        L.appendChild(t);
        var w = 0;
        try { w = t.getComputedTextLength(); } catch (e) { w = c[0].length * 1.2; }
        if (!w) w = c[0].length * 1.2;
        boxes[i] = { x0: p[1] + 0.65 - w / 2, x1: p[1] + 0.65 + w / 2, y: y, page: p[0], sys: D.nsys[id] };
      });
      // hyphens and extenders, where a changed note lies between a syllable and the next
      var starts = [];
      r.cur.forEach(function (c, i) { if (c) starts.push(i); });
      for (var s = 0; s < starts.length; s++) {
        var a = starts[s], b = s + 1 < starts.length ? starts[s + 1] : null;
        var hit = false;
        for (var i = a; i <= (b == null ? r.cur.length - 1 : b); i++) if (isCh[i]) { hit = true; break; }
        if (!hit) continue;
        var A = boxes[a] || boxOfOrig(ids[a], r.verse);
        if (!A) continue;
        var sb = r.cur[a][1];
        var L2 = layerOf(A.page);
        if (sb === "begin" || sb === "middle") {
          var B = b != null ? (boxes[b] || boxOfOrig(ids[b], r.verse)) : null;
          var x0 = A.x1, x1 = B && B.sys === A.sys ? B.x0 : A.x1 + 2.4;
          var mid = (x0 + x1) / 2, len = Math.max(0.5, Math.min(0.9, (x1 - x0) * 0.5));
          line(L2, mid - len / 2, mid + len / 2, A.y - 0.52, "ed-hy");
        } else {
          var last = (b == null ? r.cur.length : b) - 1;
          while (last > a && (!D.pos[ids[last]] || D.nsys[ids[last]] !== A.sys)) last--;
          if (last > a) line(L2, A.x1 + 0.3, D.pos[ids[last]][1] + 1.3, A.y + 0.05, "ed-ext");
        }
      }
    });
  }

  function boxOfOrig(id, verse) {
    var o = origSyl(id, verse);
    var p = D.pos[id];
    if (!o || !p) return null;
    try {
      var bb = o.getBBox();
      return { x0: bb.x, x1: bb.x + bb.width, y: bb.y + bb.height * 0.78, page: p[0], sys: D.nsys[id] };
    } catch (e) { return null; }
  }

  function line(L, x0, x1, y, cls) {
    if (!L || !(x1 > x0)) return;
    var l = document.createElementNS(SVGNS, "line");
    l.setAttribute("x1", x0.toFixed(2)); l.setAttribute("x2", x1.toFixed(2));
    l.setAttribute("y1", y.toFixed(2)); l.setAttribute("y2", y.toFixed(2));
    l.setAttribute("class", cls);
    L.appendChild(l);
  }

  // ------------------------------------------------------------ the finding's box
  function firmedOf(f) {
    var d = edits[findingId(f)];
    return d && d.kind === "alternative" ? d : null;
  }

  function stateOf(id) {
    var d = edits[id];
    if (!d) return "";
    if (!db) return "kept here";
    return same(d, saved[id]) ? "saved" : "saving";
  }

  window.RVmark = function (f) {
    var id = findingId(f), d = edits[id];
    if (!d) return "";
    var st = stateOf(id);
    return ' <span class="pill ed-pill' + (st === "saved" ? " ok" : "") + '" title="' +
      (st === "saved" ? "firmed and saved" : "firmed, " + st) + '">' + (d.alternative ? "alt " + d.alternative : "kept") +
      (st === "saved" ? " ✓" : "") + "</span>";
  };

  function renderBox() {
    var box = document.getElementById("ed-box");
    var n = RV.current();
    var f = D.findings[n];
    if (!box || !f) return;
    if (!f.pl.length) {
      box.innerHTML = '<p class="note">This finding has no span of syllables to set another way here; use “Edit underlay” on the score.</p>';
      return;
    }
    var k = preview && preview.n === n ? preview.k : 0;
    var firm = firmedOf(f);
    var tied = D.tied[f.voice + "|" + f.verse] !== false;
    var btns = f.pl.map(function (_, i) {
      var lab = i === 0 ? "Current" : "Alt " + i;
      var isF = firm && firm.alternative === i;
      return '<button type="button" class="seg' + (isF ? " firmed" : "") + '" data-k="' + i + '" aria-pressed="' + (i === k) + '">' +
        lab + (isF ? " ✓" : "") + "</button>";
    }).join("");
    var sylls = f.pl[k].map(function (p) { return esc(p[1]) + (p[2] === "begin" || p[2] === "middle" ? "-" : ""); }).join(" ");
    var st = firm ? stateOf(findingId(f)) : "";
    box.innerHTML =
      '<div class="ed-step" role="group" aria-label="Readings">' +
      '<button type="button" class="step" data-d="-1" aria-label="Previous reading">‹</button>' +
      '<div class="segs">' + btns + '</div>' +
      '<button type="button" class="step" data-d="1" aria-label="Next reading">›</button></div>' +
      '<p class="ed-now"><b>' + (k === 0 ? "Current" : "Alternative " + k) + "</b>, in the score in red: " +
      '<span class="mono">' + sylls + "</span>" +
      (tied ? "" : ' <span class="pill pill-warn">this voice is not tied to voices.ily; the score cannot show it</span>') +
      '<span class="note"> · ← → step through the readings</span></p>' +
      '<div class="ed-firm"><label for="ed-reason">Reason (optional)</label>' +
      '<input id="ed-reason" type="text" autocomplete="off" value="' + esc(firm && firm.alternative === k ? firm.reason : "") + '" placeholder="why this reading">' +
      '<button type="button" class="btn primary" id="ed-firm">' + (k === 0 ? "Keep the current reading" : "Firm alternative " + k) + "</button>" +
      (firm ? '<button type="button" class="btn" id="ed-unfirm">Withdraw</button>' : "") +
      '<span class="ed-st">' + (firm ? "Firmed: " + (firm.alternative ? "alternative " + firm.alternative : "current") + ", " + esc(st) : "") + "</span></div>";
    box.querySelectorAll(".seg").forEach(function (b) {
      b.addEventListener("click", function () { setPreview(n, parseInt(b.getAttribute("data-k"), 10)); });
    });
    box.querySelectorAll(".step").forEach(function (b) {
      b.addEventListener("click", function () { step(parseInt(b.getAttribute("data-d"), 10)); });
    });
    document.getElementById("ed-firm").addEventListener("click", function () {
      var reason = document.getElementById("ed-reason").value.trim();
      put({ id: findingId(f), slug: D.slug, kind: "alternative", finding: f.fingerprint, rule: f.rule,
            voice: f.voice, verse: f.verse, alternative: k,
            notes: spanNotes(f, k).map(function (p) { return noteRec(p[0], p[1], p[2]); }),
            reason: reason, status: "proposed" });
    });
    var un = document.getElementById("ed-unfirm");
    if (un) un.addEventListener("click", function () { withdraw(findingId(f)); });
  }

  function setPreview(n, k) {
    var f = D.findings[n];
    if (!f || !f.pl.length) return;
    k = (k + f.pl.length) % f.pl.length;
    var firm = firmedOf(f);
    preview = { n: n, k: k };
    if (k === 0 && !firm) preview = { n: n, k: 0 };
    renderBox();
    draw();
    var b = document.querySelector('#ed-box .seg[data-k="' + k + '"]');
    if (b && document.activeElement && document.activeElement.classList.contains("seg")) b.focus();
  }

  function step(d) {
    var n = RV.current();
    if (n == null) return;
    var k = preview && preview.n === n ? preview.k : 0;
    setPreview(n, k + d);
  }

  document.addEventListener("rv:finding", function (e) {
    var n = e.detail.n, f = D.findings[n];
    var firm = f && firmedOf(f);
    preview = { n: n, k: firm ? firm.alternative : 0 };
    renderBox();
    draw();
  });

  document.addEventListener("keydown", function (e) {
    if (e.key !== "ArrowLeft" && e.key !== "ArrowRight") return;
    var t = e.target;
    if (t && (t.tagName === "INPUT" || t.tagName === "TEXTAREA" || t.tagName === "SELECT" || t.isContentEditable)) return;
    if (t && t.closest && t.closest(".paper")) return;   // let the score panel scroll
    var f = D.findings[RV.current()];
    if (!f || f.pl.length < 2) return;
    e.preventDefault();
    step(e.key === "ArrowLeft" ? -1 : 1);
  });

  // ------------------------------------------------------------ custom edits
  var modeBtn = document.getElementById("ed-mode");
  var form = document.getElementById("ed-note");

  modeBtn.addEventListener("click", function () {
    editMode = !editMode;
    modeBtn.setAttribute("aria-pressed", String(editMode));
    paper.classList.toggle("editing", editMode);
    if (!editMode) closeForm();
    else if (!selNote) form.innerHTML = '<p class="note">Click a note in the score to set the syllable that starts on it.</p>';
    form.hidden = !editMode;
  });

  paper.addEventListener("click", function (e) {
    if (!editMode) return;
    // the nearest note head to the click, on its page (heads are small, and
    // overlays may lie on top of them)
    var svg = e.target.closest && e.target.closest("svg.score-page");
    if (!svg) return;
    var page = parseInt(svg.getAttribute("data-page"), 10);
    var pt = svg.createSVGPoint();
    pt.x = e.clientX; pt.y = e.clientY;
    var m = svg.getScreenCTM();
    if (!m) return;
    var q = pt.matrixTransform(m.inverse());
    var best = null, bd = 9;
    Object.keys(D.pos).forEach(function (id) {
      var p = D.pos[id];
      if (p[0] !== page) return;
      var dx = q.x - (p[1] + 0.65), dy = q.y - p[2];
      var d = dx * dx + dy * dy;
      if (d < bd) { bd = d; best = id; }
    });
    if (!best) return;
    e.preventDefault();
    openForm(best);
  });

  function effective(id, verse) {
    var v = id.split(":")[0];
    var r = readings()[v + "|" + verse];
    var i = idxOf(v)[id];
    if (r) return r.cur[i];
    var l = (D.ed[id][2] || {})[verse];
    return l ? [l[0], l[1]] : null;
  }

  function prevHyphen(id, verse) {
    var v = id.split(":")[0];
    var key = v + "|" + verse;
    var r = readings()[key];
    var cur = r ? r.cur : baseOf(v, verse);
    var i = idxOf(v)[id];
    for (var j = i - 1; j >= 0; j--) if (cur[j]) return cur[j][1] === "begin" || cur[j][1] === "middle";
    return false;
  }

  function syllabicFor(id, verse, typed) {
    var hy = /-$/.test(typed);
    var ph = prevHyphen(id, verse);
    return ph ? (hy ? "middle" : "end") : (hy ? "begin" : "single");
  }

  function openForm(id) {
    selNote = id;
    var v = id.split(":")[0];
    var verses = D.verses[v] && D.verses[v].length ? D.verses[v] : ["1"];
    var verse = form.getAttribute("data-verse");
    if (verses.indexOf(verse) < 0) verse = verses[0];
    var c = effective(id, verse);
    var n = D.notes[id];
    var val = c ? c[0] + (c[1] === "begin" || c[1] === "middle" ? "-" : "") : "";
    var tied = D.tied[v + "|" + verse] !== false;
    form.setAttribute("data-verse", verse);
    form.innerHTML =
      '<div class="ed-nh"><b>' + esc(v) + "</b> · bar " + esc(n[0]) + " · " + esc(pitch(n[1])) + " " + esc(n[2]) +
      (verses.length > 1 ? ' · <label for="ed-verse">verse</label> <select id="ed-verse">' +
        verses.map(function (x) { return '<option' + (x === verse ? " selected" : "") + ">" + esc(x) + "</option>"; }).join("") + "</select>" : "") +
      (tied ? "" : ' <span class="pill pill-warn">not tied to voices.ily</span>') + "</div>" +
      '<div class="ed-row"><label for="ed-syl">Syllable starting here</label>' +
      '<input id="ed-syl" type="text" autocomplete="off" spellcheck="false" value="' + esc(val) + '" placeholder="empty: none starts here">' +
      '<span class="note">end with - when the word goes on (Ra-)</span></div>' +
      '<div class="ed-row"><label for="ed-why">Reason (optional)</label><input id="ed-why" type="text" autocomplete="off"></div>' +
      '<div class="ed-row"><button type="button" class="btn primary" id="ed-set">Set</button>' +
      '<button type="button" class="btn" id="ed-clear">Clear syllable</button>' +
      '<button type="button" class="btn" id="ed-close">Close</button></div>';
    RV.highlight([id], false);
    var inp = document.getElementById("ed-syl");
    inp.addEventListener("input", function () { live(id, verse, inp.value); });
    inp.addEventListener("keydown", function (e) {
      if (e.key === "Enter") { e.preventDefault(); commit(id, verse, inp.value); }
      if (e.key === "Escape") { e.preventDefault(); closeForm(); }
    });
    var vs = document.getElementById("ed-verse");
    if (vs) vs.addEventListener("change", function () { form.setAttribute("data-verse", vs.value); openForm(id); });
    document.getElementById("ed-set").addEventListener("click", function () { commit(id, verse, inp.value); });
    document.getElementById("ed-clear").addEventListener("click", function () { commit(id, verse, ""); });
    document.getElementById("ed-close").addEventListener("click", closeForm);
    inp.focus();
    inp.select();
  }

  function live(id, verse, typed) {
    var t = typed.trim();
    draft = { id: id, verse: verse, syllable: t.replace(/-$/, ""), syllabic: syllabicFor(id, verse, t) };
    draw();
  }

  function commit(id, verse, typed) {
    var t = typed.trim();
    var syl = t.replace(/-$/, "");
    var sb = syl ? syllabicFor(id, verse, t) : null;
    draft = null;
    var v = id.split(":")[0];
    var bar = D.ed[id][0];
    var did = customId(v, verse, bar);
    var doc = edits[did] ? JSON.parse(JSON.stringify(edits[did])) :
      { id: did, slug: D.slug, kind: "custom", finding: null, voice: v, verse: verse, alternative: null, notes: [], reason: "", status: "proposed" };
    doc.notes = doc.notes.filter(function (x) { return x.id !== id; });
    var base = (D.ed[id][2] || {})[verse];
    var isBase = base ? (base[0] === syl && base[1] === sb) : !syl;
    if (!isBase) doc.notes.push(noteRec(id, syl, sb));
    doc.notes.sort(function (a, b) { return idxOf(v)[a.id] - idxOf(v)[b.id]; });
    var why = document.getElementById("ed-why");
    if (why && why.value.trim()) doc.reason = why.value.trim();
    if (!doc.notes.length) withdraw(did);
    else put(doc);
    openForm(id);
  }

  function closeForm() {
    draft = null;
    selNote = null;
    form.innerHTML = editMode ? '<p class="note">Click a note in the score to set the syllable that starts on it.</p>' : "";
    draw();
  }

  // ------------------------------------------------------------ the list of edits
  var listEl = document.getElementById("ed-list");
  var stEl = document.getElementById("ed-db");
  var jsonEl = document.getElementById("ed-json");
  var copyBtn = document.getElementById("ed-copy");
  var copyMsg = document.getElementById("ed-copied");

  function setDbState(s, msg) {
    dbState = s;
    stEl.textContent = msg;
    stEl.className = "note ed-db " + s;
  }

  function summary(d) {
    return d.notes.map(function (x) {
      return x.where + " " + (x.syllable ? x.syllable + (x.syllabic === "begin" || x.syllabic === "middle" ? "-" : "") : "·");
    }).join(", ");
  }

  function renderList() {
    var ids = Object.keys(edits).sort();
    document.getElementById("ed-count").textContent = ids.length ? "(" + ids.length + ")" : "";
    listEl.innerHTML = ids.length ? ids.map(function (id) {
      var d = edits[id];
      var st = stateOf(id);
      var what = d.kind === "alternative"
        ? (d.alternative ? "alternative " + d.alternative : "current reading kept") + " for " + esc(d.rule || "") + " " + esc(d.finding.split("|").slice(4, 5).join(""))
        : "custom underlay";
      return '<li><div class="ed-l1"><b>' + esc(d.voice) + (d.verse !== "1" ? " v" + esc(d.verse) : "") + "</b> · " + what +
        ' <span class="pill ed-pill' + (st === "saved" ? " ok" : "") + '">' + esc(st) + (st === "saved" ? " ✓" : "") + "</span></div>" +
        '<div class="ed-l2 mono">' + esc(summary(d)) + "</div>" +
        (d.reason ? '<div class="ed-l2">“' + esc(d.reason) + '”</div>' : "") +
        '<div class="ed-l3"><button type="button" class="btn small" data-show="' + esc(id) + '">Show</button>' +
        '<button type="button" class="btn small" data-del="' + esc(id) + '">Withdraw</button></div></li>';
    }).join("") : '<li class="note">No edits yet. Firm a reading from a finding, or use “Edit underlay” on the score.</li>';
    jsonEl.value = exportJson();
  }

  listEl.addEventListener("click", function (e) {
    var b = e.target.closest("button");
    if (!b) return;
    var id = b.getAttribute("data-show") || b.getAttribute("data-del");
    var d = edits[id];
    if (!d) return;
    if (b.hasAttribute("data-del")) { withdraw(id); return; }
    if (d.kind === "alternative") {
      var f = D.findings.filter(function (x) { return x.fingerprint === d.finding; })[0];
      if (f) { RV.show(f.n, true); return; }
    }
    RV.highlight(d.notes.map(function (x) { return x.id; }), true);
  });

  function clean(d) {
    var o = {};
    Object.keys(d).forEach(function (k) { if (k.charAt(0) !== "_") o[k] = d[k]; });
    return JSON.parse(JSON.stringify(o));
  }

  function exportJson() {
    return JSON.stringify(Object.keys(edits).sort().map(function (k) { return clean(edits[k]); }), null, 1);
  }

  copyBtn.addEventListener("click", function () {
    var text = exportJson();
    jsonEl.value = text;
    function fallback() {
      jsonEl.hidden = false;
      jsonEl.focus();
      jsonEl.select();
      copyMsg.textContent = "Selected: copy it with your keyboard or menu.";
    }
    try {
      if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(text).then(function () {
          copyMsg.textContent = "Copied " + Object.keys(edits).length + " edits. Paste them into the chat.";
        }, fallback);
      } else fallback();
    } catch (e) { fallback(); }
  });
  document.getElementById("ed-showjson").addEventListener("click", function () {
    jsonEl.hidden = !jsonEl.hidden;
    if (!jsonEl.hidden) jsonEl.value = exportJson();
  });

  function refresh() {
    renderList();
    renderBox();
    RV.renderList();
    draw();
  }

  // ------------------------------------------------------------ the store
  setDbState("waiting", "Looking for the page's shared store… Edits are kept in this page meanwhile.");
  function noDb() {
    setDbState("off", "Not saving to a shared store here (a local copy, or signed out). Edits stay in this browser; " +
      "use “Copy edits as JSON” and paste them into the chat.");
  }
  var use = window.claude && typeof window.claude.use === "function" ? window.claude.use : null;
  if (!use) noDb();
  else {
    Promise.all([use.call(window.claude, "db"), use.call(window.claude, "user")]).then(function (r) {
      db = r[0];
      var user = r[1];
      if (!db) { noDb(); return; }
      setDbState("on", "Saving each edit to this page's shared store, where Claude can read it.");
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
            if (!mine || (d.updatedAt || "") > (mine.updatedAt || "")) edits[id] = saved[id];
          });
          Object.keys(saved).forEach(function (id) { if (!seen[id]) delete saved[id]; });
          // local edits the store has never had: send them
          Object.keys(edits).forEach(function (id) {
            if (!saved[id] && !edits[id]._sent) {
              edits[id]._sent = true;
              var body = clean(edits[id]);
              db.collection("edits").doc(id).set(body).catch(function () {});
            }
          });
          lsSave();
          refresh();
        }, function (err) {
          setDbState("error", "The shared store stopped answering (" + (err && err.code || "error") + "). Copy the edits as JSON.");
        });
      });
    }, noDb);
  }

  lsLoad();
  Object.keys(edits).forEach(function (id) { if (edits[id]) delete edits[id]._sent; });
  renderList();
  var n0 = RV.current();
  if (n0 != null) {
    var f0 = D.findings[n0], fm = f0 && firmedOf(f0);
    preview = { n: n0, k: fm ? fm.alternative : 0 };
  }
  renderBox();
  RV.renderList();
  draw();
})();

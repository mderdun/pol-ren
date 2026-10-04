// Review page behaviour (tools/analyser/review.py). No storage, no requests.
(function () {
  "use strict";
  var D = JSON.parse(document.getElementById("data").textContent);
  var paper = document.getElementById("paper");
  var list = document.getElementById("findings");
  var detail = document.getElementById("detail");
  var count = document.getElementById("f-count");
  var sel = { level: document.getElementById("f-level"), rule: document.getElementById("f-rule"),
              voice: document.getElementById("f-voice"), acc: document.getElementById("f-acc") };
  var reduce = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  var current = null;

  function esc(s) {
    return String(s == null ? "" : s).replace(/[&<>"]/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c];
    });
  }

  // music21 names (E5, B-3, F#4) as Helmholtz pitch (e″, b♭, f♯′); c′ is middle C
  function pitch(n) {
    var m = /^([A-G])(#|##|-|--)?(-?\d+)$/.exec(n || "");
    if (!m) return n || "";
    var acc = { "#": "♯", "##": "𝄪", "-": "♭", "--": "𝄫" }[m[2] || ""] || "";
    var o = parseInt(m[3], 10);
    var s = m[1];
    if (o >= 3) s = s.toLowerCase();
    var marks = o >= 4 ? "′".repeat(o - 3) : (o <= 1 ? ",".repeat(2 - o) : "");
    return s + acc + marks;
  }

  // ---------------------------------------------------------------- score
  var byNote = {};
  Array.prototype.forEach.call(paper.querySelectorAll(".nh"), function (g) {
    g.getAttribute("data-n").split(" ").forEach(function (id) {
      (byNote[id] = byNote[id] || []).push(g);
    });
  });
  var pages = paper.querySelectorAll("svg.score-page");

  function clearHl() {
    Array.prototype.forEach.call(paper.querySelectorAll(".nh.hl"), function (g) { g.classList.remove("hl"); });
    Array.prototype.forEach.call(paper.querySelectorAll(".layer-hl"), function (g) { g.textContent = ""; });
  }

  function highlight(ids, scroll) {
    clearHl();
    var first = null;
    ids.forEach(function (id) {
      (byNote[id] || []).forEach(function (g) { g.classList.add("hl"); if (!first) first = g; });
      var p = D.pos[id];
      if (p && pages[p[0]]) {
        var layer = pages[p[0]].querySelector(".layer-hl");
        if (layer) {
          var c = document.createElementNS("http://www.w3.org/2000/svg", "circle");
          c.setAttribute("cx", (p[1] + 0.65).toFixed(2));
          c.setAttribute("cy", p[2].toFixed(2));
          c.setAttribute("r", "1.9");
          layer.appendChild(c);
        }
      }
    });
    if (first && scroll) {
      try { first.scrollIntoView({ behavior: reduce ? "auto" : "smooth", block: "center", inline: "center" }); }
      catch (e) { first.scrollIntoView(); }
    }
    return first !== null;
  }

  Array.prototype.forEach.call(document.querySelectorAll("[data-layer]"), function (box) {
    function apply() { paper.classList.toggle("show-" + box.getAttribute("data-layer"), box.checked); }
    box.addEventListener("change", apply);
    apply();
  });

  // the score starts at the width of its panel (at least 700px, so that a phone
  // scrolls it sideways rather than shrinking it); the buttons step by a quarter
  var w = Math.max(700, (paper.clientWidth || 1100) - 2);
  function setWidth() { document.documentElement.style.setProperty("--score-w", Math.round(w) + "px"); }
  document.getElementById("z-in").addEventListener("click", function () { w = Math.min(3200, w * 1.25); setWidth(); });
  document.getElementById("z-out").addEventListener("click", function () { w = Math.max(500, w / 1.25); setWidth(); });
  setWidth();

  // ---------------------------------------------------------------- findings
  var LEVELS = { "break": 0, warn: 1, look: 2, info: 3 };

  function visible(f) {
    var lv = sel.level.value;
    if (lv === "open" && f.level === "info") return false;
    if (lv !== "open" && lv !== "all" && f.level !== lv) return false;
    if (sel.rule.value && f.rule !== sel.rule.value) return false;
    if (sel.voice.value && f.voice !== sel.voice.value) return false;
    if (sel.acc.checked && f.status === "accepted") return false;
    return true;
  }

  function renderList() {
    var fs = D.findings.filter(visible);
    fs.sort(function (a, b) {
      return (LEVELS[a.level] - LEVELS[b.level]) || ((b.regret || 0) - (a.regret || 0)) || (a.n - b.n);
    });
    count.textContent = fs.length + " of " + D.findings.length + " findings, ranked by level, then regret";
    list.innerHTML = fs.map(function (f) {
      var rg = f.regret == null ? "—" : f.regret.toFixed(2);
      var st = f.status === "new" ? '<span class="pill st-new">new</span>'
        : (f.status === "info" ? "" : '<span class="pill">' + esc(f.status) + "</span>");
      return '<li><button type="button" class="fi ' + esc(f.level) + '" data-f="' + f.n + '"' +
        (current === f.n ? ' aria-current="true"' : "") + '>' +
        '<span class="stripe"></span><span class="rgn" title="regret">' + rg + "</span>" +
        '<span class="t1"><b>' + esc(f.rule) + "</b>" + esc(f.voice) + (f.verse !== "1" ? " v" + esc(f.verse) : "") +
        " · " + esc(f.where) + " · " + esc(f.level) + " " + st + "</span>" +
        '<span class="t2">' + esc(f.message) + "</span></button></li>";
    }).join("") || '<li class="note">No findings match.</li>';
  }

  function gridHtml(f) {
    var g = f.grid;
    if (!g) return "";
    var head = '<tr><th scope="col">Bar</th>' + g.cols.map(function (c) {
      return '<th class="' + (c.hit ? "hit" : "") + '">' + esc(c.w) + "</th>";
    }).join("") + "</tr>" +
      '<tr><th scope="col">Note</th>' + g.cols.map(function (c) {
        return '<th class="pitch' + (c.hit ? " hit" : "") + '">' + esc(pitch(c.p)) +
          '<br><span class="val">' + esc(c.d) + "</span></th>";
      }).join("") + "</tr>";
    var cur = g.rows[0].cells;
    var body = g.rows.map(function (r, k) {
      return '<tr class="' + (k === 0 ? "cur" : "") + '"><th scope="row">' + esc(r.label) + "</th>" +
        r.cells.map(function (c, i) {
          var cls = [];
          if (k > 0 && c !== cur[i] && !(c === "–" && cur[i] === "–")) cls.push("chg");
          if (c === "–") cls.push("cont");
          if (g.cols[i].hit) cls.push("hit");
          return '<td class="' + cls.join(" ") + '">' + esc(c) + "</td>";
        }).join("") + "</tr>";
    }).join("");
    return '<div class="grid-wrap"><table class="ug"><thead>' + head + "</thead><tbody>" + body +
      "</tbody></table></div>" +
      '<p class="note">One column per note (bar.minim; values L B S M Sm F, a dot for a dotted value). ' +
      "A syllable stands where it starts; a dash carries it on; red marks what an alternative changes; " +
      "shaded columns are the finding's notes. * marks a word sung again.</p>";
  }

  function altsHtml(f) {
    if (!f.alternatives.length) {
      return f.level === "break"
        ? '<p class="note">No legal reading here, moving syllables or dropping a word (10.13). The text or the notes may need changing.</p>'
        : '<p class="note">No better legal reading nearby: nothing to change.</p>';
    }
    return '<ol class="alts">' + f.alternatives.map(function (a, k) {
      var cost = a.basis === "total" ? "cost " + a.cost.toFixed(2) + " (the current reading is not legal)"
        : (a.cost > 0 ? "+" : "") + a.cost.toFixed(2) + " in total cost";
      var ed = a.edit ? ' <span class="pill pill-on">' + (a.edit === "drop" ? "drops a word, 10.13" : "repeats a word, 10.9") + "</span>" : "";
      return "<li><b>Alternative " + (k + 1) + "</b> · " + esc(cost) + ed + "<br>" +
        '<span class="mono">' + esc(a.moves.join("; ")) + "</span>" +
        (a.fixes.length ? "<br>Fixes " + esc(a.fixes.join(", ")) : "") +
        (a.introduces.length ? "<br>Costs " + esc(a.introduces.join(", ")) : "") + "</li>";
    }).join("") + "</ol>";
  }

  function explain(f) {
    var r = D.rules[f.rule] || {};
    var gates = Object.keys(r.gates || {});
    var applied = f.gates.length ? f.gates.join(", ") : "none applied";
    var gl = gates.map(function (g) {
      return "<li><b>" + esc(g) + "</b> ×" + esc(r.gates[g]) + ": " + esc(D.gates[g] || "") + "</li>";
    }).join("");
    var amount = r.weight ? f.cost / r.weight : 0;
    var lines = [];
    if (r.firm) lines.push("A firm rule: it decides which readings are legal. A break is always reported.");
    lines.push("Weight " + r.weight + " (" + esc(r.tier) + " tier); gates applied: " + esc(applied) +
      "; cost " + f.cost.toFixed(2) + (r.weight ? " (amount " + amount.toFixed(2) + " before gates)" : "") + ".");
    if (f.breakdown.length) lines.push("Costs around it: " + esc(f.breakdown.join("; ")) + ".");
    if (f.regret != null) {
      var best = f.alternatives.length ? f.alternatives[0] : null;
      lines.push("Regret " + f.regret.toFixed(2) + ": this finding's share of what the best legal reading that solves it gains" +
        (best && best.basis === "change" ? " (that reading changes the total by " + best.cost.toFixed(2) + ")" : "") +
        ". Levels: warn from " + D.levels.warn + ", look from " + D.levels.look + ".");
    }
    return "<p>" + lines.join("<br>") + "</p>" + (gl ? "<details><summary>Gates this rule accepts</summary><ul>" + gl + "</ul></details>" : "");
  }

  function show(n, scroll) {
    var f = D.findings[n];
    if (!f) return;
    current = n;
    renderList();
    var r = D.rules[f.rule] || {};
    var ptext = D.principles[f.principle] || "";
    var principle = ptext
      ? '<details class="principle"' + (ptext.length < 420 ? " open" : "") + "><summary>Principles " + esc(f.principle) +
        "</summary>" + esc(ptext) + "</details>"
      : '<p class="principle">Principles ' + esc(f.principle) + "</p>";
    detail.innerHTML =
      '<div class="dh"><span class="code">' + esc(f.rule) + "</span><h2>" + esc(f.name) + "</h2>" +
      '<span class="pill ' + (f.level === "break" ? "pill-on" : "") + '">' + esc(f.level) + "</span>" +
      (f.status === "info" ? "" : '<span class="pill ' + (f.status === "new" ? "st-new" : "") + '">' + esc(f.status) + "</span>") + "</div>" +
      '<div class="body"><p class="msg">' + esc(f.message) + "</p>" +
      '<dl class="kv"><dt>Where</dt><dd>' + esc(f.voice) + ", verse " + esc(f.verse) + ", bar " + esc(f.where) +
      " · ‘" + esc(f.text) + "’ of " + esc(f.word) + "</dd>" +
      "<dt>Source</dt><dd class=\"mono\">" + esc(f.src || "—") + "</dd>" +
      "<dt>Authority</dt><dd>" + esc(r.authority || "") + "</dd>" +
      (f.baseline ? "<dt>Baseline</dt><dd>" + esc(f.baseline.replace(/^pending: /, "")) + "</dd>" : "") +
      '<dt>Fingerprint</dt><dd class="mono">' + esc(f.fingerprint) + "</dd></dl>" +
      principle + explain(f) +
      "<h3>The notes, as they stand and as the alternatives would set them</h3>" + gridHtml(f) + altsHtml(f) +
      "</div>";
    var found = highlight(f.notes, scroll);
    if (!found && scroll) detail.scrollIntoView({ behavior: reduce ? "auto" : "smooth", block: "start" });
  }

  list.addEventListener("click", function (e) {
    var b = e.target.closest("[data-f]");
    if (b) show(parseInt(b.getAttribute("data-f"), 10), true);
  });
  Array.prototype.forEach.call(document.querySelectorAll(".tops [data-f]"), function (b) {
    b.addEventListener("click", function () { show(parseInt(b.getAttribute("data-f"), 10), true); });
  });
  Array.prototype.forEach.call(document.querySelectorAll(".lvl"), function (b) {
    b.addEventListener("click", function () {
      sel.level.value = b.getAttribute("data-level");
      renderList();
      list.scrollIntoView({ behavior: reduce ? "auto" : "smooth", block: "start" });
    });
  });
  ["level", "rule", "voice"].forEach(function (k) { sel[k].addEventListener("change", renderList); });
  sel.acc.addEventListener("change", renderList);

  // analysis tables: a row finds its notes
  Array.prototype.forEach.call(document.querySelectorAll("tr.pick"), function (tr) {
    function go() { highlight(tr.getAttribute("data-notes").split(" ").filter(Boolean), true); }
    tr.addEventListener("click", go);
    tr.addEventListener("keydown", function (e) { if (e.key === "Enter" || e.key === " ") { e.preventDefault(); go(); } });
  });

  renderList();
  var open = D.findings.filter(function (f) { return f.level !== "info" && f.status !== "accepted"; })
    .sort(function (a, b) { return (b.regret || 0) - (a.regret || 0); });
  if (open.length) show(open[0].n, false);
})();

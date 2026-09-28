/* @ds-bundle: {"format":4,"namespace":"StudyDesignSystem_e20cf4","components":[{"name":"DueForecast","sourcePath":"components/chart/DueForecast.jsx"},{"name":"PracticeHeatmap","sourcePath":"components/chart/PracticeHeatmap.jsx"},{"name":"Tip","sourcePath":"components/chart/Tip.jsx"},{"name":"TopicStrips","sourcePath":"components/chart/TopicStrips.jsx"},{"name":"Band","sourcePath":"components/core/Band.jsx"},{"name":"Button","sourcePath":"components/core/Button.jsx"},{"name":"Card","sourcePath":"components/core/Card.jsx"},{"name":"Collapsible","sourcePath":"components/core/Collapsible.jsx"},{"name":"Dialog","sourcePath":"components/core/Dialog.jsx"},{"name":"EmptyState","sourcePath":"components/core/EmptyState.jsx"},{"name":"FileTabs","sourcePath":"components/core/FileTabs.jsx"},{"name":"Icon","sourcePath":"components/core/Icon.jsx"},{"name":"Input","sourcePath":"components/core/Input.jsx"},{"name":"Kbd","sourcePath":"components/core/Kbd.jsx"},{"name":"NoteField","sourcePath":"components/core/NoteField.jsx"},{"name":"SortReset","sourcePath":"components/data/SortReset.jsx"},{"name":"Table","sourcePath":"components/data/Table.jsx"},{"name":"TaskPath","sourcePath":"components/data/TaskPath.jsx"},{"name":"TrackRail","sourcePath":"components/data/TrackRail.jsx"},{"name":"ConflictBanner","sourcePath":"components/feedback/ConflictBanner.jsx"},{"name":"FailedCase","sourcePath":"components/feedback/FailedCase.jsx"},{"name":"GraceNotice","sourcePath":"components/feedback/GraceNotice.jsx"},{"name":"NoticeBanner","sourcePath":"components/feedback/NoticeBanner.jsx"},{"name":"ResultBanner","sourcePath":"components/feedback/ResultBanner.jsx"},{"name":"StuckNudge","sourcePath":"components/feedback/StuckNudge.jsx"},{"name":"Select","sourcePath":"components/form/Select.jsx"},{"name":"Toggle","sourcePath":"components/form/Toggle.jsx"},{"name":"SpecText","sourcePath":"components/spec/SpecText.jsx"},{"name":"DepLineage","sourcePath":"components/status/DepLineage.jsx"},{"name":"RequiresTag","sourcePath":"components/status/RequiresTag.jsx"},{"name":"RowFlags","sourcePath":"components/status/RowFlags.jsx"},{"name":"StatusBadge","sourcePath":"components/status/StatusBadge.jsx"},{"name":"TagChip","sourcePath":"components/status/TagChip.jsx"},{"name":"Timer","sourcePath":"components/status/Timer.jsx"}],"sourceHashes":{"components/chart/DueForecast.jsx":"f8a6d678f474","components/chart/PracticeHeatmap.jsx":"ca4120d6f8d9","components/chart/Tip.jsx":"4b5c06a88bf9","components/chart/TopicStrips.jsx":"9ff0640bbd02","components/core/Band.jsx":"2e79da4ca430","components/core/Button.jsx":"9a2c42be1f53","components/core/Card.jsx":"23ab92c7c818","components/core/Collapsible.jsx":"b42006287c74","components/core/Dialog.jsx":"010059a7e434","components/core/EmptyState.jsx":"b581079445ea","components/core/Input.jsx":"856eed2c0cb1","components/core/Kbd.jsx":"c71a36a4c997","components/core/NoteField.jsx":"369a0e780b9e","components/data/SortReset.jsx":"11ae5ec48891","components/data/Table.jsx":"e1d7721538c9","components/data/TaskPath.jsx":"c2ef1facef9f","components/feedback/ConflictBanner.jsx":"7feac9153c27","components/feedback/GraceNotice.jsx":"b58aeae2f96f","components/feedback/NoticeBanner.jsx":"ca82ccf526eb","components/feedback/ResultBanner.jsx":"de3eb3cddcbf","components/feedback/StuckNudge.jsx":"29ca0a748fe3","components/form/Select.jsx":"14701314ebbd","components/form/Toggle.jsx":"3a587fbecf6b","components/spec/SpecText.jsx":"49b7ce18c8fa","components/status/DepLineage.jsx":"c74e69816a89","components/status/RequiresTag.jsx":"7599d94e04d5","components/status/RowFlags.jsx":"8634d48e607b","components/status/StatusBadge.jsx":"aa0b72d8fa0f","components/status/TagChip.jsx":"8a66f0b8aa1e","components/status/Timer.jsx":"5786b76742a5","explorations/progress-mock.js":"fa9e6360daf8","ui_kits/drillion/Catalogue.jsx":"e76a2e8d8bcb","ui_kits/drillion/Header.jsx":"639646690769","ui_kits/drillion/Progress.jsx":"bceecd626bd9","ui_kits/drillion/Settings.jsx":"152b6f8b0f5a","ui_kits/drillion/Stats.jsx":"0eac7a88552a","ui_kits/drillion/Task.jsx":"f7744de8bb40","ui_kits/drillion/data.js":"e7784aa95436"},"inlinedExternals":[],"unexposedExports":[]} */
var StudyDesignSystem_e20cf4 = (() => {
  var __defProp = Object.defineProperty;
  var __getOwnPropDesc = Object.getOwnPropertyDescriptor;
  var __getOwnPropNames = Object.getOwnPropertyNames;
  var __hasOwnProp = Object.prototype.hasOwnProperty;
  var __export = (target, all) => {
    for (var name in all)
      __defProp(target, name, { get: all[name], enumerable: true });
  };
  var __copyProps = (to2, from, except, desc) => {
    if (from && typeof from === "object" || typeof from === "function") {
      for (let key of __getOwnPropNames(from))
        if (!__hasOwnProp.call(to2, key) && key !== except)
          __defProp(to2, key, { get: () => from[key], enumerable: !(desc = __getOwnPropDesc(from, key)) || desc.enumerable });
    }
    return to2;
  };
  var __toCommonJS = (mod) => __copyProps(__defProp({}, "__esModule", { value: true }), mod);

  // entry.js
  var entry_exports = {};
  __export(entry_exports, {
    Band: () => Band,
    Button: () => Button,
    Card: () => Card,
    Collapsible: () => Collapsible,
    ConflictBanner: () => ConflictBanner,
    DepLineage: () => DepLineage,
    Dialog: () => Dialog,
    DueForecast: () => DueForecast,
    EmptyState: () => EmptyState,
    FailedCase: () => FailedCase,
    FileTabs: () => FileTabs,
    GraceNotice: () => GraceNotice,
    Icon: () => Icon,
    Input: () => Input,
    Kbd: () => Kbd,
    NoteField: () => NoteField,
    NoticeBanner: () => NoticeBanner,
    PracticeHeatmap: () => PracticeHeatmap,
    RequiresTag: () => RequiresTag,
    ResultBanner: () => ResultBanner,
    RowFlags: () => RowFlags,
    Select: () => Select,
    SortReset: () => SortReset,
    SpecText: () => SpecText,
    StatusBadge: () => StatusBadge,
    StuckNudge: () => StuckNudge,
    Table: () => Table,
    TagChip: () => TagChip,
    TaskPath: () => TaskPath,
    Timer: () => Timer,
    Tip: () => Tip,
    Toggle: () => Toggle,
    TopicStrips: () => TopicStrips,
    TrackRail: () => TrackRail
  });

  // shims/react.js
  var React = globalThis.React;
  var react_default = React;
  var { useState, useRef, useEffect, useMemo, useCallback, useLayoutEffect, useId, useContext, useReducer, useSyncExternalStore, Fragment, createElement, Children, cloneElement, isValidElement, memo, forwardRef, createContext } = React;

  // project/components/chart/Tip.jsx
  var s = { root: "tip-root" };
  function Tip({ text, x, y, className, style }) {
    const clamp = (el2) => {
      if (!el2) return;
      const w = el2.offsetWidth / 2 + 2;
      const room = (el2.offsetParent || el2.parentElement).clientWidth;
      el2.style.left = Math.min(Math.max(x, w), Math.max(w, room - w)) + "px";
    };
    return /* @__PURE__ */ react_default.createElement("div", { ref: clamp, className: [s.root, className].filter(Boolean).join(" "), style: { left: x, top: y == null ? -6 : y - 8, ...style } }, text);
  }

  // project/components/chart/DueForecast.jsx
  var s2 = { plot: "due-forecast-plot", bars: "due-forecast-bars", bar: "due-forecast-bar", count: "due-forecast-count", column: "due-forecast-column", over: "due-forecast-over", fill: "due-forecast-fill", capLine: "due-forecast-capLine", capLabel: "due-forecast-capLabel", axis: "due-forecast-axis", axisCell: "due-forecast-axisCell", dayLetter: "due-forecast-dayLetter", dayNum: "due-forecast-dayNum", foot: "due-forecast-foot", note: "due-forecast-note", spacer: "due-forecast-spacer", total: "due-forecast-total" };
  function DueForecast({ forecast = [], cap = 12, today, className, style }) {
    const start = /* @__PURE__ */ new Date((today || (/* @__PURE__ */ new Date()).toISOString().slice(0, 10)) + "T00:00:00");
    const dates = forecast.map((_2, i) => {
      const d = new Date(start);
      d.setDate(d.getDate() + i);
      return d;
    });
    const peak = Math.max(cap, ...forecast, 1);
    const H = 118;
    const px = (n) => n <= 0 ? 0 : Math.max(3, Math.round(n / peak * H));
    const total = forecast.reduce((a, b) => a + b, 0);
    const fmt2 = (d) => d.toLocaleDateString(void 0, { weekday: "short", day: "numeric", month: "short" });
    const aria = total === 0 ? "Due-load forecast: nothing due in the next fourteen days." : "Due-load forecast, " + cap + " reviews a day. " + dates.map((d, i) => fmt2(d) + " " + forecast[i]).join(", ") + ".";
    const [tip, setTip] = react_default.useState(null);
    const show = (e2, text) => setTip({ text, x: e2.currentTarget.offsetLeft + e2.currentTarget.offsetWidth / 2 });
    return /* @__PURE__ */ react_default.createElement("div", { className, style }, /* @__PURE__ */ react_default.createElement("div", { role: "img", "aria-label": aria, className: s2.plot, onMouseLeave: () => setTip(null) }, tip ? /* @__PURE__ */ react_default.createElement(Tip, { text: tip.text, x: tip.x }) : null, /* @__PURE__ */ react_default.createElement("div", { className: s2.bars }, forecast.map((n, i) => {
      const isToday = i === 0;
      const over = Math.max(0, n - cap);
      const base = n - over;
      const text = n + (n === 1 ? " task" : " tasks") + " due " + (isToday ? "today, " : "") + fmt2(dates[i]) + (over > 0 ? " \xB7 " + over + " over the cap" : "");
      return /* @__PURE__ */ react_default.createElement("div", { key: i, className: s2.bar, title: text, onMouseEnter: (e2) => show(e2, text) }, /* @__PURE__ */ react_default.createElement("div", { className: s2.count, "data-today": isToday ? "" : void 0 }, n), /* @__PURE__ */ react_default.createElement("div", { className: s2.column, style: { height: H } }, over > 0 ? /* @__PURE__ */ react_default.createElement("div", { className: s2.over, style: { height: px(over) } }) : null, /* @__PURE__ */ react_default.createElement("div", { className: s2.fill, "data-today": isToday && n !== 0 ? "" : void 0, "data-zero": n === 0 ? "" : void 0, "data-capped": over > 0 ? "" : void 0, style: { height: n === 0 ? 2 : px(base) } })));
    })), /* @__PURE__ */ react_default.createElement("div", { "aria-hidden": "true", className: s2.capLine, style: { bottom: px(cap) } }), /* @__PURE__ */ react_default.createElement("div", { "aria-hidden": "true", className: s2.capLabel, style: { bottom: px(cap) - 8 } }, cap, "/day")), /* @__PURE__ */ react_default.createElement("div", { className: s2.axis }, dates.map((d, i) => /* @__PURE__ */ react_default.createElement("div", { key: i, className: s2.axisCell }, /* @__PURE__ */ react_default.createElement("div", { className: s2.dayLetter, "data-today": i === 0 ? "" : void 0 }, "SMTWTFS"[d.getDay()]), /* @__PURE__ */ react_default.createElement("div", { className: s2.dayNum }, d.getDate())))), /* @__PURE__ */ react_default.createElement("div", { className: s2.foot }, /* @__PURE__ */ react_default.createElement("span", { className: s2.note }, total === 0 ? "Nothing due in the next two weeks. New tasks arrive as you pick them up." : "Today includes everything overdue. A day over the line spills into the next."), /* @__PURE__ */ react_default.createElement("div", { className: s2.spacer }), total === 0 ? null : /* @__PURE__ */ react_default.createElement("span", { className: s2.total }, total, " tasks over 14 days \xB7 ", forecast.filter((n) => n > cap).length, " days above the cap")));
  }

  // project/components/chart/PracticeHeatmap.jsx
  var s3 = { plot: "practice-heatmap-plot", weekdays: "practice-heatmap-weekdays", grid: "practice-heatmap-grid", months: "practice-heatmap-months", cells: "practice-heatmap-cells", cell: "practice-heatmap-cell", foot: "practice-heatmap-foot", note: "practice-heatmap-note", spacer: "practice-heatmap-spacer", scaleLabel: "practice-heatmap-scaleLabel", scale: "practice-heatmap-scale", swatch: "practice-heatmap-swatch" };
  var heatLevel = (n) => !n ? 0 : n <= 3 ? 1 : n <= 8 ? 2 : 3;
  function PracticeHeatmap({ days = {}, today, className, style, cell, gap = 4 }) {
    const box = react_default.useRef(null);
    const [auto, setAuto] = react_default.useState(cell || 11);
    react_default.useEffect(() => {
      if (cell || !box.current || typeof ResizeObserver === "undefined") return;
      const ro2 = new ResizeObserver(([e2]) => {
        const w = e2.contentRect.width - 28 - 52 * gap;
        setAuto(Math.max(8, Math.floor(w / 53)));
      });
      ro2.observe(box.current);
      return () => ro2.disconnect();
    }, [cell, gap]);
    const cellSize = cell || auto;
    const iso = (d) => d.getFullYear() + "-" + String(d.getMonth() + 1).padStart(2, "0") + "-" + String(d.getDate()).padStart(2, "0");
    const end = /* @__PURE__ */ new Date((today || (/* @__PURE__ */ new Date()).toISOString().slice(0, 10)) + "T00:00:00");
    const last = new Date(end);
    last.setDate(last.getDate() + (6 - end.getDay()));
    const first = new Date(last);
    first.setDate(first.getDate() - 53 * 7 + 1);
    const cols = [];
    for (let c = 0; c < 53; c++) {
      const week = [];
      for (let r = 0; r < 7; r++) {
        const d = new Date(first);
        d.setDate(d.getDate() + c * 7 + r);
        week.push(d);
      }
      cols.push(week);
    }
    const months = [];
    let prev = -1;
    cols.forEach((week, c) => {
      const m = week[0].getMonth();
      if (m !== prev && c < 51) {
        months.push({ c, m });
        prev = m;
      }
    });
    const labels = months.filter((x, i) => !months[i + 1] || months[i + 1].c - x.c >= 3);
    const MON = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
    const counts = Object.values(days);
    const practised = counts.filter((n) => n > 0).length;
    const passes = counts.reduce((a, b) => a + b, 0);
    const fmt2 = (d) => d.toLocaleDateString(void 0, { weekday: "short", day: "numeric", month: "short", year: "numeric" });
    const aria = "Practice over the last year: " + passes + " passes across " + practised + " days.";
    const [tip, setTip] = react_default.useState(null);
    const show = (e2, text) => setTip({ text, x: e2.currentTarget.offsetLeft + e2.currentTarget.offsetWidth / 2, y: e2.currentTarget.offsetTop });
    return /* @__PURE__ */ react_default.createElement("div", { className, style, ref: box }, /* @__PURE__ */ react_default.createElement("div", { role: "img", "aria-label": aria, className: s3.plot, onMouseLeave: () => setTip(null) }, tip ? /* @__PURE__ */ react_default.createElement(Tip, { text: tip.text, x: tip.x, y: tip.y }) : null, /* @__PURE__ */ react_default.createElement("div", { className: s3.weekdays, style: { gridTemplateRows: "14px repeat(7, " + cellSize + "px)", gap: gap + "px" } }, /* @__PURE__ */ react_default.createElement("div", null), /* @__PURE__ */ react_default.createElement("div", null), /* @__PURE__ */ react_default.createElement("div", null, "M"), /* @__PURE__ */ react_default.createElement("div", null), /* @__PURE__ */ react_default.createElement("div", null, "W"), /* @__PURE__ */ react_default.createElement("div", null), /* @__PURE__ */ react_default.createElement("div", null, "F"), /* @__PURE__ */ react_default.createElement("div", null)), /* @__PURE__ */ react_default.createElement("div", { className: s3.grid }, /* @__PURE__ */ react_default.createElement("div", { className: s3.months, style: { gap: gap + "px" } }, labels.map(({ c, m }) => /* @__PURE__ */ react_default.createElement("div", { key: c, style: { gridRow: 1, gridColumn: c + 1 + " / span 4" } }, MON[m]))), /* @__PURE__ */ react_default.createElement("div", { className: s3.cells, style: { gap: gap + "px", gridTemplateRows: "repeat(7, " + cellSize + "px)", marginTop: gap } }, cols.flatMap((week) => week.map((d) => {
      const future = d > end;
      const n = days[iso(d)] || 0;
      const text = n === 0 ? "No practice on " + fmt2(d) : n + (n === 1 ? " pass" : " passes") + " on " + fmt2(d);
      return /* @__PURE__ */ react_default.createElement(
        "div",
        {
          key: iso(d),
          onMouseEnter: future ? void 0 : (e2) => show(e2, text),
          className: s3.cell,
          "data-heat": heatLevel(n),
          "data-future": future ? "" : void 0,
          "data-round": cellSize > 14 ? "lg" : void 0,
          style: { height: cellSize }
        }
      );
    }))))), /* @__PURE__ */ react_default.createElement("div", { className: s3.foot }, /* @__PURE__ */ react_default.createElement("span", { className: s3.note }, passes === 0 ? "No passes yet. Every square fills in as you practise." : practised + " days practised in the last year"), /* @__PURE__ */ react_default.createElement("div", { className: s3.spacer }), /* @__PURE__ */ react_default.createElement("span", { className: s3.scaleLabel }, "less"), /* @__PURE__ */ react_default.createElement("div", { className: s3.scale }, [0, 1, 2, 3].map((i) => /* @__PURE__ */ react_default.createElement("div", { key: i, className: s3.swatch, "data-heat": i }))), /* @__PURE__ */ react_default.createElement("span", { className: s3.scaleLabel }, "more")));
  }

  // project/components/chart/TopicStrips.jsx
  var s4 = { head: "topic-strips-head", lede: "topic-strips-lede", spacer: "topic-strips-spacer", sorts: "topic-strips-sorts", sortBtn: "topic-strips-sortBtn", row: "topic-strips-row", headRow: "topic-strips-headRow", colLabel: "topic-strips-colLabel", body: "topic-strips-body", bodyRow: "topic-strips-bodyRow", tagCell: "topic-strips-tagCell", tagLink: "topic-strips-tagLink", strip: "topic-strips-strip", seg: "topic-strips-seg", num: "topic-strips-num", of: "topic-strips-of", foot: "topic-strips-foot", footNote: "topic-strips-footNote", legend: "topic-strips-legend", chip: "topic-strips-chip", footLabel: "topic-strips-footLabel" };
  var STRIP_SORTS = {
    "stuck first": (a, b) => (b.boxes[0] + b.boxes[1]) / Math.max(1, b.seen) - (a.boxes[0] + a.boxes[1]) / Math.max(1, a.seen) || b.seen - a.seen,
    "neglected first": (a, b) => b.total - b.seen - (a.total - a.seen),
    "most lapses": (a, b) => b.lapses - a.lapses,
    "a\u2013z": (a, b) => a.tag.localeCompare(b.tag)
  };
  function TopicStripsSort({ value, onChange }) {
    return /* @__PURE__ */ react_default.createElement("div", { className: s4.sorts }, Object.keys(STRIP_SORTS).map((k) => /* @__PURE__ */ react_default.createElement("button", { key: k, onClick: () => onChange(k), className: s4.sortBtn, "data-active": k === value ? "" : void 0 }, k)));
  }
  function TopicStrips({ tags = [], defaultSort = "stuck first", maxHeight = 520, className, style }) {
    const [sort, setSort] = react_default.useState(defaultSort);
    const rows = [...tags].sort(STRIP_SORTS[sort]);
    const widest = Math.max(1, ...tags.map((t) => t.total));
    return /* @__PURE__ */ react_default.createElement("div", { className, style }, /* @__PURE__ */ react_default.createElement("div", { className: s4.head }, /* @__PURE__ */ react_default.createElement("span", { className: s4.lede }, "One strip per topic: how well you know its tasks, shakiest on the left, most solid on the right."), /* @__PURE__ */ react_default.createElement("div", { className: s4.spacer }), /* @__PURE__ */ react_default.createElement(TopicStripsSort, { value: sort, onChange: setSort })), /* @__PURE__ */ react_default.createElement("div", { role: "table", "aria-label": "Practice spread per topic" }, /* @__PURE__ */ react_default.createElement("div", { role: "rowgroup" }, /* @__PURE__ */ react_default.createElement("div", { role: "row", className: s4.row + " " + s4.headRow }, /* @__PURE__ */ react_default.createElement("div", { role: "columnheader", className: s4.colLabel }, "Tag"), /* @__PURE__ */ react_default.createElement("div", { role: "columnheader", className: s4.colLabel }, "Spread"), /* @__PURE__ */ react_default.createElement("div", { role: "columnheader", className: s4.colLabel, "data-align": "right" }, "Lapses"), /* @__PURE__ */ react_default.createElement("div", { role: "columnheader", className: s4.colLabel, "data-align": "right" }, "Due 7"), /* @__PURE__ */ react_default.createElement("div", { role: "columnheader", className: s4.colLabel, "data-align": "right" }, "Seen"))), /* @__PURE__ */ react_default.createElement("div", { role: "rowgroup", className: s4.body, style: { maxHeight } }, rows.map((t) => /* @__PURE__ */ react_default.createElement("div", { key: t.tag, role: "row", className: s4.row + " " + s4.bodyRow }, /* @__PURE__ */ react_default.createElement("div", { role: "cell", className: s4.tagCell }, /* @__PURE__ */ react_default.createElement("a", { href: "#/?tag=" + t.tag, title: t.tag, className: s4.tagLink }, t.tag)), /* @__PURE__ */ react_default.createElement(
      "div",
      {
        role: "cell",
        className: s4.strip,
        style: { width: t.total / widest * 100 + "%" },
        title: t.tag + " \u2014 " + t.seen + " of " + t.total + " practised, " + (t.total - t.seen) + " not started"
      },
      t.boxes.map((n, i) => n ? /* @__PURE__ */ react_default.createElement("div", { key: i, className: s4.seg, "data-ramp": i, style: { flex: n } }) : null),
      t.total - t.seen > 0 ? /* @__PURE__ */ react_default.createElement("div", { className: s4.seg, "data-rest": "", style: { flex: t.total - t.seen } }) : null
    ), /* @__PURE__ */ react_default.createElement("div", { role: "cell", className: s4.num, "data-tone": "lapses", "data-some": t.lapses ? "" : void 0 }, t.lapses || "\u2014"), /* @__PURE__ */ react_default.createElement("div", { role: "cell", className: s4.num }, t.due7), /* @__PURE__ */ react_default.createElement("div", { role: "cell", className: s4.num, "data-tone": "seen" }, t.seen, /* @__PURE__ */ react_default.createElement("span", { className: s4.of }, "/", t.total)))))), /* @__PURE__ */ react_default.createElement("div", { className: s4.foot }, /* @__PURE__ */ react_default.createElement("span", { className: s4.footNote }, tags.length, " tags \xB7 strip width is the topic's size, segments run shakiest to most solid, then not started"), /* @__PURE__ */ react_default.createElement("div", { className: s4.spacer }), /* @__PURE__ */ react_default.createElement("div", { className: s4.legend }, [0, 1, 2, 3, 4, 5, 6].map((i) => /* @__PURE__ */ react_default.createElement("div", { key: i, className: s4.chip + " " + s4.seg, "data-ramp": i })), /* @__PURE__ */ react_default.createElement("div", { className: s4.chip + " " + s4.seg, "data-rest": "", title: "not started" })), /* @__PURE__ */ react_default.createElement("span", { className: s4.footLabel }, "shaky \u2192 solid \u2192 not started")));
  }

  // project/components/core/Band.jsx
  var s5 = { root: "band-root", label: "band-label", aside: "band-aside" };
  function Band({ label, aside, first = false, className, style }) {
    return /* @__PURE__ */ react_default.createElement("div", { "data-first": first ? "" : void 0, className: [s5.root, className].filter(Boolean).join(" "), style }, /* @__PURE__ */ react_default.createElement("span", { className: s5.label }, label), aside ? /* @__PURE__ */ react_default.createElement("span", { className: s5.aside }, aside) : null);
  }

  // project/components/core/Button.jsx
  var s6 = { root: "button-root", kbd: "button-kbd" };
  function Button({ variant = "primary", disabled = false, kbdHint, onClick, children, className, style }) {
    return /* @__PURE__ */ react_default.createElement(
      "button",
      {
        type: "button",
        disabled,
        onClick,
        "data-variant": variant,
        className: [s6.root, className].filter(Boolean).join(" "),
        style
      },
      children,
      kbdHint ? /* @__PURE__ */ react_default.createElement("kbd", { className: s6.kbd }, kbdHint) : null
    );
  }

  // project/components/core/Card.jsx
  var s7 = { root: "card-root", label: "card-label" };
  function Card({ label, children, padding = 20, className, style }) {
    return /* @__PURE__ */ react_default.createElement("section", { className: [s7.root, className].filter(Boolean).join(" "), style: { padding, ...style } }, label ? /* @__PURE__ */ react_default.createElement("div", { className: s7.label }, label) : null, children);
  }

  // project/components/core/icons.js
  var ICONS = {
    ChevronRight: { viewBox: "0 0 16 16", nodes: [["path", { "d": "M11 8 6 13 5.3 12.3 9.6 8 5.3 3.7 6 3z" }]] },
    // carbon: chevron--right (16px artwork)
    ChevronDown: { viewBox: "0 0 16 16", nodes: [["path", { "d": "M8 11 3 6 3.7 5.3 8 9.6 12.3 5.3 13 6z" }]] },
    // carbon: chevron--down (16px artwork)
    ArrowUp: { viewBox: "0 0 16 16", nodes: [["path", { "d": "M3.7 6.7 7.5 2.9 7.5 15 8.5 15 8.5 2.9 12.3 6.7 13 6 8 1 3 6z" }]] },
    // carbon: arrow--up (16px artwork)
    ArrowDown: { viewBox: "0 0 16 16", nodes: [["path", { "d": "M12.3 9.3 8.5 13.1 8.5 1 7.5 1 7.5 13.1 3.7 9.3 3 10 8 15 13 10z" }]] },
    // carbon: arrow--down (16px artwork)
    Reset: { viewBox: "0 0 32 32", nodes: [["path", { "d": "M18,28A12,12,0,1,0,6,16v6.2L2.4,18.6,1,20l6,6,6-6-1.4-1.4L8,22.2V16H8A10,10,0,1,1,18,26Z" }]] },
    // carbon: reset (32px artwork)
    Pause: { viewBox: "0 0 16 16", nodes: [["path", { "d": "M6,4v8H4V4H6 M6,3H4C3.4,3,3,3.4,3,4v8c0,0.6,0.4,1,1,1h2c0.6,0,1-0.4,1-1V4C7,3.4,6.6,3,6,3z" }], ["path", { "d": "M12,4v8h-2V4H12 M12,3h-2C9.4,3,9,3.4,9,4v8c0,0.6,0.4,1,1,1h2c0.6,0,1-0.4,1-1V4C13,3.4,12.6,3,12,3z" }]] },
    // carbon: pause (16px artwork)
    CheckmarkOutline: { viewBox: "0 0 32 32", nodes: [["path", { "d": "M14 21.414 9 16.413 10.413 15 14 18.586 21.585 11 23 12.415 14 21.414z" }], ["path", { "d": "M16,2A14,14,0,1,0,30,16,14,14,0,0,0,16,2Zm0,26A12,12,0,1,1,28,16,12,12,0,0,1,16,28Z" }]] },
    // carbon: checkmark--outline (32px artwork)
    CloseOutline: { viewBox: "0 0 32 32", nodes: [["path", { "d": "M16,2C8.2,2,2,8.2,2,16s6.2,14,14,14s14-6.2,14-14S23.8,2,16,2z M16,28C9.4,28,4,22.6,4,16S9.4,4,16,4s12,5.4,12,12 S22.6,28,16,28z" }], ["path", { "d": "M21.4 23 16 17.6 10.6 23 9 21.4 14.4 16 9 10.6 10.6 9 16 14.4 21.4 9 23 10.6 17.6 16 23 21.4z" }]] },
    // carbon: close--outline (32px artwork)
    Checkmark: { viewBox: "0 0 32 32", nodes: [["path", { "d": "M13 24 4 15 5.414 13.586 13 21.171 26.586 7.586 28 9 13 24z" }]] },
    // carbon: checkmark (32px artwork)
    Pending: { viewBox: "0 0 32 32", nodes: [["circle", { "cx": "9", "cy": "16", "r": "2" }], ["circle", { "cx": "23", "cy": "16", "r": "2" }], ["circle", { "cx": "16", "cy": "16", "r": "2" }], ["path", { "d": "M16,30A14,14,0,1,1,30,16,14.0158,14.0158,0,0,1,16,30ZM16,4A12,12,0,1,0,28,16,12.0137,12.0137,0,0,0,16,4Z" }]] },
    // carbon: pending (32px artwork)
    Close: { viewBox: "0 0 32 32", nodes: [["path", { "d": "M17.4141 16 24 9.4141 22.5859 8 16 14.5859 9.4143 8 8 9.4141 14.5859 16 8 22.5859 9.4143 24 16 17.4141 22.5859 24 24 22.5859 17.4141 16z" }]] },
    // carbon: close (32px artwork)
    ArrowRight: { viewBox: "0 0 16 16", nodes: [["path", { "d": "M9.3 3.7 13.1 7.5 1 7.5 1 8.5 13.1 8.5 9.3 12.3 10 13 15 8 10 3z" }]] },
    // carbon: arrow--right (16px artwork)
    CircleFill: { viewBox: "0 0 16 16", nodes: [["circle", { "cx": "8", "cy": "8", "r": "6" }]] },
    // carbon: circle-fill (16px artwork)
    Locked: { viewBox: "0 0 32 32", nodes: [["path", { "d": "M24,14H22V8A6,6,0,0,0,10,8v6H8a2,2,0,0,0-2,2V28a2,2,0,0,0,2,2H24a2,2,0,0,0,2-2V16A2,2,0,0,0,24,14ZM12,8a4,4,0,0,1,8,0v6H12ZM24,28H8V16H24Z" }]] },
    // carbon: locked (32px artwork)
    Unlocked: { viewBox: "0 0 16 16", nodes: [["path", { "d": "M12,7H6V4c0-1.1,0.9-2,2-2s2,0.9,2,2h1c0-1.7-1.3-3-3-3S5,2.3,5,4v3H4C3.4,7,3,7.4,3,8v6c0,0.6,0.4,1,1,1h8c0.6,0,1-0.4,1-1 V8C13,7.4,12.6,7,12,7z M12,14H4V8h8V14z" }]] },
    // carbon: unlocked (16px artwork)
    WarningAlt: { viewBox: "0 0 16 16", nodes: [["path", { "d": "M14.5,14h-13c-0.2,0-0.3-0.1-0.4-0.2c-0.1-0.2-0.1-0.3,0-0.5l6.5-12C7.7,1,8,0.9,8.2,1.1c0.1,0,0.2,0.1,0.2,0.2l6.5,12 c0.1,0.2,0.1,0.3,0,0.5C14.9,13.9,14.7,14,14.5,14z M2.3,13h11.3L8,2.5L2.3,13z" }], ["path", { "d": "M7.5 6H8.5V9.5H7.5z" }], ["path", { "d": "M8,10.8c-0.4,0-0.8,0.3-0.8,0.8s0.3,0.8,0.8,0.8c0.4,0,0.8-0.3,0.8-0.8S8.4,10.8,8,10.8z" }]] },
    // carbon: warning--alt (16px artwork)
    Information: { viewBox: "0 0 16 16", nodes: [["path", { "d": "M8.5 11 8.5 6.5 6.5 6.5 6.5 7.5 7.5 7.5 7.5 11 6 11 6 12 10 12 10 11z" }], ["path", { "d": "M8,3.5c-0.4,0-0.8,0.3-0.8,0.8S7.6,5,8,5c0.4,0,0.8-0.3,0.8-0.8S8.4,3.5,8,3.5z" }], ["path", { "d": "M8,15c-3.9,0-7-3.1-7-7s3.1-7,7-7s7,3.1,7,7S11.9,15,8,15z M8,2C4.7,2,2,4.7,2,8s2.7,6,6,6s6-2.7,6-6S11.3,2,8,2z" }]] },
    // carbon: information (16px artwork)
    Idea: { viewBox: "0 0 32 32", nodes: [["path", { "d": "M11 24H21V26H11z" }], ["path", { "d": "M13 28H19V30H13z" }], ["path", { "d": "M16,2A10,10,0,0,0,6,12a9.19,9.19,0,0,0,3.46,7.62c1,.93,1.54,1.46,1.54,2.38h2c0-1.84-1.11-2.87-2.19-3.86A7.2,7.2,0,0,1,8,12a8,8,0,0,1,16,0,7.2,7.2,0,0,1-2.82,6.14c-1.07,1-2.18,2-2.18,3.86h2c0-.92.53-1.45,1.54-2.39A9.18,9.18,0,0,0,26,12,10,10,0,0,0,16,2Z" }]] },
    // carbon: idea (32px artwork)
    Play: { viewBox: "0 0 16 16", nodes: [["path", { "d": "M3.5,14C3.2,14,3,13.8,3,13.5v-11c0-0.2,0.1-0.3,0.2-0.4C3.4,2,3.6,2,3.8,2.1l9.5,5.5c0.2,0.1,0.3,0.4,0.2,0.7 c0,0.1-0.1,0.1-0.2,0.2l-9.5,5.5C3.7,14,3.6,14,3.5,14z M4,3.4v9.3L12,8L4,3.4z" }]] },
    // carbon: play (16px artwork)
    Send: { viewBox: "0 0 32 32", nodes: [["path", { "d": "M27.45,15.11l-22-11a1,1,0,0,0-1.08.12,1,1,0,0,0-.33,1L7,16,4,26.74A1,1,0,0,0,5,28a1,1,0,0,0,.45-.11l22-11a1,1,0,0,0,0-1.78Zm-20.9,10L8.76,17H18V15H8.76L6.55,6.89,24.76,16Z" }]] },
    // carbon: send (32px artwork)
    Search: { viewBox: "0 0 16 16", nodes: [["path", { "d": "M15,14.3L10.7,10c1.9-2.3,1.6-5.8-0.7-7.7S4.2,0.7,2.3,3S0.7,8.8,3,10.7c2,1.7,5,1.7,7,0l4.3,4.3L15,14.3z M2,6.5 C2,4,4,2,6.5,2S11,4,11,6.5S9,11,6.5,11S2,9,2,6.5z" }]] },
    // carbon: search (16px artwork)
    Settings: { viewBox: "0 0 16 16", nodes: [["path", { "d": "M13.5,8.4c0-0.1,0-0.3,0-0.4c0-0.1,0-0.3,0-0.4l1-0.8c0.4-0.3,0.4-0.9,0.2-1.3l-1.2-2C13.3,3.2,13,3,12.6,3 c-0.1,0-0.2,0-0.3,0.1l-1.2,0.4c-0.2-0.1-0.4-0.3-0.7-0.4l-0.3-1.3C10.1,1.3,9.7,1,9.2,1H6.8c-0.5,0-0.9,0.3-1,0.8L5.6,3.1 C5.3,3.2,5.1,3.3,4.9,3.4L3.7,3C3.6,3,3.5,3,3.4,3C3,3,2.7,3.2,2.5,3.5l-1.2,2C1.1,5.9,1.2,6.4,1.6,6.8l0.9,0.9c0,0.1,0,0.3,0,0.4 c0,0.1,0,0.3,0,0.4L1.6,9.2c-0.4,0.3-0.5,0.9-0.2,1.3l1.2,2C2.7,12.8,3,13,3.4,13c0.1,0,0.2,0,0.3-0.1l1.2-0.4 c0.2,0.1,0.4,0.3,0.7,0.4l0.3,1.3c0.1,0.5,0.5,0.8,1,0.8h2.4c0.5,0,0.9-0.3,1-0.8l0.3-1.3c0.2-0.1,0.4-0.2,0.7-0.4l1.2,0.4 c0.1,0,0.2,0.1,0.3,0.1c0.4,0,0.7-0.2,0.9-0.5l1.1-2c0.2-0.4,0.2-0.9-0.2-1.3L13.5,8.4z M12.6,12l-1.7-0.6c-0.4,0.3-0.9,0.6-1.4,0.8 L9.2,14H6.8l-0.4-1.8c-0.5-0.2-0.9-0.5-1.4-0.8L3.4,12l-1.2-2l1.4-1.2c-0.1-0.5-0.1-1.1,0-1.6L2.2,6l1.2-2l1.7,0.6 C5.5,4.2,6,4,6.5,3.8L6.8,2h2.4l0.4,1.8c0.5,0.2,0.9,0.5,1.4,0.8L12.6,4l1.2,2l-1.4,1.2c0.1,0.5,0.1,1.1,0,1.6l1.4,1.2L12.6,12z" }], ["path", { "d": "M8,11c-1.7,0-3-1.3-3-3s1.3-3,3-3s3,1.3,3,3C11,9.6,9.7,11,8,11C8,11,8,11,8,11z M8,6C6.9,6,6,6.8,6,7.9C6,7.9,6,8,6,8 c0,1.1,0.8,2,1.9,2c0,0,0.1,0,0.1,0c1.1,0,2-0.8,2-1.9c0,0,0-0.1,0-0.1C10,6.9,9.2,6,8,6C8.1,6,8,6,8,6z" }]] },
    // carbon: settings (16px artwork)
    Sun: { viewBox: "0 0 32 32", nodes: [["path", { "d": "M16,12a4,4,0,1,1-4,4,4.0045,4.0045,0,0,1,4-4m0-2a6,6,0,1,0,6,6,6,6,0,0,0-6-6Z", "transform": "translate(0 .005)" }], ["path", { "d": "M6.854 5.375H8.854V10.333H6.854z", "transform": "rotate(-45 7.86 7.856)" }], ["path", { "d": "M2 15.005H7V17.005000000000003H2z" }], ["path", { "d": "M5.375 23.147H10.333V25.147H5.375z", "transform": "rotate(-45 7.86 24.149)" }], ["path", { "d": "M15 25.005H17V30.005H15z" }], ["path", { "d": "M23.147 21.668H25.147V26.625999999999998H23.147z", "transform": "rotate(-45 24.152 24.149)" }], ["path", { "d": "M25 15.005H30V17.005000000000003H25z" }], ["path", { "d": "M21.668 6.854H26.625999999999998V8.854H21.668z", "transform": "rotate(-45 24.152 7.856)" }], ["path", { "d": "M15 2.005H17V7.005H15z" }]] },
    // carbon: sun (32px artwork)
    Asleep: { viewBox: "0 0 16 16", nodes: [["path", { "d": "M7.2,2.3c-1,4.4,1.7,8.7,6.1,9.8c0.1,0,0.1,0,0.2,0c-1.1,1.2-2.7,1.8-4.3,1.8c-0.1,0-0.2,0-0.2,0C5.6,13.8,3,11,3.2,7.7 C3.2,5.3,4.8,3.1,7.2,2.3 M8,1L8,1C4.1,1.6,1.5,5.3,2.1,9.1c0.6,3.3,3.4,5.8,6.8,5.9c0.1,0,0.2,0,0.3,0c2.3,0,4.4-1.1,5.8-3 c0.2-0.2,0.1-0.6-0.1-0.7c-0.1-0.1-0.2-0.1-0.3-0.1c-3.9-0.3-6.7-3.8-6.4-7.6C8.3,3,8.4,2.4,8.6,1.8c0.1-0.3,0-0.6-0.3-0.7 C8.1,1,8.1,1,8,1z" }]] },
    // carbon: asleep (16px artwork)
    Folder: { viewBox: "0 0 32 32", nodes: [["path", { "d": "M11.17,6l3.42,3.41.58.59H28V26H4V6h7.17m0-2H4A2,2,0,0,0,2,6V26a2,2,0,0,0,2,2H28a2,2,0,0,0,2-2V10a2,2,0,0,0-2-2H16L12.59,4.59A2,2,0,0,0,11.17,4Z" }]] },
    // carbon: folder (32px artwork)
    DataBase: { viewBox: "0 0 32 32", nodes: [["path", { "d": "M24,3H8A2,2,0,0,0,6,5V27a2,2,0,0,0,2,2H24a2,2,0,0,0,2-2V5A2,2,0,0,0,24,3Zm0,2v6H8V5ZM8,19V13H24v6Zm0,8V21H24v6Z" }], ["circle", { "cx": "11", "cy": "8", "r": "1" }], ["circle", { "cx": "11", "cy": "16", "r": "1" }], ["circle", { "cx": "11", "cy": "24", "r": "1" }]] },
    // carbon: data--base (32px artwork)
    Copy: { viewBox: "0 0 32 32", nodes: [["path", { "d": "M28,10V28H10V10H28m0-2H10a2,2,0,0,0-2,2V28a2,2,0,0,0,2,2H28a2,2,0,0,0,2-2V10a2,2,0,0,0-2-2Z" }], ["path", { "d": "M4,18H2V4A2,2,0,0,1,4,2H18V4H4Z" }]] },
    // carbon: copy (32px artwork)
    Download: { viewBox: "0 0 16 16", nodes: [["path", { "d": "M13 7 12.3 6.3 8.5 10.1 8.5 1 7.5 1 7.5 10.1 3.7 6.3 3 7 8 12z" }], ["path", { "d": "M13,12v2H3v-2H2v2l0,0c0,0.6,0.4,1,1,1h10c0.6,0,1-0.4,1-1l0,0v-2H13z" }]] },
    // carbon: download (16px artwork)
    Upload: { viewBox: "0 0 16 16", nodes: [["path", { "d": "M3 9 3.7 9.7 7.5 5.9 7.5 15 8.5 15 8.5 5.9 12.3 9.7 13 9 8 4z" }], ["path", { "d": "M3,4V2h10v2h1V2c0-0.6-0.4-1-1-1H3C2.4,1,2,1.4,2,2v2H3z" }]] },
    // carbon: upload (16px artwork)
    Archive: { viewBox: "0 0 32 32", nodes: [["path", { "d": "M14 19H18V21H14z" }], ["path", { "d": "M6,2V28a2,2,0,0,0,2,2H24a2,2,0,0,0,2-2V2ZM24,28H8V16H24Zm0-14H8V10H24ZM8,8V4H24V8Z" }]] },
    // carbon: archive (32px artwork)
    TrashCan: { viewBox: "0 0 32 32", nodes: [["path", { "d": "M12 12H14V24H12z" }], ["path", { "d": "M18 12H20V24H18z" }], ["path", { "d": "M4,6V8H6V28a2,2,0,0,0,2,2H24a2,2,0,0,0,2-2V8h2V6ZM8,28V8H24V28Z" }], ["path", { "d": "M12 2H20V4H12z" }]] },
    // carbon: trash-can (32px artwork)
    ArrowLeft: { viewBox: "0 0 16 16", nodes: [["path", { "d": "M6.7 12.3 2.9 8.5 15 8.5 15 7.5 2.9 7.5 6.7 3.7 6 3 1 8 6 13z" }]] },
    // carbon: arrow--left (16px artwork)
    Terminal: { viewBox: "0 0 32 32", nodes: [["path", { "d": "M26,4H6A2,2,0,0,0,4,6V26a2,2,0,0,0,2,2H26a2,2,0,0,0,2-2V6A2,2,0,0,0,26,4Zm0,2v4H6V6ZM6,26V12H26V26Z" }], ["path", { "d": "M10.76 16.18 13.58 19.01 10.76 21.84 12.17 23.25 16.41 19.01 12.17 14.77 10.76 16.18z" }]] }
    // carbon: terminal (32px artwork, @carbon/icons 11.89.0)
  };
  var ICON_NAMES = Object.keys(ICONS);

  // project/components/core/Icon.jsx
  var s8 = { root: "icon-root" };
  function Icon({ name, size = 16, className, style }) {
    const icon = ICONS[name];
    if (!icon) return null;
    return /* @__PURE__ */ react_default.createElement(
      "svg",
      {
        viewBox: icon.viewBox,
        width: size,
        height: size,
        fill: "currentColor",
        "aria-hidden": "true",
        focusable: "false",
        className: [s8.root, className].filter(Boolean).join(" "),
        style
      },
      icon.nodes.map(([tag, attrs], i) => react_default.createElement(tag, { key: i, ...attrs }))
    );
  }

  // project/components/core/Collapsible.jsx
  var s9 = { head: "collapsible-head", caret: "collapsible-caret", title: "collapsible-title", meta: "collapsible-meta", body: "collapsible-body" };
  function Collapsible({ label, meta, open, defaultOpen = false, onToggle, disabled = false, mono = true, children, className, style }) {
    const [inner, setInner] = react_default.useState(defaultOpen);
    const isOpen = open === void 0 ? inner : open;
    const toggle = () => {
      if (disabled) return;
      if (open === void 0) setInner(!isOpen);
      if (onToggle) onToggle(!isOpen);
    };
    return /* @__PURE__ */ react_default.createElement("div", { className, style }, /* @__PURE__ */ react_default.createElement("button", { type: "button", "aria-expanded": isOpen, disabled, onClick: toggle, className: s9.head }, /* @__PURE__ */ react_default.createElement("span", { "aria-hidden": "true", className: s9.caret, "data-open": isOpen ? "" : void 0 }, /* @__PURE__ */ react_default.createElement(Icon, { name: "ChevronRight", size: 14 })), /* @__PURE__ */ react_default.createElement("span", { className: s9.title }, label), meta ? /* @__PURE__ */ react_default.createElement("span", { className: s9.meta }, meta) : null), isOpen ? /* @__PURE__ */ react_default.createElement("div", { className: s9.body + " m-expand", "data-prose": mono ? void 0 : "" }, children) : null);
  }

  // project/components/core/Dialog.jsx
  var s10 = { root: "dialog-root", head: "dialog-head", title: "dialog-title", spacer: "dialog-spacer", body: "dialog-body" };
  function Dialog({ open = false, onClose, label, children, className, style }) {
    const ref = react_default.useRef(null);
    react_default.useEffect(() => {
      const el2 = ref.current;
      if (!el2) return;
      if (open && !el2.open) el2.showModal();
      else if (!open && el2.open) el2.close();
    }, [open]);
    return /* @__PURE__ */ react_default.createElement(
      "dialog",
      {
        ref,
        "aria-label": label,
        onClose: () => onClose == null ? void 0 : onClose(),
        onClick: (e2) => {
          if (e2.target === ref.current) ref.current.close();
        },
        className: [s10.root, className].filter(Boolean).join(" "),
        style
      },
      /* @__PURE__ */ react_default.createElement("div", { className: s10.head }, /* @__PURE__ */ react_default.createElement("h2", { className: s10.title }, label), /* @__PURE__ */ react_default.createElement("div", { className: s10.spacer }), /* @__PURE__ */ react_default.createElement(Button, { variant: "quiet", onClick: () => {
        var _a2;
        return (_a2 = ref.current) == null ? void 0 : _a2.close();
      } }, "Close")),
      /* @__PURE__ */ react_default.createElement("div", { className: s10.body }, children)
    );
  }

  // project/components/core/EmptyState.jsx
  var s11 = { root: "empty-state-root", message: "empty-state-message", action: "empty-state-action" };
  function EmptyState({ message, actionLabel, onAction, actionDisabled = false, align = "center", className, style }) {
    return /* @__PURE__ */ react_default.createElement("div", { "data-align": align, className: [s11.root, className].filter(Boolean).join(" "), style }, /* @__PURE__ */ react_default.createElement("span", { className: s11.message }, message), actionLabel ? /* @__PURE__ */ react_default.createElement("button", { type: "button", disabled: actionDisabled, onClick: onAction, className: s11.action }, actionLabel) : null);
  }

  // project/components/core/FileTabs.jsx
  var s12 = { root: "file-tabs-root", list: "file-tabs-list", tab: "file-tabs-tab", path: "file-tabs-path", dir: "file-tabs-dir", name: "file-tabs-name", yours: "file-tabs-yours", ro: "file-tabs-ro" };
  var split = (path) => {
    const i = path.lastIndexOf("/");
    return i < 0 ? ["", path] : [path.slice(0, i + 1), path.slice(i + 1)];
  };
  var nameOf = (f, partOf) => f.path + (f.readOnly ? ", part of " + partOf + ", read-only" : ", yours, editable") + (f.marked ? ", the last run reported a problem here" : "");
  function FileTabs({ files = [], active, onSelect, label = "Chart files", partOf = "the chart", panelId, className, style }) {
    const base = react_default.useId();
    const list = react_default.useRef(null);
    const tabs = react_default.useRef([]);
    const at2 = Math.max(0, files.findIndex((f) => f.path === active));
    react_default.useLayoutEffect(() => {
      const el2 = list.current, t = tabs.current[at2];
      if (!el2 || !t) return;
      const pad = 8;
      if (t.offsetLeft - pad < el2.scrollLeft) el2.scrollLeft = t.offsetLeft - pad;
      else if (t.offsetLeft + t.offsetWidth + pad > el2.scrollLeft + el2.clientWidth)
        el2.scrollLeft = t.offsetLeft + t.offsetWidth + pad - el2.clientWidth;
    }, [at2, files.length]);
    const onKeyDown = (e2) => {
      var _a2;
      const n = files.length;
      if (!n) return;
      const from = Math.max(0, tabs.current.indexOf(e2.target));
      const to2 = e2.key === "ArrowRight" ? (from + 1) % n : e2.key === "ArrowLeft" ? (from - 1 + n) % n : e2.key === "Home" ? 0 : e2.key === "End" ? n - 1 : null;
      if (to2 === null) return;
      e2.preventDefault();
      (_a2 = tabs.current[to2]) == null ? void 0 : _a2.focus();
      if (onSelect && files[to2].path !== active) onSelect(files[to2].path);
    };
    return /* @__PURE__ */ react_default.createElement("div", { className: [s12.root, className].filter(Boolean).join(" "), style }, /* @__PURE__ */ react_default.createElement("div", { role: "tablist", "aria-label": label, ref: list, className: s12.list, onKeyDown }, files.map((f, i) => {
      const [dir, name] = split(f.path);
      const on2 = i === at2;
      return /* @__PURE__ */ react_default.createElement(react_default.Fragment, { key: f.path }, /* @__PURE__ */ react_default.createElement(
        "button",
        {
          type: "button",
          role: "tab",
          id: base + "-tab-" + i,
          ref: (el2) => {
            tabs.current[i] = el2;
          },
          "aria-selected": on2,
          "aria-controls": panelId,
          tabIndex: on2 ? 0 : -1,
          "aria-label": nameOf(f, partOf),
          "data-on": on2 ? "" : void 0,
          "data-mine": f.readOnly ? void 0 : "",
          "data-marked": f.marked ? "" : void 0,
          onClick: onSelect && !on2 ? () => onSelect(f.path) : void 0,
          className: s12.tab
        },
        /* @__PURE__ */ react_default.createElement("span", { className: s12.path }, dir ? /* @__PURE__ */ react_default.createElement("span", { className: s12.dir }, dir) : null, /* @__PURE__ */ react_default.createElement("span", { className: s12.name }, name)),
        f.readOnly ? /* @__PURE__ */ react_default.createElement("span", { className: s12.ro }, /* @__PURE__ */ react_default.createElement(Icon, { name: "Locked", size: 12 }), "read-only") : /* @__PURE__ */ react_default.createElement("span", { className: s12.yours }, "yours")
      ));
    })));
  }

  // project/components/core/Input.jsx
  var s13 = { root: "input-root" };
  function Input({ value, onChange, placeholder, mono = false, ariaLabel, className, style }) {
    return /* @__PURE__ */ react_default.createElement(
      "input",
      {
        value,
        placeholder,
        "aria-label": ariaLabel,
        "data-mono": mono ? "" : void 0,
        onChange: onChange ? (e2) => onChange(e2.target.value) : void 0,
        className: [s13.root, className].filter(Boolean).join(" "),
        style
      }
    );
  }

  // project/components/core/Kbd.jsx
  function Kbd({ children, className, style }) {
    return /* @__PURE__ */ react_default.createElement("kbd", { className, style }, children);
  }

  // project/components/core/NoteField.jsx
  var s14 = { root: "note-field-root", label: "note-field-label", hint: "note-field-hint", field: "note-field-field" };
  function NoteField({ value = "", onChange, label = "Note", hint = "yours, kept with the task", dirty = false, placeholder, rows = 3, ariaLabel, className, style }) {
    return /* @__PURE__ */ react_default.createElement("div", { "data-dirty": dirty ? "" : void 0, className: [s14.root, className].filter(Boolean).join(" "), style }, /* @__PURE__ */ react_default.createElement("div", { className: s14.label }, label, /* @__PURE__ */ react_default.createElement("span", { className: s14.hint }, " \xB7 ", dirty ? "unsaved" : hint)), /* @__PURE__ */ react_default.createElement(
      "textarea",
      {
        value,
        rows,
        placeholder,
        "aria-label": ariaLabel || label,
        className: s14.field,
        onChange: onChange ? (e2) => onChange(e2.target.value) : void 0
      }
    ));
  }

  // project/components/data/SortReset.jsx
  var s15 = { root: "sort-reset-root" };
  function SortReset({ disabled = false, onClick, title = "Reset sort", ariaLabel = "Reset sort to task number, ascending", className, style }) {
    return /* @__PURE__ */ react_default.createElement(
      "button",
      {
        type: "button",
        onClick,
        disabled,
        title,
        "aria-label": ariaLabel,
        className: [s15.root, className].filter(Boolean).join(" "),
        style
      },
      /* @__PURE__ */ react_default.createElement(Icon, { name: "Reset", size: 16 })
    );
  }

  // project/components/data/Table.jsx
  var s16 = { root: "table-root", th: "table-th", td: "table-td", sortBtn: "table-sortBtn", arrow: "table-arrow", empty: "table-empty", row: "table-row" };
  function Table({ columns = [], rows = [], sortKey, sortDir = "asc", onSort, onRowClick, emptyMessage, className, style }) {
    const cellAttrs = (col) => ({ "data-align": col.align || void 0, "data-mono": col.mono ? "" : void 0, "data-numeric": col.numeric ? "" : void 0 });
    return /* @__PURE__ */ react_default.createElement("table", { className: [s16.root, className].filter(Boolean).join(" "), style }, /* @__PURE__ */ react_default.createElement("thead", null, /* @__PURE__ */ react_default.createElement("tr", null, columns.map((col) => {
      const active = sortKey === col.key;
      const sortable = col.sortable && !!onSort;
      const nextDir = active && sortDir === "asc" ? "desc" : "asc";
      return /* @__PURE__ */ react_default.createElement(
        "th",
        {
          key: col.key,
          scope: "col",
          className: s16.th,
          ...cellAttrs(col),
          "data-sortable": sortable ? "" : void 0,
          "data-active": active ? "" : void 0,
          style: { width: col.width },
          "aria-sort": sortable ? active ? sortDir === "asc" ? "ascending" : "descending" : "none" : void 0
        },
        sortable ? /* @__PURE__ */ react_default.createElement("button", { type: "button", className: s16.sortBtn, onClick: () => onSort(col.key, nextDir), "aria-label": "Sort by " + col.label + " " + (nextDir === "asc" ? "ascending" : "descending") }, /* @__PURE__ */ react_default.createElement("span", null, col.label), /* @__PURE__ */ react_default.createElement("span", { "aria-hidden": "true", className: s16.arrow, "data-active": active ? "" : void 0 }, active ? /* @__PURE__ */ react_default.createElement(Icon, { name: sortDir === "asc" ? "ArrowUp" : "ArrowDown", size: 12 }) : null)) : col.label
      );
    }))), /* @__PURE__ */ react_default.createElement("tbody", null, rows.length === 0 ? /* @__PURE__ */ react_default.createElement("tr", null, /* @__PURE__ */ react_default.createElement("td", { colSpan: columns.length, className: s16.empty }, emptyMessage || "Nothing here.")) : rows.map((row, i) => {
      const dim = !!row.disabled;
      const clickable = !!onRowClick && !dim;
      return /* @__PURE__ */ react_default.createElement(
        "tr",
        {
          key: row.id != null ? row.id : i,
          tabIndex: clickable ? 0 : void 0,
          className: s16.row,
          "data-dim": dim ? "" : void 0,
          "data-clickable": clickable ? "" : void 0,
          onClick: clickable ? () => onRowClick(row) : void 0,
          onKeyDown: clickable ? (e2) => {
            if (e2.key === "Enter" || e2.key === " ") {
              e2.preventDefault();
              onRowClick(row);
            }
          } : void 0
        },
        columns.map((col) => /* @__PURE__ */ react_default.createElement("td", { key: col.key, className: s16.td, ...cellAttrs(col), "data-muted": col.muted ? "" : void 0, "data-small": col.small ? "" : void 0, style: { width: col.width } }, col.render ? col.render(row) : row[col.key]))
      );
    })));
  }

  // project/components/data/TaskPath.jsx
  var s17 = { root: "task-path-root", tier: "task-path-tier", tags: "task-path-tags" };
  function TaskPath({ tier, track, tags = [], separator = " \xB7 ", className, style }) {
    const path = tier || track;
    return /* @__PURE__ */ react_default.createElement("span", { title: (path ? path + "/" : "") + tags.join(separator), className: [s17.root, className].filter(Boolean).join(" "), style }, path ? /* @__PURE__ */ react_default.createElement("span", { className: s17.tier }, path, "/") : null, /* @__PURE__ */ react_default.createElement("span", { className: s17.tags }, tags.join(separator)));
  }

  // project/components/data/TrackRail.jsx
  var s18 = { root: "track-rail-root", pills: "track-rail-pills", label: "track-rail-label", pill: "track-rail-pill", icon: "track-rail-icon", body: "track-rail-body", head: "track-rail-head", name: "track-rail-name", count: "track-rail-count", meter: "track-rail-meter", fill: "track-rail-fill", seen: "track-rail-seen", foot: "track-rail-foot", readout: "track-rail-readout", aside: "track-rail-aside" };
  function standing(seen, total) {
    if (!total) return "no tasks yet";
    if (!seen) return "not started";
    if (seen >= total) return "all " + total + " seen";
    return seen + " seen";
  }
  var share = (seen, total) => total > 0 ? Math.round(seen / total * 100) : 0;
  var markOf = (name) => (name || "?").trim().charAt(0).toUpperCase();
  function TrackRail({
    tracks = [],
    active = null,
    onPick,
    label = "Tracks",
    allLabel = "All tracks",
    allTotal = 0,
    allSeen = 0,
    readout,
    aside,
    className,
    style
  }) {
    const pills = [{ name: allLabel, key: null, total: allTotal, seen: allSeen }].concat(
      tracks.map((t) => ({ ...t, key: t.name }))
    );
    return /* @__PURE__ */ react_default.createElement("div", { className: [s18.root, className].filter(Boolean).join(" "), style }, /* @__PURE__ */ react_default.createElement("div", { role: "group", "aria-label": label, className: s18.pills }, /* @__PURE__ */ react_default.createElement("span", { className: s18.label }, label), pills.map((t) => /* @__PURE__ */ react_default.createElement(
      "button",
      {
        key: t.key === null ? "\0all" : t.key,
        type: "button",
        "aria-pressed": active === t.key,
        "data-on": active === t.key ? "" : void 0,
        onClick: onPick ? () => onPick(t.key) : void 0,
        className: s18.pill
      },
      t.icon ? /* @__PURE__ */ react_default.createElement("img", { src: t.icon, alt: "", width: "22", height: "22", className: s18.icon, "data-image": "" }) : /* @__PURE__ */ react_default.createElement("span", { "aria-hidden": "true", className: s18.icon }, t.mark || markOf(t.name)),
      /* @__PURE__ */ react_default.createElement("span", { className: s18.body }, /* @__PURE__ */ react_default.createElement("span", { className: s18.head }, /* @__PURE__ */ react_default.createElement("span", { className: s18.name }, t.name), /* @__PURE__ */ react_default.createElement("span", { className: s18.count + " tabular" }, t.total)), /* @__PURE__ */ react_default.createElement("span", { className: s18.head }, /* @__PURE__ */ react_default.createElement("span", { className: s18.meter }, /* @__PURE__ */ react_default.createElement("span", { className: s18.fill, style: { width: share(t.seen, t.total) + "%" } })), /* @__PURE__ */ react_default.createElement("span", { className: s18.seen }, standing(t.seen, t.total))))
    ))), readout || aside ? /* @__PURE__ */ react_default.createElement("div", { className: s18.foot }, readout ? /* @__PURE__ */ react_default.createElement("span", { className: s18.readout }, readout) : null, aside ? /* @__PURE__ */ react_default.createElement("span", { className: s18.aside }, aside) : null) : null);
  }

  // project/components/feedback/ConflictBanner.jsx
  var s19 = { icon: "conflict-banner-icon", root: "conflict-banner-root", text: "conflict-banner-text", message: "conflict-banner-message", detail: "conflict-banner-detail", action: "conflict-banner-action" };
  function Action({ label, onClick, strong, disabled }) {
    return /* @__PURE__ */ react_default.createElement("button", { type: "button", disabled, onClick, className: s19.action, "data-strong": strong ? "" : void 0 }, label);
  }
  function ConflictBanner({ message = "This task changed on disk.", detail, reloadLabel = "Reload from disk", keepLabel = "Keep mine", onReload, onKeep, disabled = false, className, style }) {
    return /* @__PURE__ */ react_default.createElement("div", { role: "alert", className: [s19.root, className].filter(Boolean).join(" "), style }, /* @__PURE__ */ react_default.createElement("span", { "aria-hidden": "true", className: s19.icon }, /* @__PURE__ */ react_default.createElement(Icon, { name: "WarningAlt", size: 16 })), /* @__PURE__ */ react_default.createElement("div", { className: s19.text }, /* @__PURE__ */ react_default.createElement("span", { className: s19.message }, message), detail ? /* @__PURE__ */ react_default.createElement("span", { className: s19.detail }, detail) : null), /* @__PURE__ */ react_default.createElement(Action, { label: reloadLabel, onClick: onReload, disabled, strong: true }), /* @__PURE__ */ react_default.createElement(Action, { label: keepLabel, onClick: onKeep, disabled }));
  }

  // project/components/feedback/FailedCase.jsx
  var s20 = { root: "failed-case-root", field: "failed-case-field", label: "failed-case-label", value: "failed-case-value", lines: "failed-case-lines", no: "failed-case-no", ln: "failed-case-ln", arg: "failed-case-arg", argName: "failed-case-argName", line: "failed-case-line", pair: "failed-case-pair", path: "failed-case-path" };
  function Lines({ text, side }) {
    return /* @__PURE__ */ react_default.createElement("div", { className: `${s20.value} ${s20.lines}`, ...{ [`data-${side}`]: "" } }, String(text).split("\n").map((line, i) => /* @__PURE__ */ react_default.createElement(react_default.Fragment, { key: i }, /* @__PURE__ */ react_default.createElement("span", { className: s20.no, "aria-hidden": "true" }, i + 1), /* @__PURE__ */ react_default.createElement("span", { className: s20.ln }, line))));
  }
  function FailedCase({ case: found, fields }) {
    var _a2;
    if (fields == null ? void 0 : fields.length) return /* @__PURE__ */ react_default.createElement("div", { className: s20.root }, fields.map(({ label, value }, i) => /* @__PURE__ */ react_default.createElement("div", { className: s20.field, key: i }, /* @__PURE__ */ react_default.createElement("span", { className: s20.label }, /* @__PURE__ */ react_default.createElement("code", { className: s20.path }, label)), /* @__PURE__ */ react_default.createElement(Lines, { text: value, side: "wrong" }))));
    if (!found) return null;
    const args = Object.entries((_a2 = found.args) != null ? _a2 : {});
    const compared = found.expected != null && found.actual != null;
    return /* @__PURE__ */ react_default.createElement("div", { className: s20.root }, args.length ? /* @__PURE__ */ react_default.createElement("div", { className: s20.field }, /* @__PURE__ */ react_default.createElement("span", { className: s20.label }, "Input"), /* @__PURE__ */ react_default.createElement("div", { className: s20.value }, args.map(([name, value]) => /* @__PURE__ */ react_default.createElement("span", { key: name, className: s20.arg }, /* @__PURE__ */ react_default.createElement("span", { className: s20.argName }, name, " = "), value)))) : null, compared ? /* @__PURE__ */ react_default.createElement("div", { className: s20.pair }, /* @__PURE__ */ react_default.createElement("div", { className: s20.field }, /* @__PURE__ */ react_default.createElement("span", { className: s20.label }, "Your output"), /* @__PURE__ */ react_default.createElement(Lines, { text: found.actual, side: "wrong" })), /* @__PURE__ */ react_default.createElement("div", { className: s20.field }, /* @__PURE__ */ react_default.createElement("span", { className: s20.label }, "Expected"), /* @__PURE__ */ react_default.createElement(Lines, { text: found.expected, side: "right" }))) : null, found.source ? /* @__PURE__ */ react_default.createElement("div", { className: s20.line }, found.source) : null);
  }

  // project/components/feedback/GraceNotice.jsx
  var s21 = { root: "grace-notice-root", head: "grace-notice-head", eyebrow: "grace-notice-eyebrow", dismiss: "grace-notice-dismiss", body: "grace-notice-body", count: "grace-notice-count" };
  function GraceNotice({ seconds = 60, onDismiss, className, style }) {
    return /* @__PURE__ */ react_default.createElement("div", { className: [s21.root, "m-rise", className].filter(Boolean).join(" "), role: "status", style }, /* @__PURE__ */ react_default.createElement("div", { className: s21.head }, /* @__PURE__ */ react_default.createElement("span", { className: s21.eyebrow }, "Reading time"), /* @__PURE__ */ react_default.createElement("button", { type: "button", onClick: onDismiss, "aria-label": "Dismiss", className: s21.dismiss + " m-press" }, /* @__PURE__ */ react_default.createElement(Icon, { name: "Close", size: 16 }))), /* @__PURE__ */ react_default.createElement("p", { className: s21.body }, "The clock starts in ", /* @__PURE__ */ react_default.createElement("span", { className: s21.count + " tabular" }, seconds), " ", seconds === 1 ? "second" : "seconds", ". Read the whole spec before you write anything \u2014 it costs you nothing."));
  }

  // project/components/feedback/NoticeBanner.jsx
  var s22 = { icon: "notice-banner-icon", root: "notice-banner-root", message: "notice-banner-message", action: "notice-banner-action" };
  function NoticeBanner({ message, actions = [], className, style }) {
    return /* @__PURE__ */ react_default.createElement("div", { className: [s22.root, className].filter(Boolean).join(" "), style }, /* @__PURE__ */ react_default.createElement("span", { "aria-hidden": "true", className: s22.icon }, /* @__PURE__ */ react_default.createElement(Icon, { name: "Information", size: 16 })), /* @__PURE__ */ react_default.createElement("span", { className: s22.message }, message), actions.map((a, i) => /* @__PURE__ */ react_default.createElement("button", { key: i, type: "button", onClick: a.onClick, className: s22.action }, a.label)));
  }

  // project/components/feedback/ResultBanner.jsx
  var s23 = { root: "result-banner-root", headline: "result-banner-headline", details: "result-banner-details", summary: "result-banner-summary", output: "result-banner-output", grade: "result-banner-grade", backIn: "result-banner-backIn", sr: "result-banner-sr" };
  function ResultBanner({ state = "idle", headline, output, gradeLine, backIn, className, style }) {
    const cx = (extra) => [s23.root, extra, className].filter(Boolean).join(" ");
    if (state === "idle") return /* @__PURE__ */ react_default.createElement("div", { "data-state": "idle", className: cx(), style }, "Not run yet \u2014 ", /* @__PURE__ */ react_default.createElement("kbd", null, "Ctrl+Enter"), " runs the tests.");
    if (state === "running") return /* @__PURE__ */ react_default.createElement("div", { "data-state": "running", className: cx(), style, "aria-live": "polite" }, "Running\u2026");
    if (state === "failed") return /* @__PURE__ */ react_default.createElement("div", { "data-state": "failed", className: cx(), style, "aria-live": "polite" }, /* @__PURE__ */ react_default.createElement("div", { className: s23.headline }, /* @__PURE__ */ react_default.createElement(Icon, { name: "CloseOutline", size: 16 }), /* @__PURE__ */ react_default.createElement("span", null, /* @__PURE__ */ react_default.createElement("span", { className: s23.sr }, "Failed: "), headline)), output ? /* @__PURE__ */ react_default.createElement("details", { className: s23.details }, /* @__PURE__ */ react_default.createElement("summary", { className: s23.summary }, "Show full output"), /* @__PURE__ */ react_default.createElement("pre", { className: s23.output }, output)) : null);
    return /* @__PURE__ */ react_default.createElement("div", { "data-state": "passed", className: cx(), style, "aria-live": "polite" }, /* @__PURE__ */ react_default.createElement("span", { className: s23.grade }, /* @__PURE__ */ react_default.createElement(Icon, { name: "CheckmarkOutline", size: 16 }), "PASSED" + (gradeLine ? " \xB7 " + gradeLine : "")), backIn ? /* @__PURE__ */ react_default.createElement("span", { className: s23.backIn }, "back in ", backIn) : null);
  }

  // project/components/feedback/StuckNudge.jsx
  var s24 = { root: "stuck-nudge-root", head: "stuck-nudge-head", eyebrow: "stuck-nudge-eyebrow", dismiss: "stuck-nudge-dismiss", lead: "stuck-nudge-lead", sub: "stuck-nudge-sub", actions: "stuck-nudge-actions", spacer: "stuck-nudge-spacer", count: "stuck-nudge-count", btn: "stuck-nudge-btn" };
  function NudgeButton({ variant, onClick, disabled, children }) {
    return /* @__PURE__ */ react_default.createElement("button", { type: "button", className: s24.btn + " m-press", "data-variant": variant, disabled, onClick }, children);
  }
  function StuckNudge({ minutes = 30, hintsShown = 0, hintsTotal = 3, hintReady = true, onHint, onDismiss, placement = "corner", className, style }) {
    return /* @__PURE__ */ react_default.createElement("div", { className: [s24.root, "m-rise", className].filter(Boolean).join(" "), role: "status", "data-placement": placement, style }, /* @__PURE__ */ react_default.createElement("div", { className: s24.head }, /* @__PURE__ */ react_default.createElement("span", { className: s24.eyebrow }, minutes, " minutes on this task"), /* @__PURE__ */ react_default.createElement("button", { type: "button", onClick: onDismiss, "aria-label": "Dismiss", className: s24.dismiss + " m-press" }, /* @__PURE__ */ react_default.createElement(Icon, { name: "Close", size: 16 }))), /* @__PURE__ */ react_default.createElement("p", { className: s24.lead }, "Take a hint. It opens the next step, not the answer, and the pass still counts."), /* @__PURE__ */ react_default.createElement("p", { className: s24.sub }, "If the problem still doesn't come apart after one, go and read the material. You will be reading with a question in hand, which is the only way it sticks."), /* @__PURE__ */ react_default.createElement("div", { className: s24.actions }, /* @__PURE__ */ react_default.createElement(NudgeButton, { onClick: onHint, disabled: !hintReady }, "Show hint ", hintsShown + 1), /* @__PURE__ */ react_default.createElement("div", { className: s24.spacer }), /* @__PURE__ */ react_default.createElement("span", { className: s24.count }, hintsShown, " of ", hintsTotal, " shown")));
  }

  // project/components/form/Select.jsx
  var s25 = { wrap: "select-wrap", root: "select-root", caret: "select-caret" };
  function Select({ value, onChange, options = [], placeholder, disabled = false, mono = false, ariaLabel, className, style }) {
    const opts = options.map((o) => typeof o === "string" ? { value: o, label: o } : o);
    return /* @__PURE__ */ react_default.createElement("span", { className: s25.wrap }, /* @__PURE__ */ react_default.createElement(
      "select",
      {
        value,
        disabled,
        "aria-label": ariaLabel,
        "data-mono": mono ? "" : void 0,
        onChange: onChange ? (e2) => onChange(e2.target.value) : void 0,
        className: [s25.root, className].filter(Boolean).join(" "),
        style
      },
      placeholder ? /* @__PURE__ */ react_default.createElement("option", { value: "" }, placeholder) : null,
      opts.map((o) => /* @__PURE__ */ react_default.createElement("option", { key: o.value, value: o.value }, o.label))
    ), /* @__PURE__ */ react_default.createElement("span", { "aria-hidden": "true", className: s25.caret }, /* @__PURE__ */ react_default.createElement(Icon, { name: "ChevronDown", size: 14 })));
  }

  // project/components/form/Toggle.jsx
  var s26 = { root: "toggle-root", track: "toggle-track", knob: "toggle-knob", label: "toggle-label" };
  function Toggle({ checked = false, onChange, label, disabled = false, ariaLabel, className, style }) {
    const on2 = checked && !disabled;
    return /* @__PURE__ */ react_default.createElement(
      "button",
      {
        type: "button",
        role: "switch",
        "aria-checked": !!checked,
        "aria-label": label ? void 0 : ariaLabel,
        disabled,
        "data-on": on2 ? "" : void 0,
        "data-checked": checked ? "" : void 0,
        onClick: onChange ? () => onChange(!checked) : void 0,
        className: [s26.root, className].filter(Boolean).join(" "),
        style
      },
      /* @__PURE__ */ react_default.createElement("span", { "aria-hidden": "true", className: s26.track }, /* @__PURE__ */ react_default.createElement("span", { className: s26.knob })),
      label ? /* @__PURE__ */ react_default.createElement("span", { className: s26.label }, label) : null
    );
  }

  // shims/markdown.min.js
  var Zl = Object.create;
  var sn = Object.defineProperty;
  var Gl = Object.getOwnPropertyDescriptor;
  var $l = Object.getOwnPropertyNames;
  var Jl = Object.getPrototypeOf;
  var Kl = Object.prototype.hasOwnProperty;
  var at = (e2, n) => () => {
    try {
      return n || e2((n = { exports: {} }).exports, n), n.exports;
    } catch (t) {
      throw n = 0, t;
    }
  };
  var Qr = (e2, n) => {
    for (var t in n) sn(e2, t, { get: n[t], enumerable: true });
  };
  var ea = (e2, n, t, r) => {
    if (n && typeof n == "object" || typeof n == "function") for (let i of $l(n)) !Kl.call(e2, i) && i !== t && sn(e2, i, { get: () => n[i], enumerable: !(r = Gl(n, i)) || r.enumerable });
    return e2;
  };
  var Yr = (e2, n, t) => (t = e2 != null ? Zl(Jl(e2)) : {}, ea(n || !e2 || !e2.__esModule ? sn(t, "default", { value: e2, enumerable: true }) : t, e2));
  var ui = at((Wp, ai) => {
    "use strict";
    var ri = /\/\*[^*]*\*+([^/*][^*]*\*+)*\//g, ca = /\n/g, fa = /^\s*/, pa = /^(\*?[-#/*\\\w]+(\[[0-9a-z_-]+\])?)\s*/, ma = /^:\s*/, ha = /^((?:'(?:\\'|.)*?'|"(?:\\"|.)*?"|\([^)]*?\)|[^};])+)/, da = /^[;\s]*/, ga = /^\s+|\s+$/g, xa = `
`, ii = "/", oi = "*", _e = "", ka = "comment", ya = "declaration";
    function ba(e2, n) {
      if (typeof e2 != "string") throw new TypeError("First argument must be a string");
      if (!e2) return [];
      n = n || {};
      var t = 1, r = 1;
      function i(g) {
        var k = g.match(ca);
        k && (t += k.length);
        var C = g.lastIndexOf(xa);
        r = ~C ? g.length - C : r + g.length;
      }
      function l() {
        var g = { line: t, column: r };
        return function(k) {
          return k.position = new o(g), s32(), k;
        };
      }
      function o(g) {
        this.start = g, this.end = { line: t, column: r }, this.source = n.source;
      }
      o.prototype.content = e2;
      function a(g) {
        var k = new Error(n.source + ":" + t + ":" + r + ": " + g);
        if (k.reason = g, k.filename = n.source, k.line = t, k.column = r, k.source = e2, !n.silent) throw k;
      }
      function u(g) {
        var k = g.exec(e2);
        if (k) {
          var C = k[0];
          return i(C), e2 = e2.slice(C.length), k;
        }
      }
      function s32() {
        u(fa);
      }
      function c(g) {
        var k;
        for (g = g || []; k = f(); ) k !== false && g.push(k);
        return g;
      }
      function f() {
        var g = l();
        if (!(ii != e2.charAt(0) || oi != e2.charAt(1))) {
          for (var k = 2; _e != e2.charAt(k) && (oi != e2.charAt(k) || ii != e2.charAt(k + 1)); ) ++k;
          if (k += 2, _e === e2.charAt(k - 1)) return a("End of comment missing");
          var C = e2.slice(2, k - 2);
          return r += 2, i(C), e2 = e2.slice(k), r += 2, g({ type: ka, comment: C });
        }
      }
      function m() {
        var g = l(), k = u(pa);
        if (k) {
          if (f(), !u(ma)) return a("property missing ':'");
          var C = u(ha), x = g({ type: ya, property: li(k[0].replace(ri, _e)), value: C ? li(C[0].replace(ri, _e)) : _e });
          return u(da), x;
        }
      }
      function p() {
        var g = [];
        c(g);
        for (var k; k = m(); ) k !== false && (g.push(k), c(g));
        return g;
      }
      return s32(), p();
    }
    function li(e2) {
      return e2 ? e2.replace(ga, _e) : _e;
    }
    ai.exports = ba;
  });
  var si = at((ct) => {
    "use strict";
    var wa = ct && ct.__importDefault || function(e2) {
      return e2 && e2.__esModule ? e2 : { default: e2 };
    };
    Object.defineProperty(ct, "__esModule", { value: true });
    ct.default = Ca;
    var Sa = wa(ui());
    function Ca(e2, n) {
      let t = null;
      if (!e2 || typeof e2 != "string") return t;
      let r = (0, Sa.default)(e2), i = typeof n == "function";
      return r.forEach((l) => {
        if (l.type !== "declaration") return;
        let { property: o, value: a } = l;
        i ? n(o, a, l) : a && (t = t || {}, t[o] = a);
      }), t;
    }
  });
  var fi = at((vt) => {
    "use strict";
    Object.defineProperty(vt, "__esModule", { value: true });
    vt.camelCase = void 0;
    var Ea = /^--[a-zA-Z0-9_-]+$/, Ia = /-([a-z])/g, Ta = /^[^-]+$/, Aa = /^-(webkit|moz|ms|o|khtml)-/, La = /^-(ms)-/, va = function(e2) {
      return !e2 || Ta.test(e2) || Ea.test(e2);
    }, Pa = function(e2, n) {
      return n.toUpperCase();
    }, ci = function(e2, n) {
      return "".concat(n, "-");
    }, za = function(e2, n) {
      return n === void 0 && (n = {}), va(e2) ? e2 : (e2 = e2.toLowerCase(), n.reactCompat ? e2 = e2.replace(La, ci) : e2 = e2.replace(Aa, ci), e2.replace(Ia, Pa));
    };
    vt.camelCase = za;
  });
  var mi = at((bn, pi) => {
    "use strict";
    var Fa = bn && bn.__importDefault || function(e2) {
      return e2 && e2.__esModule ? e2 : { default: e2 };
    }, Da = Fa(si()), Ra = fi();
    function yn(e2, n) {
      var t = {};
      return !e2 || typeof e2 != "string" || (0, Da.default)(e2, function(r, i) {
        r && i && (t[(0, Ra.camelCase)(r, n)] = i);
      }), t;
    }
    yn.default = yn;
    pi.exports = yn;
  });
  var Vo = at((Bk, Uo) => {
    "use strict";
    var en = Object.prototype.hasOwnProperty, jo = Object.prototype.toString, Mo = Object.defineProperty, Oo = Object.getOwnPropertyDescriptor, _o = function(n) {
      return typeof Array.isArray == "function" ? Array.isArray(n) : jo.call(n) === "[object Array]";
    }, No = function(n) {
      if (!n || jo.call(n) !== "[object Object]") return false;
      var t = en.call(n, "constructor"), r = n.constructor && n.constructor.prototype && en.call(n.constructor.prototype, "isPrototypeOf");
      if (n.constructor && !t && !r) return false;
      var i;
      for (i in n) ;
      return typeof i == "undefined" || en.call(n, i);
    }, Bo = function(n, t) {
      Mo && t.name === "__proto__" ? Mo(n, t.name, { enumerable: true, configurable: true, value: t.newValue, writable: true }) : n[t.name] = t.newValue;
    }, Ho = function(n, t) {
      if (t === "__proto__") if (en.call(n, t)) {
        if (Oo) return Oo(n, t).value;
      } else return;
      return n[t];
    };
    Uo.exports = function e2() {
      var n, t, r, i, l, o, a = arguments[0], u = 1, s32 = arguments.length, c = false;
      for (typeof a == "boolean" && (c = a, a = arguments[1] || {}, u = 2), (a == null || typeof a != "object" && typeof a != "function") && (a = {}); u < s32; ++u) if (n = arguments[u], n != null) for (t in n) r = Ho(a, t), i = Ho(n, t), a !== i && (c && i && (No(i) || (l = _o(i))) ? (l ? (l = false, o = r && _o(r) ? r : []) : o = r && No(r) ? r : {}, Bo(a, { name: t, newValue: e2(c, o, i) })) : typeof i != "undefined" && Bo(a, { name: t, newValue: i }));
      return a;
    };
  });
  function Zr(e2, n) {
    let t = n || {};
    return (e2[e2.length - 1] === "" ? [...e2, ""] : e2).join((t.padRight ? " " : "") + "," + (t.padLeft === false ? "" : " ")).trim();
  }
  var ta = /^[$_\p{ID_Start}][$_\u{200C}\u{200D}\p{ID_Continue}]*$/u;
  var na = /^[$_\p{ID_Start}][-$_\u{200C}\u{200D}\p{ID_Continue}]*$/u;
  var ra = {};
  function Et(e2, n) {
    return ((n || ra).jsx ? na : ta).test(e2);
  }
  var ia = /[ \t\n\f\r]/g;
  function cn(e2) {
    return typeof e2 == "object" ? e2.type === "text" ? Gr(e2.value) : false : Gr(e2);
  }
  function Gr(e2) {
    return e2.replace(ia, "") === "";
  }
  var we = class {
    constructor(n, t, r) {
      this.normal = t, this.property = n, r && (this.space = r);
    }
  };
  we.prototype.normal = {};
  we.prototype.property = {};
  we.prototype.space = void 0;
  function fn(e2, n) {
    let t = {}, r = {};
    for (let i of e2) Object.assign(t, i.property), Object.assign(r, i.normal);
    return new we(t, r, n);
  }
  function ut(e2) {
    return e2.toLowerCase();
  }
  var K = class {
    constructor(n, t) {
      this.attribute = t, this.property = n;
    }
  };
  K.prototype.attribute = "";
  K.prototype.booleanish = false;
  K.prototype.boolean = false;
  K.prototype.commaOrSpaceSeparated = false;
  K.prototype.commaSeparated = false;
  K.prototype.defined = false;
  K.prototype.mustUseProperty = false;
  K.prototype.number = false;
  K.prototype.overloadedBoolean = false;
  K.prototype.property = "";
  K.prototype.spaceSeparated = false;
  K.prototype.space = void 0;
  var st = {};
  Qr(st, { boolean: () => z, booleanish: () => X, commaOrSpaceSeparated: () => ie, commaSeparated: () => Se, number: () => S, overloadedBoolean: () => It, spaceSeparated: () => U });
  var oa = 0;
  var z = Me();
  var X = Me();
  var It = Me();
  var S = Me();
  var U = Me();
  var Se = Me();
  var ie = Me();
  function Me() {
    return 2 ** ++oa;
  }
  var pn = Object.keys(st);
  var Oe = class extends K {
    constructor(n, t, r, i) {
      let l = -1;
      if (super(n, t), $r(this, "space", i), typeof r == "number") for (; ++l < pn.length; ) {
        let o = pn[l];
        $r(this, pn[l], (r & st[o]) === st[o]);
      }
    }
  };
  Oe.prototype.defined = true;
  function $r(e2, n, t) {
    t && (e2[n] = t);
  }
  function ue(e2) {
    let n = {}, t = {};
    for (let [r, i] of Object.entries(e2.properties)) {
      let l = new Oe(r, e2.transform(e2.attributes || {}, r), i, e2.space);
      e2.mustUseProperty && e2.mustUseProperty.includes(r) && (l.mustUseProperty = true), n[r] = l, t[ut(r)] = r, t[ut(l.attribute)] = r;
    }
    return new we(n, t, e2.space);
  }
  var mn = ue({ properties: { ariaActiveDescendant: null, ariaAtomic: X, ariaAutoComplete: null, ariaBusy: X, ariaChecked: X, ariaColCount: S, ariaColIndex: S, ariaColSpan: S, ariaControls: U, ariaCurrent: null, ariaDescribedBy: U, ariaDetails: null, ariaDisabled: X, ariaDropEffect: U, ariaErrorMessage: null, ariaExpanded: X, ariaFlowTo: U, ariaGrabbed: X, ariaHasPopup: null, ariaHidden: X, ariaInvalid: null, ariaKeyShortcuts: null, ariaLabel: null, ariaLabelledBy: U, ariaLevel: S, ariaLive: null, ariaModal: X, ariaMultiLine: X, ariaMultiSelectable: X, ariaOrientation: null, ariaOwns: U, ariaPlaceholder: null, ariaPosInSet: S, ariaPressed: X, ariaReadOnly: X, ariaRelevant: null, ariaRequired: X, ariaRoleDescription: U, ariaRowCount: S, ariaRowIndex: S, ariaRowSpan: S, ariaSelected: X, ariaSetSize: S, ariaSort: null, ariaValueMax: S, ariaValueMin: S, ariaValueNow: S, ariaValueText: null, role: null }, transform(e2, n) {
    return n === "role" ? n : "aria-" + n.slice(4).toLowerCase();
  } });
  function Tt(e2, n) {
    return n in e2 ? e2[n] : n;
  }
  function At(e2, n) {
    return Tt(e2, n.toLowerCase());
  }
  var Jr = ue({ attributes: { acceptcharset: "accept-charset", classname: "class", htmlfor: "for", httpequiv: "http-equiv" }, mustUseProperty: ["checked", "multiple", "muted", "selected"], properties: { abbr: null, accept: Se, acceptCharset: U, accessKey: U, action: null, allow: null, allowFullScreen: z, allowPaymentRequest: z, allowUserMedia: z, alpha: z, alt: null, as: null, async: z, autoCapitalize: null, autoComplete: U, autoFocus: z, autoPlay: z, blocking: U, capture: null, charSet: null, checked: z, cite: null, className: U, closedBy: null, colorSpace: null, cols: S, colSpan: S, command: null, commandFor: null, content: null, contentEditable: X, controls: z, controlsList: U, coords: S | Se, crossOrigin: null, data: null, dateTime: null, decoding: null, default: z, defer: z, dir: null, dirName: null, disabled: z, download: It, draggable: X, encType: null, enterKeyHint: null, fetchPriority: null, form: null, formAction: null, formEncType: null, formMethod: null, formNoValidate: z, formTarget: null, headers: U, height: S, hidden: It, high: S, href: null, hrefLang: null, htmlFor: U, httpEquiv: U, id: null, imageSizes: null, imageSrcSet: null, inert: z, inputMode: null, integrity: null, is: null, isMap: z, itemId: null, itemProp: U, itemRef: U, itemScope: z, itemType: U, kind: null, label: null, lang: null, language: null, list: null, loading: null, loop: z, low: S, manifest: null, max: null, maxLength: S, media: null, method: null, min: null, minLength: S, multiple: z, muted: z, name: null, nonce: null, noModule: z, noValidate: z, onAbort: null, onAfterPrint: null, onAuxClick: null, onBeforeMatch: null, onBeforePrint: null, onBeforeToggle: null, onBeforeUnload: null, onBlur: null, onCancel: null, onCanPlay: null, onCanPlayThrough: null, onChange: null, onClick: null, onClose: null, onContextLost: null, onContextMenu: null, onContextRestored: null, onCopy: null, onCueChange: null, onCut: null, onDblClick: null, onDrag: null, onDragEnd: null, onDragEnter: null, onDragExit: null, onDragLeave: null, onDragOver: null, onDragStart: null, onDrop: null, onDurationChange: null, onEmptied: null, onEnded: null, onError: null, onFocus: null, onFormData: null, onHashChange: null, onInput: null, onInvalid: null, onKeyDown: null, onKeyPress: null, onKeyUp: null, onLanguageChange: null, onLoad: null, onLoadedData: null, onLoadedMetadata: null, onLoadEnd: null, onLoadStart: null, onMessage: null, onMessageError: null, onMouseDown: null, onMouseEnter: null, onMouseLeave: null, onMouseMove: null, onMouseOut: null, onMouseOver: null, onMouseUp: null, onOffline: null, onOnline: null, onPageHide: null, onPageShow: null, onPaste: null, onPause: null, onPlay: null, onPlaying: null, onPopState: null, onProgress: null, onRateChange: null, onRejectionHandled: null, onReset: null, onResize: null, onScroll: null, onScrollEnd: null, onSecurityPolicyViolation: null, onSeeked: null, onSeeking: null, onSelect: null, onSlotChange: null, onStalled: null, onStorage: null, onSubmit: null, onSuspend: null, onTimeUpdate: null, onToggle: null, onUnhandledRejection: null, onUnload: null, onVolumeChange: null, onWaiting: null, onWheel: null, open: z, optimum: S, pattern: null, ping: U, placeholder: null, playsInline: z, popover: null, popoverTarget: null, popoverTargetAction: null, poster: null, preload: null, readOnly: z, referrerPolicy: null, rel: U, required: z, reversed: z, rows: S, rowSpan: S, sandbox: U, scope: null, scoped: z, seamless: z, selected: z, shadowRootClonable: z, shadowRootCustomElementRegistry: z, shadowRootDelegatesFocus: z, shadowRootMode: null, shadowRootSerializable: z, shape: null, size: S, sizes: null, slot: null, span: S, spellCheck: X, src: null, srcDoc: null, srcLang: null, srcSet: null, start: S, step: null, style: null, tabIndex: S, target: null, title: null, translate: null, type: null, typeMustMatch: z, useMap: null, value: X, width: S, wrap: null, writingSuggestions: null, align: null, aLink: null, archive: U, axis: null, background: null, bgColor: null, border: S, borderColor: null, bottomMargin: S, cellPadding: null, cellSpacing: null, char: null, charOff: null, classId: null, clear: null, code: null, codeBase: null, codeType: null, color: null, compact: z, declare: z, event: null, face: null, frame: null, frameBorder: null, hSpace: S, leftMargin: S, link: null, longDesc: null, lowSrc: null, marginHeight: S, marginWidth: S, noResize: z, noHref: z, noShade: z, noWrap: z, object: null, profile: null, prompt: null, rev: null, rightMargin: S, rules: null, scheme: null, scrolling: X, standby: null, summary: null, text: null, topMargin: S, valueType: null, version: null, vAlign: null, vLink: null, vSpace: S, allowTransparency: null, autoCorrect: null, autoSave: null, credentialless: z, disablePictureInPicture: z, disableRemotePlayback: z, exportParts: Se, part: U, prefix: null, property: null, results: S, security: null, unselectable: null }, space: "html", transform: At });
  var Kr = ue({ attributes: { accentHeight: "accent-height", alignmentBaseline: "alignment-baseline", arabicForm: "arabic-form", baselineShift: "baseline-shift", capHeight: "cap-height", className: "class", clipPath: "clip-path", clipRule: "clip-rule", colorInterpolation: "color-interpolation", colorInterpolationFilters: "color-interpolation-filters", colorProfile: "color-profile", colorRendering: "color-rendering", crossOrigin: "crossorigin", dataType: "datatype", dominantBaseline: "dominant-baseline", enableBackground: "enable-background", fillOpacity: "fill-opacity", fillRule: "fill-rule", floodColor: "flood-color", floodOpacity: "flood-opacity", fontFamily: "font-family", fontSize: "font-size", fontSizeAdjust: "font-size-adjust", fontStretch: "font-stretch", fontStyle: "font-style", fontVariant: "font-variant", fontWeight: "font-weight", glyphName: "glyph-name", glyphOrientationHorizontal: "glyph-orientation-horizontal", glyphOrientationVertical: "glyph-orientation-vertical", hrefLang: "hreflang", horizAdvX: "horiz-adv-x", horizOriginX: "horiz-origin-x", horizOriginY: "horiz-origin-y", imageRendering: "image-rendering", letterSpacing: "letter-spacing", lightingColor: "lighting-color", markerEnd: "marker-end", markerMid: "marker-mid", markerStart: "marker-start", maskType: "mask-type", navDown: "nav-down", navDownLeft: "nav-down-left", navDownRight: "nav-down-right", navLeft: "nav-left", navNext: "nav-next", navPrev: "nav-prev", navRight: "nav-right", navUp: "nav-up", navUpLeft: "nav-up-left", navUpRight: "nav-up-right", onAbort: "onabort", onActivate: "onactivate", onAfterPrint: "onafterprint", onBeforePrint: "onbeforeprint", onBegin: "onbegin", onCancel: "oncancel", onCanPlay: "oncanplay", onCanPlayThrough: "oncanplaythrough", onChange: "onchange", onClick: "onclick", onClose: "onclose", onCopy: "oncopy", onCueChange: "oncuechange", onCut: "oncut", onDblClick: "ondblclick", onDrag: "ondrag", onDragEnd: "ondragend", onDragEnter: "ondragenter", onDragExit: "ondragexit", onDragLeave: "ondragleave", onDragOver: "ondragover", onDragStart: "ondragstart", onDrop: "ondrop", onDurationChange: "ondurationchange", onEmptied: "onemptied", onEnd: "onend", onEnded: "onended", onError: "onerror", onFocus: "onfocus", onFocusIn: "onfocusin", onFocusOut: "onfocusout", onHashChange: "onhashchange", onInput: "oninput", onInvalid: "oninvalid", onKeyDown: "onkeydown", onKeyPress: "onkeypress", onKeyUp: "onkeyup", onLoad: "onload", onLoadedData: "onloadeddata", onLoadedMetadata: "onloadedmetadata", onLoadStart: "onloadstart", onMessage: "onmessage", onMouseDown: "onmousedown", onMouseEnter: "onmouseenter", onMouseLeave: "onmouseleave", onMouseMove: "onmousemove", onMouseOut: "onmouseout", onMouseOver: "onmouseover", onMouseUp: "onmouseup", onMouseWheel: "onmousewheel", onOffline: "onoffline", onOnline: "ononline", onPageHide: "onpagehide", onPageShow: "onpageshow", onPaste: "onpaste", onPause: "onpause", onPlay: "onplay", onPlaying: "onplaying", onPopState: "onpopstate", onProgress: "onprogress", onRateChange: "onratechange", onRepeat: "onrepeat", onReset: "onreset", onResize: "onresize", onScroll: "onscroll", onSeeked: "onseeked", onSeeking: "onseeking", onSelect: "onselect", onShow: "onshow", onStalled: "onstalled", onStorage: "onstorage", onSubmit: "onsubmit", onSuspend: "onsuspend", onTimeUpdate: "ontimeupdate", onToggle: "ontoggle", onUnload: "onunload", onVolumeChange: "onvolumechange", onWaiting: "onwaiting", onZoom: "onzoom", overlinePosition: "overline-position", overlineThickness: "overline-thickness", paintOrder: "paint-order", panose1: "panose-1", pointerEvents: "pointer-events", referrerPolicy: "referrerpolicy", renderingIntent: "rendering-intent", shapeRendering: "shape-rendering", stopColor: "stop-color", stopOpacity: "stop-opacity", strikethroughPosition: "strikethrough-position", strikethroughThickness: "strikethrough-thickness", strokeDashArray: "stroke-dasharray", strokeDashOffset: "stroke-dashoffset", strokeLineCap: "stroke-linecap", strokeLineJoin: "stroke-linejoin", strokeMiterLimit: "stroke-miterlimit", strokeOpacity: "stroke-opacity", strokeWidth: "stroke-width", tabIndex: "tabindex", textAnchor: "text-anchor", textDecoration: "text-decoration", textRendering: "text-rendering", transformOrigin: "transform-origin", typeOf: "typeof", underlinePosition: "underline-position", underlineThickness: "underline-thickness", unicodeBidi: "unicode-bidi", unicodeRange: "unicode-range", unitsPerEm: "units-per-em", vAlphabetic: "v-alphabetic", vHanging: "v-hanging", vIdeographic: "v-ideographic", vMathematical: "v-mathematical", vectorEffect: "vector-effect", vertAdvY: "vert-adv-y", vertOriginX: "vert-origin-x", vertOriginY: "vert-origin-y", wordSpacing: "word-spacing", writingMode: "writing-mode", xHeight: "x-height", playbackOrder: "playbackorder", timelineBegin: "timelinebegin" }, properties: { about: ie, accentHeight: S, accumulate: null, additive: null, alignmentBaseline: null, alphabetic: S, amplitude: S, arabicForm: null, ascent: S, attributeName: null, attributeType: null, azimuth: S, bandwidth: null, baselineShift: null, baseFrequency: null, baseProfile: null, bbox: null, begin: null, bias: S, by: null, calcMode: null, capHeight: S, className: U, clip: null, clipPath: null, clipPathUnits: null, clipRule: null, color: null, colorInterpolation: null, colorInterpolationFilters: null, colorProfile: null, colorRendering: null, content: null, contentScriptType: null, contentStyleType: null, crossOrigin: null, cursor: null, cx: null, cy: null, d: null, dataType: null, defaultAction: null, descent: S, diffuseConstant: S, direction: null, display: null, dur: null, divisor: S, dominantBaseline: null, download: z, dx: null, dy: null, edgeMode: null, editable: null, elevation: S, enableBackground: null, end: null, event: null, exponent: S, externalResourcesRequired: null, fill: null, fillOpacity: S, fillRule: null, filter: null, filterRes: null, filterUnits: null, floodColor: null, floodOpacity: null, focusable: null, focusHighlight: null, fontFamily: null, fontSize: null, fontSizeAdjust: null, fontStretch: null, fontStyle: null, fontVariant: null, fontWeight: null, format: null, fr: null, from: null, fx: null, fy: null, g1: Se, g2: Se, glyphName: Se, glyphOrientationHorizontal: null, glyphOrientationVertical: null, glyphRef: null, gradientTransform: null, gradientUnits: null, handler: null, hanging: S, hatchContentUnits: null, hatchUnits: null, height: null, href: null, hrefLang: null, horizAdvX: S, horizOriginX: S, horizOriginY: S, id: null, ideographic: S, imageRendering: null, initialVisibility: null, in: null, in2: null, intercept: S, k: S, k1: S, k2: S, k3: S, k4: S, kernelMatrix: ie, kernelUnitLength: null, keyPoints: null, keySplines: null, keyTimes: null, kerning: null, lang: null, lengthAdjust: null, letterSpacing: null, lightingColor: null, limitingConeAngle: S, local: null, markerEnd: null, markerMid: null, markerStart: null, markerHeight: null, markerUnits: null, markerWidth: null, mask: null, maskContentUnits: null, maskType: null, maskUnits: null, mathematical: null, max: null, media: null, mediaCharacterEncoding: null, mediaContentEncodings: null, mediaSize: S, mediaTime: null, method: null, min: null, mode: null, name: null, navDown: null, navDownLeft: null, navDownRight: null, navLeft: null, navNext: null, navPrev: null, navRight: null, navUp: null, navUpLeft: null, navUpRight: null, numOctaves: null, observer: null, offset: null, onAbort: null, onActivate: null, onAfterPrint: null, onBeforePrint: null, onBegin: null, onCancel: null, onCanPlay: null, onCanPlayThrough: null, onChange: null, onClick: null, onClose: null, onCopy: null, onCueChange: null, onCut: null, onDblClick: null, onDrag: null, onDragEnd: null, onDragEnter: null, onDragExit: null, onDragLeave: null, onDragOver: null, onDragStart: null, onDrop: null, onDurationChange: null, onEmptied: null, onEnd: null, onEnded: null, onError: null, onFocus: null, onFocusIn: null, onFocusOut: null, onHashChange: null, onInput: null, onInvalid: null, onKeyDown: null, onKeyPress: null, onKeyUp: null, onLoad: null, onLoadedData: null, onLoadedMetadata: null, onLoadStart: null, onMessage: null, onMouseDown: null, onMouseEnter: null, onMouseLeave: null, onMouseMove: null, onMouseOut: null, onMouseOver: null, onMouseUp: null, onMouseWheel: null, onOffline: null, onOnline: null, onPageHide: null, onPageShow: null, onPaste: null, onPause: null, onPlay: null, onPlaying: null, onPopState: null, onProgress: null, onRateChange: null, onRepeat: null, onReset: null, onResize: null, onScroll: null, onSeeked: null, onSeeking: null, onSelect: null, onShow: null, onStalled: null, onStorage: null, onSubmit: null, onSuspend: null, onTimeUpdate: null, onToggle: null, onUnload: null, onVolumeChange: null, onWaiting: null, onZoom: null, opacity: null, operator: null, order: null, orient: null, orientation: null, origin: null, overflow: null, overlay: null, overlinePosition: S, overlineThickness: S, paintOrder: null, panose1: null, path: null, pathLength: S, patternContentUnits: null, patternTransform: null, patternUnits: null, phase: null, ping: U, pitch: null, playbackOrder: null, pointerEvents: null, points: null, pointsAtX: S, pointsAtY: S, pointsAtZ: S, preserveAlpha: null, preserveAspectRatio: null, primitiveUnits: null, propagate: null, property: ie, r: null, radius: null, referrerPolicy: null, refX: null, refY: null, rel: ie, rev: ie, renderingIntent: null, repeatCount: null, repeatDur: null, requiredExtensions: ie, requiredFeatures: ie, requiredFonts: ie, requiredFormats: ie, resource: null, restart: null, result: null, rotate: null, rx: null, ry: null, scale: null, seed: null, shapeRendering: null, side: null, slope: null, snapshotTime: null, specularConstant: S, specularExponent: S, spreadMethod: null, spacing: null, startOffset: null, stdDeviation: null, stemh: null, stemv: null, stitchTiles: null, stopColor: null, stopOpacity: null, strikethroughPosition: S, strikethroughThickness: S, string: null, stroke: null, strokeDashArray: ie, strokeDashOffset: null, strokeLineCap: null, strokeLineJoin: null, strokeMiterLimit: S, strokeOpacity: S, strokeWidth: null, style: null, surfaceScale: S, syncBehavior: null, syncBehaviorDefault: null, syncMaster: null, syncTolerance: null, syncToleranceDefault: null, systemLanguage: ie, tabIndex: S, tableValues: null, target: null, targetX: S, targetY: S, textAnchor: null, textDecoration: null, textRendering: null, textLength: null, timelineBegin: null, title: null, transformBehavior: null, type: null, typeOf: ie, to: null, transform: null, transformOrigin: null, u1: null, u2: null, underlinePosition: S, underlineThickness: S, unicode: null, unicodeBidi: null, unicodeRange: null, unitsPerEm: S, values: null, vAlphabetic: S, vMathematical: S, vectorEffect: null, vHanging: S, vIdeographic: S, version: null, vertAdvY: S, vertOriginX: S, vertOriginY: S, viewBox: null, viewTarget: null, visibility: null, width: null, widths: null, wordSpacing: null, writingMode: null, x: null, x1: null, x2: null, xChannelSelector: null, xHeight: S, y: null, y1: null, y2: null, yChannelSelector: null, z: null, zoomAndPan: null }, space: "svg", transform: Tt });
  var hn = ue({ properties: { xLinkActuate: null, xLinkArcRole: null, xLinkHref: null, xLinkRole: null, xLinkShow: null, xLinkTitle: null, xLinkType: null }, space: "xlink", transform(e2, n) {
    return "xlink:" + n.slice(5).toLowerCase();
  } });
  var dn = ue({ attributes: { xmlnsxlink: "xmlns:xlink" }, properties: { xmlnsXLink: null, xmlns: null }, space: "xmlns", transform: At });
  var gn = ue({ properties: { xmlBase: null, xmlLang: null, xmlSpace: null }, space: "xml", transform(e2, n) {
    return "xml:" + n.slice(3).toLowerCase();
  } });
  var xn = { classId: "classID", dataType: "datatype", itemId: "itemID", strokeDashArray: "strokeDasharray", strokeDashOffset: "strokeDashoffset", strokeLineCap: "strokeLinecap", strokeLineJoin: "strokeLinejoin", strokeMiterLimit: "strokeMiterlimit", typeOf: "typeof", xLinkActuate: "xlinkActuate", xLinkArcRole: "xlinkArcrole", xLinkHref: "xlinkHref", xLinkRole: "xlinkRole", xLinkShow: "xlinkShow", xLinkTitle: "xlinkTitle", xLinkType: "xlinkType", xmlnsXLink: "xmlnsXlink" };
  var la = /[A-Z]/g;
  var ei = /-[a-z]/g;
  var aa = /^data[-\w.:]+$/i;
  function kn(e2, n) {
    let t = ut(n), r = n, i = K;
    if (t in e2.normal) return e2.property[e2.normal[t]];
    if (t.length > 4 && t.slice(0, 4) === "data" && aa.test(n)) {
      if (n.charAt(4) === "-") {
        let l = n.slice(5).replace(ei, sa);
        r = "data" + l.charAt(0).toUpperCase() + l.slice(1);
      } else {
        let l = n.slice(4);
        if (!ei.test(l)) {
          let o = l.replace(la, ua);
          o.charAt(0) !== "-" && (o = "-" + o), n = "data" + o;
        }
      }
      i = Oe;
    }
    return new i(r, n);
  }
  function ua(e2) {
    return "-" + e2.toLowerCase();
  }
  function sa(e2) {
    return e2.charAt(1).toUpperCase();
  }
  var ti = fn([mn, Jr, hn, dn, gn], "html");
  var Lt = fn([mn, Kr, hn, dn, gn], "svg");
  function ni(e2) {
    return e2.join(" ").trim();
  }
  var xi = Yr(mi(), 1);
  var Pt = hi("end");
  var Ge = hi("start");
  function hi(e2) {
    return n;
    function n(t) {
      let r = t && t.position && t.position[e2] || {};
      if (typeof r.line == "number" && r.line > 0 && typeof r.column == "number" && r.column > 0) return { line: r.line, column: r.column, offset: typeof r.offset == "number" && r.offset > -1 ? r.offset : void 0 };
    }
  }
  function wn(e2) {
    let n = Ge(e2), t = Pt(e2);
    if (n && t) return { start: n, end: t };
  }
  function Te(e2) {
    return !e2 || typeof e2 != "object" ? "" : "position" in e2 || "type" in e2 ? di(e2.position) : "start" in e2 || "end" in e2 ? di(e2) : "line" in e2 || "column" in e2 ? Sn(e2) : "";
  }
  function Sn(e2) {
    return gi(e2 && e2.line) + ":" + gi(e2 && e2.column);
  }
  function di(e2) {
    return Sn(e2 && e2.start) + "-" + Sn(e2 && e2.end);
  }
  function gi(e2) {
    return e2 && typeof e2 == "number" ? e2 : 1;
  }
  var Y = class extends Error {
    constructor(n, t, r) {
      super(), typeof t == "string" && (r = t, t = void 0);
      let i = "", l = {}, o = false;
      if (t && ("line" in t && "column" in t ? l = { place: t } : "start" in t && "end" in t ? l = { place: t } : "type" in t ? l = { ancestors: [t], place: t.position } : l = { ...t }), typeof n == "string" ? i = n : !l.cause && n && (o = true, i = n.message, l.cause = n), !l.ruleId && !l.source && typeof r == "string") {
        let u = r.indexOf(":");
        u === -1 ? l.ruleId = r : (l.source = r.slice(0, u), l.ruleId = r.slice(u + 1));
      }
      if (!l.place && l.ancestors && l.ancestors) {
        let u = l.ancestors[l.ancestors.length - 1];
        u && (l.place = u.position);
      }
      let a = l.place && "start" in l.place ? l.place.start : l.place;
      this.ancestors = l.ancestors || void 0, this.cause = l.cause || void 0, this.column = a ? a.column : void 0, this.fatal = void 0, this.file = "", this.message = i, this.line = a ? a.line : void 0, this.name = Te(l.place) || "1:1", this.place = l.place || void 0, this.reason = this.message, this.ruleId = l.ruleId || void 0, this.source = l.source || void 0, this.stack = o && l.cause && typeof l.cause.stack == "string" ? l.cause.stack : "", this.actual = void 0, this.expected = void 0, this.note = void 0, this.url = void 0;
    }
  };
  Y.prototype.file = "";
  Y.prototype.name = "";
  Y.prototype.reason = "";
  Y.prototype.message = "";
  Y.prototype.stack = "";
  Y.prototype.column = void 0;
  Y.prototype.line = void 0;
  Y.prototype.ancestors = void 0;
  Y.prototype.cause = void 0;
  Y.prototype.fatal = void 0;
  Y.prototype.place = void 0;
  Y.prototype.ruleId = void 0;
  Y.prototype.source = void 0;
  var Cn = {}.hasOwnProperty;
  var Ma = /* @__PURE__ */ new Map();
  var Oa = /[A-Z]/g;
  var _a = /* @__PURE__ */ new Set(["table", "tbody", "thead", "tfoot", "tr"]);
  var Na = /* @__PURE__ */ new Set(["td", "th"]);
  var ki = "https://github.com/syntax-tree/hast-util-to-jsx-runtime";
  function En(e2, n) {
    if (!n || n.Fragment === void 0) throw new TypeError("Expected `Fragment` in options");
    let t = n.filePath || void 0, r;
    if (n.development) {
      if (typeof n.jsxDEV != "function") throw new TypeError("Expected `jsxDEV` in options when `development: true`");
      r = Xa(t, n.jsxDEV);
    } else {
      if (typeof n.jsx != "function") throw new TypeError("Expected `jsx` in production options");
      if (typeof n.jsxs != "function") throw new TypeError("Expected `jsxs` in production options");
      r = Wa(t, n.jsx, n.jsxs);
    }
    let i = { Fragment: n.Fragment, ancestors: [], components: n.components || {}, create: r, elementAttributeNameCase: n.elementAttributeNameCase || "react", evaluater: n.createEvaluater ? n.createEvaluater() : void 0, filePath: t, ignoreInvalidStyle: n.ignoreInvalidStyle || false, passKeys: n.passKeys !== false, passNode: n.passNode || false, schema: n.space === "svg" ? Lt : ti, stylePropertyNameCase: n.stylePropertyNameCase || "dom", tableCellAlignToStyle: n.tableCellAlignToStyle !== false }, l = yi(i, e2, void 0);
    return l && typeof l != "string" ? l : i.create(e2, i.Fragment, { children: l || void 0 }, void 0);
  }
  function yi(e2, n, t) {
    if (n.type === "element") return Ba(e2, n, t);
    if (n.type === "mdxFlowExpression" || n.type === "mdxTextExpression") return Ha(e2, n);
    if (n.type === "mdxJsxFlowElement" || n.type === "mdxJsxTextElement") return Ua(e2, n, t);
    if (n.type === "mdxjsEsm") return ja(e2, n);
    if (n.type === "root") return Va(e2, n, t);
    if (n.type === "text") return qa(e2, n);
  }
  function Ba(e2, n, t) {
    let r = e2.schema, i = r;
    n.tagName.toLowerCase() === "svg" && r.space === "html" && (i = Lt, e2.schema = i), e2.ancestors.push(n);
    let l = wi(e2, n.tagName, false), o = Qa(e2, n), a = Tn(e2, n);
    return _a.has(n.tagName) && (a = a.filter(function(u) {
      return typeof u == "string" ? !cn(u) : true;
    })), bi(e2, o, l, n), In(o, a), e2.ancestors.pop(), e2.schema = r, e2.create(n, l, o, t);
  }
  function Ha(e2, n) {
    if (n.data && n.data.estree && e2.evaluater) {
      let r = n.data.estree.body[0];
      return r.type, e2.evaluater.evaluateExpression(r.expression);
    }
    ft(e2, n.position);
  }
  function ja(e2, n) {
    if (n.data && n.data.estree && e2.evaluater) return e2.evaluater.evaluateProgram(n.data.estree);
    ft(e2, n.position);
  }
  function Ua(e2, n, t) {
    let r = e2.schema, i = r;
    n.name === "svg" && r.space === "html" && (i = Lt, e2.schema = i), e2.ancestors.push(n);
    let l = n.name === null ? e2.Fragment : wi(e2, n.name, true), o = Ya(e2, n), a = Tn(e2, n);
    return bi(e2, o, l, n), In(o, a), e2.ancestors.pop(), e2.schema = r, e2.create(n, l, o, t);
  }
  function Va(e2, n, t) {
    let r = {};
    return In(r, Tn(e2, n)), e2.create(n, e2.Fragment, r, t);
  }
  function qa(e2, n) {
    return n.value;
  }
  function bi(e2, n, t, r) {
    typeof t != "string" && t !== e2.Fragment && e2.passNode && (n.node = r);
  }
  function In(e2, n) {
    if (n.length > 0) {
      let t = n.length > 1 ? n : n[0];
      t && (e2.children = t);
    }
  }
  function Wa(e2, n, t) {
    return r;
    function r(i, l, o, a) {
      let s32 = Array.isArray(o.children) ? t : n;
      return a ? s32(l, o, a) : s32(l, o);
    }
  }
  function Xa(e2, n) {
    return t;
    function t(r, i, l, o) {
      let a = Array.isArray(l.children), u = Ge(r);
      return n(i, l, o, a, { columnNumber: u ? u.column - 1 : void 0, fileName: e2, lineNumber: u ? u.line : void 0 }, void 0);
    }
  }
  function Qa(e2, n) {
    let t = {}, r, i;
    for (i in n.properties) if (i !== "children" && Cn.call(n.properties, i)) {
      let l = Za(e2, i, n.properties[i]);
      if (l) {
        let [o, a] = l;
        e2.tableCellAlignToStyle && o === "align" && typeof a == "string" && Na.has(n.tagName) ? r = a : t[o] = a;
      }
    }
    if (r) {
      let l = t.style || (t.style = {});
      l[e2.stylePropertyNameCase === "css" ? "text-align" : "textAlign"] = r;
    }
    return t;
  }
  function Ya(e2, n) {
    let t = {};
    for (let r of n.attributes) if (r.type === "mdxJsxExpressionAttribute") if (r.data && r.data.estree && e2.evaluater) {
      let l = r.data.estree.body[0];
      l.type;
      let o = l.expression;
      o.type;
      let a = o.properties[0];
      a.type, Object.assign(t, e2.evaluater.evaluateExpression(a.argument));
    } else ft(e2, n.position);
    else {
      let i = r.name, l;
      if (r.value && typeof r.value == "object") if (r.value.data && r.value.data.estree && e2.evaluater) {
        let a = r.value.data.estree.body[0];
        a.type, l = e2.evaluater.evaluateExpression(a.expression);
      } else ft(e2, n.position);
      else l = r.value === null ? true : r.value;
      t[i] = l;
    }
    return t;
  }
  function Tn(e2, n) {
    let t = [], r = -1, i = e2.passKeys ? /* @__PURE__ */ new Map() : Ma;
    for (; ++r < n.children.length; ) {
      let l = n.children[r], o;
      if (e2.passKeys) {
        let u = l.type === "element" ? l.tagName : l.type === "mdxJsxFlowElement" || l.type === "mdxJsxTextElement" ? l.name : void 0;
        if (u) {
          let s32 = i.get(u) || 0;
          o = u + "-" + s32, i.set(u, s32 + 1);
        }
      }
      let a = yi(e2, l, o);
      a !== void 0 && t.push(a);
    }
    return t;
  }
  function Za(e2, n, t) {
    let r = kn(e2.schema, n);
    if (!(t == null || typeof t == "number" && Number.isNaN(t))) {
      if (Array.isArray(t) && (t = r.commaSeparated ? Zr(t) : ni(t)), r.property === "style") {
        let i = typeof t == "object" ? t : Ga(e2, String(t));
        return e2.stylePropertyNameCase === "css" && (i = $a(i)), ["style", i];
      }
      return [e2.elementAttributeNameCase === "react" && r.space ? xn[r.property] || r.property : r.attribute, t];
    }
  }
  function Ga(e2, n) {
    try {
      return (0, xi.default)(n, { reactCompat: true });
    } catch (t) {
      if (e2.ignoreInvalidStyle) return {};
      let r = t, i = new Y("Cannot parse `style` attribute", { ancestors: e2.ancestors, cause: r, ruleId: "style", source: "hast-util-to-jsx-runtime" });
      throw i.file = e2.filePath || void 0, i.url = ki + "#cannot-parse-style-attribute", i;
    }
  }
  function wi(e2, n, t) {
    let r;
    if (!t) r = { type: "Literal", value: n };
    else if (n.includes(".")) {
      let i = n.split("."), l = -1, o;
      for (; ++l < i.length; ) {
        let a = Et(i[l]) ? { type: "Identifier", name: i[l] } : { type: "Literal", value: i[l] };
        o = o ? { type: "MemberExpression", object: o, property: a, computed: !!(l && a.type === "Literal"), optional: false } : a;
      }
      r = o;
    } else r = Et(n) && !/^[a-z]/.test(n) ? { type: "Identifier", name: n } : { type: "Literal", value: n };
    if (r.type === "Literal") {
      let i = r.value;
      return Cn.call(e2.components, i) ? e2.components[i] : i;
    }
    if (e2.evaluater) return e2.evaluater.evaluateExpression(r);
    ft(e2);
  }
  function ft(e2, n) {
    let t = new Y("Cannot handle MDX estrees without `createEvaluater`", { ancestors: e2.ancestors, place: n, ruleId: "mdx-estree", source: "hast-util-to-jsx-runtime" });
    throw t.file = e2.filePath || void 0, t.url = ki + "#cannot-handle-mdx-estrees-without-createevaluater", t;
  }
  function $a(e2) {
    let n = {}, t;
    for (t in e2) Cn.call(e2, t) && (n[Ja(t)] = e2[t]);
    return n;
  }
  function Ja(e2) {
    let n = e2.replace(Oa, Ka);
    return n.slice(0, 3) === "ms-" && (n = "-" + n), n;
  }
  function Ka(e2) {
    return "-" + e2.toLowerCase();
  }
  var pt = { action: ["form"], cite: ["blockquote", "del", "ins", "q"], data: ["object"], formAction: ["button", "input"], href: ["a", "area", "base", "link"], icon: ["menuitem"], itemId: null, manifest: ["html"], ping: ["a", "area"], poster: ["video"], src: ["audio", "embed", "iframe", "img", "input", "script", "source", "track", "video"] };
  var zt = globalThis.React;
  var Si = zt.Fragment;
  function Ci(e2, n, t, r) {
    var i = {}, l = n ? n.children : void 0;
    for (var o in n) o !== "children" && (i[o] = n[o]);
    return t !== void 0 && (i.key = t), l === void 0 ? zt.createElement(e2, i) : r && Array.isArray(l) ? zt.createElement.apply(null, [e2, i].concat(l)) : zt.createElement(e2, i, l);
  }
  function Ei(e2, n, t) {
    return Ci(e2, n, t, false);
  }
  function Ii(e2, n, t) {
    return Ci(e2, n, t, true);
  }
  var eu = globalThis.React;
  var { useState: tu, useRef: km, useEffect: nu, useMemo: ym, useCallback: bm, useLayoutEffect: wm, useId: Sm, useContext: Cm, useReducer: Em, useSyncExternalStore: Im, Fragment: Tm, createElement: Am, Children: Lm, cloneElement: vm, isValidElement: Pm, memo: zm, forwardRef: Fm, createContext: Dm } = eu;
  var ru = {};
  function Ne(e2, n) {
    let t = n || ru, r = typeof t.includeImageAlt == "boolean" ? t.includeImageAlt : true, i = typeof t.includeHtml == "boolean" ? t.includeHtml : true;
    return Ai(e2, r, i);
  }
  function Ai(e2, n, t) {
    if (iu(e2)) {
      if ("value" in e2) return e2.type === "html" && !t ? "" : e2.value;
      if (n && "alt" in e2 && e2.alt) return e2.alt;
      if ("children" in e2) return Ti(e2.children, n, t);
    }
    return Array.isArray(e2) ? Ti(e2, n, t) : "";
  }
  function Ti(e2, n, t) {
    let r = [], i = -1;
    for (; ++i < e2.length; ) r[i] = Ai(e2[i], n, t);
    return r.join("");
  }
  function iu(e2) {
    return !!(e2 && typeof e2 == "object");
  }
  var Li = document.createElement("i");
  function $e(e2) {
    let n = "&" + e2 + ";";
    Li.innerHTML = n;
    let t = Li.textContent;
    return t.charCodeAt(t.length - 1) === 59 && e2 !== "semi" || t === n ? false : t;
  }
  function Z(e2, n, t, r) {
    let i = e2.length, l = 0, o;
    if (n < 0 ? n = -n > i ? 0 : i + n : n = n > i ? i : n, t = t > 0 ? t : 0, r.length < 1e4) o = Array.from(r), o.unshift(n, t), e2.splice(...o);
    else for (t && e2.splice(n, t); l < r.length; ) o = r.slice(l, l + 1e4), o.unshift(n, 0), e2.splice(...o), l += 1e4, n += 1e4;
  }
  function re(e2, n) {
    return e2.length > 0 ? (Z(e2, e2.length, 0, n), e2) : n;
  }
  var vi = {}.hasOwnProperty;
  function Ft(e2) {
    let n = {}, t = -1;
    for (; ++t < e2.length; ) ou(n, e2[t]);
    return n;
  }
  function ou(e2, n) {
    let t;
    for (t in n) {
      let i = (vi.call(e2, t) ? e2[t] : void 0) || (e2[t] = {}), l = n[t], o;
      if (l) for (o in l) {
        vi.call(i, o) || (i[o] = []);
        let a = l[o];
        lu(i[o], Array.isArray(a) ? a : a ? [a] : []);
      }
    }
  }
  function lu(e2, n) {
    let t = -1, r = [];
    for (; ++t < n.length; ) (n[t].add === "after" ? e2 : r).push(n[t]);
    Z(e2, 0, 0, r);
  }
  function Dt(e2, n) {
    let t = Number.parseInt(e2, n);
    return t < 9 || t === 11 || t > 13 && t < 32 || t > 126 && t < 160 || t > 55295 && t < 57344 || t > 64975 && t < 65008 || (t & 65535) === 65535 || (t & 65535) === 65534 || t > 1114111 ? "\uFFFD" : String.fromCodePoint(t);
  }
  function te(e2) {
    return e2.replace(/[\t\n\r ]+/g, " ").replace(/^ | $/g, "").toLowerCase().toUpperCase();
  }
  var $ = Ae(/[A-Za-z]/);
  var Q = Ae(/[\dA-Za-z]/);
  var Pi = Ae(/[#-'*+\--9=?A-Z^-~]/);
  function Be(e2) {
    return e2 !== null && (e2 < 32 || e2 === 127);
  }
  var mt = Ae(/\d/);
  var zi = Ae(/[\dA-Fa-f]/);
  var Fi = Ae(/[!-/:-@[-`{-~]/);
  function A(e2) {
    return e2 !== null && e2 < -2;
  }
  function _(e2) {
    return e2 !== null && (e2 < 0 || e2 === 32);
  }
  function P(e2) {
    return e2 === -2 || e2 === -1 || e2 === 32;
  }
  var He = Ae(/\p{P}|\p{S}/u);
  var he = Ae(/\s/);
  function Ae(e2) {
    return n;
    function n(t) {
      return t !== null && t > -1 && e2.test(String.fromCharCode(t));
    }
  }
  function se(e2) {
    let n = [], t = -1, r = 0, i = 0;
    for (; ++t < e2.length; ) {
      let l = e2.charCodeAt(t), o = "";
      if (l === 37 && Q(e2.charCodeAt(t + 1)) && Q(e2.charCodeAt(t + 2))) i = 2;
      else if (l < 128) /[!#$&-;=?-Z_a-z~]/.test(String.fromCharCode(l)) || (o = String.fromCharCode(l));
      else if (l > 55295 && l < 57344) {
        let a = e2.charCodeAt(t + 1);
        l < 56320 && a > 56319 && a < 57344 ? (o = String.fromCharCode(l, a), i = 1) : o = "\uFFFD";
      } else o = String.fromCharCode(l);
      o && (n.push(e2.slice(r, t), encodeURIComponent(o)), r = t + i + 1, o = ""), i && (t += i, i = 0);
    }
    return n.join("") + e2.slice(r);
  }
  function v(e2, n, t, r) {
    let i = r ? r - 1 : Number.POSITIVE_INFINITY, l = 0;
    return o;
    function o(u) {
      return P(u) ? (e2.enter(t), a(u)) : n(u);
    }
    function a(u) {
      return P(u) && l++ < i ? (e2.consume(u), a) : (e2.exit(t), n(u));
    }
  }
  var Di = { tokenize: au };
  function au(e2) {
    let n = e2.attempt(this.parser.constructs.contentInitial, r, i), t;
    return n;
    function r(a) {
      if (a === null) {
        e2.consume(a);
        return;
      }
      return e2.enter("lineEnding"), e2.consume(a), e2.exit("lineEnding"), v(e2, n, "linePrefix");
    }
    function i(a) {
      return e2.enter("paragraph"), l(a);
    }
    function l(a) {
      let u = e2.enter("chunkText", { contentType: "text", previous: t });
      return t && (t.next = u), t = u, o(a);
    }
    function o(a) {
      if (a === null) {
        e2.exit("chunkText"), e2.exit("paragraph"), e2.consume(a);
        return;
      }
      return A(a) ? (e2.consume(a), e2.exit("chunkText"), l) : (e2.consume(a), o);
    }
  }
  var Mi = { tokenize: uu };
  var Ri = { tokenize: su };
  function uu(e2) {
    let n = this, t = [], r = 0, i, l, o;
    return a;
    function a(E) {
      if (r < t.length) {
        let M = t[r];
        return n.containerState = M[1], e2.attempt(M[0].continuation, u, s32)(E);
      }
      return s32(E);
    }
    function u(E) {
      if (r++, n.containerState._closeFlow) {
        n.containerState._closeFlow = void 0, i && T();
        let M = n.events.length, O = M, w;
        for (; O--; ) if (n.events[O][0] === "exit" && n.events[O][1].type === "chunkFlow") {
          w = n.events[O][1].end;
          break;
        }
        x(r);
        let B = M;
        for (; B < n.events.length; ) n.events[B][1].end = { ...w }, B++;
        return Z(n.events, O + 1, 0, n.events.slice(M)), n.events.length = B, s32(E);
      }
      return a(E);
    }
    function s32(E) {
      if (r === t.length) {
        if (!i) return m(E);
        if (i.currentConstruct && i.currentConstruct.concrete) return g(E);
        n.interrupt = !!(i.currentConstruct && !i._gfmTableDynamicInterruptHack);
      }
      return n.containerState = {}, e2.check(Ri, c, f)(E);
    }
    function c(E) {
      return i && T(), x(r), m(E);
    }
    function f(E) {
      return n.parser.lazy[n.now().line] = r !== t.length, o = n.now().offset, g(E);
    }
    function m(E) {
      return n.containerState = {}, e2.attempt(Ri, p, g)(E);
    }
    function p(E) {
      return r++, t.push([n.currentConstruct, n.containerState]), m(E);
    }
    function g(E) {
      if (E === null) {
        i && T(), x(0), e2.consume(E);
        return;
      }
      return i = i || n.parser.flow(n.now()), e2.enter("chunkFlow", { _tokenizer: i, contentType: "flow", previous: l }), k(E);
    }
    function k(E) {
      if (E === null) {
        C(e2.exit("chunkFlow"), true), x(0), e2.consume(E);
        return;
      }
      return A(E) ? (e2.consume(E), C(e2.exit("chunkFlow")), r = 0, n.interrupt = void 0, a) : (e2.consume(E), k);
    }
    function C(E, M) {
      let O = n.sliceStream(E);
      if (M && O.push(null), E.previous = l, l && (l.next = E), l = E, i.defineSkip(E.start), i.write(O), n.parser.lazy[E.start.line]) {
        let w = i.events.length;
        for (; w--; ) if (i.events[w][1].start.offset < o && (!i.events[w][1].end || i.events[w][1].end.offset > o)) return;
        let B = n.events.length, q = B, H, y;
        for (; q--; ) if (n.events[q][0] === "exit" && n.events[q][1].type === "chunkFlow") {
          if (H) {
            y = n.events[q][1].end;
            break;
          }
          H = true;
        }
        for (x(r), w = B; w < n.events.length; ) n.events[w][1].end = { ...y }, w++;
        Z(n.events, q + 1, 0, n.events.slice(B)), n.events.length = w;
      }
    }
    function x(E) {
      let M = t.length;
      for (; M-- > E; ) {
        let O = t[M];
        n.containerState = O[1], O[0].exit.call(n, e2);
      }
      t.length = E;
    }
    function T() {
      i.write([null]), l = void 0, i = void 0, n.containerState._closeFlow = void 0;
    }
  }
  function su(e2, n, t) {
    return v(e2, e2.attempt(this.parser.constructs.document, n, t), "linePrefix", this.parser.constructs.disable.null.includes("codeIndented") ? void 0 : 4);
  }
  function Ce(e2) {
    if (e2 === null || _(e2) || he(e2)) return 1;
    if (He(e2)) return 2;
  }
  function Le(e2, n, t) {
    let r = [], i = -1;
    for (; ++i < e2.length; ) {
      let l = e2[i].resolveAll;
      l && !r.includes(l) && (n = l(n, t), r.push(l));
    }
    return n;
  }
  var ht = { name: "attention", resolveAll: cu, tokenize: fu };
  function cu(e2, n) {
    let t = -1, r, i, l, o, a, u, s32, c;
    for (; ++t < e2.length; ) if (e2[t][0] === "enter" && e2[t][1].type === "attentionSequence" && e2[t][1]._close) {
      for (r = t; r--; ) if (e2[r][0] === "exit" && e2[r][1].type === "attentionSequence" && e2[r][1]._open && n.sliceSerialize(e2[r][1]).charCodeAt(0) === n.sliceSerialize(e2[t][1]).charCodeAt(0)) {
        if ((e2[r][1]._close || e2[t][1]._open) && (e2[t][1].end.offset - e2[t][1].start.offset) % 3 && !((e2[r][1].end.offset - e2[r][1].start.offset + e2[t][1].end.offset - e2[t][1].start.offset) % 3)) continue;
        u = e2[r][1].end.offset - e2[r][1].start.offset > 1 && e2[t][1].end.offset - e2[t][1].start.offset > 1 ? 2 : 1;
        let f = { ...e2[r][1].end }, m = { ...e2[t][1].start };
        Oi(f, -u), Oi(m, u), o = { type: u > 1 ? "strongSequence" : "emphasisSequence", start: f, end: { ...e2[r][1].end } }, a = { type: u > 1 ? "strongSequence" : "emphasisSequence", start: { ...e2[t][1].start }, end: m }, l = { type: u > 1 ? "strongText" : "emphasisText", start: { ...e2[r][1].end }, end: { ...e2[t][1].start } }, i = { type: u > 1 ? "strong" : "emphasis", start: { ...o.start }, end: { ...a.end } }, e2[r][1].end = { ...o.start }, e2[t][1].start = { ...a.end }, s32 = [], e2[r][1].end.offset - e2[r][1].start.offset && (s32 = re(s32, [["enter", e2[r][1], n], ["exit", e2[r][1], n]])), s32 = re(s32, [["enter", i, n], ["enter", o, n], ["exit", o, n], ["enter", l, n]]), s32 = re(s32, Le(n.parser.constructs.insideSpan.null, e2.slice(r + 1, t), n)), s32 = re(s32, [["exit", l, n], ["enter", a, n], ["exit", a, n], ["exit", i, n]]), e2[t][1].end.offset - e2[t][1].start.offset ? (c = 2, s32 = re(s32, [["enter", e2[t][1], n], ["exit", e2[t][1], n]])) : c = 0, Z(e2, r - 1, t - r + 3, s32), t = r + s32.length - c - 2;
        break;
      }
    }
    for (t = -1; ++t < e2.length; ) e2[t][1].type === "attentionSequence" && (e2[t][1].type = "data");
    return e2;
  }
  function fu(e2, n) {
    let t = this.parser.constructs.attentionMarkers.null, r = this.previous, i = Ce(r), l;
    return o;
    function o(u) {
      return l = u, e2.enter("attentionSequence"), a(u);
    }
    function a(u) {
      if (u === l) return e2.consume(u), a;
      let s32 = e2.exit("attentionSequence"), c = Ce(u), f = !c || c === 2 && i || t.includes(u), m = !i || i === 2 && c || t.includes(r);
      return s32._open = !!(l === 42 ? f : f && (i || !m)), s32._close = !!(l === 42 ? m : m && (c || !f)), n(u);
    }
  }
  function Oi(e2, n) {
    e2.column += n, e2.offset += n, e2._bufferIndex += n;
  }
  var An = { name: "autolink", tokenize: pu };
  function pu(e2, n, t) {
    let r = 0;
    return i;
    function i(p) {
      return e2.enter("autolink"), e2.enter("autolinkMarker"), e2.consume(p), e2.exit("autolinkMarker"), e2.enter("autolinkProtocol"), l;
    }
    function l(p) {
      return $(p) ? (e2.consume(p), o) : p === 64 ? t(p) : s32(p);
    }
    function o(p) {
      return p === 43 || p === 45 || p === 46 || Q(p) ? (r = 1, a(p)) : s32(p);
    }
    function a(p) {
      return p === 58 ? (e2.consume(p), r = 0, u) : (p === 43 || p === 45 || p === 46 || Q(p)) && r++ < 32 ? (e2.consume(p), a) : (r = 0, s32(p));
    }
    function u(p) {
      return p === 62 ? (e2.exit("autolinkProtocol"), e2.enter("autolinkMarker"), e2.consume(p), e2.exit("autolinkMarker"), e2.exit("autolink"), n) : p === null || p === 32 || p === 60 || Be(p) ? t(p) : (e2.consume(p), u);
    }
    function s32(p) {
      return p === 64 ? (e2.consume(p), c) : Pi(p) ? (e2.consume(p), s32) : t(p);
    }
    function c(p) {
      return Q(p) ? f(p) : t(p);
    }
    function f(p) {
      return p === 46 ? (e2.consume(p), r = 0, c) : p === 62 ? (e2.exit("autolinkProtocol").type = "autolinkEmail", e2.enter("autolinkMarker"), e2.consume(p), e2.exit("autolinkMarker"), e2.exit("autolink"), n) : m(p);
    }
    function m(p) {
      if ((p === 45 || Q(p)) && r++ < 63) {
        let g = p === 45 ? m : f;
        return e2.consume(p), g;
      }
      return t(p);
    }
  }
  var de = { partial: true, tokenize: mu };
  function mu(e2, n, t) {
    return r;
    function r(l) {
      return P(l) ? v(e2, i, "linePrefix")(l) : i(l);
    }
    function i(l) {
      return l === null || A(l) ? n(l) : t(l);
    }
  }
  var Rt = { continuation: { tokenize: du }, exit: gu, name: "blockQuote", tokenize: hu };
  function hu(e2, n, t) {
    let r = this;
    return i;
    function i(o) {
      if (o === 62) {
        let a = r.containerState;
        return a.open || (e2.enter("blockQuote", { _container: true }), a.open = true), e2.enter("blockQuotePrefix"), e2.enter("blockQuoteMarker"), e2.consume(o), e2.exit("blockQuoteMarker"), l;
      }
      return t(o);
    }
    function l(o) {
      return P(o) ? (e2.enter("blockQuotePrefixWhitespace"), e2.consume(o), e2.exit("blockQuotePrefixWhitespace"), e2.exit("blockQuotePrefix"), n) : (e2.exit("blockQuotePrefix"), n(o));
    }
  }
  function du(e2, n, t) {
    let r = this;
    return i;
    function i(o) {
      return P(o) ? v(e2, l, "linePrefix", r.parser.constructs.disable.null.includes("codeIndented") ? void 0 : 4)(o) : l(o);
    }
    function l(o) {
      return e2.attempt(Rt, n, t)(o);
    }
  }
  function gu(e2) {
    e2.exit("blockQuote");
  }
  var Mt = { name: "characterEscape", tokenize: xu };
  function xu(e2, n, t) {
    return r;
    function r(l) {
      return e2.enter("characterEscape"), e2.enter("escapeMarker"), e2.consume(l), e2.exit("escapeMarker"), i;
    }
    function i(l) {
      return Fi(l) ? (e2.enter("characterEscapeValue"), e2.consume(l), e2.exit("characterEscapeValue"), e2.exit("characterEscape"), n) : t(l);
    }
  }
  var Ot = { name: "characterReference", tokenize: ku };
  function ku(e2, n, t) {
    let r = this, i = 0, l, o;
    return a;
    function a(f) {
      return e2.enter("characterReference"), e2.enter("characterReferenceMarker"), e2.consume(f), e2.exit("characterReferenceMarker"), u;
    }
    function u(f) {
      return f === 35 ? (e2.enter("characterReferenceMarkerNumeric"), e2.consume(f), e2.exit("characterReferenceMarkerNumeric"), s32) : (e2.enter("characterReferenceValue"), l = 31, o = Q, c(f));
    }
    function s32(f) {
      return f === 88 || f === 120 ? (e2.enter("characterReferenceMarkerHexadecimal"), e2.consume(f), e2.exit("characterReferenceMarkerHexadecimal"), e2.enter("characterReferenceValue"), l = 6, o = zi, c) : (e2.enter("characterReferenceValue"), l = 7, o = mt, c(f));
    }
    function c(f) {
      if (f === 59 && i) {
        let m = e2.exit("characterReferenceValue");
        return o === Q && !$e(r.sliceSerialize(m)) ? t(f) : (e2.enter("characterReferenceMarker"), e2.consume(f), e2.exit("characterReferenceMarker"), e2.exit("characterReference"), n);
      }
      return o(f) && i++ < l ? (e2.consume(f), c) : t(f);
    }
  }
  var _i = { partial: true, tokenize: bu };
  var _t = { concrete: true, name: "codeFenced", tokenize: yu };
  function yu(e2, n, t) {
    let r = this, i = { partial: true, tokenize: O }, l = 0, o = 0, a;
    return u;
    function u(w) {
      return s32(w);
    }
    function s32(w) {
      let B = r.events[r.events.length - 1];
      return l = B && B[1].type === "linePrefix" ? B[2].sliceSerialize(B[1], true).length : 0, a = w, e2.enter("codeFenced"), e2.enter("codeFencedFence"), e2.enter("codeFencedFenceSequence"), c(w);
    }
    function c(w) {
      return w === a ? (o++, e2.consume(w), c) : o < 3 ? t(w) : (e2.exit("codeFencedFenceSequence"), P(w) ? v(e2, f, "whitespace")(w) : f(w));
    }
    function f(w) {
      return w === null || A(w) ? (e2.exit("codeFencedFence"), r.interrupt ? n(w) : e2.check(_i, k, M)(w)) : (e2.enter("codeFencedFenceInfo"), e2.enter("chunkString", { contentType: "string" }), m(w));
    }
    function m(w) {
      return w === null || A(w) ? (e2.exit("chunkString"), e2.exit("codeFencedFenceInfo"), f(w)) : P(w) ? (e2.exit("chunkString"), e2.exit("codeFencedFenceInfo"), v(e2, p, "whitespace")(w)) : w === 96 && w === a ? t(w) : (e2.consume(w), m);
    }
    function p(w) {
      return w === null || A(w) ? f(w) : (e2.enter("codeFencedFenceMeta"), e2.enter("chunkString", { contentType: "string" }), g(w));
    }
    function g(w) {
      return w === null || A(w) ? (e2.exit("chunkString"), e2.exit("codeFencedFenceMeta"), f(w)) : w === 96 && w === a ? t(w) : (e2.consume(w), g);
    }
    function k(w) {
      return e2.attempt(i, M, C)(w);
    }
    function C(w) {
      return e2.enter("lineEnding"), e2.consume(w), e2.exit("lineEnding"), x;
    }
    function x(w) {
      return l > 0 && P(w) ? v(e2, T, "linePrefix", l + 1)(w) : T(w);
    }
    function T(w) {
      return w === null || A(w) ? e2.check(_i, k, M)(w) : (e2.enter("codeFlowValue"), E(w));
    }
    function E(w) {
      return w === null || A(w) ? (e2.exit("codeFlowValue"), T(w)) : (e2.consume(w), E);
    }
    function M(w) {
      return e2.exit("codeFenced"), n(w);
    }
    function O(w, B, q) {
      let H = 0;
      return y;
      function y(R) {
        return w.enter("lineEnding"), w.consume(R), w.exit("lineEnding"), J;
      }
      function J(R) {
        return w.enter("codeFencedFence"), P(R) ? v(w, j, "linePrefix", r.parser.constructs.disable.null.includes("codeIndented") ? void 0 : 4)(R) : j(R);
      }
      function j(R) {
        return R === a ? (w.enter("codeFencedFenceSequence"), L(R)) : q(R);
      }
      function L(R) {
        return R === a ? (H++, w.consume(R), L) : H >= o ? (w.exit("codeFencedFenceSequence"), P(R) ? v(w, D, "whitespace")(R) : D(R)) : q(R);
      }
      function D(R) {
        return R === null || A(R) ? (w.exit("codeFencedFence"), B(R)) : q(R);
      }
    }
  }
  function bu(e2, n, t) {
    let r = this;
    return i;
    function i(o) {
      return o === null ? t(o) : (e2.enter("lineEnding"), e2.consume(o), e2.exit("lineEnding"), l);
    }
    function l(o) {
      return r.parser.lazy[r.now().line] ? t(o) : n(o);
    }
  }
  var dt = { name: "codeIndented", tokenize: Su };
  var wu = { partial: true, tokenize: Cu };
  function Su(e2, n, t) {
    let r = this;
    return i;
    function i(s32) {
      return e2.enter("codeIndented"), v(e2, l, "linePrefix", 5)(s32);
    }
    function l(s32) {
      let c = r.events[r.events.length - 1];
      return c && c[1].type === "linePrefix" && c[2].sliceSerialize(c[1], true).length >= 4 ? o(s32) : t(s32);
    }
    function o(s32) {
      return s32 === null ? u(s32) : A(s32) ? e2.attempt(wu, o, u)(s32) : (e2.enter("codeFlowValue"), a(s32));
    }
    function a(s32) {
      return s32 === null || A(s32) ? (e2.exit("codeFlowValue"), o(s32)) : (e2.consume(s32), a);
    }
    function u(s32) {
      return e2.exit("codeIndented"), n(s32);
    }
  }
  function Cu(e2, n, t) {
    let r = this;
    return i;
    function i(o) {
      return r.parser.lazy[r.now().line] ? t(o) : A(o) ? (e2.enter("lineEnding"), e2.consume(o), e2.exit("lineEnding"), i) : v(e2, l, "linePrefix", 5)(o);
    }
    function l(o) {
      let a = r.events[r.events.length - 1];
      return a && a[1].type === "linePrefix" && a[2].sliceSerialize(a[1], true).length >= 4 ? n(o) : A(o) ? i(o) : t(o);
    }
  }
  var Ln = { name: "codeText", previous: Iu, resolve: Eu, tokenize: Tu };
  function Eu(e2) {
    let n = e2.length - 4, t = 3, r, i;
    if ((e2[t][1].type === "lineEnding" || e2[t][1].type === "space") && (e2[n][1].type === "lineEnding" || e2[n][1].type === "space")) {
      for (r = t; ++r < n; ) if (e2[r][1].type === "codeTextData") {
        e2[t][1].type = "codeTextPadding", e2[n][1].type = "codeTextPadding", t += 2, n -= 2;
        break;
      }
    }
    for (r = t - 1, n++; ++r <= n; ) i === void 0 ? r !== n && e2[r][1].type !== "lineEnding" && (i = r) : (r === n || e2[r][1].type === "lineEnding") && (e2[i][1].type = "codeTextData", r !== i + 2 && (e2[i][1].end = e2[r - 1][1].end, e2.splice(i + 2, r - i - 2), n -= r - i - 2, r = i + 2), i = void 0);
    return e2;
  }
  function Iu(e2) {
    return e2 !== 96 || this.events[this.events.length - 1][1].type === "characterEscape";
  }
  function Tu(e2, n, t) {
    let r = this, i = 0, l, o;
    return a;
    function a(m) {
      return e2.enter("codeText"), e2.enter("codeTextSequence"), u(m);
    }
    function u(m) {
      return m === 96 ? (e2.consume(m), i++, u) : (e2.exit("codeTextSequence"), s32(m));
    }
    function s32(m) {
      return m === null ? t(m) : m === 32 ? (e2.enter("space"), e2.consume(m), e2.exit("space"), s32) : m === 96 ? (o = e2.enter("codeTextSequence"), l = 0, f(m)) : A(m) ? (e2.enter("lineEnding"), e2.consume(m), e2.exit("lineEnding"), s32) : (e2.enter("codeTextData"), c(m));
    }
    function c(m) {
      return m === null || m === 32 || m === 96 || A(m) ? (e2.exit("codeTextData"), s32(m)) : (e2.consume(m), c);
    }
    function f(m) {
      return m === 96 ? (e2.consume(m), l++, f) : l === i ? (e2.exit("codeTextSequence"), e2.exit("codeText"), n(m)) : (o.type = "codeTextData", c(m));
    }
  }
  var Nt = class {
    constructor(n) {
      this.left = n ? [...n] : [], this.right = [];
    }
    get(n) {
      if (n < 0 || n >= this.left.length + this.right.length) throw new RangeError("Cannot access index `" + n + "` in a splice buffer of size `" + (this.left.length + this.right.length) + "`");
      return n < this.left.length ? this.left[n] : this.right[this.right.length - n + this.left.length - 1];
    }
    get length() {
      return this.left.length + this.right.length;
    }
    shift() {
      return this.setCursor(0), this.right.pop();
    }
    slice(n, t) {
      let r = t == null ? Number.POSITIVE_INFINITY : t;
      return r < this.left.length ? this.left.slice(n, r) : n > this.left.length ? this.right.slice(this.right.length - r + this.left.length, this.right.length - n + this.left.length).reverse() : this.left.slice(n).concat(this.right.slice(this.right.length - r + this.left.length).reverse());
    }
    splice(n, t, r) {
      let i = t || 0;
      this.setCursor(Math.trunc(n));
      let l = this.right.splice(this.right.length - i, Number.POSITIVE_INFINITY);
      return r && gt(this.left, r), l.reverse();
    }
    pop() {
      return this.setCursor(Number.POSITIVE_INFINITY), this.left.pop();
    }
    push(n) {
      this.setCursor(Number.POSITIVE_INFINITY), this.left.push(n);
    }
    pushMany(n) {
      this.setCursor(Number.POSITIVE_INFINITY), gt(this.left, n);
    }
    unshift(n) {
      this.setCursor(0), this.right.push(n);
    }
    unshiftMany(n) {
      this.setCursor(0), gt(this.right, n.reverse());
    }
    setCursor(n) {
      if (!(n === this.left.length || n > this.left.length && this.right.length === 0 || n < 0 && this.left.length === 0)) if (n < this.left.length) {
        let t = this.left.splice(n, Number.POSITIVE_INFINITY);
        gt(this.right, t.reverse());
      } else {
        let t = this.right.splice(this.left.length + this.right.length - n, Number.POSITIVE_INFINITY);
        gt(this.left, t.reverse());
      }
    }
  };
  function gt(e2, n) {
    let t = 0;
    if (n.length < 1e4) e2.push(...n);
    else for (; t < n.length; ) e2.push(...n.slice(t, t + 1e4)), t += 1e4;
  }
  function Bt(e2) {
    let n = {}, t = -1, r, i, l, o, a, u, s32, c = new Nt(e2);
    for (; ++t < c.length; ) {
      for (; t in n; ) t = n[t];
      if (r = c.get(t), t && r[1].type === "chunkFlow" && c.get(t - 1)[1].type === "listItemPrefix" && (u = r[1]._tokenizer.events, l = 0, l < u.length && u[l][1].type === "lineEndingBlank" && (l += 2), l < u.length && u[l][1].type === "content")) for (; ++l < u.length && u[l][1].type !== "content"; ) u[l][1].type === "chunkText" && (u[l][1]._isInFirstContentOfListItem = true, l++);
      if (r[0] === "enter") r[1].contentType && (Object.assign(n, Au(c, t)), t = n[t], s32 = true);
      else if (r[1]._container) {
        for (l = t, i = void 0; l--; ) if (o = c.get(l), o[1].type === "lineEnding" || o[1].type === "lineEndingBlank") o[0] === "enter" && (i && (c.get(i)[1].type = "lineEndingBlank"), o[1].type = "lineEnding", i = l);
        else if (!(o[1].type === "linePrefix" || o[1].type === "listItemIndent")) break;
        i && (r[1].end = { ...c.get(i)[1].start }, a = c.slice(i, t), a.unshift(r), c.splice(i, t - i + 1, a));
      }
    }
    return Z(e2, 0, Number.POSITIVE_INFINITY, c.slice(0)), !s32;
  }
  function Au(e2, n) {
    let t = e2.get(n)[1], r = e2.get(n)[2], i = n - 1, l = [], o = t._tokenizer;
    o || (o = r.parser[t.contentType](t.start), t._contentTypeTextTrailing && (o._contentTypeTextTrailing = true));
    let a = o.events, u = [], s32 = {}, c, f, m = -1, p = t, g = 0, k = 0, C = [k];
    for (; p; ) {
      for (; e2.get(++i)[1] !== p; ) ;
      l.push(i), p._tokenizer || (c = r.sliceStream(p), p.next || c.push(null), f && o.defineSkip(p.start), p._isInFirstContentOfListItem && (o._gfmTasklistFirstContentOfListItem = true), o.write(c), p._isInFirstContentOfListItem && (o._gfmTasklistFirstContentOfListItem = void 0)), f = p, p = p.next;
    }
    for (p = t; ++m < a.length; ) a[m][0] === "exit" && a[m - 1][0] === "enter" && a[m][1].type === a[m - 1][1].type && a[m][1].start.line !== a[m][1].end.line && (k = m + 1, C.push(k), p._tokenizer = void 0, p.previous = void 0, p = p.next);
    for (o.events = [], p ? (p._tokenizer = void 0, p.previous = void 0) : C.pop(), m = C.length; m--; ) {
      let x = a.slice(C[m], C[m + 1]), T = l.pop();
      u.push([T, T + x.length - 1]), e2.splice(T, 2, x);
    }
    for (u.reverse(), m = -1; ++m < u.length; ) s32[g + u[m][0]] = g + u[m][1], g += u[m][1] - u[m][0] - 1;
    return s32;
  }
  var vn = { resolve: vu, tokenize: Pu };
  var Lu = { partial: true, tokenize: zu };
  function vu(e2) {
    return Bt(e2), e2;
  }
  function Pu(e2, n) {
    let t;
    return r;
    function r(a) {
      return e2.enter("content"), t = e2.enter("chunkContent", { contentType: "content" }), i(a);
    }
    function i(a) {
      return a === null ? l(a) : A(a) ? e2.check(Lu, o, l)(a) : (e2.consume(a), i);
    }
    function l(a) {
      return e2.exit("chunkContent"), e2.exit("content"), n(a);
    }
    function o(a) {
      return e2.consume(a), e2.exit("chunkContent"), t.next = e2.enter("chunkContent", { contentType: "content", previous: t }), t = t.next, i;
    }
  }
  function zu(e2, n, t) {
    let r = this;
    return i;
    function i(o) {
      return e2.exit("chunkContent"), e2.enter("lineEnding"), e2.consume(o), e2.exit("lineEnding"), v(e2, l, "linePrefix");
    }
    function l(o) {
      if (o === null || A(o)) return t(o);
      let a = r.events[r.events.length - 1];
      return !r.parser.constructs.disable.null.includes("codeIndented") && a && a[1].type === "linePrefix" && a[2].sliceSerialize(a[1], true).length >= 4 ? n(o) : e2.interrupt(r.parser.constructs.flow, t, n)(o);
    }
  }
  function Ht(e2, n, t, r, i, l, o, a, u) {
    let s32 = u || Number.POSITIVE_INFINITY, c = 0;
    return f;
    function f(x) {
      return x === 60 ? (e2.enter(r), e2.enter(i), e2.enter(l), e2.consume(x), e2.exit(l), m) : x === null || x === 32 || x === 41 || Be(x) ? t(x) : (e2.enter(r), e2.enter(o), e2.enter(a), e2.enter("chunkString", { contentType: "string" }), k(x));
    }
    function m(x) {
      return x === 62 ? (e2.enter(l), e2.consume(x), e2.exit(l), e2.exit(i), e2.exit(r), n) : (e2.enter(a), e2.enter("chunkString", { contentType: "string" }), p(x));
    }
    function p(x) {
      return x === 62 ? (e2.exit("chunkString"), e2.exit(a), m(x)) : x === null || x === 60 || A(x) ? t(x) : (e2.consume(x), x === 92 ? g : p);
    }
    function g(x) {
      return x === 60 || x === 62 || x === 92 ? (e2.consume(x), p) : p(x);
    }
    function k(x) {
      return !c && (x === null || x === 41 || _(x)) ? (e2.exit("chunkString"), e2.exit(a), e2.exit(o), e2.exit(r), n(x)) : c < s32 && x === 40 ? (e2.consume(x), c++, k) : x === 41 ? (e2.consume(x), c--, k) : x === null || x === 32 || x === 40 || Be(x) ? t(x) : (e2.consume(x), x === 92 ? C : k);
    }
    function C(x) {
      return x === 40 || x === 41 || x === 92 ? (e2.consume(x), k) : k(x);
    }
  }
  function jt(e2, n, t, r, i, l) {
    let o = this, a = 0, u;
    return s32;
    function s32(p) {
      return e2.enter(r), e2.enter(i), e2.consume(p), e2.exit(i), e2.enter(l), c;
    }
    function c(p) {
      return a > 999 || p === null || p === 91 || p === 93 && !u || p === 94 && !a && "_hiddenFootnoteSupport" in o.parser.constructs ? t(p) : p === 93 ? (e2.exit(l), e2.enter(i), e2.consume(p), e2.exit(i), e2.exit(r), n) : A(p) ? (e2.enter("lineEnding"), e2.consume(p), e2.exit("lineEnding"), c) : (e2.enter("chunkString", { contentType: "string" }), f(p));
    }
    function f(p) {
      return p === null || p === 91 || p === 93 || A(p) || a++ > 999 ? (e2.exit("chunkString"), c(p)) : (e2.consume(p), u || (u = !P(p)), p === 92 ? m : f);
    }
    function m(p) {
      return p === 91 || p === 92 || p === 93 ? (e2.consume(p), a++, f) : f(p);
    }
  }
  function Ut(e2, n, t, r, i, l) {
    let o;
    return a;
    function a(m) {
      return m === 34 || m === 39 || m === 40 ? (e2.enter(r), e2.enter(i), e2.consume(m), e2.exit(i), o = m === 40 ? 41 : m, u) : t(m);
    }
    function u(m) {
      return m === o ? (e2.enter(i), e2.consume(m), e2.exit(i), e2.exit(r), n) : (e2.enter(l), s32(m));
    }
    function s32(m) {
      return m === o ? (e2.exit(l), u(o)) : m === null ? t(m) : A(m) ? (e2.enter("lineEnding"), e2.consume(m), e2.exit("lineEnding"), v(e2, s32, "linePrefix")) : (e2.enter("chunkString", { contentType: "string" }), c(m));
    }
    function c(m) {
      return m === o || m === null || A(m) ? (e2.exit("chunkString"), s32(m)) : (e2.consume(m), m === 92 ? f : c);
    }
    function f(m) {
      return m === o || m === 92 ? (e2.consume(m), c) : c(m);
    }
  }
  function je(e2, n) {
    let t;
    return r;
    function r(i) {
      return A(i) ? (e2.enter("lineEnding"), e2.consume(i), e2.exit("lineEnding"), t = true, r) : P(i) ? v(e2, r, t ? "linePrefix" : "lineSuffix")(i) : n(i);
    }
  }
  var Pn = { name: "definition", tokenize: Du };
  var Fu = { partial: true, tokenize: Ru };
  function Du(e2, n, t) {
    let r = this, i;
    return l;
    function l(p) {
      return e2.enter("definition"), o(p);
    }
    function o(p) {
      return jt.call(r, e2, a, t, "definitionLabel", "definitionLabelMarker", "definitionLabelString")(p);
    }
    function a(p) {
      return i = te(r.sliceSerialize(r.events[r.events.length - 1][1]).slice(1, -1)), p === 58 ? (e2.enter("definitionMarker"), e2.consume(p), e2.exit("definitionMarker"), u) : t(p);
    }
    function u(p) {
      return _(p) ? je(e2, s32)(p) : s32(p);
    }
    function s32(p) {
      return Ht(e2, c, t, "definitionDestination", "definitionDestinationLiteral", "definitionDestinationLiteralMarker", "definitionDestinationRaw", "definitionDestinationString")(p);
    }
    function c(p) {
      return e2.attempt(Fu, f, f)(p);
    }
    function f(p) {
      return P(p) ? v(e2, m, "whitespace")(p) : m(p);
    }
    function m(p) {
      return p === null || A(p) ? (e2.exit("definition"), r.parser.defined.push(i), n(p)) : t(p);
    }
  }
  function Ru(e2, n, t) {
    return r;
    function r(a) {
      return _(a) ? je(e2, i)(a) : t(a);
    }
    function i(a) {
      return Ut(e2, l, t, "definitionTitle", "definitionTitleMarker", "definitionTitleString")(a);
    }
    function l(a) {
      return P(a) ? v(e2, o, "whitespace")(a) : o(a);
    }
    function o(a) {
      return a === null || A(a) ? n(a) : t(a);
    }
  }
  var zn = { name: "hardBreakEscape", tokenize: Mu };
  function Mu(e2, n, t) {
    return r;
    function r(l) {
      return e2.enter("hardBreakEscape"), e2.consume(l), i;
    }
    function i(l) {
      return A(l) ? (e2.exit("hardBreakEscape"), n(l)) : t(l);
    }
  }
  var Fn = { name: "headingAtx", resolve: Ou, tokenize: _u };
  function Ou(e2, n) {
    let t = e2.length - 2, r = 3, i, l;
    return e2[r][1].type === "whitespace" && (r += 2), t - 2 > r && e2[t][1].type === "whitespace" && (t -= 2), e2[t][1].type === "atxHeadingSequence" && (r === t - 1 || t - 4 > r && e2[t - 2][1].type === "whitespace") && (t -= r + 1 === t ? 2 : 4), t > r && (i = { type: "atxHeadingText", start: e2[r][1].start, end: e2[t][1].end }, l = { type: "chunkText", start: e2[r][1].start, end: e2[t][1].end, contentType: "text" }, Z(e2, r, t - r + 1, [["enter", i, n], ["enter", l, n], ["exit", l, n], ["exit", i, n]])), e2;
  }
  function _u(e2, n, t) {
    let r = 0;
    return i;
    function i(c) {
      return e2.enter("atxHeading"), l(c);
    }
    function l(c) {
      return e2.enter("atxHeadingSequence"), o(c);
    }
    function o(c) {
      return c === 35 && r++ < 6 ? (e2.consume(c), o) : c === null || _(c) ? (e2.exit("atxHeadingSequence"), a(c)) : t(c);
    }
    function a(c) {
      return c === 35 ? (e2.enter("atxHeadingSequence"), u(c)) : c === null || A(c) ? (e2.exit("atxHeading"), n(c)) : P(c) ? v(e2, a, "whitespace")(c) : (e2.enter("atxHeadingText"), s32(c));
    }
    function u(c) {
      return c === 35 ? (e2.consume(c), u) : (e2.exit("atxHeadingSequence"), a(c));
    }
    function s32(c) {
      return c === null || c === 35 || _(c) ? (e2.exit("atxHeadingText"), a(c)) : (e2.consume(c), s32);
    }
  }
  var Ni = ["address", "article", "aside", "base", "basefont", "blockquote", "body", "caption", "center", "col", "colgroup", "dd", "details", "dialog", "dir", "div", "dl", "dt", "fieldset", "figcaption", "figure", "footer", "form", "frame", "frameset", "h1", "h2", "h3", "h4", "h5", "h6", "head", "header", "hr", "html", "iframe", "legend", "li", "link", "main", "menu", "menuitem", "nav", "noframes", "ol", "optgroup", "option", "p", "param", "search", "section", "summary", "table", "tbody", "td", "tfoot", "th", "thead", "title", "tr", "track", "ul"];
  var Dn = ["pre", "script", "style", "textarea"];
  var Rn = { concrete: true, name: "htmlFlow", resolveTo: Hu, tokenize: ju };
  var Nu = { partial: true, tokenize: Vu };
  var Bu = { partial: true, tokenize: Uu };
  function Hu(e2) {
    let n = e2.length;
    for (; n-- && !(e2[n][0] === "enter" && e2[n][1].type === "htmlFlow"); ) ;
    return n > 1 && e2[n - 2][1].type === "linePrefix" && (e2[n][1].start = e2[n - 2][1].start, e2[n + 1][1].start = e2[n - 2][1].start, e2.splice(n - 2, 2)), e2;
  }
  function ju(e2, n, t) {
    let r = this, i, l, o, a, u;
    return s32;
    function s32(d) {
      return c(d);
    }
    function c(d) {
      return e2.enter("htmlFlow"), e2.enter("htmlFlowData"), e2.consume(d), f;
    }
    function f(d) {
      return d === 33 ? (e2.consume(d), m) : d === 47 ? (e2.consume(d), l = true, k) : d === 63 ? (e2.consume(d), i = 3, r.interrupt ? n : h) : $(d) ? (e2.consume(d), o = String.fromCharCode(d), C) : t(d);
    }
    function m(d) {
      return d === 45 ? (e2.consume(d), i = 2, p) : d === 91 ? (e2.consume(d), i = 5, a = 0, g) : $(d) ? (e2.consume(d), i = 4, r.interrupt ? n : h) : t(d);
    }
    function p(d) {
      return d === 45 ? (e2.consume(d), r.interrupt ? n : h) : t(d);
    }
    function g(d) {
      let oe = "CDATA[";
      return d === oe.charCodeAt(a++) ? (e2.consume(d), a === oe.length ? r.interrupt ? n : j : g) : t(d);
    }
    function k(d) {
      return $(d) ? (e2.consume(d), o = String.fromCharCode(d), C) : t(d);
    }
    function C(d) {
      if (d === null || d === 47 || d === 62 || _(d)) {
        let oe = d === 47, Fe = o.toLowerCase();
        return !oe && !l && Dn.includes(Fe) ? (i = 1, r.interrupt ? n(d) : j(d)) : Ni.includes(o.toLowerCase()) ? (i = 6, oe ? (e2.consume(d), x) : r.interrupt ? n(d) : j(d)) : (i = 7, r.interrupt && !r.parser.lazy[r.now().line] ? t(d) : l ? T(d) : E(d));
      }
      return d === 45 || Q(d) ? (e2.consume(d), o += String.fromCharCode(d), C) : t(d);
    }
    function x(d) {
      return d === 62 ? (e2.consume(d), r.interrupt ? n : j) : t(d);
    }
    function T(d) {
      return P(d) ? (e2.consume(d), T) : y(d);
    }
    function E(d) {
      return d === 47 ? (e2.consume(d), y) : d === 58 || d === 95 || $(d) ? (e2.consume(d), M) : P(d) ? (e2.consume(d), E) : y(d);
    }
    function M(d) {
      return d === 45 || d === 46 || d === 58 || d === 95 || Q(d) ? (e2.consume(d), M) : O(d);
    }
    function O(d) {
      return d === 61 ? (e2.consume(d), w) : P(d) ? (e2.consume(d), O) : E(d);
    }
    function w(d) {
      return d === null || d === 60 || d === 61 || d === 62 || d === 96 ? t(d) : d === 34 || d === 39 ? (e2.consume(d), u = d, B) : P(d) ? (e2.consume(d), w) : q(d);
    }
    function B(d) {
      return d === u ? (e2.consume(d), u = null, H) : d === null || A(d) ? t(d) : (e2.consume(d), B);
    }
    function q(d) {
      return d === null || d === 34 || d === 39 || d === 47 || d === 60 || d === 61 || d === 62 || d === 96 || _(d) ? O(d) : (e2.consume(d), q);
    }
    function H(d) {
      return d === 47 || d === 62 || P(d) ? E(d) : t(d);
    }
    function y(d) {
      return d === 62 ? (e2.consume(d), J) : t(d);
    }
    function J(d) {
      return d === null || A(d) ? j(d) : P(d) ? (e2.consume(d), J) : t(d);
    }
    function j(d) {
      return d === 45 && i === 2 ? (e2.consume(d), W) : d === 60 && i === 1 ? (e2.consume(d), G) : d === 62 && i === 4 ? (e2.consume(d), ae) : d === 63 && i === 3 ? (e2.consume(d), h) : d === 93 && i === 5 ? (e2.consume(d), me) : A(d) && (i === 6 || i === 7) ? (e2.exit("htmlFlowData"), e2.check(Nu, xe, L)(d)) : d === null || A(d) ? (e2.exit("htmlFlowData"), L(d)) : (e2.consume(d), j);
    }
    function L(d) {
      return e2.check(Bu, D, xe)(d);
    }
    function D(d) {
      return e2.enter("lineEnding"), e2.consume(d), e2.exit("lineEnding"), R;
    }
    function R(d) {
      return d === null || A(d) ? L(d) : (e2.enter("htmlFlowData"), j(d));
    }
    function W(d) {
      return d === 45 ? (e2.consume(d), h) : j(d);
    }
    function G(d) {
      return d === 47 ? (e2.consume(d), o = "", ce) : j(d);
    }
    function ce(d) {
      if (d === 62) {
        let oe = o.toLowerCase();
        return Dn.includes(oe) ? (e2.consume(d), ae) : j(d);
      }
      return $(d) && o.length < 8 ? (e2.consume(d), o += String.fromCharCode(d), ce) : j(d);
    }
    function me(d) {
      return d === 93 ? (e2.consume(d), h) : j(d);
    }
    function h(d) {
      return d === 62 ? (e2.consume(d), ae) : d === 45 && i === 2 ? (e2.consume(d), h) : j(d);
    }
    function ae(d) {
      return d === null || A(d) ? (e2.exit("htmlFlowData"), xe(d)) : (e2.consume(d), ae);
    }
    function xe(d) {
      return e2.exit("htmlFlow"), n(d);
    }
  }
  function Uu(e2, n, t) {
    let r = this;
    return i;
    function i(o) {
      return A(o) ? (e2.enter("lineEnding"), e2.consume(o), e2.exit("lineEnding"), l) : t(o);
    }
    function l(o) {
      return r.parser.lazy[r.now().line] ? t(o) : n(o);
    }
  }
  function Vu(e2, n, t) {
    return r;
    function r(i) {
      return e2.enter("lineEnding"), e2.consume(i), e2.exit("lineEnding"), e2.attempt(de, n, t);
    }
  }
  var Mn = { name: "htmlText", tokenize: qu };
  function qu(e2, n, t) {
    let r = this, i, l, o;
    return a;
    function a(h) {
      return e2.enter("htmlText"), e2.enter("htmlTextData"), e2.consume(h), u;
    }
    function u(h) {
      return h === 33 ? (e2.consume(h), s32) : h === 47 ? (e2.consume(h), O) : h === 63 ? (e2.consume(h), E) : $(h) ? (e2.consume(h), q) : t(h);
    }
    function s32(h) {
      return h === 45 ? (e2.consume(h), c) : h === 91 ? (e2.consume(h), l = 0, g) : $(h) ? (e2.consume(h), T) : t(h);
    }
    function c(h) {
      return h === 45 ? (e2.consume(h), p) : t(h);
    }
    function f(h) {
      return h === null ? t(h) : h === 45 ? (e2.consume(h), m) : A(h) ? (o = f, G(h)) : (e2.consume(h), f);
    }
    function m(h) {
      return h === 45 ? (e2.consume(h), p) : f(h);
    }
    function p(h) {
      return h === 62 ? W(h) : h === 45 ? m(h) : f(h);
    }
    function g(h) {
      let ae = "CDATA[";
      return h === ae.charCodeAt(l++) ? (e2.consume(h), l === ae.length ? k : g) : t(h);
    }
    function k(h) {
      return h === null ? t(h) : h === 93 ? (e2.consume(h), C) : A(h) ? (o = k, G(h)) : (e2.consume(h), k);
    }
    function C(h) {
      return h === 93 ? (e2.consume(h), x) : k(h);
    }
    function x(h) {
      return h === 62 ? W(h) : h === 93 ? (e2.consume(h), x) : k(h);
    }
    function T(h) {
      return h === null || h === 62 ? W(h) : A(h) ? (o = T, G(h)) : (e2.consume(h), T);
    }
    function E(h) {
      return h === null ? t(h) : h === 63 ? (e2.consume(h), M) : A(h) ? (o = E, G(h)) : (e2.consume(h), E);
    }
    function M(h) {
      return h === 62 ? W(h) : E(h);
    }
    function O(h) {
      return $(h) ? (e2.consume(h), w) : t(h);
    }
    function w(h) {
      return h === 45 || Q(h) ? (e2.consume(h), w) : B(h);
    }
    function B(h) {
      return A(h) ? (o = B, G(h)) : P(h) ? (e2.consume(h), B) : W(h);
    }
    function q(h) {
      return h === 45 || Q(h) ? (e2.consume(h), q) : h === 47 || h === 62 || _(h) ? H(h) : t(h);
    }
    function H(h) {
      return h === 47 ? (e2.consume(h), W) : h === 58 || h === 95 || $(h) ? (e2.consume(h), y) : A(h) ? (o = H, G(h)) : P(h) ? (e2.consume(h), H) : W(h);
    }
    function y(h) {
      return h === 45 || h === 46 || h === 58 || h === 95 || Q(h) ? (e2.consume(h), y) : J(h);
    }
    function J(h) {
      return h === 61 ? (e2.consume(h), j) : A(h) ? (o = J, G(h)) : P(h) ? (e2.consume(h), J) : H(h);
    }
    function j(h) {
      return h === null || h === 60 || h === 61 || h === 62 || h === 96 ? t(h) : h === 34 || h === 39 ? (e2.consume(h), i = h, L) : A(h) ? (o = j, G(h)) : P(h) ? (e2.consume(h), j) : (e2.consume(h), D);
    }
    function L(h) {
      return h === i ? (e2.consume(h), i = void 0, R) : h === null ? t(h) : A(h) ? (o = L, G(h)) : (e2.consume(h), L);
    }
    function D(h) {
      return h === null || h === 34 || h === 39 || h === 60 || h === 61 || h === 96 ? t(h) : h === 47 || h === 62 || _(h) ? H(h) : (e2.consume(h), D);
    }
    function R(h) {
      return h === 47 || h === 62 || _(h) ? H(h) : t(h);
    }
    function W(h) {
      return h === 62 ? (e2.consume(h), e2.exit("htmlTextData"), e2.exit("htmlText"), n) : t(h);
    }
    function G(h) {
      return e2.exit("htmlTextData"), e2.enter("lineEnding"), e2.consume(h), e2.exit("lineEnding"), ce;
    }
    function ce(h) {
      return P(h) ? v(e2, me, "linePrefix", r.parser.constructs.disable.null.includes("codeIndented") ? void 0 : 4)(h) : me(h);
    }
    function me(h) {
      return e2.enter("htmlTextData"), o(h);
    }
  }
  var Ue = { name: "labelEnd", resolveAll: Yu, resolveTo: Zu, tokenize: Gu };
  var Wu = { tokenize: $u };
  var Xu = { tokenize: Ju };
  var Qu = { tokenize: Ku };
  function Yu(e2) {
    let n = -1, t = [];
    for (; ++n < e2.length; ) {
      let r = e2[n][1];
      if (t.push(e2[n]), r.type === "labelImage" || r.type === "labelLink" || r.type === "labelEnd") {
        let i = r.type === "labelImage" ? 4 : 2;
        r.type = "data", n += i;
      }
    }
    return e2.length !== t.length && Z(e2, 0, e2.length, t), e2;
  }
  function Zu(e2, n) {
    let t = e2.length, r = 0, i, l, o, a;
    for (; t--; ) if (i = e2[t][1], l) {
      if (i.type === "link" || i.type === "labelLink" && i._inactive) break;
      e2[t][0] === "enter" && i.type === "labelLink" && (i._inactive = true);
    } else if (o) {
      if (e2[t][0] === "enter" && (i.type === "labelImage" || i.type === "labelLink") && !i._balanced && (l = t, i.type !== "labelLink")) {
        r = 2;
        break;
      }
    } else i.type === "labelEnd" && (o = t);
    let u = { type: e2[l][1].type === "labelLink" ? "link" : "image", start: { ...e2[l][1].start }, end: { ...e2[e2.length - 1][1].end } }, s32 = { type: "label", start: { ...e2[l][1].start }, end: { ...e2[o][1].end } }, c = { type: "labelText", start: { ...e2[l + r + 2][1].end }, end: { ...e2[o - 2][1].start } };
    return a = [["enter", u, n], ["enter", s32, n]], a = re(a, e2.slice(l + 1, l + r + 3)), a = re(a, [["enter", c, n]]), a = re(a, Le(n.parser.constructs.insideSpan.null, e2.slice(l + r + 4, o - 3), n)), a = re(a, [["exit", c, n], e2[o - 2], e2[o - 1], ["exit", s32, n]]), a = re(a, e2.slice(o + 1)), a = re(a, [["exit", u, n]]), Z(e2, l, e2.length, a), e2;
  }
  function Gu(e2, n, t) {
    let r = this, i = r.events.length, l, o;
    for (; i--; ) if ((r.events[i][1].type === "labelImage" || r.events[i][1].type === "labelLink") && !r.events[i][1]._balanced) {
      l = r.events[i][1];
      break;
    }
    return a;
    function a(m) {
      return l ? l._inactive ? f(m) : (o = r.parser.defined.includes(te(r.sliceSerialize({ start: l.end, end: r.now() }))), e2.enter("labelEnd"), e2.enter("labelMarker"), e2.consume(m), e2.exit("labelMarker"), e2.exit("labelEnd"), u) : t(m);
    }
    function u(m) {
      return m === 40 ? e2.attempt(Wu, c, o ? c : f)(m) : m === 91 ? e2.attempt(Xu, c, o ? s32 : f)(m) : o ? c(m) : f(m);
    }
    function s32(m) {
      return e2.attempt(Qu, c, f)(m);
    }
    function c(m) {
      return n(m);
    }
    function f(m) {
      return l._balanced = true, t(m);
    }
  }
  function $u(e2, n, t) {
    return r;
    function r(f) {
      return e2.enter("resource"), e2.enter("resourceMarker"), e2.consume(f), e2.exit("resourceMarker"), i;
    }
    function i(f) {
      return _(f) ? je(e2, l)(f) : l(f);
    }
    function l(f) {
      return f === 41 ? c(f) : Ht(e2, o, a, "resourceDestination", "resourceDestinationLiteral", "resourceDestinationLiteralMarker", "resourceDestinationRaw", "resourceDestinationString", 32)(f);
    }
    function o(f) {
      return _(f) ? je(e2, u)(f) : c(f);
    }
    function a(f) {
      return t(f);
    }
    function u(f) {
      return f === 34 || f === 39 || f === 40 ? Ut(e2, s32, t, "resourceTitle", "resourceTitleMarker", "resourceTitleString")(f) : c(f);
    }
    function s32(f) {
      return _(f) ? je(e2, c)(f) : c(f);
    }
    function c(f) {
      return f === 41 ? (e2.enter("resourceMarker"), e2.consume(f), e2.exit("resourceMarker"), e2.exit("resource"), n) : t(f);
    }
  }
  function Ju(e2, n, t) {
    let r = this;
    return i;
    function i(a) {
      return jt.call(r, e2, l, o, "reference", "referenceMarker", "referenceString")(a);
    }
    function l(a) {
      return r.parser.defined.includes(te(r.sliceSerialize(r.events[r.events.length - 1][1]).slice(1, -1))) ? n(a) : t(a);
    }
    function o(a) {
      return t(a);
    }
  }
  function Ku(e2, n, t) {
    return r;
    function r(l) {
      return e2.enter("reference"), e2.enter("referenceMarker"), e2.consume(l), e2.exit("referenceMarker"), i;
    }
    function i(l) {
      return l === 93 ? (e2.enter("referenceMarker"), e2.consume(l), e2.exit("referenceMarker"), e2.exit("reference"), n) : t(l);
    }
  }
  var On = { name: "labelStartImage", resolveAll: Ue.resolveAll, tokenize: es };
  function es(e2, n, t) {
    let r = this;
    return i;
    function i(a) {
      return e2.enter("labelImage"), e2.enter("labelImageMarker"), e2.consume(a), e2.exit("labelImageMarker"), l;
    }
    function l(a) {
      return a === 91 ? (e2.enter("labelMarker"), e2.consume(a), e2.exit("labelMarker"), e2.exit("labelImage"), o) : t(a);
    }
    function o(a) {
      return a === 94 && "_hiddenFootnoteSupport" in r.parser.constructs ? t(a) : n(a);
    }
  }
  var _n = { name: "labelStartLink", resolveAll: Ue.resolveAll, tokenize: ts };
  function ts(e2, n, t) {
    let r = this;
    return i;
    function i(o) {
      return e2.enter("labelLink"), e2.enter("labelMarker"), e2.consume(o), e2.exit("labelMarker"), e2.exit("labelLink"), l;
    }
    function l(o) {
      return o === 94 && "_hiddenFootnoteSupport" in r.parser.constructs ? t(o) : n(o);
    }
  }
  var xt = { name: "lineEnding", tokenize: ns };
  function ns(e2, n) {
    return t;
    function t(r) {
      return e2.enter("lineEnding"), e2.consume(r), e2.exit("lineEnding"), v(e2, n, "linePrefix");
    }
  }
  var Ve = { name: "thematicBreak", tokenize: rs };
  function rs(e2, n, t) {
    let r = 0, i;
    return l;
    function l(s32) {
      return e2.enter("thematicBreak"), o(s32);
    }
    function o(s32) {
      return i = s32, a(s32);
    }
    function a(s32) {
      return s32 === i ? (e2.enter("thematicBreakSequence"), u(s32)) : r >= 3 && (s32 === null || A(s32)) ? (e2.exit("thematicBreak"), n(s32)) : t(s32);
    }
    function u(s32) {
      return s32 === i ? (e2.consume(s32), r++, u) : (e2.exit("thematicBreakSequence"), P(s32) ? v(e2, a, "whitespace")(s32) : a(s32));
    }
  }
  var ne = { continuation: { tokenize: as }, exit: ss, name: "list", tokenize: ls };
  var is = { partial: true, tokenize: cs };
  var os = { partial: true, tokenize: us };
  function ls(e2, n, t) {
    let r = this, i = r.events[r.events.length - 1], l = i && i[1].type === "linePrefix" ? i[2].sliceSerialize(i[1], true).length : 0, o = 0;
    return a;
    function a(p) {
      let g = r.containerState.type || (p === 42 || p === 43 || p === 45 ? "listUnordered" : "listOrdered");
      if (g === "listUnordered" ? !r.containerState.marker || p === r.containerState.marker : mt(p)) {
        if (r.containerState.type || (r.containerState.type = g, e2.enter(g, { _container: true })), g === "listUnordered") return e2.enter("listItemPrefix"), p === 42 || p === 45 ? e2.check(Ve, t, s32)(p) : s32(p);
        if (!r.interrupt || p === 49) return e2.enter("listItemPrefix"), e2.enter("listItemValue"), u(p);
      }
      return t(p);
    }
    function u(p) {
      return mt(p) && ++o < 10 ? (e2.consume(p), u) : (!r.interrupt || o < 2) && (r.containerState.marker ? p === r.containerState.marker : p === 41 || p === 46) ? (e2.exit("listItemValue"), s32(p)) : t(p);
    }
    function s32(p) {
      return e2.enter("listItemMarker"), e2.consume(p), e2.exit("listItemMarker"), r.containerState.marker = r.containerState.marker || p, e2.check(de, r.interrupt ? t : c, e2.attempt(is, m, f));
    }
    function c(p) {
      return r.containerState.initialBlankLine = true, l++, m(p);
    }
    function f(p) {
      return P(p) ? (e2.enter("listItemPrefixWhitespace"), e2.consume(p), e2.exit("listItemPrefixWhitespace"), m) : t(p);
    }
    function m(p) {
      return r.containerState.size = l + r.sliceSerialize(e2.exit("listItemPrefix"), true).length, n(p);
    }
  }
  function as(e2, n, t) {
    let r = this;
    return r.containerState._closeFlow = void 0, e2.check(de, i, l);
    function i(a) {
      return r.containerState.furtherBlankLines = r.containerState.furtherBlankLines || r.containerState.initialBlankLine, v(e2, n, "listItemIndent", r.containerState.size + 1)(a);
    }
    function l(a) {
      return r.containerState.furtherBlankLines || !P(a) ? (r.containerState.furtherBlankLines = void 0, r.containerState.initialBlankLine = void 0, o(a)) : (r.containerState.furtherBlankLines = void 0, r.containerState.initialBlankLine = void 0, e2.attempt(os, n, o)(a));
    }
    function o(a) {
      return r.containerState._closeFlow = true, r.interrupt = void 0, v(e2, e2.attempt(ne, n, t), "linePrefix", r.parser.constructs.disable.null.includes("codeIndented") ? void 0 : 4)(a);
    }
  }
  function us(e2, n, t) {
    let r = this;
    return v(e2, i, "listItemIndent", r.containerState.size + 1);
    function i(l) {
      let o = r.events[r.events.length - 1];
      return o && o[1].type === "listItemIndent" && o[2].sliceSerialize(o[1], true).length === r.containerState.size ? n(l) : t(l);
    }
  }
  function ss(e2) {
    e2.exit(this.containerState.type);
  }
  function cs(e2, n, t) {
    let r = this;
    return v(e2, i, "listItemPrefixWhitespace", r.parser.constructs.disable.null.includes("codeIndented") ? void 0 : 5);
    function i(l) {
      let o = r.events[r.events.length - 1];
      return !P(l) && o && o[1].type === "listItemPrefixWhitespace" ? n(l) : t(l);
    }
  }
  var Vt = { name: "setextUnderline", resolveTo: fs, tokenize: ps };
  function fs(e2, n) {
    let t = e2.length, r, i, l;
    for (; t--; ) if (e2[t][0] === "enter") {
      if (e2[t][1].type === "content") {
        r = t;
        break;
      }
      e2[t][1].type === "paragraph" && (i = t);
    } else e2[t][1].type === "content" && e2.splice(t, 1), !l && e2[t][1].type === "definition" && (l = t);
    let o = { type: "setextHeading", start: { ...e2[r][1].start }, end: { ...e2[e2.length - 1][1].end } };
    return e2[i][1].type = "setextHeadingText", l ? (e2.splice(i, 0, ["enter", o, n]), e2.splice(l + 1, 0, ["exit", e2[r][1], n]), e2[r][1].end = { ...e2[l][1].end }) : e2[r][1] = o, e2.push(["exit", o, n]), e2;
  }
  function ps(e2, n, t) {
    let r = this, i;
    return l;
    function l(s32) {
      let c = r.events.length, f;
      for (; c--; ) if (r.events[c][1].type !== "lineEnding" && r.events[c][1].type !== "linePrefix" && r.events[c][1].type !== "content") {
        f = r.events[c][1].type === "paragraph";
        break;
      }
      return !r.parser.lazy[r.now().line] && (r.interrupt || f) ? (e2.enter("setextHeadingLine"), i = s32, o(s32)) : t(s32);
    }
    function o(s32) {
      return e2.enter("setextHeadingLineSequence"), a(s32);
    }
    function a(s32) {
      return s32 === i ? (e2.consume(s32), a) : (e2.exit("setextHeadingLineSequence"), P(s32) ? v(e2, u, "lineSuffix")(s32) : u(s32));
    }
    function u(s32) {
      return s32 === null || A(s32) ? (e2.exit("setextHeadingLine"), n(s32)) : t(s32);
    }
  }
  var Bi = { tokenize: ms };
  function ms(e2) {
    let n = this, t = e2.attempt(de, r, e2.attempt(this.parser.constructs.flowInitial, i, v(e2, e2.attempt(this.parser.constructs.flow, i, e2.attempt(vn, i)), "linePrefix")));
    return t;
    function r(l) {
      if (l === null) {
        e2.consume(l);
        return;
      }
      return e2.enter("lineEndingBlank"), e2.consume(l), e2.exit("lineEndingBlank"), n.currentConstruct = void 0, t;
    }
    function i(l) {
      if (l === null) {
        e2.consume(l);
        return;
      }
      return e2.enter("lineEnding"), e2.consume(l), e2.exit("lineEnding"), n.currentConstruct = void 0, t;
    }
  }
  var Hi = { resolveAll: qi() };
  var ji = Vi("string");
  var Ui = Vi("text");
  function Vi(e2) {
    return { resolveAll: qi(e2 === "text" ? hs : void 0), tokenize: n };
    function n(t) {
      let r = this, i = this.parser.constructs[e2], l = t.attempt(i, o, a);
      return o;
      function o(c) {
        return s32(c) ? l(c) : a(c);
      }
      function a(c) {
        if (c === null) {
          t.consume(c);
          return;
        }
        return t.enter("data"), t.consume(c), u;
      }
      function u(c) {
        return s32(c) ? (t.exit("data"), l(c)) : (t.consume(c), u);
      }
      function s32(c) {
        if (c === null) return true;
        let f = i[c], m = -1;
        if (f) for (; ++m < f.length; ) {
          let p = f[m];
          if (!p.previous || p.previous.call(r, r.previous)) return true;
        }
        return false;
      }
    }
  }
  function qi(e2) {
    return n;
    function n(t, r) {
      let i = -1, l;
      for (; ++i <= t.length; ) l === void 0 ? t[i] && t[i][1].type === "data" && (l = i, i++) : (!t[i] || t[i][1].type !== "data") && (i !== l + 2 && (t[l][1].end = t[i - 1][1].end, t.splice(l + 2, i - l - 2), i = l + 2), l = void 0);
      return e2 ? e2(t, r) : t;
    }
  }
  function hs(e2, n) {
    let t = 0;
    for (; ++t <= e2.length; ) if ((t === e2.length || e2[t][1].type === "lineEnding") && e2[t - 1][1].type === "data") {
      let r = e2[t - 1][1], i = n.sliceStream(r), l = i.length, o = -1, a = 0, u;
      for (; l--; ) {
        let s32 = i[l];
        if (typeof s32 == "string") {
          for (o = s32.length; s32.charCodeAt(o - 1) === 32; ) a++, o--;
          if (o) break;
          o = -1;
        } else if (s32 === -2) u = true, a++;
        else if (s32 !== -1) {
          l++;
          break;
        }
      }
      if (n._contentTypeTextTrailing && t === e2.length && (a = 0), a) {
        let s32 = { type: t === e2.length || u || a < 2 ? "lineSuffix" : "hardBreakTrailing", start: { _bufferIndex: l ? o : r.start._bufferIndex + o, _index: r.start._index + l, line: r.end.line, column: r.end.column - a, offset: r.end.offset - a }, end: { ...r.end } };
        r.end = { ...s32.start }, r.start.offset === r.end.offset ? Object.assign(r, s32) : (e2.splice(t, 0, ["enter", s32, n], ["exit", s32, n]), t += 2);
      }
      t++;
    }
    return e2;
  }
  var Nn = {};
  Qr(Nn, { attentionMarkers: () => Ss, contentInitial: () => gs, disable: () => Cs, document: () => ds, flow: () => ks, flowInitial: () => xs, insideSpan: () => ws, string: () => ys, text: () => bs });
  var ds = { 42: ne, 43: ne, 45: ne, 48: ne, 49: ne, 50: ne, 51: ne, 52: ne, 53: ne, 54: ne, 55: ne, 56: ne, 57: ne, 62: Rt };
  var gs = { 91: Pn };
  var xs = { [-2]: dt, [-1]: dt, 32: dt };
  var ks = { 35: Fn, 42: Ve, 45: [Vt, Ve], 60: Rn, 61: Vt, 95: Ve, 96: _t, 126: _t };
  var ys = { 38: Ot, 92: Mt };
  var bs = { [-5]: xt, [-4]: xt, [-3]: xt, 33: On, 38: Ot, 42: ht, 60: [An, Mn], 91: _n, 92: [zn, Mt], 93: Ue, 95: ht, 96: Ln };
  var ws = { null: [ht, Hi] };
  var Ss = { null: [42, 95] };
  var Cs = { null: [] };
  function Wi(e2, n, t) {
    let r = { _bufferIndex: -1, _index: 0, line: t && t.line || 1, column: t && t.column || 1, offset: t && t.offset || 0 }, i = {}, l = [], o = [], a = [], u = true, s32 = { attempt: H(B), check: H(q), consume: M, enter: O, exit: w, interrupt: H(q, { interrupt: true }) }, c = { code: null, containerState: {}, defineSkip: x, events: [], now: C, parser: e2, previous: null, sliceSerialize: g, sliceStream: k, write: p }, f = n.tokenize.call(c, s32), m;
    return n.resolveAll && l.push(n), c;
    function p(L) {
      return o = re(o, L), T(), o[o.length - 1] !== null ? [] : (y(n, 0), c.events = Le(l, c.events, c), c.events);
    }
    function g(L, D) {
      return Is(k(L), D);
    }
    function k(L) {
      return Es(o, L);
    }
    function C() {
      let { _bufferIndex: L, _index: D, line: R, column: W, offset: G } = r;
      return { _bufferIndex: L, _index: D, line: R, column: W, offset: G };
    }
    function x(L) {
      i[L.line] = L.column, j();
    }
    function T() {
      let L;
      for (; r._index < o.length; ) {
        let D = o[r._index];
        if (typeof D == "string") for (L = r._index, r._bufferIndex < 0 && (r._bufferIndex = 0); r._index === L && r._bufferIndex < D.length; ) E(D.charCodeAt(r._bufferIndex));
        else E(D);
      }
    }
    function E(L) {
      u = void 0, m = L, f = f(L);
    }
    function M(L) {
      A(L) ? (r.line++, r.column = 1, r.offset += L === -3 ? 2 : 1, j()) : L !== -1 && (r.column++, r.offset++), r._bufferIndex < 0 ? r._index++ : (r._bufferIndex++, r._bufferIndex === o[r._index].length && (r._bufferIndex = -1, r._index++)), c.previous = L, u = true;
    }
    function O(L, D) {
      let R = D || {};
      return R.type = L, R.start = C(), c.events.push(["enter", R, c]), a.push(R), R;
    }
    function w(L) {
      let D = a.pop();
      return D.end = C(), c.events.push(["exit", D, c]), D;
    }
    function B(L, D) {
      y(L, D.from);
    }
    function q(L, D) {
      D.restore();
    }
    function H(L, D) {
      return R;
      function R(W, G, ce) {
        let me, h, ae, xe;
        return Array.isArray(W) ? oe(W) : "tokenize" in W ? oe([W]) : d(W);
        function d(ee) {
          return it;
          function it(ke) {
            let De = ke !== null && ee[ke], Ye = ke !== null && ee.null, un = [...Array.isArray(De) ? De : De ? [De] : [], ...Array.isArray(Ye) ? Ye : Ye ? [Ye] : []];
            return oe(un)(ke);
          }
        }
        function oe(ee) {
          return me = ee, h = 0, ee.length === 0 ? ce : Fe(ee[h]);
        }
        function Fe(ee) {
          return it;
          function it(ke) {
            return xe = J(), ae = ee, ee.partial || (c.currentConstruct = ee), ee.name && c.parser.constructs.disable.null.includes(ee.name) ? Ct(ke) : ee.tokenize.call(D ? Object.assign(Object.create(c), D) : c, s32, an, Ct)(ke);
          }
        }
        function an(ee) {
          return u = true, L(ae, xe), G;
        }
        function Ct(ee) {
          return u = true, xe.restore(), ++h < me.length ? Fe(me[h]) : ce;
        }
      }
    }
    function y(L, D) {
      L.resolveAll && !l.includes(L) && l.push(L), L.resolve && Z(c.events, D, c.events.length - D, L.resolve(c.events.slice(D), c)), L.resolveTo && (c.events = L.resolveTo(c.events, c));
    }
    function J() {
      let L = C(), D = c.previous, R = c.currentConstruct, W = c.events.length, G = Array.from(a);
      return { from: W, restore: ce };
      function ce() {
        r = L, c.previous = D, c.currentConstruct = R, c.events.length = W, a = G, j();
      }
    }
    function j() {
      r.line in i && r.column < 2 && (r.column = i[r.line], r.offset += i[r.line] - 1);
    }
  }
  function Es(e2, n) {
    let t = n.start._index, r = n.start._bufferIndex, i = n.end._index, l = n.end._bufferIndex, o;
    if (t === i) o = [e2[t].slice(r, l)];
    else {
      if (o = e2.slice(t, i), r > -1) {
        let a = o[0];
        typeof a == "string" ? o[0] = a.slice(r) : o.shift();
      }
      l > 0 && o.push(e2[i].slice(0, l));
    }
    return o;
  }
  function Is(e2, n) {
    let t = -1, r = [], i;
    for (; ++t < e2.length; ) {
      let l = e2[t], o;
      if (typeof l == "string") o = l;
      else switch (l) {
        case -5: {
          o = "\r";
          break;
        }
        case -4: {
          o = `
`;
          break;
        }
        case -3: {
          o = `\r
`;
          break;
        }
        case -2: {
          o = n ? " " : "	";
          break;
        }
        case -1: {
          if (!n && i) continue;
          o = " ";
          break;
        }
        default:
          o = String.fromCharCode(l);
      }
      i = l === -2, r.push(o);
    }
    return r.join("");
  }
  function Bn(e2) {
    let r = { constructs: Ft([Nn, ...(e2 || {}).extensions || []]), content: i(Di), defined: [], document: i(Mi), flow: i(Bi), lazy: {}, string: i(ji), text: i(Ui) };
    return r;
    function i(l) {
      return o;
      function o(a) {
        return Wi(r, l, a);
      }
    }
  }
  function Hn(e2) {
    for (; !Bt(e2); ) ;
    return e2;
  }
  var Xi = /[\0\t\n\r]/g;
  function jn() {
    let e2 = 1, n = "", t = true, r;
    return i;
    function i(l, o, a) {
      let u = [], s32, c, f, m, p;
      for (l = n + (typeof l == "string" ? l.toString() : new TextDecoder(o || void 0).decode(l)), f = 0, n = "", t && (l.charCodeAt(0) === 65279 && f++, t = void 0); f < l.length; ) {
        if (Xi.lastIndex = f, s32 = Xi.exec(l), m = s32 && s32.index !== void 0 ? s32.index : l.length, p = l.charCodeAt(m), !s32) {
          n = l.slice(f);
          break;
        }
        if (p === 10 && f === m && r) u.push(-3), r = void 0;
        else switch (r && (u.push(-5), r = void 0), f < m && (u.push(l.slice(f, m)), e2 += m - f), p) {
          case 0: {
            u.push(65533), e2++;
            break;
          }
          case 9: {
            for (c = Math.ceil(e2 / 4) * 4, u.push(-2); e2++ < c; ) u.push(-1);
            break;
          }
          case 10: {
            u.push(-4), e2 = 1;
            break;
          }
          default:
            r = true, e2 = 1;
        }
        f = m + 1;
      }
      return a && (r && u.push(-5), n && u.push(n), u.push(null)), u;
    }
  }
  var Ts = /\\([!-/:-@[-`{-~])|&(#(?:\d{1,7}|x[\da-f]{1,6})|[\da-z]{1,31});/gi;
  function Qi(e2) {
    return e2.replace(Ts, As);
  }
  function As(e2, n, t) {
    if (n) return n;
    if (t.charCodeAt(0) === 35) {
      let i = t.charCodeAt(1), l = i === 120 || i === 88;
      return Dt(t.slice(l ? 2 : 1), l ? 16 : 10);
    }
    return $e(t) || e2;
  }
  var Zi = {}.hasOwnProperty;
  function Un(e2, n, t) {
    return n && typeof n == "object" && (t = n, n = void 0), Ls(t)(Hn(Bn(t).document().write(jn()(e2, n, true))));
  }
  function Ls(e2) {
    let n = { transforms: [], canContainEols: ["emphasis", "fragment", "heading", "paragraph", "strong"], enter: { autolink: l(Wr), autolinkProtocol: H, autolinkEmail: H, atxHeading: l(Ur), blockQuote: l(ke), characterEscape: H, characterReference: H, codeFenced: l(De), codeFencedFenceInfo: o, codeFencedFenceMeta: o, codeIndented: l(De, o), codeText: l(Ye, o), codeTextData: H, data: H, codeFlowValue: H, definition: l(un), definitionDestinationString: o, definitionLabelString: o, definitionTitleString: o, emphasis: l(Ul), hardBreakEscape: l(Vr), hardBreakTrailing: l(Vr), htmlFlow: l(qr, o), htmlFlowData: H, htmlText: l(qr, o), htmlTextData: H, image: l(Vl), label: o, link: l(Wr), listItem: l(ql), listItemValue: m, listOrdered: l(Xr, f), listUnordered: l(Xr), paragraph: l(Wl), reference: d, referenceString: o, resourceDestinationString: o, resourceTitleString: o, setextHeading: l(Ur), strong: l(Xl), thematicBreak: l(Yl) }, exit: { atxHeading: u(), atxHeadingSequence: O, autolink: u(), autolinkEmail: it, autolinkProtocol: ee, blockQuote: u(), characterEscapeValue: y, characterReferenceMarkerHexadecimal: Fe, characterReferenceMarkerNumeric: Fe, characterReferenceValue: an, characterReference: Ct, codeFenced: u(C), codeFencedFence: k, codeFencedFenceInfo: p, codeFencedFenceMeta: g, codeFlowValue: y, codeIndented: u(x), codeText: u(R), codeTextData: y, data: y, definition: u(), definitionDestinationString: M, definitionLabelString: T, definitionTitleString: E, emphasis: u(), hardBreakEscape: u(j), hardBreakTrailing: u(j), htmlFlow: u(L), htmlFlowData: y, htmlText: u(D), htmlTextData: y, image: u(G), label: me, labelText: ce, lineEnding: J, link: u(W), listItem: u(), listOrdered: u(), listUnordered: u(), paragraph: u(), referenceString: oe, resourceDestinationString: h, resourceTitleString: ae, resource: xe, setextHeading: u(q), setextHeadingLineSequence: B, setextHeadingText: w, strong: u(), thematicBreak: u() } };
    Gi(n, (e2 || {}).mdastExtensions || []);
    let t = {};
    return r;
    function r(b) {
      let I = { type: "root", children: [] }, F = { stack: [I], tokenStack: [], config: n, enter: a, exit: s32, buffer: o, resume: c, data: t }, N = [], V = -1;
      for (; ++V < b.length; ) if (b[V][1].type === "listOrdered" || b[V][1].type === "listUnordered") if (b[V][0] === "enter") N.push(V);
      else {
        let fe = N.pop();
        V = i(b, fe, V);
      }
      for (V = -1; ++V < b.length; ) {
        let fe = n[b[V][0]];
        Zi.call(fe, b[V][1].type) && fe[b[V][1].type].call(Object.assign({ sliceSerialize: b[V][2].sliceSerialize }, F), b[V][1]);
      }
      if (F.tokenStack.length > 0) {
        let fe = F.tokenStack[F.tokenStack.length - 1];
        (fe[1] || Yi).call(F, void 0, fe[0]);
      }
      for (I.position = { start: ve(b.length > 0 ? b[0][1].start : { line: 1, column: 1, offset: 0 }), end: ve(b.length > 0 ? b[b.length - 2][1].end : { line: 1, column: 1, offset: 0 }) }, V = -1; ++V < n.transforms.length; ) I = n.transforms[V](I) || I;
      return I;
    }
    function i(b, I, F) {
      let N = I - 1, V = -1, fe = false, Re, ye, ot, lt;
      for (; ++N <= F; ) {
        let le = b[N];
        switch (le[1].type) {
          case "listUnordered":
          case "listOrdered":
          case "blockQuote": {
            le[0] === "enter" ? V++ : V--, lt = void 0;
            break;
          }
          case "lineEndingBlank": {
            le[0] === "enter" && (Re && !lt && !V && !ot && (ot = N), lt = void 0);
            break;
          }
          case "linePrefix":
          case "listItemValue":
          case "listItemMarker":
          case "listItemPrefix":
          case "listItemPrefixWhitespace":
            break;
          default:
            lt = void 0;
        }
        if (!V && le[0] === "enter" && le[1].type === "listItemPrefix" || V === -1 && le[0] === "exit" && (le[1].type === "listUnordered" || le[1].type === "listOrdered")) {
          if (Re) {
            let Ze = N;
            for (ye = void 0; Ze--; ) {
              let be = b[Ze];
              if (be[1].type === "lineEnding" || be[1].type === "lineEndingBlank") {
                if (be[0] === "exit") continue;
                ye && (b[ye][1].type = "lineEndingBlank", fe = true), be[1].type = "lineEnding", ye = Ze;
              } else if (!(be[1].type === "linePrefix" || be[1].type === "blockQuotePrefix" || be[1].type === "blockQuotePrefixWhitespace" || be[1].type === "blockQuoteMarker" || be[1].type === "listItemIndent")) break;
            }
            ot && (!ye || ot < ye) && (Re._spread = true), Re.end = Object.assign({}, ye ? b[ye][1].start : le[1].end), b.splice(ye || N, 0, ["exit", Re, le[2]]), N++, F++;
          }
          if (le[1].type === "listItemPrefix") {
            let Ze = { type: "listItem", _spread: false, start: Object.assign({}, le[1].start), end: void 0 };
            Re = Ze, b.splice(N, 0, ["enter", Ze, le[2]]), N++, F++, ot = void 0, lt = true;
          }
        }
      }
      return b[I][1]._spread = fe, F;
    }
    function l(b, I) {
      return F;
      function F(N) {
        a.call(this, b(N), N), I && I.call(this, N);
      }
    }
    function o() {
      this.stack.push({ type: "fragment", children: [] });
    }
    function a(b, I, F) {
      this.stack[this.stack.length - 1].children.push(b), this.stack.push(b), this.tokenStack.push([I, F || void 0]), b.position = { start: ve(I.start), end: void 0 };
    }
    function u(b) {
      return I;
      function I(F) {
        b && b.call(this, F), s32.call(this, F);
      }
    }
    function s32(b, I) {
      let F = this.stack.pop(), N = this.tokenStack.pop();
      if (N) N[0].type !== b.type && (I ? I.call(this, b, N[0]) : (N[1] || Yi).call(this, b, N[0]));
      else throw new Error("Cannot close `" + b.type + "` (" + Te({ start: b.start, end: b.end }) + "): it\u2019s not open");
      F.position.end = ve(b.end);
    }
    function c() {
      return Ne(this.stack.pop());
    }
    function f() {
      this.data.expectingFirstListItemValue = true;
    }
    function m(b) {
      if (this.data.expectingFirstListItemValue) {
        let I = this.stack[this.stack.length - 2];
        I.start = Number.parseInt(this.sliceSerialize(b), 10), this.data.expectingFirstListItemValue = void 0;
      }
    }
    function p() {
      let b = this.resume(), I = this.stack[this.stack.length - 1];
      I.lang = b;
    }
    function g() {
      let b = this.resume(), I = this.stack[this.stack.length - 1];
      I.meta = b;
    }
    function k() {
      this.data.flowCodeInside || (this.buffer(), this.data.flowCodeInside = true);
    }
    function C() {
      let b = this.resume(), I = this.stack[this.stack.length - 1];
      I.value = b.replace(/^(\r?\n|\r)|(\r?\n|\r)$/g, ""), this.data.flowCodeInside = void 0;
    }
    function x() {
      let b = this.resume(), I = this.stack[this.stack.length - 1];
      I.value = b.replace(/(\r?\n|\r)$/g, "");
    }
    function T(b) {
      let I = this.resume(), F = this.stack[this.stack.length - 1];
      F.label = I, F.identifier = te(this.sliceSerialize(b)).toLowerCase();
    }
    function E() {
      let b = this.resume(), I = this.stack[this.stack.length - 1];
      I.title = b;
    }
    function M() {
      let b = this.resume(), I = this.stack[this.stack.length - 1];
      I.url = b;
    }
    function O(b) {
      let I = this.stack[this.stack.length - 1];
      if (!I.depth) {
        let F = this.sliceSerialize(b).length;
        I.depth = F;
      }
    }
    function w() {
      this.data.setextHeadingSlurpLineEnding = true;
    }
    function B(b) {
      let I = this.stack[this.stack.length - 1];
      I.depth = this.sliceSerialize(b).codePointAt(0) === 61 ? 1 : 2;
    }
    function q() {
      this.data.setextHeadingSlurpLineEnding = void 0;
    }
    function H(b) {
      let F = this.stack[this.stack.length - 1].children, N = F[F.length - 1];
      (!N || N.type !== "text") && (N = Ql(), N.position = { start: ve(b.start), end: void 0 }, F.push(N)), this.stack.push(N);
    }
    function y(b) {
      let I = this.stack.pop();
      I.value += this.sliceSerialize(b), I.position.end = ve(b.end);
    }
    function J(b) {
      let I = this.stack[this.stack.length - 1];
      if (this.data.atHardBreak) {
        let F = I.children[I.children.length - 1];
        F.position.end = ve(b.end), this.data.atHardBreak = void 0;
        return;
      }
      !this.data.setextHeadingSlurpLineEnding && n.canContainEols.includes(I.type) && (H.call(this, b), y.call(this, b));
    }
    function j() {
      this.data.atHardBreak = true;
    }
    function L() {
      let b = this.resume(), I = this.stack[this.stack.length - 1];
      I.value = b;
    }
    function D() {
      let b = this.resume(), I = this.stack[this.stack.length - 1];
      I.value = b;
    }
    function R() {
      let b = this.resume(), I = this.stack[this.stack.length - 1];
      I.value = b;
    }
    function W() {
      let b = this.stack[this.stack.length - 1];
      if (this.data.inReference) {
        let I = this.data.referenceType || "shortcut";
        b.type += "Reference", b.referenceType = I, delete b.url, delete b.title;
      } else delete b.identifier, delete b.label;
      this.data.referenceType = void 0;
    }
    function G() {
      let b = this.stack[this.stack.length - 1];
      if (this.data.inReference) {
        let I = this.data.referenceType || "shortcut";
        b.type += "Reference", b.referenceType = I, delete b.url, delete b.title;
      } else delete b.identifier, delete b.label;
      this.data.referenceType = void 0;
    }
    function ce(b) {
      let I = this.sliceSerialize(b), F = this.stack[this.stack.length - 2];
      F.label = Qi(I), F.identifier = te(I).toLowerCase();
    }
    function me() {
      let b = this.stack[this.stack.length - 1], I = this.resume(), F = this.stack[this.stack.length - 1];
      if (this.data.inReference = true, F.type === "link") {
        let N = b.children;
        F.children = N;
      } else F.alt = I;
    }
    function h() {
      let b = this.resume(), I = this.stack[this.stack.length - 1];
      I.url = b;
    }
    function ae() {
      let b = this.resume(), I = this.stack[this.stack.length - 1];
      I.title = b;
    }
    function xe() {
      this.data.inReference = void 0;
    }
    function d() {
      this.data.referenceType = "collapsed";
    }
    function oe(b) {
      let I = this.resume(), F = this.stack[this.stack.length - 1];
      F.label = I, F.identifier = te(this.sliceSerialize(b)).toLowerCase(), this.data.referenceType = "full";
    }
    function Fe(b) {
      this.data.characterReferenceType = b.type;
    }
    function an(b) {
      let I = this.sliceSerialize(b), F = this.data.characterReferenceType, N;
      F ? (N = Dt(I, F === "characterReferenceMarkerNumeric" ? 10 : 16), this.data.characterReferenceType = void 0) : N = $e(I);
      let V = this.stack[this.stack.length - 1];
      V.value += N;
    }
    function Ct(b) {
      let I = this.stack.pop();
      I.position.end = ve(b.end);
    }
    function ee(b) {
      y.call(this, b);
      let I = this.stack[this.stack.length - 1];
      I.url = this.sliceSerialize(b);
    }
    function it(b) {
      y.call(this, b);
      let I = this.stack[this.stack.length - 1];
      I.url = "mailto:" + this.sliceSerialize(b);
    }
    function ke() {
      return { type: "blockquote", children: [] };
    }
    function De() {
      return { type: "code", lang: null, meta: null, value: "" };
    }
    function Ye() {
      return { type: "inlineCode", value: "" };
    }
    function un() {
      return { type: "definition", identifier: "", label: null, title: null, url: "" };
    }
    function Ul() {
      return { type: "emphasis", children: [] };
    }
    function Ur() {
      return { type: "heading", depth: 0, children: [] };
    }
    function Vr() {
      return { type: "break" };
    }
    function qr() {
      return { type: "html", value: "" };
    }
    function Vl() {
      return { type: "image", title: null, url: "", alt: null };
    }
    function Wr() {
      return { type: "link", title: null, url: "", children: [] };
    }
    function Xr(b) {
      return { type: "list", ordered: b.type === "listOrdered", start: null, spread: b._spread, children: [] };
    }
    function ql(b) {
      return { type: "listItem", spread: b._spread, checked: null, children: [] };
    }
    function Wl() {
      return { type: "paragraph", children: [] };
    }
    function Xl() {
      return { type: "strong", children: [] };
    }
    function Ql() {
      return { type: "text", value: "" };
    }
    function Yl() {
      return { type: "thematicBreak" };
    }
  }
  function ve(e2) {
    return { line: e2.line, column: e2.column, offset: e2.offset };
  }
  function Gi(e2, n) {
    let t = -1;
    for (; ++t < n.length; ) {
      let r = n[t];
      Array.isArray(r) ? Gi(e2, r) : vs(e2, r);
    }
  }
  function vs(e2, n) {
    let t;
    for (t in n) if (Zi.call(n, t)) switch (t) {
      case "canContainEols": {
        let r = n[t];
        r && e2[t].push(...r);
        break;
      }
      case "transforms": {
        let r = n[t];
        r && e2[t].push(...r);
        break;
      }
      case "enter":
      case "exit": {
        let r = n[t];
        r && Object.assign(e2[t], r);
        break;
      }
    }
  }
  function Yi(e2, n) {
    throw e2 ? new Error("Cannot close `" + e2.type + "` (" + Te({ start: e2.start, end: e2.end }) + "): a different token (`" + n.type + "`, " + Te({ start: n.start, end: n.end }) + ") is open") : new Error("Cannot close document, a token (`" + n.type + "`, " + Te({ start: n.start, end: n.end }) + ") is still open");
  }
  function qt(e2) {
    let n = this;
    n.parser = t;
    function t(r) {
      return Un(r, { ...n.data("settings"), ...e2, extensions: n.data("micromarkExtensions") || [], mdastExtensions: n.data("fromMarkdownExtensions") || [] });
    }
  }
  function $i(e2, n) {
    let t = { type: "element", tagName: "blockquote", properties: {}, children: e2.wrap(e2.all(n), true) };
    return e2.patch(n, t), e2.applyData(n, t);
  }
  function Ji(e2, n) {
    let t = { type: "element", tagName: "br", properties: {}, children: [] };
    return e2.patch(n, t), [e2.applyData(n, t), { type: "text", value: `
` }];
  }
  function Ki(e2, n) {
    let t = n.value ? n.value + `
` : "", r = {}, i = n.lang ? n.lang.split(/\s+/) : [];
    i.length > 0 && (r.className = ["language-" + i[0]]);
    let l = { type: "element", tagName: "code", properties: r, children: [{ type: "text", value: t }] };
    return n.meta && (l.data = { meta: n.meta }), e2.patch(n, l), l = e2.applyData(n, l), l = { type: "element", tagName: "pre", properties: {}, children: [l] }, e2.patch(n, l), l;
  }
  function eo(e2, n) {
    let t = { type: "element", tagName: "del", properties: {}, children: e2.all(n) };
    return e2.patch(n, t), e2.applyData(n, t);
  }
  function to(e2, n) {
    let t = { type: "element", tagName: "em", properties: {}, children: e2.all(n) };
    return e2.patch(n, t), e2.applyData(n, t);
  }
  function no(e2, n) {
    let t = typeof e2.options.clobberPrefix == "string" ? e2.options.clobberPrefix : "user-content-", r = String(n.identifier).toUpperCase(), i = se(r.toLowerCase()), l = e2.footnoteOrder.indexOf(r), o, a = e2.footnoteCounts.get(r);
    a === void 0 ? (a = 0, e2.footnoteOrder.push(r), o = e2.footnoteOrder.length) : o = l + 1, a += 1, e2.footnoteCounts.set(r, a);
    let u = { type: "element", tagName: "a", properties: { href: "#" + t + "fn-" + i, id: t + "fnref-" + i + (a > 1 ? "-" + a : ""), dataFootnoteRef: true, ariaDescribedBy: ["footnote-label"] }, children: [{ type: "text", value: String(o) }] };
    e2.patch(n, u);
    let s32 = { type: "element", tagName: "sup", properties: {}, children: [u] };
    return e2.patch(n, s32), e2.applyData(n, s32);
  }
  function ro(e2, n) {
    let t = { type: "element", tagName: "h" + n.depth, properties: {}, children: e2.all(n) };
    return e2.patch(n, t), e2.applyData(n, t);
  }
  function io(e2, n) {
    if (e2.options.allowDangerousHtml) {
      let t = { type: "raw", value: n.value };
      return e2.patch(n, t), e2.applyData(n, t);
    }
  }
  function Wt(e2, n) {
    let t = n.referenceType, r = "]";
    if (t === "collapsed" ? r += "[]" : t === "full" && (r += "[" + (n.label || n.identifier) + "]"), n.type === "imageReference") return [{ type: "text", value: "![" + n.alt + r }];
    let i = e2.all(n), l = i[0];
    l && l.type === "text" ? l.value = "[" + l.value : i.unshift({ type: "text", value: "[" });
    let o = i[i.length - 1];
    return o && o.type === "text" ? o.value += r : i.push({ type: "text", value: r }), i;
  }
  function oo(e2, n) {
    let t = String(n.identifier).toUpperCase(), r = e2.definitionById.get(t);
    if (!r) return Wt(e2, n);
    let i = { src: se(r.url || ""), alt: n.alt };
    r.title !== null && r.title !== void 0 && (i.title = r.title);
    let l = { type: "element", tagName: "img", properties: i, children: [] };
    return e2.patch(n, l), e2.applyData(n, l);
  }
  function lo(e2, n) {
    let t = { src: se(n.url) };
    n.alt !== null && n.alt !== void 0 && (t.alt = n.alt), n.title !== null && n.title !== void 0 && (t.title = n.title);
    let r = { type: "element", tagName: "img", properties: t, children: [] };
    return e2.patch(n, r), e2.applyData(n, r);
  }
  function ao(e2, n) {
    let t = { type: "text", value: n.value.replace(/\r?\n|\r/g, " ") };
    e2.patch(n, t);
    let r = { type: "element", tagName: "code", properties: {}, children: [t] };
    return e2.patch(n, r), e2.applyData(n, r);
  }
  function uo(e2, n) {
    let t = String(n.identifier).toUpperCase(), r = e2.definitionById.get(t);
    if (!r) return Wt(e2, n);
    let i = { href: se(r.url || "") };
    r.title !== null && r.title !== void 0 && (i.title = r.title);
    let l = { type: "element", tagName: "a", properties: i, children: e2.all(n) };
    return e2.patch(n, l), e2.applyData(n, l);
  }
  function so(e2, n) {
    let t = { href: se(n.url) };
    n.title !== null && n.title !== void 0 && (t.title = n.title);
    let r = { type: "element", tagName: "a", properties: t, children: e2.all(n) };
    return e2.patch(n, r), e2.applyData(n, r);
  }
  function co(e2, n, t) {
    let r = e2.all(n), i = t ? Ps(t) : fo(n), l = {}, o = [];
    if (typeof n.checked == "boolean") {
      let c = r[0], f;
      c && c.type === "element" && c.tagName === "p" ? f = c : (f = { type: "element", tagName: "p", properties: {}, children: [] }, r.unshift(f)), f.children.length > 0 && f.children.unshift({ type: "text", value: " " }), f.children.unshift({ type: "element", tagName: "input", properties: { type: "checkbox", checked: n.checked, disabled: true }, children: [] }), l.className = ["task-list-item"];
    }
    let a = -1;
    for (; ++a < r.length; ) {
      let c = r[a];
      (i || a !== 0 || c.type !== "element" || c.tagName !== "p") && o.push({ type: "text", value: `
` }), c.type === "element" && c.tagName === "p" && !i ? o.push(...c.children) : o.push(c);
    }
    let u = r[r.length - 1];
    u && (i || u.type !== "element" || u.tagName !== "p") && o.push({ type: "text", value: `
` });
    let s32 = { type: "element", tagName: "li", properties: l, children: o };
    return e2.patch(n, s32), e2.applyData(n, s32);
  }
  function Ps(e2) {
    let n = false;
    if (e2.type === "list") {
      n = e2.spread || false;
      let t = e2.children, r = -1;
      for (; !n && ++r < t.length; ) n = fo(t[r]);
    }
    return n;
  }
  function fo(e2) {
    let n = e2.spread;
    return n == null ? e2.children.length > 1 : n;
  }
  function po(e2, n) {
    let t = {}, r = e2.all(n), i = -1;
    for (typeof n.start == "number" && n.start !== 1 && (t.start = n.start); ++i < r.length; ) {
      let o = r[i];
      if (o.type === "element" && o.tagName === "li" && o.properties && Array.isArray(o.properties.className) && o.properties.className.includes("task-list-item")) {
        t.className = ["contains-task-list"];
        break;
      }
    }
    let l = { type: "element", tagName: n.ordered ? "ol" : "ul", properties: t, children: e2.wrap(r, true) };
    return e2.patch(n, l), e2.applyData(n, l);
  }
  function mo(e2, n) {
    let t = { type: "element", tagName: "p", properties: {}, children: e2.all(n) };
    return e2.patch(n, t), e2.applyData(n, t);
  }
  function ho(e2, n) {
    let t = { type: "root", children: e2.wrap(e2.all(n)) };
    return e2.patch(n, t), e2.applyData(n, t);
  }
  function go(e2, n) {
    let t = { type: "element", tagName: "strong", properties: {}, children: e2.all(n) };
    return e2.patch(n, t), e2.applyData(n, t);
  }
  function xo(e2, n) {
    let t = e2.all(n), r = t.shift(), i = [];
    if (r) {
      let o = { type: "element", tagName: "thead", properties: {}, children: e2.wrap([r], true) };
      e2.patch(n.children[0], o), i.push(o);
    }
    if (t.length > 0) {
      let o = { type: "element", tagName: "tbody", properties: {}, children: e2.wrap(t, true) }, a = Ge(n.children[1]), u = Pt(n.children[n.children.length - 1]);
      a && u && (o.position = { start: a, end: u }), i.push(o);
    }
    let l = { type: "element", tagName: "table", properties: {}, children: e2.wrap(i, true) };
    return e2.patch(n, l), e2.applyData(n, l);
  }
  function ko(e2, n, t) {
    let r = t ? t.children : void 0, l = (r ? r.indexOf(n) : 1) === 0 ? "th" : "td", o = t && t.type === "table" ? t.align : void 0, a = o ? o.length : n.children.length, u = -1, s32 = [];
    for (; ++u < a; ) {
      let f = n.children[u], m = {}, p = o ? o[u] : void 0;
      p && (m.align = p);
      let g = { type: "element", tagName: l, properties: m, children: [] };
      f && (g.children = e2.all(f), e2.patch(f, g), g = e2.applyData(f, g)), s32.push(g);
    }
    let c = { type: "element", tagName: "tr", properties: {}, children: e2.wrap(s32, true) };
    return e2.patch(n, c), e2.applyData(n, c);
  }
  function yo(e2, n) {
    let t = { type: "element", tagName: "td", properties: {}, children: e2.all(n) };
    return e2.patch(n, t), e2.applyData(n, t);
  }
  function wo(e2) {
    let n = String(e2), t = /\r?\n|\r/g, r = t.exec(n), i = 0, l = [];
    for (; r; ) l.push(bo(n.slice(i, r.index), i > 0, true), r[0]), i = r.index + r[0].length, r = t.exec(n);
    return l.push(bo(n.slice(i), i > 0, false)), l.join("");
  }
  function bo(e2, n, t) {
    let r = 0, i = e2.length;
    if (n) {
      let l = e2.codePointAt(r);
      for (; l === 9 || l === 32; ) r++, l = e2.codePointAt(r);
    }
    if (t) {
      let l = e2.codePointAt(i - 1);
      for (; l === 9 || l === 32; ) i--, l = e2.codePointAt(i - 1);
    }
    return i > r ? e2.slice(r, i) : "";
  }
  function So(e2, n) {
    let t = { type: "text", value: wo(String(n.value)) };
    return e2.patch(n, t), e2.applyData(n, t);
  }
  function Co(e2, n) {
    let t = { type: "element", tagName: "hr", properties: {}, children: [] };
    return e2.patch(n, t), e2.applyData(n, t);
  }
  var Eo = { blockquote: $i, break: Ji, code: Ki, delete: eo, emphasis: to, footnoteReference: no, heading: ro, html: io, imageReference: oo, image: lo, inlineCode: ao, linkReference: uo, link: so, listItem: co, list: po, paragraph: mo, root: ho, strong: go, table: xo, tableCell: yo, tableRow: ko, text: So, thematicBreak: Co, toml: Xt, yaml: Xt, definition: Xt, footnoteDefinition: Xt };
  function Xt() {
  }
  var { defineProperty: Rs } = Object;
  var Po = typeof self == "object" ? self : globalThis;
  var Io = (e2, n) => {
    switch (e2) {
      case "Function":
      case "SharedWorker":
      case "Worker":
      case "eval":
      case "setInterval":
      case "setTimeout":
        throw new TypeError("unable to deserialize " + e2);
    }
    return new Po[e2](n);
  };
  var Ms = (e2, n) => {
    let t = (i, l) => (e2.set(l, i), i), r = (i) => {
      if (e2.has(i)) return e2.get(i);
      let [l, o] = n[i];
      switch (l) {
        case 0:
        case -1:
          return t(o, i);
        case 1: {
          let a = t([], i);
          for (let u of o) a.push(r(u));
          return a;
        }
        case 2: {
          let a = t({}, i);
          for (let [u, s32] of o) {
            let c = r(u), f = r(s32);
            c === "__proto__" ? Rs(a, c, { value: f, configurable: true, enumerable: true, writable: true }) : a[c] = f;
          }
          return a;
        }
        case 3:
          return t(new Date(o), i);
        case 4: {
          let { source: a, flags: u } = o;
          return t(new RegExp(a, u), i);
        }
        case 5: {
          let a = t(/* @__PURE__ */ new Map(), i);
          for (let [u, s32] of o) a.set(r(u), r(s32));
          return a;
        }
        case 6: {
          let a = t(/* @__PURE__ */ new Set(), i);
          for (let u of o) a.add(r(u));
          return a;
        }
        case 7: {
          let { name: a, message: u } = o;
          return t(typeof Po[a] == "function" ? Io(a, u) : new Error(u), i);
        }
        case 8:
          return t(BigInt(o), i);
        case "BigInt":
          return t(Object(BigInt(o)), i);
        case "ArrayBuffer":
          return t(new Uint8Array(o).buffer, o);
        case "DataView": {
          let { buffer: a } = new Uint8Array(o);
          return t(new DataView(a), o);
        }
        case "-0":
          return -0;
      }
      return t(Io(l, o), i);
    };
    return r;
  };
  var Wn = (e2) => Ms(/* @__PURE__ */ new Map(), e2)(0);
  var qe = "";
  var { toString: Os } = {};
  var { keys: _s, is: Ns } = Object;
  var kt = (e2) => {
    let n = typeof e2;
    if (n !== "object" || !e2) return [0, n];
    let t = Os.call(e2).slice(8, -1);
    switch (t) {
      case "Array":
        return [1, qe];
      case "Object":
        return [2, qe];
      case "Date":
        return [3, qe];
      case "RegExp":
        return [4, qe];
      case "Map":
        return [5, qe];
      case "Set":
        return [6, qe];
      case "DataView":
        return [1, t];
    }
    return t.includes("Array") ? [1, t] : e2 instanceof Error ? [7, e2.name || "Error"] : [2, t];
  };
  var Yt = ([e2, n]) => e2 === 0 && (n === "function" || n === "symbol");
  var Bs = (e2, n, t, r) => {
    let i = (o, a) => {
      let u = r.push(o) - 1;
      return t.set(a, u), u;
    }, l = (o) => {
      if (t.has(o)) return t.get(o);
      let [a, u] = kt(o);
      switch (a) {
        case 0: {
          let c = o;
          switch (u) {
            case "bigint":
              a = 8, c = o.toString();
              break;
            case "number":
              if (!o && Ns(o, -0)) return r.push(["-0"]) - 1;
              break;
            case "function":
            case "symbol":
              if (e2) throw new TypeError("unable to serialize " + u);
              c = null;
              break;
            case "undefined":
              return i([-1], o);
          }
          return i([a, c], o);
        }
        case 1: {
          if (u) {
            let m = o;
            return u === "DataView" ? m = new Uint8Array(o.buffer) : u === "ArrayBuffer" && (m = new Uint8Array(o)), i([u, [...m]], o);
          }
          let c = [], f = i([a, c], o);
          for (let m of o) c.push(l(m));
          return f;
        }
        case 2: {
          if (u) switch (u) {
            case "BigInt":
              return i([u, o.toString()], o);
            case "Boolean":
            case "Number":
            case "String":
              return i([u, o.valueOf()], o);
          }
          if (n && "toJSON" in o) return l(o.toJSON());
          let c = [], f = i([a, c], o);
          for (let m of _s(o)) (e2 || !Yt(kt(o[m]))) && c.push([l(m), l(o[m])]);
          return f;
        }
        case 3:
          return i([a, isNaN(o.getTime()) ? qe : o.toISOString()], o);
        case 4: {
          let { source: c, flags: f } = o;
          return i([a, { source: c, flags: f }], o);
        }
        case 5: {
          let c = [], f = i([a, c], o);
          for (let [m, p] of o) (e2 || !(Yt(kt(m)) || Yt(kt(p)))) && c.push([l(m), l(p)]);
          return f;
        }
        case 6: {
          let c = [], f = i([a, c], o);
          for (let m of o) (e2 || !Yt(kt(m))) && c.push(l(m));
          return f;
        }
      }
      let { message: s32 } = o;
      return i([a, { name: u, message: s32 }], o);
    };
    return l;
  };
  var Xn = (e2, { json: n, lossy: t } = {}) => {
    let r = [];
    return Bs(!(n || t), !!n, /* @__PURE__ */ new Map(), r)(e2), r;
  };
  var Je = typeof structuredClone == "function" ? (e2, n) => n && ("json" in n || "lossy" in n) ? Wn(Xn(e2, n)) : structuredClone(e2) : (e2, n) => Wn(Xn(e2, n));
  function Hs(e2, n) {
    let t = [{ type: "text", value: "\u21A9" }];
    return n > 1 && t.push({ type: "element", tagName: "sup", properties: {}, children: [{ type: "text", value: String(n) }] }), t;
  }
  function js(e2, n) {
    return "Back to reference " + (e2 + 1) + (n > 1 ? "-" + n : "");
  }
  function zo(e2) {
    let n = typeof e2.options.clobberPrefix == "string" ? e2.options.clobberPrefix : "user-content-", t = e2.options.footnoteBackContent || Hs, r = e2.options.footnoteBackLabel || js, i = e2.options.footnoteLabel || "Footnotes", l = e2.options.footnoteLabelTagName || "h2", o = e2.options.footnoteLabelProperties || { className: ["sr-only"] }, a = [], u = -1;
    for (; ++u < e2.footnoteOrder.length; ) {
      let s32 = e2.footnoteById.get(e2.footnoteOrder[u]);
      if (!s32) continue;
      let c = e2.all(s32), f = String(s32.identifier).toUpperCase(), m = se(f.toLowerCase()), p = 0, g = [], k = e2.footnoteCounts.get(f);
      for (; k !== void 0 && ++p <= k; ) {
        g.length > 0 && g.push({ type: "text", value: " " });
        let T = typeof t == "string" ? t : t(u, p);
        typeof T == "string" && (T = { type: "text", value: T }), g.push({ type: "element", tagName: "a", properties: { href: "#" + n + "fnref-" + m + (p > 1 ? "-" + p : ""), dataFootnoteBackref: "", ariaLabel: typeof r == "string" ? r : r(u, p), className: ["data-footnote-backref"] }, children: Array.isArray(T) ? T : [T] });
      }
      let C = c[c.length - 1];
      if (C && C.type === "element" && C.tagName === "p") {
        let T = C.children[C.children.length - 1];
        T && T.type === "text" ? T.value += " " : C.children.push({ type: "text", value: " " }), C.children.push(...g);
      } else c.push(...g);
      let x = { type: "element", tagName: "li", properties: { id: n + "fn-" + m }, children: e2.wrap(c, true) };
      e2.patch(s32, x), a.push(x);
    }
    if (a.length !== 0) return { type: "element", tagName: "section", properties: { dataFootnotes: true, className: ["footnotes"] }, children: [{ type: "element", tagName: l, properties: { ...Je(o), id: "footnote-label" }, children: [{ type: "text", value: i }] }, { type: "text", value: `
` }, { type: "element", tagName: "ol", properties: {}, children: e2.wrap(a, true) }, { type: "text", value: `
` }] };
  }
  var Pe = (function(e2) {
    if (e2 == null) return Ws;
    if (typeof e2 == "function") return Zt(e2);
    if (typeof e2 == "object") return Array.isArray(e2) ? Us(e2) : Vs(e2);
    if (typeof e2 == "string") return qs(e2);
    throw new Error("Expected function, string, or object as test");
  });
  function Us(e2) {
    let n = [], t = -1;
    for (; ++t < e2.length; ) n[t] = Pe(e2[t]);
    return Zt(r);
    function r(...i) {
      let l = -1;
      for (; ++l < n.length; ) if (n[l].apply(this, i)) return true;
      return false;
    }
  }
  function Vs(e2) {
    let n = e2;
    return Zt(t);
    function t(r) {
      let i = r, l;
      for (l in e2) if (i[l] !== n[l]) return false;
      return true;
    }
  }
  function qs(e2) {
    return Zt(n);
    function n(t) {
      return t && t.type === e2;
    }
  }
  function Zt(e2) {
    return n;
    function n(t, r, i) {
      return !!(Xs(t) && e2.call(this, t, typeof r == "number" ? r : void 0, i || void 0));
    }
  }
  function Ws() {
    return true;
  }
  function Xs(e2) {
    return e2 !== null && typeof e2 == "object" && "type" in e2;
  }
  var Fo = [];
  var Gt = true;
  var We = false;
  var $t = "skip";
  function yt(e2, n, t, r) {
    let i;
    typeof n == "function" && typeof t != "function" ? (r = t, t = n) : i = n;
    let l = Pe(i), o = r ? -1 : 1;
    a(e2, void 0, [])();
    function a(u, s32, c) {
      let f = u && typeof u == "object" ? u : {};
      if (typeof f.type == "string") {
        let p = typeof f.tagName == "string" ? f.tagName : typeof f.name == "string" ? f.name : void 0;
        Object.defineProperty(m, "name", { value: "node (" + (u.type + (p ? "<" + p + ">" : "")) + ")" });
      }
      return m;
      function m() {
        let p = Fo, g, k, C;
        if ((!n || l(u, s32, c[c.length - 1] || void 0)) && (p = Qs(t(u, c)), p[0] === We)) return p;
        if ("children" in u && u.children) {
          let x = u;
          if (x.children && p[0] !== $t) for (k = (r ? x.children.length : -1) + o, C = c.concat(x); k > -1 && k < x.children.length; ) {
            let T = x.children[k];
            if (g = a(T, k, C)(), g[0] === We) return g;
            k = typeof g[1] == "number" ? g[1] : k + o;
          }
        }
        return p;
      }
    }
  }
  function Qs(e2) {
    return Array.isArray(e2) ? e2 : typeof e2 == "number" ? [Gt, e2] : e2 == null ? Fo : [e2];
  }
  function Ee(e2, n, t, r) {
    let i, l, o;
    typeof n == "function" && typeof t != "function" ? (l = void 0, o = n, i = t) : (l = n, o = t, i = r), yt(e2, l, a, i);
    function a(u, s32) {
      let c = s32[s32.length - 1], f = c ? c.children.indexOf(u) : void 0;
      return o(u, f, c);
    }
  }
  var Qn = {}.hasOwnProperty;
  var Ys = {};
  function Ro(e2, n) {
    let t = n || Ys, r = /* @__PURE__ */ new Map(), i = /* @__PURE__ */ new Map(), l = /* @__PURE__ */ new Map(), o = { ...Eo, ...t.handlers }, a = { all: s32, applyData: Gs, definitionById: r, footnoteById: i, footnoteCounts: l, footnoteOrder: [], handlers: o, one: u, options: t, patch: Zs, wrap: Js };
    return Ee(e2, function(c) {
      if (c.type === "definition" || c.type === "footnoteDefinition") {
        let f = c.type === "definition" ? r : i, m = String(c.identifier).toUpperCase();
        f.has(m) || f.set(m, c);
      }
    }), a;
    function u(c, f) {
      let m = c.type, p = a.handlers[m];
      if (Qn.call(a.handlers, m) && p) return p(a, c, f);
      if (a.options.passThrough && a.options.passThrough.includes(m)) {
        if ("children" in c) {
          let { children: k, ...C } = c, x = Je(C);
          return x.children = a.all(c), x;
        }
        return Je(c);
      }
      return (a.options.unknownHandler || $s)(a, c, f);
    }
    function s32(c) {
      let f = [];
      if ("children" in c) {
        let m = c.children, p = -1;
        for (; ++p < m.length; ) {
          let g = a.one(m[p], c);
          if (g) {
            if (p && m[p - 1].type === "break" && (!Array.isArray(g) && g.type === "text" && (g.value = Do(g.value)), !Array.isArray(g) && g.type === "element")) {
              let k = g.children[0];
              k && k.type === "text" && (k.value = Do(k.value));
            }
            Array.isArray(g) ? f.push(...g) : f.push(g);
          }
        }
      }
      return f;
    }
  }
  function Zs(e2, n) {
    e2.position && (n.position = wn(e2));
  }
  function Gs(e2, n) {
    let t = n;
    if (e2 && e2.data) {
      let r = e2.data.hName, i = e2.data.hChildren, l = e2.data.hProperties;
      if (typeof r == "string") if (t.type === "element") t.tagName = r;
      else {
        let o = "children" in t ? t.children : [t];
        t = { type: "element", tagName: r, properties: {}, children: o };
      }
      t.type === "element" && l && Object.assign(t.properties, Je(l)), "children" in t && t.children && i !== null && i !== void 0 && (t.children = i);
    }
    return t;
  }
  function $s(e2, n) {
    let t = n.data || {}, r = "value" in n && !(Qn.call(t, "hProperties") || Qn.call(t, "hChildren")) ? { type: "text", value: n.value } : { type: "element", tagName: "div", properties: {}, children: e2.all(n) };
    return e2.patch(n, r), e2.applyData(n, r);
  }
  function Js(e2, n) {
    let t = [], r = -1;
    for (n && t.push({ type: "text", value: `
` }); ++r < e2.length; ) r && t.push({ type: "text", value: `
` }), t.push(e2[r]);
    return n && e2.length > 0 && t.push({ type: "text", value: `
` }), t;
  }
  function Do(e2) {
    let n = 0, t = e2.charCodeAt(n);
    for (; t === 9 || t === 32; ) n++, t = e2.charCodeAt(n);
    return e2.slice(n);
  }
  function Jt(e2, n) {
    let t = Ro(e2, n), r = t.one(e2, void 0), i = zo(t), l = Array.isArray(r) ? { type: "root", children: r } : r || { type: "root", children: [] };
    return i && ("children" in l, l.children.push({ type: "text", value: `
` }, i)), l;
  }
  function Kt(e2, n) {
    return e2 && "run" in e2 ? async function(t, r) {
      let i = Jt(t, { file: r, ...n });
      await e2.run(i, r);
    } : function(t, r) {
      return Jt(t, { file: r, ...e2 || n });
    };
  }
  function Yn(e2) {
    if (e2) throw e2;
  }
  var nn = Yr(Vo(), 1);
  function bt(e2) {
    if (typeof e2 != "object" || e2 === null) return false;
    let n = Object.getPrototypeOf(e2);
    return (n === null || n === Object.prototype || Object.getPrototypeOf(n) === null) && !(Symbol.toStringTag in e2) && !(Symbol.iterator in e2);
  }
  function Zn() {
    let e2 = [], n = { run: t, use: r };
    return n;
    function t(...i) {
      let l = -1, o = i.pop();
      if (typeof o != "function") throw new TypeError("Expected function as last argument, not " + o);
      a(null, ...i);
      function a(u, ...s32) {
        let c = e2[++l], f = -1;
        if (u) {
          o(u);
          return;
        }
        for (; ++f < i.length; ) (s32[f] === null || s32[f] === void 0) && (s32[f] = i[f]);
        i = s32, c ? qo(c, a)(...s32) : o(null, ...s32);
      }
    }
    function r(i) {
      if (typeof i != "function") throw new TypeError("Expected `middelware` to be a function, not " + i);
      return e2.push(i), n;
    }
  }
  function qo(e2, n) {
    let t;
    return r;
    function r(...o) {
      let a = e2.length > o.length, u;
      a && o.push(i);
      try {
        u = e2.apply(this, o);
      } catch (s32) {
        let c = s32;
        if (a && t) throw c;
        return i(c);
      }
      a || (u && u.then && typeof u.then == "function" ? u.then(l, i) : u instanceof Error ? i(u) : l(u));
    }
    function i(o, ...a) {
      t || (t = true, n(o, ...a));
    }
    function l(o) {
      i(null, o);
    }
  }
  var pe = { basename: Ks, dirname: ec, extname: tc, join: nc, sep: "/" };
  function Ks(e2, n) {
    if (n !== void 0 && typeof n != "string") throw new TypeError('"ext" argument must be a string');
    wt(e2);
    let t = 0, r = -1, i = e2.length, l;
    if (n === void 0 || n.length === 0 || n.length > e2.length) {
      for (; i--; ) if (e2.codePointAt(i) === 47) {
        if (l) {
          t = i + 1;
          break;
        }
      } else r < 0 && (l = true, r = i + 1);
      return r < 0 ? "" : e2.slice(t, r);
    }
    if (n === e2) return "";
    let o = -1, a = n.length - 1;
    for (; i--; ) if (e2.codePointAt(i) === 47) {
      if (l) {
        t = i + 1;
        break;
      }
    } else o < 0 && (l = true, o = i + 1), a > -1 && (e2.codePointAt(i) === n.codePointAt(a--) ? a < 0 && (r = i) : (a = -1, r = o));
    return t === r ? r = o : r < 0 && (r = e2.length), e2.slice(t, r);
  }
  function ec(e2) {
    if (wt(e2), e2.length === 0) return ".";
    let n = -1, t = e2.length, r;
    for (; --t; ) if (e2.codePointAt(t) === 47) {
      if (r) {
        n = t;
        break;
      }
    } else r || (r = true);
    return n < 0 ? e2.codePointAt(0) === 47 ? "/" : "." : n === 1 && e2.codePointAt(0) === 47 ? "//" : e2.slice(0, n);
  }
  function tc(e2) {
    wt(e2);
    let n = e2.length, t = -1, r = 0, i = -1, l = 0, o;
    for (; n--; ) {
      let a = e2.codePointAt(n);
      if (a === 47) {
        if (o) {
          r = n + 1;
          break;
        }
        continue;
      }
      t < 0 && (o = true, t = n + 1), a === 46 ? i < 0 ? i = n : l !== 1 && (l = 1) : i > -1 && (l = -1);
    }
    return i < 0 || t < 0 || l === 0 || l === 1 && i === t - 1 && i === r + 1 ? "" : e2.slice(i, t);
  }
  function nc(...e2) {
    let n = -1, t;
    for (; ++n < e2.length; ) wt(e2[n]), e2[n] && (t = t === void 0 ? e2[n] : t + "/" + e2[n]);
    return t === void 0 ? "." : rc(t);
  }
  function rc(e2) {
    wt(e2);
    let n = e2.codePointAt(0) === 47, t = ic(e2, !n);
    return t.length === 0 && !n && (t = "."), t.length > 0 && e2.codePointAt(e2.length - 1) === 47 && (t += "/"), n ? "/" + t : t;
  }
  function ic(e2, n) {
    let t = "", r = 0, i = -1, l = 0, o = -1, a, u;
    for (; ++o <= e2.length; ) {
      if (o < e2.length) a = e2.codePointAt(o);
      else {
        if (a === 47) break;
        a = 47;
      }
      if (a === 47) {
        if (!(i === o - 1 || l === 1)) if (i !== o - 1 && l === 2) {
          if (t.length < 2 || r !== 2 || t.codePointAt(t.length - 1) !== 46 || t.codePointAt(t.length - 2) !== 46) {
            if (t.length > 2) {
              if (u = t.lastIndexOf("/"), u !== t.length - 1) {
                u < 0 ? (t = "", r = 0) : (t = t.slice(0, u), r = t.length - 1 - t.lastIndexOf("/")), i = o, l = 0;
                continue;
              }
            } else if (t.length > 0) {
              t = "", r = 0, i = o, l = 0;
              continue;
            }
          }
          n && (t = t.length > 0 ? t + "/.." : "..", r = 2);
        } else t.length > 0 ? t += "/" + e2.slice(i + 1, o) : t = e2.slice(i + 1, o), r = o - i - 1;
        i = o, l = 0;
      } else a === 46 && l > -1 ? l++ : l = -1;
    }
    return t;
  }
  function wt(e2) {
    if (typeof e2 != "string") throw new TypeError("Path must be a string. Received " + JSON.stringify(e2));
  }
  var Wo = { cwd: oc };
  function oc() {
    return "/";
  }
  function Ke(e2) {
    return !!(e2 !== null && typeof e2 == "object" && "href" in e2 && e2.href && "protocol" in e2 && e2.protocol && e2.auth === void 0);
  }
  function Xo(e2) {
    if (typeof e2 == "string") e2 = new URL(e2);
    else if (!Ke(e2)) {
      let n = new TypeError('The "path" argument must be of type string or an instance of URL. Received `' + e2 + "`");
      throw n.code = "ERR_INVALID_ARG_TYPE", n;
    }
    if (e2.protocol !== "file:") {
      let n = new TypeError("The URL must be of scheme file");
      throw n.code = "ERR_INVALID_URL_SCHEME", n;
    }
    return lc(e2);
  }
  function lc(e2) {
    if (e2.hostname !== "") {
      let r = new TypeError('File URL host must be "localhost" or empty on darwin');
      throw r.code = "ERR_INVALID_FILE_URL_HOST", r;
    }
    let n = e2.pathname, t = -1;
    for (; ++t < n.length; ) if (n.codePointAt(t) === 37 && n.codePointAt(t + 1) === 50) {
      let r = n.codePointAt(t + 2);
      if (r === 70 || r === 102) {
        let i = new TypeError("File URL path must not include encoded / characters");
        throw i.code = "ERR_INVALID_FILE_URL_PATH", i;
      }
    }
    return decodeURIComponent(n);
  }
  var Gn = ["history", "path", "basename", "stem", "extname", "dirname"];
  var Xe = class {
    constructor(n) {
      let t;
      n ? Ke(n) ? t = { path: n } : typeof n == "string" || ac(n) ? t = { value: n } : t = n : t = {}, this.cwd = "cwd" in t ? "" : Wo.cwd(), this.data = {}, this.history = [], this.messages = [], this.value, this.map, this.result, this.stored;
      let r = -1;
      for (; ++r < Gn.length; ) {
        let l = Gn[r];
        l in t && t[l] !== void 0 && t[l] !== null && (this[l] = l === "history" ? [...t[l]] : t[l]);
      }
      let i;
      for (i in t) Gn.includes(i) || (this[i] = t[i]);
    }
    get basename() {
      return typeof this.path == "string" ? pe.basename(this.path) : void 0;
    }
    set basename(n) {
      Jn(n, "basename"), $n(n, "basename"), this.path = pe.join(this.dirname || "", n);
    }
    get dirname() {
      return typeof this.path == "string" ? pe.dirname(this.path) : void 0;
    }
    set dirname(n) {
      Qo(this.basename, "dirname"), this.path = pe.join(n || "", this.basename);
    }
    get extname() {
      return typeof this.path == "string" ? pe.extname(this.path) : void 0;
    }
    set extname(n) {
      if ($n(n, "extname"), Qo(this.dirname, "extname"), n) {
        if (n.codePointAt(0) !== 46) throw new Error("`extname` must start with `.`");
        if (n.includes(".", 1)) throw new Error("`extname` cannot contain multiple dots");
      }
      this.path = pe.join(this.dirname, this.stem + (n || ""));
    }
    get path() {
      return this.history[this.history.length - 1];
    }
    set path(n) {
      Ke(n) && (n = Xo(n)), Jn(n, "path"), this.path !== n && this.history.push(n);
    }
    get stem() {
      return typeof this.path == "string" ? pe.basename(this.path, this.extname) : void 0;
    }
    set stem(n) {
      Jn(n, "stem"), $n(n, "stem"), this.path = pe.join(this.dirname || "", n + (this.extname || ""));
    }
    fail(n, t, r) {
      let i = this.message(n, t, r);
      throw i.fatal = true, i;
    }
    info(n, t, r) {
      let i = this.message(n, t, r);
      return i.fatal = void 0, i;
    }
    message(n, t, r) {
      let i = new Y(n, t, r);
      return this.path && (i.name = this.path + ":" + i.name, i.file = this.path), i.fatal = false, this.messages.push(i), i;
    }
    toString(n) {
      return this.value === void 0 ? "" : typeof this.value == "string" ? this.value : new TextDecoder(n || void 0).decode(this.value);
    }
  };
  function $n(e2, n) {
    if (e2 && e2.includes(pe.sep)) throw new Error("`" + n + "` cannot be a path: did not expect `" + pe.sep + "`");
  }
  function Jn(e2, n) {
    if (!e2) throw new Error("`" + n + "` cannot be empty");
  }
  function Qo(e2, n) {
    if (!e2) throw new Error("Setting `" + n + "` requires `path` to be set too");
  }
  function ac(e2) {
    return !!(e2 && typeof e2 == "object" && "byteLength" in e2 && "byteOffset" in e2);
  }
  var Yo = (function(e2) {
    let r = this.constructor.prototype, i = r[e2], l = function() {
      return i.apply(l, arguments);
    };
    return Object.setPrototypeOf(l, r), l;
  });
  var uc = {}.hasOwnProperty;
  var nr = class e extends Yo {
    constructor() {
      super("copy"), this.Compiler = void 0, this.Parser = void 0, this.attachers = [], this.compiler = void 0, this.freezeIndex = -1, this.frozen = void 0, this.namespace = {}, this.parser = void 0, this.transformers = Zn();
    }
    copy() {
      let n = new e(), t = -1;
      for (; ++t < this.attachers.length; ) {
        let r = this.attachers[t];
        n.use(...r);
      }
      return n.data((0, nn.default)(true, {}, this.namespace)), n;
    }
    data(n, t) {
      return typeof n == "string" ? arguments.length === 2 ? (tr("data", this.frozen), this.namespace[n] = t, this) : uc.call(this.namespace, n) && this.namespace[n] || void 0 : n ? (tr("data", this.frozen), this.namespace = n, this) : this.namespace;
    }
    freeze() {
      if (this.frozen) return this;
      let n = this;
      for (; ++this.freezeIndex < this.attachers.length; ) {
        let [t, ...r] = this.attachers[this.freezeIndex];
        if (r[0] === false) continue;
        r[0] === true && (r[0] = void 0);
        let i = t.call(n, ...r);
        typeof i == "function" && this.transformers.use(i);
      }
      return this.frozen = true, this.freezeIndex = Number.POSITIVE_INFINITY, this;
    }
    parse(n) {
      this.freeze();
      let t = tn(n), r = this.parser || this.Parser;
      return Kn("parse", r), r(String(t), t);
    }
    process(n, t) {
      let r = this;
      return this.freeze(), Kn("process", this.parser || this.Parser), er("process", this.compiler || this.Compiler), t ? i(void 0, t) : new Promise(i);
      function i(l, o) {
        let a = tn(n), u = r.parse(a);
        r.run(u, a, function(c, f, m) {
          if (c || !f || !m) return s32(c);
          let p = f, g = r.stringify(p, m);
          cc(g) ? m.value = g : m.result = g, s32(c, m);
        });
        function s32(c, f) {
          c || !f ? o(c) : l ? l(f) : t(void 0, f);
        }
      }
    }
    processSync(n) {
      let t = false, r;
      return this.freeze(), Kn("processSync", this.parser || this.Parser), er("processSync", this.compiler || this.Compiler), this.process(n, i), Go("processSync", "process", t), r;
      function i(l, o) {
        t = true, Yn(l), r = o;
      }
    }
    run(n, t, r) {
      Zo(n), this.freeze();
      let i = this.transformers;
      return !r && typeof t == "function" && (r = t, t = void 0), r ? l(void 0, r) : new Promise(l);
      function l(o, a) {
        let u = tn(t);
        i.run(n, u, s32);
        function s32(c, f, m) {
          let p = f || n;
          c ? a(c) : o ? o(p) : r(void 0, p, m);
        }
      }
    }
    runSync(n, t) {
      let r = false, i;
      return this.run(n, t, l), Go("runSync", "run", r), i;
      function l(o, a) {
        Yn(o), i = a, r = true;
      }
    }
    stringify(n, t) {
      this.freeze();
      let r = tn(t), i = this.compiler || this.Compiler;
      return er("stringify", i), Zo(n), i(n, r);
    }
    use(n, ...t) {
      let r = this.attachers, i = this.namespace;
      if (tr("use", this.frozen), n != null) if (typeof n == "function") u(n, t);
      else if (typeof n == "object") Array.isArray(n) ? a(n) : o(n);
      else throw new TypeError("Expected usable value, not `" + n + "`");
      return this;
      function l(s32) {
        if (typeof s32 == "function") u(s32, []);
        else if (typeof s32 == "object") if (Array.isArray(s32)) {
          let [c, ...f] = s32;
          u(c, f);
        } else o(s32);
        else throw new TypeError("Expected usable value, not `" + s32 + "`");
      }
      function o(s32) {
        if (!("plugins" in s32) && !("settings" in s32)) throw new Error("Expected usable value but received an empty preset, which is probably a mistake: presets typically come with `plugins` and sometimes with `settings`, but this has neither");
        a(s32.plugins), s32.settings && (i.settings = (0, nn.default)(true, i.settings, s32.settings));
      }
      function a(s32) {
        let c = -1;
        if (s32 != null) if (Array.isArray(s32)) for (; ++c < s32.length; ) {
          let f = s32[c];
          l(f);
        }
        else throw new TypeError("Expected a list of plugins, not `" + s32 + "`");
      }
      function u(s32, c) {
        let f = -1, m = -1;
        for (; ++f < r.length; ) if (r[f][0] === s32) {
          m = f;
          break;
        }
        if (m === -1) r.push([s32, ...c]);
        else if (c.length > 0) {
          let [p, ...g] = c, k = r[m][1];
          bt(k) && bt(p) && (p = (0, nn.default)(true, k, p)), r[m] = [s32, p, ...g];
        }
      }
    }
  };
  var rr = new nr().freeze();
  function Kn(e2, n) {
    if (typeof n != "function") throw new TypeError("Cannot `" + e2 + "` without `parser`");
  }
  function er(e2, n) {
    if (typeof n != "function") throw new TypeError("Cannot `" + e2 + "` without `compiler`");
  }
  function tr(e2, n) {
    if (n) throw new Error("Cannot call `" + e2 + "` on a frozen processor.\nCreate a new processor first, by calling it: use `processor()` instead of `processor`.");
  }
  function Zo(e2) {
    if (!bt(e2) || typeof e2.type != "string") throw new TypeError("Expected node, got `" + e2 + "`");
  }
  function Go(e2, n, t) {
    if (!t) throw new Error("`" + e2 + "` finished async. Use `" + n + "` instead");
  }
  function tn(e2) {
    return sc(e2) ? e2 : new Xe(e2);
  }
  function sc(e2) {
    return !!(e2 && typeof e2 == "object" && "message" in e2 && "messages" in e2);
  }
  function cc(e2) {
    return typeof e2 == "string" || fc(e2);
  }
  function fc(e2) {
    return !!(e2 && typeof e2 == "object" && "byteLength" in e2 && "byteOffset" in e2);
  }
  var pc = "https://github.com/remarkjs/react-markdown/blob/main/changelog.md";
  var $o = [];
  var Jo = { allowDangerousHtml: true };
  var mc = /^(https?|ircs?|mailto|xmpp)$/i;
  var hc = [{ from: "astPlugins", id: "remove-buggy-html-in-markdown-parser" }, { from: "allowDangerousHtml", id: "remove-buggy-html-in-markdown-parser" }, { from: "allowNode", id: "replace-allownode-allowedtypes-and-disallowedtypes", to: "allowElement" }, { from: "allowedTypes", id: "replace-allownode-allowedtypes-and-disallowedtypes", to: "allowedElements" }, { from: "className", id: "remove-classname" }, { from: "disallowedTypes", id: "replace-allownode-allowedtypes-and-disallowedtypes", to: "disallowedElements" }, { from: "escapeHtml", id: "remove-buggy-html-in-markdown-parser" }, { from: "includeElementIndex", id: "#remove-includeelementindex" }, { from: "includeNodeIndex", id: "change-includenodeindex-to-includeelementindex" }, { from: "linkTarget", id: "remove-linktarget" }, { from: "plugins", id: "change-plugins-to-remarkplugins", to: "remarkPlugins" }, { from: "rawSourcePos", id: "#remove-rawsourcepos" }, { from: "renderers", id: "change-renderers-to-components", to: "components" }, { from: "source", id: "change-source-to-children", to: "children" }, { from: "sourcePos", id: "#remove-sourcepos" }, { from: "transformImageUri", id: "#add-urltransform", to: "urlTransform" }, { from: "transformLinkUri", id: "#add-urltransform", to: "urlTransform" }];
  function Ko(e2) {
    let n = dc(e2), t = gc(e2);
    return xc(n.runSync(n.parse(t), t), e2);
  }
  function dc(e2) {
    let n = e2.rehypePlugins || $o, t = e2.remarkPlugins || $o, r = e2.remarkRehypeOptions ? { ...e2.remarkRehypeOptions, ...Jo } : Jo;
    return rr().use(qt).use(t).use(Kt, r).use(n);
  }
  function gc(e2) {
    let n = e2.children || "", t = new Xe();
    return typeof n == "string" ? t.value = n : ("" + n, void 0), t;
  }
  function xc(e2, n) {
    let t = n.allowedElements, r = n.allowElement, i = n.components, l = n.disallowedElements, o = n.skipHtml, a = n.unwrapDisallowed, u = n.urlTransform || el;
    for (let c of hc) Object.hasOwn(n, c.from) && ("" + c.from + (c.to ? "use `" + c.to + "` instead" : "remove it") + pc + c.id, void 0);
    return t && l && void 0, Ee(e2, s32), En(e2, { Fragment: Si, components: i, ignoreInvalidStyle: true, jsx: Ei, jsxs: Ii, passKeys: true, passNode: true });
    function s32(c, f, m) {
      if (c.type === "raw" && m && typeof f == "number") return o ? m.children.splice(f, 1) : m.children[f] = { type: "text", value: c.value }, f;
      if (c.type === "element") {
        let p;
        for (p in pt) if (Object.hasOwn(pt, p) && Object.hasOwn(c.properties, p)) {
          let g = c.properties[p], k = pt[p];
          (k === null || k.includes(c.tagName)) && (c.properties[p] = u(String(g || ""), p, c));
        }
      }
      if (c.type === "element") {
        let p = t ? !t.includes(c.tagName) : l ? l.includes(c.tagName) : false;
        if (!p && r && typeof f == "number" && (p = !r(c, f, m)), p && m && typeof f == "number") return a && c.children ? m.children.splice(f, 1, ...c.children) : m.children.splice(f, 1), f;
      }
    }
  }
  function el(e2) {
    let n = e2.indexOf(":"), t = e2.indexOf("?"), r = e2.indexOf("#"), i = e2.indexOf("/");
    return n === -1 || i !== -1 && n > i || t !== -1 && n > t || r !== -1 && n > r || mc.test(e2.slice(0, n)) ? e2 : "";
  }
  function ir(e2, n) {
    let t = String(e2);
    if (typeof n != "string") throw new TypeError("Expected character");
    let r = 0, i = t.indexOf(n);
    for (; i !== -1; ) r++, i = t.indexOf(n, i + n.length);
    return r;
  }
  function or(e2) {
    if (typeof e2 != "string") throw new TypeError("Expected a string");
    return e2.replace(/[|\\{}()[\]^$+*?.]/g, "\\$&").replace(/-/g, "\\x2d");
  }
  function lr(e2, n, t) {
    let i = Pe((t || {}).ignore || []), l = kc(n), o = -1;
    for (; ++o < l.length; ) yt(e2, "text", a);
    function a(s32, c) {
      let f = -1, m;
      for (; ++f < c.length; ) {
        let p = c[f], g = m ? m.children : void 0;
        if (i(p, g ? g.indexOf(p) : void 0, m)) return;
        m = p;
      }
      if (m) return u(s32, c);
    }
    function u(s32, c) {
      let f = c[c.length - 1], m = l[o][0], p = l[o][1], g = 0, C = f.children.indexOf(s32), x = false, T = [];
      m.lastIndex = 0;
      let E = m.exec(s32.value);
      for (; E; ) {
        let M = E.index, O = { index: E.index, input: E.input, stack: [...c, s32] }, w = p(...E, O);
        if (typeof w == "string" && (w = w.length > 0 ? { type: "text", value: w } : void 0), w === false ? m.lastIndex = M + 1 : (g !== M && T.push({ type: "text", value: s32.value.slice(g, M) }), Array.isArray(w) ? T.push(...w) : w && T.push(w), g = M + E[0].length, x = true), !m.global) break;
        E = m.exec(s32.value);
      }
      return x ? (g < s32.value.length && T.push({ type: "text", value: s32.value.slice(g) }), f.children.splice(C, 1, ...T)) : T = [s32], C + T.length;
    }
  }
  function kc(e2) {
    let n = [];
    if (!Array.isArray(e2)) throw new TypeError("Expected find and replace tuple or list of tuples");
    let t = !e2[0] || Array.isArray(e2[0]) ? e2 : [e2], r = -1;
    for (; ++r < t.length; ) {
      let i = t[r];
      n.push([yc(i[0]), bc(i[1])]);
    }
    return n;
  }
  function yc(e2) {
    return typeof e2 == "string" ? new RegExp(or(e2), "g") : e2;
  }
  function bc(e2) {
    return typeof e2 == "function" ? e2 : function() {
      return e2;
    };
  }
  var ar = "phrasing";
  var ur = ["autolink", "link", "image", "label"];
  function cr() {
    return { transforms: [Tc], enter: { literalAutolink: wc, literalAutolinkEmail: sr, literalAutolinkHttp: sr, literalAutolinkWww: sr }, exit: { literalAutolink: Ic, literalAutolinkEmail: Ec, literalAutolinkHttp: Sc, literalAutolinkWww: Cc } };
  }
  function fr() {
    return { unsafe: [{ character: "@", before: "[+\\-.\\w]", after: "[\\-.\\w]", inConstruct: ar, notInConstruct: ur }, { character: ".", before: "[Ww]", after: "[\\-.\\w]", inConstruct: ar, notInConstruct: ur }, { character: ":", before: "[ps]", after: "\\/", inConstruct: ar, notInConstruct: ur }] };
  }
  function wc(e2) {
    this.enter({ type: "link", title: null, url: "", children: [] }, e2);
  }
  function sr(e2) {
    this.config.enter.autolinkProtocol.call(this, e2);
  }
  function Sc(e2) {
    this.config.exit.autolinkProtocol.call(this, e2);
  }
  function Cc(e2) {
    this.config.exit.data.call(this, e2);
    let n = this.stack[this.stack.length - 1];
    n.type, n.url = "http://" + this.sliceSerialize(e2);
  }
  function Ec(e2) {
    this.config.exit.autolinkEmail.call(this, e2);
  }
  function Ic(e2) {
    this.exit(e2);
  }
  function Tc(e2) {
    lr(e2, [[/(https?:\/\/|www(?=\.))([-.\w]+)([^ \t\r\n]*)/gi, Ac], [/(?<=^|\s|\p{P}|\p{S})([-.\w+]+)@([-\w]+(?:\.[-\w]+)+)/gu, Lc]], { ignore: ["link", "linkReference"] });
  }
  function Ac(e2, n, t, r, i) {
    let l = "";
    if (!tl(i) || (/^w/i.test(n) && (t = n + t, n = "", l = "http://"), !vc(t))) return false;
    let o = Pc(t + r);
    if (!o[0]) return false;
    let a = { type: "link", title: null, url: l + n + o[0], children: [{ type: "text", value: n + o[0] }] };
    return o[1] ? [a, { type: "text", value: o[1] }] : a;
  }
  function Lc(e2, n, t, r) {
    return !tl(r, true) || /[-\d_]$/.test(t) ? false : { type: "link", title: null, url: "mailto:" + n + "@" + t, children: [{ type: "text", value: n + "@" + t }] };
  }
  function vc(e2) {
    let n = e2.split(".");
    return !(n.length < 2 || n[n.length - 1] && (/_/.test(n[n.length - 1]) || !/[a-zA-Z\d]/.test(n[n.length - 1])) || n[n.length - 2] && (/_/.test(n[n.length - 2]) || !/[a-zA-Z\d]/.test(n[n.length - 2])));
  }
  function Pc(e2) {
    let n = /[!"&'),.:;<>?\]}]+$/.exec(e2);
    if (!n) return [e2, void 0];
    e2 = e2.slice(0, n.index);
    let t = n[0], r = t.indexOf(")"), i = ir(e2, "("), l = ir(e2, ")");
    for (; r !== -1 && i > l; ) e2 += t.slice(0, r + 1), t = t.slice(r + 1), r = t.indexOf(")"), l++;
    return [e2, t];
  }
  function tl(e2, n) {
    let t = e2.input.charCodeAt(e2.index - 1);
    return (e2.index === 0 || he(t) || He(t)) && (!n || t !== 47);
  }
  nl.peek = Bc;
  function zc() {
    this.buffer();
  }
  function Fc(e2) {
    this.enter({ type: "footnoteReference", identifier: "", label: "" }, e2);
  }
  function Dc() {
    this.buffer();
  }
  function Rc(e2) {
    this.enter({ type: "footnoteDefinition", identifier: "", label: "", children: [] }, e2);
  }
  function Mc(e2) {
    let n = this.resume(), t = this.stack[this.stack.length - 1];
    t.type, t.identifier = te(this.sliceSerialize(e2)).toLowerCase(), t.label = n;
  }
  function Oc(e2) {
    this.exit(e2);
  }
  function _c(e2) {
    let n = this.resume(), t = this.stack[this.stack.length - 1];
    t.type, t.identifier = te(this.sliceSerialize(e2)).toLowerCase(), t.label = n;
  }
  function Nc(e2) {
    this.exit(e2);
  }
  function Bc() {
    return "[";
  }
  function nl(e2, n, t, r) {
    let i = t.createTracker(r), l = i.move("[^"), o = t.enter("footnoteReference"), a = t.enter("reference");
    return l += i.move(t.safe(t.associationId(e2), { after: "]", before: l })), a(), o(), l += i.move("]"), l;
  }
  function pr() {
    return { enter: { gfmFootnoteCallString: zc, gfmFootnoteCall: Fc, gfmFootnoteDefinitionLabelString: Dc, gfmFootnoteDefinition: Rc }, exit: { gfmFootnoteCallString: Mc, gfmFootnoteCall: Oc, gfmFootnoteDefinitionLabelString: _c, gfmFootnoteDefinition: Nc } };
  }
  function mr(e2) {
    let n = false;
    return e2 && e2.firstLineBlank && (n = true), { handlers: { footnoteDefinition: t, footnoteReference: nl }, unsafe: [{ character: "[", inConstruct: ["label", "phrasing", "reference"] }] };
    function t(r, i, l, o) {
      let a = l.createTracker(o), u = a.move("[^"), s32 = l.enter("footnoteDefinition"), c = l.enter("label");
      return u += a.move(l.safe(l.associationId(r), { before: u, after: "]" })), c(), u += a.move("]:"), r.children && r.children.length > 0 && (a.shift(4), u += a.move((n ? `
` : " ") + l.indentLines(l.containerFlow(r, a.current()), n ? rl : Hc))), s32(), u;
    }
  }
  function Hc(e2, n, t) {
    return n === 0 ? e2 : rl(e2, n, t);
  }
  function rl(e2, n, t) {
    return (t ? "" : "    ") + e2;
  }
  var jc = ["autolink", "destinationLiteral", "destinationRaw", "reference", "titleQuote", "titleApostrophe"];
  il.peek = qc;
  function hr() {
    return { canContainEols: ["delete"], enter: { strikethrough: Uc }, exit: { strikethrough: Vc } };
  }
  function dr() {
    return { unsafe: [{ character: "~", inConstruct: "phrasing", notInConstruct: jc }], handlers: { delete: il } };
  }
  function Uc(e2) {
    this.enter({ type: "delete", children: [] }, e2);
  }
  function Vc(e2) {
    this.exit(e2);
  }
  function il(e2, n, t, r) {
    let i = t.createTracker(r), l = t.enter("strikethrough"), o = i.move("~~");
    return o += t.containerPhrasing(e2, { ...i.current(), before: o, after: "~" }), o += i.move("~~"), l(), o;
  }
  function qc() {
    return "~";
  }
  function Wc(e2) {
    return e2.length;
  }
  function ll(e2, n) {
    let t = n || {}, r = (t.align || []).concat(), i = t.stringLength || Wc, l = [], o = [], a = [], u = [], s32 = 0, c = -1;
    for (; ++c < e2.length; ) {
      let k = [], C = [], x = -1;
      for (e2[c].length > s32 && (s32 = e2[c].length); ++x < e2[c].length; ) {
        let T = Xc(e2[c][x]);
        if (t.alignDelimiters !== false) {
          let E = i(T);
          C[x] = E, (u[x] === void 0 || E > u[x]) && (u[x] = E);
        }
        k.push(T);
      }
      o[c] = k, a[c] = C;
    }
    let f = -1;
    if (typeof r == "object" && "length" in r) for (; ++f < s32; ) l[f] = ol(r[f]);
    else {
      let k = ol(r);
      for (; ++f < s32; ) l[f] = k;
    }
    f = -1;
    let m = [], p = [];
    for (; ++f < s32; ) {
      let k = l[f], C = "", x = "";
      k === 99 ? (C = ":", x = ":") : k === 108 ? C = ":" : k === 114 && (x = ":");
      let T = t.alignDelimiters === false ? 1 : Math.max(1, u[f] - C.length - x.length), E = C + "-".repeat(T) + x;
      t.alignDelimiters !== false && (T = C.length + T + x.length, T > u[f] && (u[f] = T), p[f] = T), m[f] = E;
    }
    o.splice(1, 0, m), a.splice(1, 0, p), c = -1;
    let g = [];
    for (; ++c < o.length; ) {
      let k = o[c], C = a[c];
      f = -1;
      let x = [];
      for (; ++f < s32; ) {
        let T = k[f] || "", E = "", M = "";
        if (t.alignDelimiters !== false) {
          let O = u[f] - (C[f] || 0), w = l[f];
          w === 114 ? E = " ".repeat(O) : w === 99 ? O % 2 ? (E = " ".repeat(O / 2 + 0.5), M = " ".repeat(O / 2 - 0.5)) : (E = " ".repeat(O / 2), M = E) : M = " ".repeat(O);
        }
        t.delimiterStart !== false && !f && x.push("|"), t.padding !== false && !(t.alignDelimiters === false && T === "") && (t.delimiterStart !== false || f) && x.push(" "), t.alignDelimiters !== false && x.push(E), x.push(T), t.alignDelimiters !== false && x.push(M), t.padding !== false && x.push(" "), (t.delimiterEnd !== false || f !== s32 - 1) && x.push("|");
      }
      g.push(t.delimiterEnd === false ? x.join("").replace(/ +$/, "") : x.join(""));
    }
    return g.join(`
`);
  }
  function Xc(e2) {
    return e2 == null ? "" : String(e2);
  }
  function ol(e2) {
    let n = typeof e2 == "string" ? e2.codePointAt(0) : 0;
    return n === 67 || n === 99 ? 99 : n === 76 || n === 108 ? 108 : n === 82 || n === 114 ? 114 : 0;
  }
  function al(e2, n, t, r) {
    let i = t.enter("blockquote"), l = t.createTracker(r);
    l.move("> "), l.shift(2);
    let o = t.indentLines(t.containerFlow(e2, l.current()), Qc);
    return i(), o;
  }
  function Qc(e2, n, t) {
    return ">" + (t ? "" : " ") + e2;
  }
  function sl(e2, n) {
    return ul(e2, n.inConstruct, true) && !ul(e2, n.notInConstruct, false);
  }
  function ul(e2, n, t) {
    if (typeof n == "string" && (n = [n]), !n || n.length === 0) return t;
    let r = -1;
    for (; ++r < n.length; ) if (e2.includes(n[r])) return true;
    return false;
  }
  function gr(e2, n, t, r) {
    let i = -1;
    for (; ++i < t.unsafe.length; ) if (t.unsafe[i].character === `
` && sl(t.stack, t.unsafe[i])) return /[ \t]/.test(r.before) ? "" : " ";
    return `\\
`;
  }
  function cl(e2, n) {
    let t = String(e2), r = t.indexOf(n), i = r, l = 0, o = 0;
    if (typeof n != "string") throw new TypeError("Expected substring");
    for (; r !== -1; ) r === i ? ++l > o && (o = l) : l = 1, i = r + n.length, r = t.indexOf(n, i);
    return o;
  }
  function fl(e2, n) {
    return !!(n.options.fences === false && e2.value && !e2.lang && /[^ \r\n]/.test(e2.value) && !/^[\t ]*(?:[\r\n]|$)|(?:^|[\r\n])[\t ]*$/.test(e2.value));
  }
  function pl(e2) {
    let n = e2.options.fence || "`";
    if (n !== "`" && n !== "~") throw new Error("Cannot serialize code with `" + n + "` for `options.fence`, expected `` ` `` or `~`");
    return n;
  }
  function ml(e2, n, t, r) {
    let i = pl(t), l = e2.value || "", o = i === "`" ? "GraveAccent" : "Tilde";
    if (fl(e2, t)) {
      let f = t.enter("codeIndented"), m = t.indentLines(l, Yc);
      return f(), m;
    }
    let a = t.createTracker(r), u = i.repeat(Math.max(cl(l, i) + 1, 3)), s32 = t.enter("codeFenced"), c = a.move(u);
    if (e2.lang) {
      let f = t.enter(`codeFencedLang${o}`);
      c += a.move(t.safe(e2.lang, { before: c, after: " ", encode: ["`"], ...a.current() })), f();
    }
    if (e2.lang && e2.meta) {
      let f = t.enter(`codeFencedMeta${o}`);
      c += a.move(" "), c += a.move(t.safe(e2.meta, { before: c, after: `
`, encode: ["`"], ...a.current() })), f();
    }
    return c += a.move(`
`), l && (c += a.move(l + `
`)), c += a.move(u), s32(), c;
  }
  function Yc(e2, n, t) {
    return (t ? "" : "    ") + e2;
  }
  function et(e2) {
    let n = e2.options.quote || '"';
    if (n !== '"' && n !== "'") throw new Error("Cannot serialize title with `" + n + "` for `options.quote`, expected `\"`, or `'`");
    return n;
  }
  function hl(e2, n, t, r) {
    let i = et(t), l = i === '"' ? "Quote" : "Apostrophe", o = t.enter("definition"), a = t.enter("label"), u = t.createTracker(r), s32 = u.move("[");
    return s32 += u.move(t.safe(t.associationId(e2), { before: s32, after: "]", ...u.current() })), s32 += u.move("]: "), a(), !e2.url || /[\0- \u007F]/.test(e2.url) ? (a = t.enter("destinationLiteral"), s32 += u.move("<"), s32 += u.move(t.safe(e2.url, { before: s32, after: ">", ...u.current() })), s32 += u.move(">")) : (a = t.enter("destinationRaw"), s32 += u.move(t.safe(e2.url, { before: s32, after: e2.title ? " " : `
`, ...u.current() }))), a(), e2.title && (a = t.enter(`title${l}`), s32 += u.move(" " + i), s32 += u.move(t.safe(e2.title, { before: s32, after: i, ...u.current() })), s32 += u.move(i), a()), o(), s32;
  }
  function dl(e2) {
    let n = e2.options.emphasis || "*";
    if (n !== "*" && n !== "_") throw new Error("Cannot serialize emphasis with `" + n + "` for `options.emphasis`, expected `*`, or `_`");
    return n;
  }
  function ze(e2) {
    return "&#x" + e2.toString(16).toUpperCase() + ";";
  }
  function tt(e2, n, t) {
    let r = Ce(e2), i = Ce(n);
    return r === void 0 ? i === void 0 ? t === "_" ? { inside: true, outside: true } : { inside: false, outside: false } : i === 1 ? { inside: true, outside: true } : { inside: false, outside: true } : r === 1 ? i === void 0 ? { inside: false, outside: false } : i === 1 ? { inside: true, outside: true } : { inside: false, outside: false } : i === void 0 ? { inside: false, outside: false } : i === 1 ? { inside: true, outside: false } : { inside: false, outside: false };
  }
  xr.peek = Zc;
  function xr(e2, n, t, r) {
    let i = dl(t), l = t.enter("emphasis"), o = t.createTracker(r), a = o.move(i), u = o.move(t.containerPhrasing(e2, { after: i, before: a, ...o.current() })), s32 = u.charCodeAt(0), c = tt(r.before.charCodeAt(r.before.length - 1), s32, i);
    c.inside && (u = ze(s32) + u.slice(1));
    let f = u.charCodeAt(u.length - 1), m = tt(r.after.charCodeAt(0), f, i);
    m.inside && (u = u.slice(0, -1) + ze(f));
    let p = o.move(i);
    return l(), t.attentionEncodeSurroundingInfo = { after: m.outside, before: c.outside }, a + u + p;
  }
  function Zc(e2, n, t) {
    return t.options.emphasis || "*";
  }
  function gl(e2, n) {
    let t = false;
    return Ee(e2, function(r) {
      if ("value" in r && /\r?\n|\r/.test(r.value) || r.type === "break") return t = true, We;
    }), !!((!e2.depth || e2.depth < 3) && Ne(e2) && (n.options.setext || t));
  }
  function xl(e2, n, t, r) {
    let i = Math.max(Math.min(6, e2.depth || 1), 1), l = t.createTracker(r);
    if (gl(e2, t)) {
      let c = t.enter("headingSetext"), f = t.enter("phrasing"), m = t.containerPhrasing(e2, { ...l.current(), before: `
`, after: `
` });
      return f(), c(), m + `
` + (i === 1 ? "=" : "-").repeat(m.length - (Math.max(m.lastIndexOf("\r"), m.lastIndexOf(`
`)) + 1));
    }
    let o = "#".repeat(i), a = t.enter("headingAtx"), u = t.enter("phrasing");
    l.move(o + " ");
    let s32 = t.containerPhrasing(e2, { before: "# ", after: `
`, ...l.current() });
    return /^[\t ]/.test(s32) && (s32 = ze(s32.charCodeAt(0)) + s32.slice(1)), s32 = s32 ? o + " " + s32 : o, t.options.closeAtx && (s32 += " " + o), u(), a(), s32;
  }
  kr.peek = Gc;
  function kr(e2) {
    return e2.value || "";
  }
  function Gc() {
    return "<";
  }
  yr.peek = $c;
  function yr(e2, n, t, r) {
    let i = et(t), l = i === '"' ? "Quote" : "Apostrophe", o = t.enter("image"), a = t.enter("label"), u = t.createTracker(r), s32 = u.move("![");
    return s32 += u.move(t.safe(e2.alt, { before: s32, after: "]", ...u.current() })), s32 += u.move("]("), a(), !e2.url && e2.title || /[\0- \u007F]/.test(e2.url) ? (a = t.enter("destinationLiteral"), s32 += u.move("<"), s32 += u.move(t.safe(e2.url, { before: s32, after: ">", ...u.current() })), s32 += u.move(">")) : (a = t.enter("destinationRaw"), s32 += u.move(t.safe(e2.url, { before: s32, after: e2.title ? " " : ")", ...u.current() }))), a(), e2.title && (a = t.enter(`title${l}`), s32 += u.move(" " + i), s32 += u.move(t.safe(e2.title, { before: s32, after: i, ...u.current() })), s32 += u.move(i), a()), s32 += u.move(")"), o(), s32;
  }
  function $c() {
    return "!";
  }
  br.peek = Jc;
  function br(e2, n, t, r) {
    let i = e2.referenceType, l = t.enter("imageReference"), o = t.enter("label"), a = t.createTracker(r), u = a.move("!["), s32 = t.safe(e2.alt, { before: u, after: "]", ...a.current() });
    u += a.move(s32 + "]["), o();
    let c = t.stack;
    t.stack = [], o = t.enter("reference");
    let f = t.safe(t.associationId(e2), { before: u, after: "]", ...a.current() });
    return o(), t.stack = c, l(), i === "full" || !s32 || s32 !== f ? u += a.move(f + "]") : i === "shortcut" ? u = u.slice(0, -1) : u += a.move("]"), u;
  }
  function Jc() {
    return "!";
  }
  wr.peek = Kc;
  function wr(e2, n, t) {
    let r = e2.value || "", i = "`", l = -1;
    for (; new RegExp("(^|[^`])" + i + "([^`]|$)").test(r); ) i += "`";
    for (/[^ \r\n]/.test(r) && (/^[ \r\n]/.test(r) && /[ \r\n]$/.test(r) || /^`|`$/.test(r)) && (r = " " + r + " "); ++l < t.unsafe.length; ) {
      let o = t.unsafe[l], a = t.compilePattern(o), u;
      if (o.atBreak) for (; u = a.exec(r); ) {
        let s32 = u.index;
        r.charCodeAt(s32) === 10 && r.charCodeAt(s32 - 1) === 13 && s32--, r = r.slice(0, s32) + " " + r.slice(u.index + 1);
      }
    }
    return i + r + i;
  }
  function Kc() {
    return "`";
  }
  function Sr(e2, n) {
    let t = Ne(e2);
    return !!(!n.options.resourceLink && e2.url && !e2.title && e2.children && e2.children.length === 1 && e2.children[0].type === "text" && (t === e2.url || "mailto:" + t === e2.url) && /^[a-z][a-z+.-]+:/i.test(e2.url) && !/[\0- <>\u007F]/.test(e2.url));
  }
  Cr.peek = ef;
  function Cr(e2, n, t, r) {
    let i = et(t), l = i === '"' ? "Quote" : "Apostrophe", o = t.createTracker(r), a, u;
    if (Sr(e2, t)) {
      let c = t.stack;
      t.stack = [], a = t.enter("autolink");
      let f = o.move("<");
      return f += o.move(t.containerPhrasing(e2, { before: f, after: ">", ...o.current() })), f += o.move(">"), a(), t.stack = c, f;
    }
    a = t.enter("link"), u = t.enter("label");
    let s32 = o.move("[");
    return s32 += o.move(t.containerPhrasing(e2, { before: s32, after: "](", ...o.current() })), s32 += o.move("]("), u(), !e2.url && e2.title || /[\0- \u007F]/.test(e2.url) ? (u = t.enter("destinationLiteral"), s32 += o.move("<"), s32 += o.move(t.safe(e2.url, { before: s32, after: ">", ...o.current() })), s32 += o.move(">")) : (u = t.enter("destinationRaw"), s32 += o.move(t.safe(e2.url, { before: s32, after: e2.title ? " " : ")", ...o.current() }))), u(), e2.title && (u = t.enter(`title${l}`), s32 += o.move(" " + i), s32 += o.move(t.safe(e2.title, { before: s32, after: i, ...o.current() })), s32 += o.move(i), u()), s32 += o.move(")"), a(), s32;
  }
  function ef(e2, n, t) {
    return Sr(e2, t) ? "<" : "[";
  }
  Er.peek = tf;
  function Er(e2, n, t, r) {
    let i = e2.referenceType, l = t.enter("linkReference"), o = t.enter("label"), a = t.createTracker(r), u = a.move("["), s32 = t.containerPhrasing(e2, { before: u, after: "]", ...a.current() });
    u += a.move(s32 + "]["), o();
    let c = t.stack;
    t.stack = [], o = t.enter("reference");
    let f = t.safe(t.associationId(e2), { before: u, after: "]", ...a.current() });
    return o(), t.stack = c, l(), i === "full" || !s32 || s32 !== f ? u += a.move(f + "]") : i === "shortcut" ? u = u.slice(0, -1) : u += a.move("]"), u;
  }
  function tf() {
    return "[";
  }
  function nt(e2) {
    let n = e2.options.bullet || "*";
    if (n !== "*" && n !== "+" && n !== "-") throw new Error("Cannot serialize items with `" + n + "` for `options.bullet`, expected `*`, `+`, or `-`");
    return n;
  }
  function kl(e2) {
    let n = nt(e2), t = e2.options.bulletOther;
    if (!t) return n === "*" ? "-" : "*";
    if (t !== "*" && t !== "+" && t !== "-") throw new Error("Cannot serialize items with `" + t + "` for `options.bulletOther`, expected `*`, `+`, or `-`");
    if (t === n) throw new Error("Expected `bullet` (`" + n + "`) and `bulletOther` (`" + t + "`) to be different");
    return t;
  }
  function yl(e2) {
    let n = e2.options.bulletOrdered || ".";
    if (n !== "." && n !== ")") throw new Error("Cannot serialize items with `" + n + "` for `options.bulletOrdered`, expected `.` or `)`");
    return n;
  }
  function rn(e2) {
    let n = e2.options.rule || "*";
    if (n !== "*" && n !== "-" && n !== "_") throw new Error("Cannot serialize rules with `" + n + "` for `options.rule`, expected `*`, `-`, or `_`");
    return n;
  }
  function bl(e2, n, t, r) {
    let i = t.enter("list"), l = t.bulletCurrent, o = e2.ordered ? yl(t) : nt(t), a = e2.ordered ? o === "." ? ")" : "." : kl(t), u = n && t.bulletLastUsed ? o === t.bulletLastUsed : false;
    if (!e2.ordered) {
      let c = e2.children ? e2.children[0] : void 0;
      if ((o === "*" || o === "-") && c && (!c.children || !c.children[0]) && t.stack[t.stack.length - 1] === "list" && t.stack[t.stack.length - 2] === "listItem" && t.stack[t.stack.length - 3] === "list" && t.stack[t.stack.length - 4] === "listItem" && t.indexStack[t.indexStack.length - 1] === 0 && t.indexStack[t.indexStack.length - 2] === 0 && t.indexStack[t.indexStack.length - 3] === 0 && (u = true), rn(t) === o && c) {
        let f = -1;
        for (; ++f < e2.children.length; ) {
          let m = e2.children[f];
          if (m && m.type === "listItem" && m.children && m.children[0] && m.children[0].type === "thematicBreak") {
            u = true;
            break;
          }
        }
      }
    }
    u && (o = a), t.bulletCurrent = o;
    let s32 = t.containerFlow(e2, r);
    return t.bulletLastUsed = o, t.bulletCurrent = l, i(), s32;
  }
  function wl(e2) {
    let n = e2.options.listItemIndent || "one";
    if (n !== "tab" && n !== "one" && n !== "mixed") throw new Error("Cannot serialize items with `" + n + "` for `options.listItemIndent`, expected `tab`, `one`, or `mixed`");
    return n;
  }
  function Sl(e2, n, t, r) {
    let i = wl(t), l = t.bulletCurrent || nt(t);
    n && n.type === "list" && n.ordered && (l = (typeof n.start == "number" && n.start > -1 ? n.start : 1) + (t.options.incrementListMarker === false ? 0 : n.children.indexOf(e2)) + l);
    let o = l.length + 1;
    (i === "tab" || i === "mixed" && (n && n.type === "list" && n.spread || e2.spread)) && (o = Math.ceil(o / 4) * 4);
    let a = t.createTracker(r);
    a.move(l + " ".repeat(o - l.length)), a.shift(o);
    let u = t.enter("listItem"), s32 = t.indentLines(t.containerFlow(e2, a.current()), c);
    return u(), s32;
    function c(f, m, p) {
      return m ? (p ? "" : " ".repeat(o)) + f : (p ? l : l + " ".repeat(o - l.length)) + f;
    }
  }
  function Cl(e2, n, t, r) {
    let i = t.enter("paragraph"), l = t.enter("phrasing"), o = t.containerPhrasing(e2, r);
    return l(), i(), o;
  }
  var Ir = Pe(["break", "delete", "emphasis", "footnote", "footnoteReference", "image", "imageReference", "inlineCode", "inlineMath", "link", "linkReference", "mdxJsxTextElement", "mdxTextExpression", "strong", "text", "textDirective"]);
  function El(e2, n, t, r) {
    return (e2.children.some(function(o) {
      return Ir(o);
    }) ? t.containerPhrasing : t.containerFlow).call(t, e2, r);
  }
  function Il(e2) {
    let n = e2.options.strong || "*";
    if (n !== "*" && n !== "_") throw new Error("Cannot serialize strong with `" + n + "` for `options.strong`, expected `*`, or `_`");
    return n;
  }
  Tr.peek = nf;
  function Tr(e2, n, t, r) {
    let i = Il(t), l = t.enter("strong"), o = t.createTracker(r), a = o.move(i + i), u = o.move(t.containerPhrasing(e2, { after: i, before: a, ...o.current() })), s32 = u.charCodeAt(0), c = tt(r.before.charCodeAt(r.before.length - 1), s32, i);
    c.inside && (u = ze(s32) + u.slice(1));
    let f = u.charCodeAt(u.length - 1), m = tt(r.after.charCodeAt(0), f, i);
    m.inside && (u = u.slice(0, -1) + ze(f));
    let p = o.move(i + i);
    return l(), t.attentionEncodeSurroundingInfo = { after: m.outside, before: c.outside }, a + u + p;
  }
  function nf(e2, n, t) {
    return t.options.strong || "*";
  }
  function Tl(e2, n, t, r) {
    return t.safe(e2.value, r);
  }
  function Al(e2) {
    let n = e2.options.ruleRepetition || 3;
    if (n < 3) throw new Error("Cannot serialize rules with repetition `" + n + "` for `options.ruleRepetition`, expected `3` or more");
    return n;
  }
  function Ll(e2, n, t) {
    let r = (rn(t) + (t.options.ruleSpaces ? " " : "")).repeat(Al(t));
    return t.options.ruleSpaces ? r.slice(0, -1) : r;
  }
  var St = { blockquote: al, break: gr, code: ml, definition: hl, emphasis: xr, hardBreak: gr, heading: xl, html: kr, image: yr, imageReference: br, inlineCode: wr, link: Cr, linkReference: Er, list: bl, listItem: Sl, paragraph: Cl, root: El, strong: Tr, text: Tl, thematicBreak: Ll };
  function Lr() {
    return { enter: { table: rf, tableData: vl, tableHeader: vl, tableRow: lf }, exit: { codeText: af, table: of, tableData: Ar, tableHeader: Ar, tableRow: Ar } };
  }
  function rf(e2) {
    let n = e2._align;
    this.enter({ type: "table", align: n.map(function(t) {
      return t === "none" ? null : t;
    }), children: [] }, e2), this.data.inTable = true;
  }
  function of(e2) {
    this.exit(e2), this.data.inTable = void 0;
  }
  function lf(e2) {
    this.enter({ type: "tableRow", children: [] }, e2);
  }
  function Ar(e2) {
    this.exit(e2);
  }
  function vl(e2) {
    this.enter({ type: "tableCell", children: [] }, e2);
  }
  function af(e2) {
    let n = this.resume();
    this.data.inTable && (n = n.replace(/\\([\\|])/g, uf));
    let t = this.stack[this.stack.length - 1];
    t.type, t.value = n, this.exit(e2);
  }
  function uf(e2, n) {
    return n === "|" ? n : e2;
  }
  function vr(e2) {
    let n = e2 || {}, t = n.tableCellPadding, r = n.tablePipeAlign, i = n.stringLength, l = t ? " " : "|";
    return { unsafe: [{ character: "\r", inConstruct: "tableCell" }, { character: `
`, inConstruct: "tableCell" }, { atBreak: true, character: "|", after: "[	 :-]" }, { character: "|", inConstruct: "tableCell" }, { atBreak: true, character: ":", after: "-" }, { atBreak: true, character: "-", after: "[:|-]" }], handlers: { inlineCode: m, table: o, tableCell: u, tableRow: a } };
    function o(p, g, k, C) {
      return s32(c(p, k, C), p.align);
    }
    function a(p, g, k, C) {
      let x = f(p, k, C), T = s32([x]);
      return T.slice(0, T.indexOf(`
`));
    }
    function u(p, g, k, C) {
      let x = k.enter("tableCell"), T = k.enter("phrasing"), E = k.containerPhrasing(p, { ...C, before: l, after: l });
      return T(), x(), E;
    }
    function s32(p, g) {
      return ll(p, { align: g, alignDelimiters: r, padding: t, stringLength: i });
    }
    function c(p, g, k) {
      let C = p.children, x = -1, T = [], E = g.enter("table");
      for (; ++x < C.length; ) T[x] = f(C[x], g, k);
      return E(), T;
    }
    function f(p, g, k) {
      let C = p.children, x = -1, T = [], E = g.enter("tableRow");
      for (; ++x < C.length; ) T[x] = u(C[x], p, g, k);
      return E(), T;
    }
    function m(p, g, k) {
      let C = St.inlineCode(p, g, k);
      return k.stack.includes("tableCell") && (C = C.replace(/\|/g, "\\$&")), C;
    }
  }
  function Pr() {
    return { exit: { taskListCheckValueChecked: Pl, taskListCheckValueUnchecked: Pl, paragraph: sf } };
  }
  function zr() {
    return { unsafe: [{ atBreak: true, character: "-", after: "[:|-]" }], handlers: { listItem: cf } };
  }
  function Pl(e2) {
    let n = this.stack[this.stack.length - 2];
    n.type, n.checked = e2.type === "taskListCheckValueChecked";
  }
  function sf(e2) {
    let n = this.stack[this.stack.length - 2];
    if (n && n.type === "listItem" && typeof n.checked == "boolean") {
      let t = this.stack[this.stack.length - 1];
      t.type;
      let r = t.children[0];
      if (r && r.type === "text") {
        let i = n.children, l = -1, o;
        for (; ++l < i.length; ) {
          let a = i[l];
          if (a.type === "paragraph") {
            o = a;
            break;
          }
        }
        o === t && (r.value = r.value.slice(1), r.value.length === 0 ? t.children.shift() : t.position && r.position && typeof r.position.start.offset == "number" && (r.position.start.column++, r.position.start.offset++, t.position.start = Object.assign({}, r.position.start)));
      }
    }
    this.exit(e2);
  }
  function cf(e2, n, t, r) {
    let i = e2.children[0], l = typeof e2.checked == "boolean" && i && i.type === "paragraph", o = "[" + (e2.checked ? "x" : " ") + "] ", a = t.createTracker(r);
    l && a.move(o);
    let u = St.listItem(e2, n, t, { ...r, ...a.current() });
    return l && (u = u.replace(/^(?:[*+-]|\d+\.)([\r\n]| {1,3})/, s32)), u;
    function s32(c) {
      return c + o;
    }
  }
  function Fr() {
    return [cr(), pr(), hr(), Lr(), Pr()];
  }
  function Dr(e2) {
    return { extensions: [fr(), mr(e2), dr(), vr(e2), zr()] };
  }
  var ff = { tokenize: gf, partial: true };
  var zl = { tokenize: xf, partial: true };
  var Fl = { tokenize: kf, partial: true };
  var Dl = { tokenize: yf, partial: true };
  var pf = { tokenize: bf, partial: true };
  var Rl = { name: "wwwAutolink", tokenize: hf, previous: Ol };
  var Ml = { name: "protocolAutolink", tokenize: df, previous: _l };
  var Ie = { name: "emailAutolink", tokenize: mf, previous: Nl };
  var ge = {};
  function Mr() {
    return { text: ge };
  }
  var Qe = 48;
  for (; Qe < 123; ) ge[Qe] = Ie, Qe++, Qe === 58 ? Qe = 65 : Qe === 91 && (Qe = 97);
  ge[43] = Ie;
  ge[45] = Ie;
  ge[46] = Ie;
  ge[95] = Ie;
  ge[72] = [Ie, Ml];
  ge[104] = [Ie, Ml];
  ge[87] = [Ie, Rl];
  ge[119] = [Ie, Rl];
  function mf(e2, n, t) {
    let r = this, i, l;
    return o;
    function o(f) {
      return !Rr(f) || !Nl.call(r, r.previous) || Or(r.events) ? t(f) : (e2.enter("literalAutolink"), e2.enter("literalAutolinkEmail"), a(f));
    }
    function a(f) {
      return Rr(f) ? (e2.consume(f), a) : f === 64 ? (e2.consume(f), u) : t(f);
    }
    function u(f) {
      return f === 46 ? e2.check(pf, c, s32)(f) : f === 45 || f === 95 || Q(f) ? (l = true, e2.consume(f), u) : c(f);
    }
    function s32(f) {
      return e2.consume(f), i = true, u;
    }
    function c(f) {
      return l && i && $(r.previous) ? (e2.exit("literalAutolinkEmail"), e2.exit("literalAutolink"), n(f)) : t(f);
    }
  }
  function hf(e2, n, t) {
    let r = this;
    return i;
    function i(o) {
      return o !== 87 && o !== 119 || !Ol.call(r, r.previous) || Or(r.events) ? t(o) : (e2.enter("literalAutolink"), e2.enter("literalAutolinkWww"), e2.check(ff, e2.attempt(zl, e2.attempt(Fl, l), t), t)(o));
    }
    function l(o) {
      return e2.exit("literalAutolinkWww"), e2.exit("literalAutolink"), n(o);
    }
  }
  function df(e2, n, t) {
    let r = this, i = "", l = false;
    return o;
    function o(f) {
      return (f === 72 || f === 104) && _l.call(r, r.previous) && !Or(r.events) ? (e2.enter("literalAutolink"), e2.enter("literalAutolinkHttp"), i += String.fromCodePoint(f), e2.consume(f), a) : t(f);
    }
    function a(f) {
      if ($(f) && i.length < 5) return i += String.fromCodePoint(f), e2.consume(f), a;
      if (f === 58) {
        let m = i.toLowerCase();
        if (m === "http" || m === "https") return e2.consume(f), u;
      }
      return t(f);
    }
    function u(f) {
      return f === 47 ? (e2.consume(f), l ? s32 : (l = true, u)) : t(f);
    }
    function s32(f) {
      return f === null || Be(f) || _(f) || he(f) || He(f) ? t(f) : e2.attempt(zl, e2.attempt(Fl, c), t)(f);
    }
    function c(f) {
      return e2.exit("literalAutolinkHttp"), e2.exit("literalAutolink"), n(f);
    }
  }
  function gf(e2, n, t) {
    let r = 0;
    return i;
    function i(o) {
      return (o === 87 || o === 119) && r < 3 ? (r++, e2.consume(o), i) : o === 46 && r === 3 ? (e2.consume(o), l) : t(o);
    }
    function l(o) {
      return o === null ? t(o) : n(o);
    }
  }
  function xf(e2, n, t) {
    let r, i, l;
    return o;
    function o(s32) {
      return s32 === 46 || s32 === 95 ? e2.check(Dl, u, a)(s32) : s32 === null || _(s32) || he(s32) || s32 !== 45 && He(s32) ? u(s32) : (l = true, e2.consume(s32), o);
    }
    function a(s32) {
      return s32 === 95 ? r = true : (i = r, r = void 0), e2.consume(s32), o;
    }
    function u(s32) {
      return i || r || !l ? t(s32) : n(s32);
    }
  }
  function kf(e2, n) {
    let t = 0, r = 0;
    return i;
    function i(o) {
      return o === 40 ? (t++, e2.consume(o), i) : o === 41 && r < t ? l(o) : o === 33 || o === 34 || o === 38 || o === 39 || o === 41 || o === 42 || o === 44 || o === 46 || o === 58 || o === 59 || o === 60 || o === 63 || o === 93 || o === 95 || o === 126 ? e2.check(Dl, n, l)(o) : o === null || _(o) || he(o) ? n(o) : (e2.consume(o), i);
    }
    function l(o) {
      return o === 41 && r++, e2.consume(o), i;
    }
  }
  function yf(e2, n, t) {
    return r;
    function r(a) {
      return a === 33 || a === 34 || a === 39 || a === 41 || a === 42 || a === 44 || a === 46 || a === 58 || a === 59 || a === 63 || a === 95 || a === 126 ? (e2.consume(a), r) : a === 38 ? (e2.consume(a), l) : a === 93 ? (e2.consume(a), i) : a === 60 || a === null || _(a) || he(a) ? n(a) : t(a);
    }
    function i(a) {
      return a === null || a === 40 || a === 91 || _(a) || he(a) ? n(a) : r(a);
    }
    function l(a) {
      return $(a) ? o(a) : t(a);
    }
    function o(a) {
      return a === 59 ? (e2.consume(a), r) : $(a) ? (e2.consume(a), o) : t(a);
    }
  }
  function bf(e2, n, t) {
    return r;
    function r(l) {
      return e2.consume(l), i;
    }
    function i(l) {
      return Q(l) ? t(l) : n(l);
    }
  }
  function Ol(e2) {
    return e2 === null || e2 === 40 || e2 === 42 || e2 === 95 || e2 === 91 || e2 === 93 || e2 === 126 || _(e2);
  }
  function _l(e2) {
    return !$(e2);
  }
  function Nl(e2) {
    return !(e2 === 47 || Rr(e2));
  }
  function Rr(e2) {
    return e2 === 43 || e2 === 45 || e2 === 46 || e2 === 95 || Q(e2);
  }
  function Or(e2) {
    let n = e2.length, t = false;
    for (; n--; ) {
      let r = e2[n][1];
      if ((r.type === "labelLink" || r.type === "labelImage") && !r._balanced) {
        t = true;
        break;
      }
      if (r._gfmAutolinkLiteralWalkedInto) {
        t = false;
        break;
      }
    }
    return e2.length > 0 && !t && (e2[e2.length - 1][1]._gfmAutolinkLiteralWalkedInto = true), t;
  }
  var wf = { tokenize: Lf, partial: true };
  function _r() {
    return { document: { 91: { name: "gfmFootnoteDefinition", tokenize: If, continuation: { tokenize: Tf }, exit: Af } }, text: { 91: { name: "gfmFootnoteCall", tokenize: Ef }, 93: { name: "gfmPotentialFootnoteCall", add: "after", tokenize: Sf, resolveTo: Cf } } };
  }
  function Sf(e2, n, t) {
    let r = this, i = r.events.length, l = r.parser.gfmFootnotes || (r.parser.gfmFootnotes = []), o;
    for (; i--; ) {
      let u = r.events[i][1];
      if (u.type === "labelImage") {
        o = u;
        break;
      }
      if (u.type === "gfmFootnoteCall" || u.type === "labelLink" || u.type === "label" || u.type === "image" || u.type === "link") break;
    }
    return a;
    function a(u) {
      if (!o || !o._balanced) return t(u);
      let s32 = te(r.sliceSerialize({ start: o.end, end: r.now() }));
      return s32.codePointAt(0) !== 94 || !l.includes(s32.slice(1)) ? t(u) : (e2.enter("gfmFootnoteCallLabelMarker"), e2.consume(u), e2.exit("gfmFootnoteCallLabelMarker"), n(u));
    }
  }
  function Cf(e2, n) {
    let t = e2.length, r;
    for (; t--; ) if (e2[t][1].type === "labelImage" && e2[t][0] === "enter") {
      r = e2[t][1];
      break;
    }
    e2[t + 1][1].type = "data", e2[t + 3][1].type = "gfmFootnoteCallLabelMarker";
    let i = { type: "gfmFootnoteCall", start: Object.assign({}, e2[t + 3][1].start), end: Object.assign({}, e2[e2.length - 1][1].end) }, l = { type: "gfmFootnoteCallMarker", start: Object.assign({}, e2[t + 3][1].end), end: Object.assign({}, e2[t + 3][1].end) };
    l.end.column++, l.end.offset++, l.end._bufferIndex++;
    let o = { type: "gfmFootnoteCallString", start: Object.assign({}, l.end), end: Object.assign({}, e2[e2.length - 1][1].start) }, a = { type: "chunkString", contentType: "string", start: Object.assign({}, o.start), end: Object.assign({}, o.end) }, u = [e2[t + 1], e2[t + 2], ["enter", i, n], e2[t + 3], e2[t + 4], ["enter", l, n], ["exit", l, n], ["enter", o, n], ["enter", a, n], ["exit", a, n], ["exit", o, n], e2[e2.length - 2], e2[e2.length - 1], ["exit", i, n]];
    return e2.splice(t, e2.length - t + 1, ...u), e2;
  }
  function Ef(e2, n, t) {
    let r = this, i = r.parser.gfmFootnotes || (r.parser.gfmFootnotes = []), l = 0, o;
    return a;
    function a(f) {
      return e2.enter("gfmFootnoteCall"), e2.enter("gfmFootnoteCallLabelMarker"), e2.consume(f), e2.exit("gfmFootnoteCallLabelMarker"), u;
    }
    function u(f) {
      return f !== 94 ? t(f) : (e2.enter("gfmFootnoteCallMarker"), e2.consume(f), e2.exit("gfmFootnoteCallMarker"), e2.enter("gfmFootnoteCallString"), e2.enter("chunkString").contentType = "string", s32);
    }
    function s32(f) {
      if (l > 999 || f === 93 && !o || f === null || f === 91 || _(f)) return t(f);
      if (f === 93) {
        e2.exit("chunkString");
        let m = e2.exit("gfmFootnoteCallString");
        return i.includes(te(r.sliceSerialize(m))) ? (e2.enter("gfmFootnoteCallLabelMarker"), e2.consume(f), e2.exit("gfmFootnoteCallLabelMarker"), e2.exit("gfmFootnoteCall"), n) : t(f);
      }
      return _(f) || (o = true), l++, e2.consume(f), f === 92 ? c : s32;
    }
    function c(f) {
      return f === 91 || f === 92 || f === 93 ? (e2.consume(f), l++, s32) : s32(f);
    }
  }
  function If(e2, n, t) {
    let r = this, i = r.parser.gfmFootnotes || (r.parser.gfmFootnotes = []), l, o = 0, a;
    return u;
    function u(g) {
      return e2.enter("gfmFootnoteDefinition")._container = true, e2.enter("gfmFootnoteDefinitionLabel"), e2.enter("gfmFootnoteDefinitionLabelMarker"), e2.consume(g), e2.exit("gfmFootnoteDefinitionLabelMarker"), s32;
    }
    function s32(g) {
      return g === 94 ? (e2.enter("gfmFootnoteDefinitionMarker"), e2.consume(g), e2.exit("gfmFootnoteDefinitionMarker"), e2.enter("gfmFootnoteDefinitionLabelString"), e2.enter("chunkString").contentType = "string", c) : t(g);
    }
    function c(g) {
      if (o > 999 || g === 93 && !a || g === null || g === 91 || _(g)) return t(g);
      if (g === 93) {
        e2.exit("chunkString");
        let k = e2.exit("gfmFootnoteDefinitionLabelString");
        return l = te(r.sliceSerialize(k)), e2.enter("gfmFootnoteDefinitionLabelMarker"), e2.consume(g), e2.exit("gfmFootnoteDefinitionLabelMarker"), e2.exit("gfmFootnoteDefinitionLabel"), m;
      }
      return _(g) || (a = true), o++, e2.consume(g), g === 92 ? f : c;
    }
    function f(g) {
      return g === 91 || g === 92 || g === 93 ? (e2.consume(g), o++, c) : c(g);
    }
    function m(g) {
      return g === 58 ? (e2.enter("definitionMarker"), e2.consume(g), e2.exit("definitionMarker"), i.includes(l) || i.push(l), v(e2, p, "gfmFootnoteDefinitionWhitespace")) : t(g);
    }
    function p(g) {
      return n(g);
    }
  }
  function Tf(e2, n, t) {
    return e2.check(de, n, e2.attempt(wf, n, t));
  }
  function Af(e2) {
    e2.exit("gfmFootnoteDefinition");
  }
  function Lf(e2, n, t) {
    let r = this;
    return v(e2, i, "gfmFootnoteDefinitionIndent", 5);
    function i(l) {
      let o = r.events[r.events.length - 1];
      return o && o[1].type === "gfmFootnoteDefinitionIndent" && o[2].sliceSerialize(o[1], true).length === 4 ? n(l) : t(l);
    }
  }
  function Nr(e2) {
    let t = (e2 || {}).singleTilde, r = { name: "strikethrough", tokenize: l, resolveAll: i };
    return t == null && (t = true), { text: { 126: r }, insideSpan: { null: [r] }, attentionMarkers: { null: [126] } };
    function i(o, a) {
      let u = -1;
      for (; ++u < o.length; ) if (o[u][0] === "enter" && o[u][1].type === "strikethroughSequenceTemporary" && o[u][1]._close) {
        let s32 = u;
        for (; s32--; ) if (o[s32][0] === "exit" && o[s32][1].type === "strikethroughSequenceTemporary" && o[s32][1]._open && o[u][1].end.offset - o[u][1].start.offset === o[s32][1].end.offset - o[s32][1].start.offset) {
          o[u][1].type = "strikethroughSequence", o[s32][1].type = "strikethroughSequence";
          let c = { type: "strikethrough", start: Object.assign({}, o[s32][1].start), end: Object.assign({}, o[u][1].end) }, f = { type: "strikethroughText", start: Object.assign({}, o[s32][1].end), end: Object.assign({}, o[u][1].start) }, m = [["enter", c, a], ["enter", o[s32][1], a], ["exit", o[s32][1], a], ["enter", f, a]], p = a.parser.constructs.insideSpan.null;
          p && Z(m, m.length, 0, Le(p, o.slice(s32 + 1, u), a)), Z(m, m.length, 0, [["exit", f, a], ["enter", o[u][1], a], ["exit", o[u][1], a], ["exit", c, a]]), Z(o, s32 - 1, u - s32 + 3, m), u = s32 + m.length - 2;
          break;
        }
      }
      for (u = -1; ++u < o.length; ) o[u][1].type === "strikethroughSequenceTemporary" && (o[u][1].type = "data");
      return o;
    }
    function l(o, a, u) {
      let s32 = this.previous, c = this.events, f = 0;
      return m;
      function m(g) {
        return s32 === 126 && c[c.length - 1][1].type !== "characterEscape" ? u(g) : (o.enter("strikethroughSequenceTemporary"), p(g));
      }
      function p(g) {
        let k = Ce(s32);
        if (g === 126) return f > 1 ? u(g) : (o.consume(g), f++, p);
        if (f < 2 && !t) return u(g);
        let C = o.exit("strikethroughSequenceTemporary"), x = Ce(g);
        return C._open = !x || x === 2 && !!k, C._close = !k || k === 2 && !!x, a(g);
      }
    }
  }
  var on = class {
    constructor() {
      this.map = [], this.index = /* @__PURE__ */ new Map();
    }
    add(n, t, r) {
      vf(this, n, t, r);
    }
    consume(n) {
      if (this.map.sort(function(l, o) {
        return l[0] - o[0];
      }), this.map.length === 0) return;
      let t = this.map.length, r = [];
      for (; t > 0; ) t -= 1, r.push(n.slice(this.map[t][0] + this.map[t][1]), this.map[t][2]), n.length = this.map[t][0];
      r.push(n.slice()), n.length = 0;
      let i = r.pop();
      for (; i; ) {
        for (let l of i) n.push(l);
        i = r.pop();
      }
      this.map.length = 0, this.index.clear();
    }
  };
  function vf(e2, n, t, r) {
    if (t === 0 && r.length === 0) return;
    let i = e2.index.get(n);
    if (i) {
      i[1] += t, i[2].push(...r);
      return;
    }
    let l = [n, t, r];
    e2.map.push(l), e2.index.set(n, l);
  }
  function Bl(e2, n) {
    let t = false, r = [];
    for (; n < e2.length; ) {
      let i = e2[n];
      if (t) {
        if (i[0] === "enter") i[1].type === "tableContent" && r.push(e2[n + 1][1].type === "tableDelimiterMarker" ? "left" : "none");
        else if (i[1].type === "tableContent") {
          if (e2[n - 1][1].type === "tableDelimiterMarker") {
            let l = r.length - 1;
            r[l] = r[l] === "left" ? "center" : "right";
          }
        } else if (i[1].type === "tableDelimiterRow") break;
      } else i[0] === "enter" && i[1].type === "tableDelimiterRow" && (t = true);
      n += 1;
    }
    return r;
  }
  function Br() {
    return { flow: { null: { name: "table", tokenize: Pf, resolveAll: zf } } };
  }
  function Pf(e2, n, t) {
    let r = this, i = 0, l = 0, o;
    return a;
    function a(y) {
      let J = r.events.length - 1;
      for (; J > -1; ) {
        let { type: D } = r.events[J][1];
        if (D === "lineEnding" || D === "linePrefix") J--;
        else break;
      }
      let j = J > -1 ? r.events[J][1].type : null, L = j === "tableHead" || j === "tableRow" ? w : u;
      return L === w && r.parser.lazy[r.now().line] ? t(y) : L(y);
    }
    function u(y) {
      return e2.enter("tableHead"), e2.enter("tableRow"), s32(y);
    }
    function s32(y) {
      return y === 124 || (o = true, l += 1), c(y);
    }
    function c(y) {
      return y === null ? t(y) : A(y) ? l > 1 ? (l = 0, r.interrupt = true, e2.exit("tableRow"), e2.enter("lineEnding"), e2.consume(y), e2.exit("lineEnding"), p) : t(y) : P(y) ? v(e2, c, "whitespace")(y) : (l += 1, o && (o = false, i += 1), y === 124 ? (e2.enter("tableCellDivider"), e2.consume(y), e2.exit("tableCellDivider"), o = true, c) : (e2.enter("data"), f(y)));
    }
    function f(y) {
      return y === null || y === 124 || _(y) ? (e2.exit("data"), c(y)) : (e2.consume(y), y === 92 ? m : f);
    }
    function m(y) {
      return y === 92 || y === 124 ? (e2.consume(y), f) : f(y);
    }
    function p(y) {
      return r.interrupt = false, r.parser.lazy[r.now().line] ? t(y) : (e2.enter("tableDelimiterRow"), o = false, P(y) ? v(e2, g, "linePrefix", r.parser.constructs.disable.null.includes("codeIndented") ? void 0 : 4)(y) : g(y));
    }
    function g(y) {
      return y === 45 || y === 58 ? C(y) : y === 124 ? (o = true, e2.enter("tableCellDivider"), e2.consume(y), e2.exit("tableCellDivider"), k) : O(y);
    }
    function k(y) {
      return P(y) ? v(e2, C, "whitespace")(y) : C(y);
    }
    function C(y) {
      return y === 58 ? (l += 1, o = true, e2.enter("tableDelimiterMarker"), e2.consume(y), e2.exit("tableDelimiterMarker"), x) : y === 45 ? (l += 1, x(y)) : y === null || A(y) ? M(y) : O(y);
    }
    function x(y) {
      return y === 45 ? (e2.enter("tableDelimiterFiller"), T(y)) : O(y);
    }
    function T(y) {
      return y === 45 ? (e2.consume(y), T) : y === 58 ? (o = true, e2.exit("tableDelimiterFiller"), e2.enter("tableDelimiterMarker"), e2.consume(y), e2.exit("tableDelimiterMarker"), E) : (e2.exit("tableDelimiterFiller"), E(y));
    }
    function E(y) {
      return P(y) ? v(e2, M, "whitespace")(y) : M(y);
    }
    function M(y) {
      return y === 124 ? g(y) : y === null || A(y) ? !o || i !== l ? O(y) : (e2.exit("tableDelimiterRow"), e2.exit("tableHead"), n(y)) : O(y);
    }
    function O(y) {
      return t(y);
    }
    function w(y) {
      return e2.enter("tableRow"), B(y);
    }
    function B(y) {
      return y === 124 ? (e2.enter("tableCellDivider"), e2.consume(y), e2.exit("tableCellDivider"), B) : y === null || A(y) ? (e2.exit("tableRow"), n(y)) : P(y) ? v(e2, B, "whitespace")(y) : (e2.enter("data"), q(y));
    }
    function q(y) {
      return y === null || y === 124 || _(y) ? (e2.exit("data"), B(y)) : (e2.consume(y), y === 92 ? H : q);
    }
    function H(y) {
      return y === 92 || y === 124 ? (e2.consume(y), q) : q(y);
    }
  }
  function zf(e2, n) {
    let t = -1, r = true, i = 0, l = [0, 0, 0, 0], o = [0, 0, 0, 0], a = false, u = 0, s32, c, f, m = new on();
    for (; ++t < e2.length; ) {
      let p = e2[t], g = p[1];
      p[0] === "enter" ? g.type === "tableHead" ? (a = false, u !== 0 && (Hl(m, n, u, s32, c), c = void 0, u = 0), s32 = { type: "table", start: Object.assign({}, g.start), end: Object.assign({}, g.end) }, m.add(t, 0, [["enter", s32, n]])) : g.type === "tableRow" || g.type === "tableDelimiterRow" ? (r = true, f = void 0, l = [0, 0, 0, 0], o = [0, t + 1, 0, 0], a && (a = false, c = { type: "tableBody", start: Object.assign({}, g.start), end: Object.assign({}, g.end) }, m.add(t, 0, [["enter", c, n]])), i = g.type === "tableDelimiterRow" ? 2 : c ? 3 : 1) : i && (g.type === "data" || g.type === "tableDelimiterMarker" || g.type === "tableDelimiterFiller") ? (r = false, o[2] === 0 && (l[1] !== 0 && (o[0] = o[1], f = ln(m, n, l, i, void 0, f), l = [0, 0, 0, 0]), o[2] = t)) : g.type === "tableCellDivider" && (r ? r = false : (l[1] !== 0 && (o[0] = o[1], f = ln(m, n, l, i, void 0, f)), l = o, o = [l[1], t, 0, 0])) : g.type === "tableHead" ? (a = true, u = t) : g.type === "tableRow" || g.type === "tableDelimiterRow" ? (u = t, l[1] !== 0 ? (o[0] = o[1], f = ln(m, n, l, i, t, f)) : o[1] !== 0 && (f = ln(m, n, o, i, t, f)), i = 0) : i && (g.type === "data" || g.type === "tableDelimiterMarker" || g.type === "tableDelimiterFiller") && (o[3] = t);
    }
    for (u !== 0 && Hl(m, n, u, s32, c), m.consume(n.events), t = -1; ++t < n.events.length; ) {
      let p = n.events[t];
      p[0] === "enter" && p[1].type === "table" && (p[1]._align = Bl(n.events, t));
    }
    return e2;
  }
  function ln(e2, n, t, r, i, l) {
    let o = r === 1 ? "tableHeader" : r === 2 ? "tableDelimiter" : "tableData", a = "tableContent";
    t[0] !== 0 && (l.end = Object.assign({}, rt(n.events, t[0])), e2.add(t[0], 0, [["exit", l, n]]));
    let u = rt(n.events, t[1]);
    if (l = { type: o, start: Object.assign({}, u), end: Object.assign({}, u) }, e2.add(t[1], 0, [["enter", l, n]]), t[2] !== 0) {
      let s32 = rt(n.events, t[2]), c = rt(n.events, t[3]), f = { type: a, start: Object.assign({}, s32), end: Object.assign({}, c) };
      if (e2.add(t[2], 0, [["enter", f, n]]), r !== 2) {
        let m = n.events[t[2]], p = n.events[t[3]];
        if (m[1].end = Object.assign({}, p[1].end), m[1].type = "chunkText", m[1].contentType = "text", t[3] > t[2] + 1) {
          let g = t[2] + 1, k = t[3] - t[2] - 1;
          e2.add(g, k, []);
        }
      }
      e2.add(t[3] + 1, 0, [["exit", f, n]]);
    }
    return i !== void 0 && (l.end = Object.assign({}, rt(n.events, i)), e2.add(i, 0, [["exit", l, n]]), l = void 0), l;
  }
  function Hl(e2, n, t, r, i) {
    let l = [], o = rt(n.events, t);
    i && (i.end = Object.assign({}, o), l.push(["exit", i, n])), r.end = Object.assign({}, o), l.push(["exit", r, n]), e2.add(t + 1, 0, l);
  }
  function rt(e2, n) {
    let t = e2[n], r = t[0] === "enter" ? "start" : "end";
    return t[1][r];
  }
  var Ff = { name: "tasklistCheck", tokenize: Df };
  function Hr() {
    return { text: { 91: Ff } };
  }
  function Df(e2, n, t) {
    let r = this;
    return i;
    function i(u) {
      return r.previous !== null || !r._gfmTasklistFirstContentOfListItem ? t(u) : (e2.enter("taskListCheck"), e2.enter("taskListCheckMarker"), e2.consume(u), e2.exit("taskListCheckMarker"), l);
    }
    function l(u) {
      return _(u) ? (e2.enter("taskListCheckValueUnchecked"), e2.consume(u), e2.exit("taskListCheckValueUnchecked"), o) : u === 88 || u === 120 ? (e2.enter("taskListCheckValueChecked"), e2.consume(u), e2.exit("taskListCheckValueChecked"), o) : t(u);
    }
    function o(u) {
      return u === 93 ? (e2.enter("taskListCheckMarker"), e2.consume(u), e2.exit("taskListCheckMarker"), e2.exit("taskListCheck"), a) : t(u);
    }
    function a(u) {
      return A(u) ? n(u) : P(u) ? e2.check({ tokenize: Rf }, n, t)(u) : t(u);
    }
  }
  function Rf(e2, n, t) {
    return v(e2, r, "whitespace");
    function r(i) {
      return i === null ? t(i) : n(i);
    }
  }
  function jl(e2) {
    return Ft([Mr(), _r(), Nr(e2), Br(), Hr()]);
  }
  var Mf = {};
  function jr(e2) {
    let n = this, t = e2 || Mf, r = n.data(), i = r.micromarkExtensions || (r.micromarkExtensions = []), l = r.fromMarkdownExtensions || (r.fromMarkdownExtensions = []), o = r.toMarkdownExtensions || (r.toMarkdownExtensions = []);
    i.push(jl(t)), l.push(Fr()), o.push(Dr(t));
  }
  var Of = /^\[!(NOTE|TIP|IMPORTANT|WARNING|CAUTION)\]/i;
  var _f = /^\[!(NOTE|TIP|IMPORTANT|WARNING|CAUTION)(\/.*)?\]/i;
  var Nf = ({ legacyTitle: e2 = false, tagName: n = "div", classNames: t = "" } = {}) => (r) => {
    Ee(r, "blockquote", (i, l, o) => {
      let a = "", u = "", s32 = true, c = i.children.map((f) => {
        if (s32 && f.type === "paragraph") {
          let m = f.children[0], p = m.type === "text" ? m.value : "", g = e2 ? _f : Of, k = p.match(g);
          if (k && (s32 = false, a = k[1].toLocaleLowerCase(), u = e2 && k[2] || a.toLocaleUpperCase(), p.includes(`
`) && (f.children[0] = { type: "text", value: p.replace(g, "").replace(/^\n+/, "") }), !p.includes(`
`))) {
            let C = [];
            f.children.forEach((x, T) => {
              T != 0 && (T == 1 && x.type === "break" || C.push(x));
            }), f.children = [...C];
          }
        }
        return f;
      });
      a && (i.data = { hName: n, hProperties: { className: ["markdown-alert", `markdown-alert-${a}`, ...t.split(" ").filter((f) => f.length)], dir: "auto" } }, c.unshift({ type: "paragraph", children: [Bf(a), { type: "text", value: u.replace(/^\//, "") }], data: { hProperties: { className: "markdown-alert-title", dir: "auto" } } })), i.children = [...c];
    });
  };
  function Bf(e2) {
    var t;
    let n = (t = Hf[e2]) != null ? t : "";
    return { type: "emphasis", data: { hName: "svg", hProperties: { className: ["octicon"], viewBox: "0 0 16 16", width: "16", height: "16", ariaHidden: "true" } }, children: [{ type: "emphasis", data: { hName: "path", hProperties: { d: n } }, children: [] }] };
  }
  var Hf = { note: "M0 8a8 8 0 1 1 16 0A8 8 0 0 1 0 8Zm8-6.5a6.5 6.5 0 1 0 0 13 6.5 6.5 0 0 0 0-13ZM6.5 7.75A.75.75 0 0 1 7.25 7h1a.75.75 0 0 1 .75.75v2.75h.25a.75.75 0 0 1 0 1.5h-2a.75.75 0 0 1 0-1.5h.25v-2h-.25a.75.75 0 0 1-.75-.75ZM8 6a1 1 0 1 1 0-2 1 1 0 0 1 0 2Z", tip: "M8 1.5c-2.363 0-4 1.69-4 3.75 0 .984.424 1.625.984 2.304l.214.253c.223.264.47.556.673.848.284.411.537.896.621 1.49a.75.75 0 0 1-1.484.211c-.04-.282-.163-.547-.37-.847a8.456 8.456 0 0 0-.542-.68c-.084-.1-.173-.205-.268-.32C3.201 7.75 2.5 6.766 2.5 5.25 2.5 2.31 4.863 0 8 0s5.5 2.31 5.5 5.25c0 1.516-.701 2.5-1.328 3.259-.095.115-.184.22-.268.319-.207.245-.383.453-.541.681-.208.3-.33.565-.37.847a.751.751 0 0 1-1.485-.212c.084-.593.337-1.078.621-1.489.203-.292.45-.584.673-.848.075-.088.147-.173.213-.253.561-.679.985-1.32.985-2.304 0-2.06-1.637-3.75-4-3.75ZM5.75 12h4.5a.75.75 0 0 1 0 1.5h-4.5a.75.75 0 0 1 0-1.5ZM6 15.25a.75.75 0 0 1 .75-.75h2.5a.75.75 0 0 1 0 1.5h-2.5a.75.75 0 0 1-.75-.75Z", important: "M0 1.75C0 .784.784 0 1.75 0h12.5C15.216 0 16 .784 16 1.75v9.5A1.75 1.75 0 0 1 14.25 13H8.06l-2.573 2.573A1.458 1.458 0 0 1 3 14.543V13H1.75A1.75 1.75 0 0 1 0 11.25Zm1.75-.25a.25.25 0 0 0-.25.25v9.5c0 .138.112.25.25.25h2a.75.75 0 0 1 .75.75v2.19l2.72-2.72a.749.749 0 0 1 .53-.22h6.5a.25.25 0 0 0 .25-.25v-9.5a.25.25 0 0 0-.25-.25Zm7 2.25v2.5a.75.75 0 0 1-1.5 0v-2.5a.75.75 0 0 1 1.5 0ZM9 9a1 1 0 1 1-2 0 1 1 0 0 1 2 0Z", warning: "M6.457 1.047c.659-1.234 2.427-1.234 3.086 0l6.082 11.378A1.75 1.75 0 0 1 14.082 15H1.918a1.75 1.75 0 0 1-1.543-2.575Zm1.763.707a.25.25 0 0 0-.44 0L1.698 13.132a.25.25 0 0 0 .22.368h12.164a.25.25 0 0 0 .22-.368Zm.53 3.996v2.5a.75.75 0 0 1-1.5 0v-2.5a.75.75 0 0 1 1.5 0ZM9 11a1 1 0 1 1-2 0 1 1 0 0 1 2 0Z", caution: "M4.47.22A.749.749 0 0 1 5 0h6c.199 0 .389.079.53.22l4.25 4.25c.141.14.22.331.22.53v6a.749.749 0 0 1-.22.53l-4.25 4.25A.749.749 0 0 1 11 16H5a.749.749 0 0 1-.53-.22L.22 11.53A.749.749 0 0 1 0 11V5c0-.199.079-.389.22-.53Zm.84 1.28L1.5 5.31v5.38l3.81 3.81h5.38l3.81-3.81V5.31L10.69 1.5ZM8 4a.75.75 0 0 1 .75.75v3.5a.75.75 0 0 1-1.5 0v-3.5A.75.75 0 0 1 8 4Zm0 8a1 1 0 1 1 0-2 1 1 0 0 1 0 2Z" };

  // project/components/spec/SpecText.jsx
  var s27 = { root: "spec-text-root", tok: "spec-text-tok", p: "spec-text-p", code: "spec-text-code", pre: "spec-text-pre", h1: "spec-text-h1", h2: "spec-text-h2", h3: "spec-text-h3", h4: "spec-text-h4", ul: "spec-text-ul", ol: "spec-text-ol", li: "spec-text-li", blockquote: "spec-text-blockquote", hr: "spec-text-hr", img: "spec-text-img", table: "spec-text-table", th: "spec-text-th", td: "spec-text-td" };
  var KEYWORDS = /(#[^\n]*)|("[^"]*"|'[^']*')|\b(def|return|for|in|if|else|elif|from|import|lambda|None|True|False|not|and|or|while|class|raise|with|as|try|except|finally|yield|assert|pass|break|continue|global|nonlocal|del|is)\b|\b(\d+(?:\.\d+)?)\b/g;
  function highlight(code) {
    const out = [];
    let i = 0, k = 0, m;
    KEYWORDS.lastIndex = 0;
    while (m = KEYWORDS.exec(code)) {
      if (m.index > i) out.push(code.slice(i, m.index));
      const [full, comment, str, kw] = m;
      const token = comment ? "comment" : str ? "string" : kw ? "keyword" : "number";
      out.push(/* @__PURE__ */ react_default.createElement("span", { key: k++, className: s27.tok, "data-tok": token }, full));
      i = m.index + full.length;
    }
    if (i < code.length) out.push(code.slice(i));
    return out;
  }
  function SpecText({ text = "", hideTitle = true, slug, className: rootClassName, style }) {
    const components = react_default.useMemo(() => ({
      h1: hideTitle ? () => null : ({ children }) => /* @__PURE__ */ react_default.createElement("h1", { className: s27.h1 }, children),
      h2: ({ children }) => /* @__PURE__ */ react_default.createElement("h2", { className: s27.h2 }, children),
      h3: ({ children }) => /* @__PURE__ */ react_default.createElement("h3", { className: s27.h3 }, children),
      h4: ({ children }) => /* @__PURE__ */ react_default.createElement("h4", { className: s27.h4 }, children),
      // className has to survive: the alert plugin marks its label `<p class="markdown-alert-title">`,
      // and dropping the class left the label unstyled with the raw octicon showing through.
      p: ({ children, className }) => /* @__PURE__ */ react_default.createElement("p", { className: className || s27.p }, children),
      ul: ({ children }) => /* @__PURE__ */ react_default.createElement("ul", { className: s27.ul }, children),
      ol: ({ children }) => /* @__PURE__ */ react_default.createElement("ol", { className: s27.ol }, children),
      li: ({ children }) => /* @__PURE__ */ react_default.createElement("li", { className: s27.li }, children),
      blockquote: ({ children }) => /* @__PURE__ */ react_default.createElement("blockquote", { className: s27.blockquote }, children),
      hr: () => /* @__PURE__ */ react_default.createElement("hr", { className: s27.hr }),
      a: ({ href, children }) => /* @__PURE__ */ react_default.createElement("a", { href, target: "_blank", rel: "noreferrer" }, children),
      img: ({ src, alt }) => /* @__PURE__ */ react_default.createElement("img", { src: src && slug && !/^\w+:/.test(src) ? `/api/task/${slug}/assets/${src}` : src, alt, className: s27.img }),
      table: ({ children }) => /* @__PURE__ */ react_default.createElement("table", { className: s27.table }, children),
      th: ({ children }) => /* @__PURE__ */ react_default.createElement("th", { className: s27.th }, children),
      td: ({ children }) => /* @__PURE__ */ react_default.createElement("td", { className: s27.td }, children),
      pre: ({ children }) => /* @__PURE__ */ react_default.createElement(react_default.Fragment, null, children),
      code: ({ className, children }) => {
        const source = String(children).replace(/\n$/, "");
        if (!className) {
          return /* @__PURE__ */ react_default.createElement("code", { className: s27.code }, source);
        }
        return /* @__PURE__ */ react_default.createElement("pre", { tabIndex: 0, className: s27.pre }, /python/.test(className) ? highlight(source) : source);
      }
    }), [hideTitle, slug]);
    return /* @__PURE__ */ react_default.createElement("div", { className: [s27.root, "spec", rootClassName].filter(Boolean).join(" "), style }, /* @__PURE__ */ react_default.createElement(Ko, { remarkPlugins: [jr, Nf], components }, text));
  }

  // project/components/status/StatusBadge.jsx
  var s28 = { root: "status-badge-root" };
  function StatusBadge({ status = "new", children, className, style }) {
    return /* @__PURE__ */ react_default.createElement("span", { "data-status": status, className: [s28.root, className].filter(Boolean).join(" "), style }, children || status);
  }

  // project/components/status/TagChip.jsx
  var s29 = { root: "tag-chip-root" };
  function TagChip({ label, active = false, onClick, small = false, className, style }) {
    const attrs = {
      "data-active": active ? "" : void 0,
      "data-small": small ? "" : void 0,
      className: [s29.root, className].filter(Boolean).join(" "),
      style
    };
    return onClick ? /* @__PURE__ */ react_default.createElement("button", { type: "button", "aria-pressed": active, onClick, "data-clickable": "", ...attrs }, label) : /* @__PURE__ */ react_default.createElement("span", { ...attrs }, label);
  }

  // project/components/status/DepLineage.jsx
  var css = { root: "dep-lineage-root", toolbar: "dep-lineage-toolbar", spacer: "dep-lineage-spacer", graphLink: "dep-lineage-graphLink", closeBtn: "dep-lineage-closeBtn", scroll: "dep-lineage-scroll", board: "dep-lineage-board", wires: "dep-lineage-wires", node: "dep-lineage-node", num: "dep-lineage-num", title: "dep-lineage-title", foot: "dep-lineage-foot", chip: "dep-lineage-chip", mini: "dep-lineage-mini", footText: "dep-lineage-footText", empty: "dep-lineage-empty", foldRow: "dep-lineage-foldRow", foldBtn: "dep-lineage-foldBtn", path: "dep-lineage-path", pathLabel: "dep-lineage-pathLabel", pathArrow: "dep-lineage-pathArrow", pathNum: "dep-lineage-pathNum", legend: "dep-lineage-legend", legendItem: "dep-lineage-legendItem" };
  var NODE_W = 216;
  var NODE_H = 96;
  var GAP = 16;
  var BIG_W = 272;
  var BIG_H = 118;
  var WIRE = 96;
  var BOARD_W = NODE_W * 2 + BIG_W + WIRE * 2;
  var FAN = 26;
  var EDGE = BIG_H - 28;
  var FOLD = 8;
  var numL = (n) => String(n).padStart(3, "0");
  var stackTop = (n, height) => (height - (n * (NODE_H + GAP) - GAP)) / 2;
  var nodeMid = (i, n, height) => stackTop(n, height) + i * (NODE_H + GAP) + NODE_H / 2;
  var wire = (x1, y1, x2, y2) => {
    const dx = (x2 - x1) / 2;
    return "M" + x1 + "," + y1 + " C" + (x1 + dx) + "," + y1 + " " + (x2 - dx) + "," + y2 + " " + x2 + "," + y2;
  };
  function Node({ node, x, y, w, tone, href, footer, onPrefetch, children }) {
    const As2 = href ? "a" : "div";
    const tag = node.tags && node.tags.length ? node.tags[0] : null;
    return /* @__PURE__ */ react_default.createElement(
      As2,
      {
        href,
        className: css.node,
        "data-tone": tone,
        "data-link": href ? "" : void 0,
        onMouseEnter: href && onPrefetch ? () => onPrefetch(node) : void 0,
        onFocus: href && onPrefetch ? () => onPrefetch(node) : void 0,
        style: { left: x, top: y, width: w, height: tone === "this" ? BIG_H : NODE_H }
      },
      /* @__PURE__ */ react_default.createElement("div", { className: css.num + " tabular" }, numL(node.topic)),
      /* @__PURE__ */ react_default.createElement("div", { title: node.title, className: css.title }, node.title),
      /* @__PURE__ */ react_default.createElement("div", { className: css.foot }, children, tag ? /* @__PURE__ */ react_default.createElement(TagChip, { label: tag, small: true, className: css.chip }) : null, footer && tone !== "this" ? /* @__PURE__ */ react_default.createElement("span", { className: css.footText }, footer) : null),
      footer && tone === "this" ? /* @__PURE__ */ react_default.createElement("div", { className: css.footText }, footer) : null
    );
  }
  function DepLineage({ task, requires = [], unlocks = [], hrefOf, onPrefetch, shortestPath, graphHref, onClose, className, style }) {
    const [unfolded, setUnfolded] = react_default.useState({});
    const fold = (list, key) => unfolded[key] || list.length <= FOLD ? list : list.slice(0, FOLD);
    const req = fold(requires, "requires");
    const unl = fold(unlocks, "unlocks");
    const rows = Math.max(req.length, unl.length, 1);
    const H = Math.max(rows * (NODE_H + GAP) - GAP, BIG_H) + 8;
    const midY = H / 2;
    const colX = [0, NODE_W + WIRE, NODE_W + WIRE + BIG_W + WIRE];
    const link = (r) => hrefOf ? hrefOf(r) : void 0;
    const fan = (i, n) => n < 2 ? midY : midY + (i - (n - 1) / 2) * Math.min(FAN, EDGE / (n - 1));
    const folded = (key, all, shown) => {
      if (all.length <= FOLD) return null;
      const open = !!unfolded[key];
      return /* @__PURE__ */ react_default.createElement("button", { key, type: "button", className: css.foldBtn, onClick: () => setUnfolded((u) => ({ ...u, [key]: !open })) }, open ? key + ": showing all " + all.length + " \u2014 show " + FOLD : key + ": showing " + shown.length + " of " + all.length + " \u2014 show all");
    };
    const empty = (text, x) => /* @__PURE__ */ react_default.createElement("span", { className: css.empty, style: { left: x, top: midY - 9, width: NODE_W } }, text);
    return /* @__PURE__ */ react_default.createElement("div", { className: [css.root, className].filter(Boolean).join(" "), style }, graphHref || onClose ? /* @__PURE__ */ react_default.createElement("div", { className: css.toolbar }, /* @__PURE__ */ react_default.createElement("span", { className: css.spacer }), graphHref ? /* @__PURE__ */ react_default.createElement("a", { href: graphHref, className: css.graphLink }, "whole graph", /* @__PURE__ */ react_default.createElement(Icon, { name: "ArrowRight", size: 14 })) : null, onClose ? /* @__PURE__ */ react_default.createElement("button", { type: "button", onClick: onClose, "aria-label": "Close lineage", className: css.closeBtn }, "Close") : null) : null, /* @__PURE__ */ react_default.createElement("div", { className: css.scroll }, /* @__PURE__ */ react_default.createElement("div", { key: task.topic, className: css.board + " m-stagger", style: { width: BOARD_W, height: H } }, /* @__PURE__ */ react_default.createElement("svg", { className: css.wires + " m-fade", width: BOARD_W, height: H, "aria-hidden": "true" }, /* @__PURE__ */ react_default.createElement("defs", null, /* @__PURE__ */ react_default.createElement("marker", { id: "dep-arrow", viewBox: "0 0 8 8", refX: "7", refY: "4", markerWidth: "7", markerHeight: "7", orient: "auto" }, /* @__PURE__ */ react_default.createElement("path", { d: "M0,0 L8,4 L0,8 z", fill: "var(--border-strong)" })), /* @__PURE__ */ react_default.createElement("marker", { id: "dep-arrow-blocked", viewBox: "0 0 8 8", refX: "7", refY: "4", markerWidth: "7", markerHeight: "7", orient: "auto" }, /* @__PURE__ */ react_default.createElement("path", { d: "M0,0 L8,4 L0,8 z", fill: "var(--text-faint)" }))), req.map((r, i) => {
      const blocked = r.state === "blocked";
      return /* @__PURE__ */ react_default.createElement(
        "path",
        {
          key: r.topic,
          fill: "none",
          strokeWidth: "1.5",
          stroke: blocked ? "var(--text-faint)" : "var(--border-strong)",
          strokeDasharray: blocked ? "5 4" : void 0,
          markerEnd: "url(#dep-arrow" + (blocked ? "-blocked" : "") + ")",
          d: wire(colX[0] + NODE_W, nodeMid(i, req.length, H), colX[1] - 6, fan(i, req.length))
        }
      );
    }), unl.map((u, i) => /* @__PURE__ */ react_default.createElement(
      "path",
      {
        key: u.topic,
        fill: "none",
        stroke: "var(--border-strong)",
        strokeWidth: "1.5",
        markerEnd: "url(#dep-arrow)",
        d: wire(colX[1] + BIG_W, fan(i, unl.length), colX[2] - 6, nodeMid(i, unl.length, H))
      }
    ))), req.length ? req.map((r, i) => /* @__PURE__ */ react_default.createElement(
      Node,
      {
        key: r.topic,
        node: r,
        x: colX[0],
        y: stackTop(req.length, H) + i * (NODE_H + GAP),
        w: NODE_W,
        tone: r.state,
        href: link(r),
        onPrefetch,
        footer: r.state === "passed" ? "passed" : "not passed yet"
      }
    )) : empty("nothing \u2014 this one stands on its own", colX[0]), /* @__PURE__ */ react_default.createElement(Node, { node: task, x: colX[1], y: (H - BIG_H) / 2, w: BIG_W, tone: "this", footer: task.aside }, task.strength ? /* @__PURE__ */ react_default.createElement(StatusBadge, { status: task.strength }) : null), unl.length ? unl.map((u, i) => /* @__PURE__ */ react_default.createElement(
      Node,
      {
        key: u.topic,
        node: u,
        x: colX[2],
        y: stackTop(unl.length, H) + i * (NODE_H + GAP),
        w: NODE_W,
        href: link(u),
        onPrefetch,
        footer: u.also && u.also.length ? "also needs " + u.also.map(numL).join(", ") : "the only block"
      }
    )) : empty("nothing waits on this one yet", colX[2]))), requires.length > FOLD || unlocks.length > FOLD ? /* @__PURE__ */ react_default.createElement("div", { className: css.foldRow }, folded("requires", requires, req), folded("unlocks", unlocks, unl)) : null, shortestPath && shortestPath.length ? /* @__PURE__ */ react_default.createElement("div", { className: css.path }, /* @__PURE__ */ react_default.createElement("span", { className: css.pathLabel }, "shortest way in"), shortestPath.map((p, i) => /* @__PURE__ */ react_default.createElement(react_default.Fragment, { key: p.topic }, i ? /* @__PURE__ */ react_default.createElement("span", { "aria-hidden": "true", className: css.pathArrow }, /* @__PURE__ */ react_default.createElement(Icon, { name: "ArrowRight", size: 12 })) : null, /* @__PURE__ */ react_default.createElement("code", { className: css.pathNum + " tabular" }, numL(p.topic))))) : null, /* @__PURE__ */ react_default.createElement("div", { className: css.legend }, /* @__PURE__ */ react_default.createElement("span", { className: css.legendItem }, /* @__PURE__ */ react_default.createElement("svg", { width: "22", height: "4", "aria-hidden": "true" }, /* @__PURE__ */ react_default.createElement("line", { x1: "0", y1: "2", x2: "22", y2: "2", stroke: "var(--border-strong)", strokeWidth: "1.5" })), "passed"), /* @__PURE__ */ react_default.createElement("span", { className: css.legendItem }, /* @__PURE__ */ react_default.createElement("svg", { width: "22", height: "4", "aria-hidden": "true" }, /* @__PURE__ */ react_default.createElement("line", { x1: "0", y1: "2", x2: "22", y2: "2", stroke: "var(--text-faint)", strokeWidth: "1.5", strokeDasharray: "5 4" })), "blocking"), /* @__PURE__ */ react_default.createElement("span", null, "left to right: what gates this task, the task, what it gates")));
  }

  // project/components/status/RequiresTag.jsx
  var css2 = { root: "requires-tag-root", mark: "requires-tag-mark", num: "requires-tag-num" };
  var MARK = { passed: "Checkmark", blocked: "Pending", neutral: "" };
  var numR = (n) => String(n).padStart(3, "0");
  function RequiresTag({ topic, title, state = "neutral", href, onClick, onPointerEnter, className, style }) {
    const interactive = !!(href || onClick);
    const why = state === "passed" ? "passed \u2014 you have this one" : state === "blocked" ? "not passed yet \u2014 this is what is blocking" : "";
    const body = /* @__PURE__ */ react_default.createElement(react_default.Fragment, null, MARK[state] ? /* @__PURE__ */ react_default.createElement("span", { "aria-hidden": "true", className: css2.mark }, /* @__PURE__ */ react_default.createElement(Icon, { name: MARK[state], size: 12 })) : null, /* @__PURE__ */ react_default.createElement("span", { className: css2.num + " tabular" }, numR(topic)), title ? /* @__PURE__ */ react_default.createElement("span", null, title) : null);
    const shared = {
      className: [css2.root, className].filter(Boolean).join(" "),
      style,
      "data-state": state,
      "data-interactive": interactive ? "" : void 0,
      title: [numR(topic) + (title ? " " + title : ""), why].filter(Boolean).join(" \u2014 "),
      onPointerEnter,
      onFocus: onPointerEnter
    };
    if (onClick && !href) return /* @__PURE__ */ react_default.createElement("button", { type: "button", onClick, ...shared }, body);
    return /* @__PURE__ */ react_default.createElement("a", { href: href || "#", onClick, ...shared }, body);
  }

  // project/components/status/RowFlags.jsx
  var s30 = { root: "row-flags-root", needsBtn: "row-flags-needsBtn" };
  var numFlag = (n) => "#" + String(n).padStart(3, "0");
  var asRef = (t) => typeof t === "object" ? t : { topic: t };
  function RowFlags({ needs = [], onNeedsClick, lapses = 0, lapseLimit = 0, className, style }) {
    const marks = [];
    if (needs.length) {
      const refs = needs.map(asRef);
      const label = "needs " + refs.map((r) => numFlag(r.topic)).join(" ");
      const why = "Not offered as a new pick until these are passed: " + refs.map((r) => numFlag(r.topic) + (r.title ? " " + r.title : "")).join(", ");
      marks.push(onNeedsClick ? /* @__PURE__ */ react_default.createElement(
        "button",
        {
          key: "needs",
          type: "button",
          title: why + " \u2014 opens the lineage",
          className: s30.needsBtn,
          onClick: (e2) => {
            e2.preventDefault();
            e2.stopPropagation();
            onNeedsClick(e2);
          }
        },
        label
      ) : /* @__PURE__ */ react_default.createElement("span", { key: "needs", title: why }, label));
    }
    if (lapseLimit && lapses >= lapseLimit) {
      marks.push(
        /* @__PURE__ */ react_default.createElement("span", { key: "lapses", title: "You have struggled with this " + lapses + " times; the hints or the prereqs may be the problem, not you." }, "struggled ", lapses, "\xD7")
      );
    }
    if (!marks.length) return null;
    return /* @__PURE__ */ react_default.createElement("span", { className: [s30.root, className].filter(Boolean).join(" "), style }, marks);
  }

  // project/components/status/Timer.jsx
  var s31 = { root: "timer-root", par: "timer-par", sr: "timer-sr" };
  function fmt(sec) {
    const m = Math.floor(sec / 60), r = sec % 60;
    return String(m).padStart(2, "0") + ":" + String(r).padStart(2, "0");
  }
  function Timer({ seconds = 0, parMinutes, paused = false, className, style }) {
    const par = (parMinutes || 0) * 60;
    const over = par && seconds >= par * 2 ? "double" : par && seconds >= par ? "par" : void 0;
    return /* @__PURE__ */ react_default.createElement("span", { "data-over": over, className: [s31.root, className].filter(Boolean).join(" "), style }, paused ? /* @__PURE__ */ react_default.createElement(react_default.Fragment, null, /* @__PURE__ */ react_default.createElement(Icon, { name: "Pause", size: 14 }), /* @__PURE__ */ react_default.createElement("span", { className: s31.sr }, "paused ")) : null, fmt(seconds), parMinutes ? /* @__PURE__ */ react_default.createElement("span", { className: s31.par }, " / ", fmt(par), " par") : null);
  }
  return __toCommonJS(entry_exports);
})();

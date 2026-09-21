import React from "react";
import s from "./TrackRail.module.css";

/** What the faint line beside the meter says. A track you have opened every task in
 *  stops reading as progress and says so, because "11 seen" beside "11" is a riddle. */
function standing(seen, total) {
  if (!total) return "no tasks yet";
  if (!seen) return "not started";
  if (seen >= total) return "all " + total + " seen";
  return seen + " seen";
}

const share = (seen, total) => (total > 0 ? Math.round((seen / total) * 100) : 0);
const markOf = (name) => (name || "?").trim().charAt(0).toUpperCase();

/** The tracks, as the row of pills the home screen opens with. Picking one sets `focus`,
 *  which gates NEW PICKS only — reviews keep coming from the whole catalogue. Say that in
 *  `readout`/`aside` rather than letting the control imply a mode it does not deliver. */
export function TrackRail({
  tracks = [], active = null, onPick, label = "Tracks",
  allLabel = "All tracks", allTotal = 0, allSeen = 0,
  readout, aside, className, style,
}) {
  const pills = [{ name: allLabel, key: null, total: allTotal, seen: allSeen }].concat(
    tracks.map((t) => ({ ...t, key: t.name }))
  );
  return (
    <div className={[s.root, className].filter(Boolean).join(" ")} style={style}>
      <div role="group" aria-label={label} className={s.pills}>
        <span className={s.label}>{label}</span>
        {pills.map((t) => (
          <button key={t.key === null ? "\u0000all" : t.key} type="button"
            aria-pressed={active === t.key} data-on={active === t.key ? "" : undefined}
            onClick={onPick ? () => onPick(t.key) : undefined} className={s.pill}>
            {t.icon
              ? <img src={t.icon} alt="" width="22" height="22" className={s.icon} data-image="" />
              : <span aria-hidden="true" className={s.icon}>{t.mark || markOf(t.name)}</span>}
            <span className={s.body}>
              <span className={s.head}>
                <span className={s.name}>{t.name}</span>
                <span className={s.count + " tabular"}>{t.total}</span>
              </span>
              <span className={s.head}>
                <span className={s.meter}>
                  <span className={s.fill} style={{ width: share(t.seen, t.total) + "%" }}></span>
                </span>
                <span className={s.seen}>{standing(t.seen, t.total)}</span>
              </span>
            </span>
          </button>
        ))}
      </div>
      {readout || aside ? (
        <div className={s.foot}>
          {readout ? <span className={s.readout}>{readout}</span> : null}
          {aside ? <span className={s.aside}>{aside}</span> : null}
        </div>
      ) : null}
    </div>
  );
}

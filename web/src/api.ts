// Every shape here mirrors a response of src/drillion/api.py.

export type Status = "new" | "due" | "open" | "done";
export type Grade = "quick" | "pass" | "struggled" | "abandoned";

/** The task's own facts, `public()`'s allowlist — the same block in a catalogue row and
 *  in `Task.meta`. */
export interface Meta {
  topic: number; title: string;
  difficulty: "easy" | "medium" | "hard"; tier: "core" | "advanced" | "packages"; track?: string;
  tags: string[]; source?: string;
}
/** A catalogue row: the task's facts plus this learner's card. */
export interface Row extends Meta {
  slug: string;
  status: Status; box: number; due: string; seen: number;
  /** Struggles on this card, never reset. At `stats.lapse_limit` the row says so. */
  lapses: number;
  /** Not offered today — `POST /api/task/{slug}/bury`. The schedule is untouched. */
  buried: boolean;
  /** the spec flattened and already lowercased for the search box */
  text: string;
  /** prereqs not yet passed, so the task is not offered as a new pick */
  blocked: string[];
}
/** GET /api/health — the version the header shows; never hardcode it here. */
export interface Health { version: string; tasks: number }
export interface Catalogue {
  focus: string | null; tags: string[]; tiers: string[]; tracks: string[];
  today: {
    /** the day's reviews, most overdue first — CAPPED. `due_total` is the real backlog. */
    review: string[];
    /** held empty while `behind`: no new material until the backlog is back under the cap */
    new: string[];
    recent: string[]; done_today: number;
    due_total: number; behind: boolean;
    /** the one reason `new` is empty, named by `queue()`; null when there is something to offer */
    no_new: { why: "behind" | "focus" | "done" | "buried" } | { why: "cap"; ready: number }
      | { why: "prereqs"; nearest: string } | null;
  };
  /** `due` is the whole backlog, not `review.length` — the two differ once `behind`.
   *  `stuck` is the tag with the most flagged tasks, or null when none stands out. */
  stats: { boxes: number[]; ladder: number[]; due: number; seen: number; total: number; practised: number; window: number; lapse_limit: number; stuck: { tag: string; flagged: number } | null };
  tasks: Row[];
}
export interface Progress {
  boxes: number[]; ladder: number[]; due: number; seen: number; total: number; practised: number; window: number;
  today: string;
  /** cards due per day for the next 14, [0] today with everything overdue folded in */
  forecast: number[];
  /** reviews served a day — the line the forecast draws */
  cap: number;
  /** passes per calendar day, all history */
  days: Record<string, number>;
  per_tag: Record<string, { seen: number; total: number; boxes: number[]; lapses: number; due7: number }>;
  log: { date: string; slug: string; grade: Grade; attempts: number; secs: number; new: boolean }[];
}
/** One end of a prereq edge, already resolved server-side: the browser never maps a slug
 *  to a title itself. */
export interface DepRef { slug: string; topic: number; title: string; tags: string[] }
export interface Task {
  slug: string; meta: Meta;
  spec_md: string; code: string; etag: string; has_given: boolean;
  status: Status; buried: boolean;
  /** passes on this card, ever — the lineage screen's `seen N×` line */
  seen: number;
  /** this card's rung, 0 when it is not on the ladder — the lineage draws it */
  box: number;
  /** every prereq, not just the unpassed ones. `passed` is box 1, the bar `blocked` uses —
   *  never re-derive it from `status`, which says `done` on a card that has lapsed. */
  requires: (DepRef & { state: "passed" | "blocked"; box: number })[];
  /** the direct reverse edge, one hop: what passing this opens up. `also` is what else
   *  still gates that task — passing this one is not always enough. */
  unlocks: (DepRef & { also: number[] })[];
  attempt: { attempts: number; active: number; seed: number; solution_shown: boolean } | null;
  /** at `lapse_limit` the task is flagged as one that keeps beating you */
  lapses: number; lapse_limit: number;
  /** the scheduler's return intervals, one per box */
  ladder: number[];
  /** the server owns the half-hour threshold; the page renders the offer */
  nudge: boolean;
  /** the reference answer once the server opens it; null until passed, and again while due back */
  reference: string | null;
  hints: { total: number; shown: string[]; next_in: number | null };
  solution: { unlocked: boolean; need_attempts: number; need_secs: number };
  /** `code` is the answer you wrote that day, null while the server keeps it closed */
  archive: { date: string; grade: Grade; code: string | null }[];
  /** The learner's one note on the task, `""` when there is none — `PUT /api/task/{slug}/note`. */
  note: string;
}
interface RunBase { attempts: number; headline: string[]; output: string; etag: string }
/** The grade and everything it decided exist iff `passed && graded`. A plain Run is
 *  `graded: false`: it costs no attempt and moves no card, however green it came back.
 *  `stepped` is the scheduler's answer to whether the card moved — never re-derive it
 *  from `box`. */
export type RunResult =
  | (RunBase & { passed: false; graded: boolean })
  | (RunBase & { passed: true; graded: false })
  | (RunBase & {
      passed: true; graded: true;
      grade: Grade; box: number; stepped: boolean; from_box: number;
      due_in: number; code: string; reason: string; reference: string; lapses: number;
      next: string | null;
    });

/** Every non-2xx body api.py can send, in one all-optional shape. */
export interface ApiErrorBody {
  error?: string; line?: number | null;
  etag?: string; code?: string;
  wait_secs?: number;
  need_attempts?: number; need_secs?: number;
}

export class ApiError extends Error {
  constructor(readonly status: number, readonly detail: ApiErrorBody | null) {
    super(detail?.error || `HTTP ${status}`);
  }
}

/** The one fetch wrapper. Non-2xx raises ApiError so callers can branch on 409/423/400. */
export async function api<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch("/api" + path, {
    ...init,
    headers: init?.body ? { "content-type": "application/json" } : undefined,
  });
  const body = await res.json().catch(() => null);
  if (!res.ok) throw new ApiError(res.status, body?.detail ?? body);
  return body as T;
}

export const post = <T,>(path: string, body?: unknown) =>
  api<T>(path, { method: "POST", body: body === undefined ? undefined : JSON.stringify(body) });

// The JSON API in src/drillion/api.py. Every shape here is that file's response, nothing more.

export type Status = "new" | "due" | "open" | "done";   // api.py _status(): no fifth branch
export type Grade = "quick" | "pass" | "struggled" | "abandoned";

export interface Row {
  slug: string; topic: number; title: string;
  difficulty: "easy" | "medium" | "hard"; tier: "core" | "advanced" | "packages"; track?: string;
  tags: string[]; prereqs?: number[]; source?: string;
  status: Status; box: number; due: string; seen: number;
  /** Struggles on this card, never reset. At `stats.lapse_limit` the row says so. */
  lapses: number;
  /** Put aside for today only — `POST /api/task/{slug}/bury`. Never a fifth `status`: the
   *  card is still exactly what it was (`due`, usually), it is just not offered today, and
   *  the bury lapses on its own tomorrow. Nothing about the schedule moves either way. */
  buried: boolean;
  /** Catalogue rows only: the spec's Why / You get / You return / Rules, flattened and
   *  already lowercased for the search box. `GET /api/task` sends `spec_md` instead. */
  text?: string;
}
/** GET /api/health — the version the header shows; never hardcode it here. */
export interface Health { status: string; version: string; tasks: number; root: string }
export interface Catalogue {
  focus: string | null; tags: string[]; tiers: string[]; tracks: string[];
  today: {
    /** the day's reviews, most overdue first — CAPPED. `due_total` is the real backlog. */
    review: string[];
    /** held empty while `behind`: no new material until the backlog is back under the cap */
    new: string[];
    recent: string[]; done_today: number;
    due_total: number; behind: boolean;
  };
  /** `due` is the whole backlog, not `review.length` — the two differ once `behind`. */
  stats: { boxes: number[]; due: number; seen: number; total: number; practised: number; window: number; lapse_limit: number };
  tasks: Row[];
}
export interface Progress {
  boxes: number[]; due: number; seen: number; total: number; practised: number; window: number;
  per_tag: Record<string, { seen: number; total: number }>;
  log: { date: string; slug: string; grade: Grade; attempts: number; secs: number; new: boolean }[];
}
export interface Task {
  slug: string; meta: Omit<Row, "slug" | "status" | "box" | "due" | "seen" | "lapses" | "buried">;
  spec_md: string; code: string; etag: string; has_given: boolean;
  marker_line: number; status: Status; buried: boolean;
  attempt: { attempts: number; hints: number; active: number; seed: number; solution_shown: boolean } | null;
  /** the task has cost this many lapses; at `lapse_limit` it is flagged as one that keeps
   *  beating you — a message about the task, never a punishment on the card */
  lapses: number; lapse_limit: number;
  /** half an hour of active reading with nothing run and no hint taken. The server owns
   *  the threshold; the page renders the offer. */
  nudge: boolean;
  /** the reference answer, once the server's gate has opened it: `null` until the task has
   *  been passed, and `null` again while that card is due back. Never the page's call. */
  reference: string | null;
  hints: { total: number; shown: string[]; next_in: number | null };
  solution: { unlocked: boolean; need_attempts: number; need_secs: number };
  archive: { date: string; grade: Grade; code?: string }[];
}
export interface RunResult {
  passed: boolean; attempts: number; headline: string[]; output: string; etag: string;
  /** `stepped` is the scheduler's answer to "did the card move?" — false for a `quick`
   *  that clamps at the top box, and for a first sighting that stayed in box 0. Never
   *  re-derive it from `box`. `from_box` is where the card stood before the grade landed:
   *  a `struggled` pass steps it *down*, so a move has a direction. */
  grade?: Grade; box?: number; stepped?: boolean; from_box?: number; due_in?: number; code?: string;
  /** why `grade` landed where it did — the cause, never par's number. See issue #13. */
  reason?: string; reference?: string; lapses?: number;
}

export class ApiError extends Error {
  constructor(readonly status: number, readonly detail: any) {
    super(typeof detail === "string" ? detail : detail?.error || `HTTP ${status}`);
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

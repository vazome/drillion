// The JSON API in src/drillion/api.py. Every shape here is that file's response, nothing more.

export type Status = "new" | "due" | "open" | "done";   // api.py _status(): no fifth branch
export type Grade = "quick" | "pass" | "struggled" | "abandoned";

export interface Row {
  slug: string; topic: number; title: string;
  difficulty: "easy" | "medium" | "hard"; tier: "core" | "advanced" | "packages"; track?: string;
  tags: string[]; prereqs?: number[]; practices?: number[]; source?: string;
  status: Status; box: number; due: string; seen: number;
}
export interface Catalogue {
  focus: string | null; tags: string[]; tiers: string[]; tracks: string[];
  today: { review: string[]; new: string[]; done_today: number };
  stats: { boxes: number[]; due: number; seen: number; total: number; practised: number; window: number };
  tasks: Row[];
}
export interface Progress {
  boxes: number[]; due: number; seen: number; total: number; practised: number; window: number;
  per_tag: Record<string, { seen: number; total: number }>;
  log: { date: string; slug: string; grade: Grade; attempts: number; secs: number; new: boolean }[];
}
export interface Task {
  slug: string; meta: Omit<Row, "slug" | "status" | "box" | "due" | "seen">;
  spec_md: string; code: string; etag: string; has_given: boolean;
  marker_line: number; status: Status;
  attempt: { attempts: number; hints: number; active: number; seed: number; solution_shown: boolean } | null;
  hints: { total: number; shown: string[]; next_in: number | null };
  solution: { unlocked: boolean; need_attempts: number; need_secs: number };
  archive: { date: string; grade: Grade; code?: string }[];
}
export interface RunResult {
  passed: boolean; attempts: number; headline: string[]; output: string; etag: string;
  /** `stepped` is the scheduler's answer to "did the card move?" — false for a
   *  `struggled` pass, for a `quick` that clamps at the top box, and for a first
   *  sighting that stayed in box 0. Never re-derive it from `box`. */
  grade?: Grade; box?: number; stepped?: boolean; due_in?: number; code?: string;
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

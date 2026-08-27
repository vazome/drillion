import { useCallback, useEffect, useRef, useState } from "react";
import { ApiError, api, post, type Task as TaskData } from "./api";

const AUTOSAVE_MS = 800;
const draftKey = (slug: string) => `drillion-draft-${slug}`;

/** The optimistic lock's 409, or null for any other failure. */
const conflictOf = ({ status, detail }: ApiError) =>
  status === 409 && detail?.etag !== undefined && detail.code !== undefined
    ? { etag: detail.etag, code: detail.code }
    : null;

/** The values the async chain reads live; state alone would capture a stale closure. */
type Live = { code: string; saved: string; note: string; noteSaved: string; etag: string; attempt: boolean };

const EMPTY: Live = { code: "", saved: "", note: "", noteSaved: "", etag: "", attempt: false };

/** The task page's draft: the code and the note against what the server last confirmed of
 *  them, the optimistic lock, both debounced saves, the attempt the server wants open before
 *  it takes an edit, and the local copy that outlives a save the server never got.
 *  `onPayload`/`onError` must be stable or `ensureOpen`/`reset` rebuild every render. */
export function useDraft(
  slug: string,
  onPayload: (p: TaskData) => void,
  onError: (message: string, at?: "editor" | "note") => void,
) {
  const [buf, setBuf] = useState<Live>(EMPTY);
  const [syntaxBad, setSyntaxBad] = useState(false);
  const [conflict, setConflict] = useState<{ etag: string; code: string } | null>(null);
  const [offer, setOffer] = useState<string | null>(null);

  const live = useRef<Live>({ ...EMPTY });
  const timer = useRef<number | undefined>(undefined);
  const noteTimer = useRef<number | undefined>(undefined);
  const inflight = useRef<Promise<void> | null>(null);
  const opening = useRef<Promise<void> | null>(null);
  const url = `/task/${encodeURIComponent(slug)}`;

  const commit = useCallback((next: Partial<Live>) => {
    setBuf({ ...Object.assign(live.current, next) });
  }, []);

  /** The server's note, unless one is part way through being typed here. */
  const serverNote = (p: TaskData): Partial<Live> =>
    live.current.note === live.current.noteSaved ? { note: p.note, noteSaved: p.note } : {};

  /** A later payload: its lock always, its code only over a buffer nobody has typed into. */
  const adopt = useCallback((p: TaskData) => {
    live.current.attempt = !!p.attempt;
    commit(live.current.code === live.current.saved
      ? { code: p.code, saved: p.code, etag: p.etag, ...serverNote(p) }
      : { saved: p.code, etag: p.etag, ...serverNote(p) });
    onPayload(p);
  }, [commit, onPayload]);

  /** The first payload, or the stub an abandon puts back: the buffer is the file's again,
   *  and a stored draft about that same file is offered over it. */
  const reset = useCallback((p: TaskData) => {
    live.current.attempt = !!p.attempt;
    commit({ code: p.code, saved: p.code, etag: p.etag, ...serverNote(p) });
    try {
      const stored = JSON.parse(localStorage.getItem(draftKey(slug)) || "null");
      setOffer(stored && stored.etag === p.etag && stored.code !== p.code ? stored.code : null);
    } catch { setOffer(null); }
    onPayload(p);
  }, [slug, commit, onPayload]);

  /** An attempt must exist before the server will accept an edit, a run or a hint.
   * Concurrent callers share one POST — the debounced save and Run can arrive together. */
  const ensureOpen = useCallback(async () => {
    if (live.current.attempt) return;
    opening.current ??= post<TaskData>(`${url}/open`)
      .then(adopt)
      .finally(() => { opening.current = null; });
    await opening.current;
  }, [url, adopt]);

  /** A failure the draft owns: a 409 becomes the conflict banner, a 400 the amber dot. */
  const absorb = (e: unknown) => {
    if (!(e instanceof ApiError)) return false;
    if (e.status === 400) { setSyntaxBad(true); return true; }    // silent: an amber dot, no banner
    const clash = conflictOf(e);
    if (clash) { setConflict(clash); return true; }
    return false;
  };

  const save = async (sent: string, force = false) => {
    if (!live.current.etag || (!force && live.current.code === live.current.saved)) return;
    try {
      await ensureOpen();                  // typing is starting work; the PUT 409s without this
      const r = await api<{ etag: string }>(url, {
        method: "PUT", body: JSON.stringify({ code: sent, etag: live.current.etag }),
      });
      commit({ saved: sent, etag: r.etag });
      setSyntaxBad(false);
    } catch (e) {
      // never rethrow: `edit()` fires this unawaited and `run()` awaits it
      if (absorb(e)) return;
      onError(e instanceof ApiError ? e.message : `could not save — ${(e as Error).message}`);
    }
  };

  /** The note's save: debounce, then one PUT. No etag and no attempt to open — one note,
   * last write wins. */
  const saveNote = useCallback(async (text: string) => {
    try {
      await api(`${url}/note`, { method: "PUT", body: JSON.stringify({ text }) });
      if (live.current.note === text) commit({ noteSaved: text });
    } catch (e) {
      onError(`note not saved — ${(e as Error).message}`, "note");
    }
  }, [url, commit, onError]);

  const edit = (next: string) => {
    commit({ code: next });
    localStorage.setItem(draftKey(slug), JSON.stringify({ code: next, etag: live.current.etag }));
    clearTimeout(timer.current);
    timer.current = setTimeout(() => { inflight.current = save(next); }, AUTOSAVE_MS);
  };

  const editNote = (next: string) => {
    commit({ note: next });
    clearTimeout(noteTimer.current);
    noteTimer.current = setTimeout(() => saveNote(next), AUTOSAVE_MS);
  };

  const discard = () => {
    localStorage.removeItem(draftKey(slug));
    setOffer(null);
  };

  useEffect(() => () => {
    clearTimeout(timer.current); clearTimeout(noteTimer.current);
    // leaving mid-debounce must not eat it
    if (live.current.note !== live.current.noteSaved) saveNote(live.current.note);
  }, [slug, saveNote]);

  return {
    code: buf.code, dirty: buf.code !== buf.saved, syntaxBad, conflict, offer,
    note: buf.note, noteDirty: buf.note !== buf.noteSaved,
    adopt, reset, edit, editNote, ensureOpen, discard, absorb,
    /** A run came back: its etag, and on a pass its archived code over the local draft. */
    landed: (etag: string, code?: string) => {
      setSyntaxBad(false);
      if (code === undefined) commit({ saved: live.current.code, etag });
      else { discard(); commit({ code, saved: code, etag }); }
    },
    restore: () => { if (offer !== null) edit(offer); setOffer(null); },
    takeDisk: () => {
      if (!conflict) return;
      commit({ code: conflict.code, saved: conflict.code, etag: conflict.etag });
      discard();
      setConflict(null);
    },
    keepMine: () => {
      if (!conflict) return;
      commit({ etag: conflict.etag });      // adopt the disk version's etag, then overwrite with ours
      setConflict(null);
      inflight.current = save(live.current.code, true);
    },
    /** The save already on the wire, whose etag the caller rides. */
    pending: () => inflight.current,
    /** The same, and cancels a save still in the debounce. */
    settle: () => { clearTimeout(timer.current); return inflight.current; },
    current: () => ({ code: live.current.code, etag: live.current.etag }),
  };
}

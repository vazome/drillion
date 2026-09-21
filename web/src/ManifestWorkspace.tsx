import { FailedCase, ResultBanner } from "./ds/index.js";
import type { Diagnostic } from "./api";
import s from "./ManifestWorkspace.module.css";

/** What the grader said, field by field. The server sends diagnostics, so nothing here
 *  reads a sentence back into data: `path` is where in the YAML, `message` is what is
 *  wrong with it, and a diagnostic with no path is about the document as a whole. */
export function ManifestFailure({ diagnostics }: { diagnostics: Diagnostic[] }) {
  const fields = diagnostics.filter((d) => d.path);
  const general = diagnostics.filter((d) => !d.path);
  return (
    <div>
      <ResultBanner state="failed" headline={fields.length ? "Check these manifest fields" : "Your manifest needs another look"} />
      {fields.length ? <p className={s.aside}>Paths start at the top of your YAML file.</p> : null}
      {general.map((d, i) => <p key={i} className={s.aside}>{d.message}</p>)}
      {fields.map((d, i) => <div key={i}>
        <FailedCase fields={[{ label: d.path!, value: d.message }]} />
        {d.message === "expected integer, but got string" ? <p className={s.aside}>Use a whole number without quotes, for example <code>2</code> instead of <code>"2"</code>.</p> : null}
      </div>)}
      <p className={s.aside}>Only reported problems are shown. Run again after editing to check the updated document.</p>
    </div>
  );
}

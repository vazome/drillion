import { useId, useState, type ReactNode } from "react";
import { FailedCase, FileTabs, ResultBanner } from "./ds/index.js";
import type { ChartFile, Diagnostic, Meta } from "./api";
import s from "./ManifestWorkspace.module.css";

/** What the grader said, field by field. The server sends diagnostics, so nothing here
 *  reads a sentence back into data: `path` is where in the YAML, `message` is what is
 *  wrong with it, and a diagnostic with no path is about the document as a whole. On a Helm
 *  task the paths are into what Helm rendered, not into the file the learner wrote. */
const LOOK: Partial<Record<Meta["kind"], string>> = { helm: "Your chart needs another look", docker: "Your Dockerfile needs another look" };

export function ManifestFailure({ diagnostics, kind }: { diagnostics: Diagnostic[]; kind: Meta["kind"] }) {
  const fields = diagnostics.filter((d) => d.path);
  const general = diagnostics.filter((d) => !d.path);
  const helm = kind === "helm";
  return (
    <div>
      <ResultBanner state="failed" headline={fields.length ? "Check these manifest fields" : LOOK[kind] ?? "Your manifest needs another look"} />
      {fields.length ? <p className={s.aside}>kubeconform · Paths start at the top of {helm ? "the rendered manifest, under Rendered below" : "your YAML file"}.</p> : null}
      {general.map((d, i) => <p key={i} className={s.aside + " " + s.said}>{d.message}</p>)}
      {fields.map((d, i) => <div key={i}>
        <FailedCase fields={[{ label: d.path!, value: d.message }]} />
        {d.message.endsWith("expected integer, but got string") ? <p className={s.aside}>Use a whole number without quotes, for example <code>2</code> instead of <code>"2"</code>.</p> : null}
      </div>)}
      <p className={s.aside}>Only reported problems are shown. Run again after editing to check the updated document.</p>
    </div>
  );
}

/** A Helm task's chart, or a Dockerfile's build context, around the editor: the learner's
 *  file first, the rest read-only.
 *  A chart file is laid over the editor rather than swapped in, so the editor keeps its
 *  cursor, undo and layout, and it is `inert` meanwhile so focus cannot reach under. */
export function ChartFiles({ edits, chart, diagnostics, context = false, children }: {
  edits: string; chart: ChartFile[]; diagnostics: Diagnostic[]; context?: boolean; children: ReactNode;
}) {
  const [open, setOpen] = useState(edits);
  const panel = useId();
  const marked = new Set(diagnostics.map((d) => d.file));
  const files = [
    { path: edits, readOnly: false, marked: marked.has(edits) },
    ...chart.map((f) => ({ path: f.path, readOnly: true, marked: marked.has(f.path) })),
  ];
  const shown = chart.find((f) => f.path === open);
  return (
    <div className={s.chart}>
      <FileTabs files={files} active={open} onSelect={setOpen} panelId={panel}
        {...(context ? { label: "Build context files", partOf: "the build context" } : {})} />
      <div id={panel} role="tabpanel" aria-label={open} className={s.panel}>
        <div inert={!!shown} className={s.fill}>{children}</div>
        {shown ? <pre tabIndex={0} className={s.chartFile}>{shown.text}</pre> : null}
      </div>
    </div>
  );
}

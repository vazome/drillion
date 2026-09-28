import { useEffect, useId, useState, type ReactNode } from "react";
import { FailedCase, FileTabs } from "./ds/index.js";
import type { ChartFile, Diagnostic, Meta } from "./api";
import s from "./ManifestWorkspace.module.css";

/** What the grader said, field by field. The server sends diagnostics, so nothing here
 *  reads a sentence back into data: `path` is where in the YAML, `message` is what is
 *  wrong with it, and a diagnostic with no path is about the document as a whole. On a Helm
 *  task the paths are into what Helm rendered, not into the file the learner wrote. */
const LOOK: Partial<Record<Meta["kind"], string>> = { helm: "Your chart needs another look", docker: "Your Dockerfile needs another look", sql: "Your SQL needs another look", git: "Your repository needs another look", workflow: "Your workflow needs another look" };

export function ManifestFailure({ diagnostics, kind }: { diagnostics: Diagnostic[]; kind: Meta["kind"] }) {
  const fields = diagnostics.filter((d) => d.path);
  const general = diagnostics.filter((d) => !d.path);
  const helm = kind === "helm";
  return (
    <div>
      <p className={s.what}>{fields.length ? "Check these manifest fields" : LOOK[kind] ?? "Your manifest needs another look"}</p>
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

/** One of the files around the editor, coloured the way the editor colours; plain until the
 *  colouring comes back, which is a frame or two. */
function ReadOnly({ path, text }: { path: string; text: string }) {
  const [html, setHtml] = useState<string | null>(null);
  useEffect(() => {
    let live = true;
    // loaded here, not at the top: the editor is already on the page by now, and a render
    // with no browser (the component tests) never gets as far as Monaco
    import("./Editor").then((m) => m.colorize(text, path)).then((h) => { if (live) setHtml(h); }, () => {});
    return () => { live = false; };
  }, [path, text]);
  return html === null
    ? <pre tabIndex={0} className={s.chartFile}>{text}</pre>
    : <pre tabIndex={0} className={s.chartFile} dangerouslySetInnerHTML={{ __html: html }} />;
}

/** A Helm task's chart, a Dockerfile's build context or a SQL task's database, around the
 *  editor: the learner's file first, the rest read-only.
 *  A chart file is laid over the editor rather than swapped in, so the editor keeps its
 *  cursor, undo and layout, and it is `inert` meanwhile so focus cannot reach under. */
export function ChartFiles({ edits, chart, diagnostics, labels, children }: {
  edits: string; chart: ChartFile[]; diagnostics: Diagnostic[]; labels?: { label: string; partOf: string }; children: ReactNode;
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
        {...(labels ?? {})} />
      <div id={panel} role="tabpanel" aria-label={open} className={s.panel}>
        <div inert={!!shown} className={s.fill}>{children}</div>
        {shown ? <ReadOnly key={shown.path} path={shown.path} text={shown.text} /> : null}
      </div>
    </div>
  );
}

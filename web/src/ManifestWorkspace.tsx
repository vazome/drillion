import { Button, Collapsible, FailedCase, ResultBanner, SpecText } from "./ds/index.js";
import { manifestFeedback } from "./manifestFeedback";
import s from "./ManifestWorkspace.module.css";

export const YAML_OUTLINE = `# Fill in the resource requested in this sitting.
apiVersion: # API group/version
kind: # Resource type
metadata:
  name: # Requested name
spec: {}
# Replace {} with the resource's configuration.
# Indent nested fields with spaces, not tabs.
`;

/** The authored specification stays intact. The brief remains server-rendered so
 * opening a new sitting never leaves a name or count from the previous one. */
export function ManifestBrief({ text, slug, started }: { text: string; slug: string; started: boolean }) {
  return (
    <div className={s.brief}>
      <div className={s.intro}>
        <span className={s.file}>task.yaml</span>
        <span>{started ? "Requirements for this sitting" : "Read the brief to get started"}</span>
      </div>
      <SpecText text={text} slug={slug} hideTitle />
      <p className={s.aside}>Write one YAML document. Run checks your draft without using an attempt. Submit when you are ready to be graded.</p>
    </div>
  );
}

export function ManifestHelp({ code, onChange, disabled }: { code: string; onChange: (code: string) => void; disabled: boolean }) {
  return (
    <div className={s.help}>
      <div className={s.filebar}><span className={s.file}>task.yaml</span><span>YAML · whole document</span></div>
      <Collapsible label="Need a starting point?" mono={false} defaultOpen={!code.trim()}>
        <p className={s.explanation}>Start with the resource envelope, then fill in the fields from the brief. This outline is incomplete and will not pass a check.</p>
        <pre className={s.outline} tabIndex={0}>{YAML_OUTLINE}</pre>
        <div className={s.actions}>
          <Button variant="secondary" disabled={disabled || !!code.trim()} onClick={() => onChange(YAML_OUTLINE)}>Insert outline</Button>
          {code === YAML_OUTLINE ? <Button variant="quiet" disabled={disabled} onClick={() => onChange("")}>Remove outline</Button> : null}
          {code.trim() && code !== YAML_OUTLINE ? <span>Your draft is kept. Use the example as a guide.</span> : null}
        </div>
      </Collapsible>
    </div>
  );
}

export function ManifestFailure({ headline }: { headline: string }) {
  const feedback = manifestFeedback(headline);
  return (
    <div>
      <ResultBanner state="failed" headline={feedback.title} />
      <p className={s.aside}>{feedback.fields.length ? "kubeconform · " : null}{feedback.message}</p>
      {feedback.fields.map((field, i) => <div key={i}>
        <FailedCase fields={[{ label: field.path, value: field.message }]} />
        {field.message === "expected integer, but got string" ? <p className={s.aside}>Use a whole number without quotes, for example <code>2</code> instead of <code>"2"</code>.</p> : null}
      </div>)}
      <p className={s.aside}>Only reported problems are shown. Run again after editing to check the updated document.</p>
    </div>
  );
}

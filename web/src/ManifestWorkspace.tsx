import { FailedCase, ResultBanner } from "./ds/index.js";
import { manifestFeedback } from "./manifestFeedback";
import s from "./ManifestWorkspace.module.css";

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

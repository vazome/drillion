/** The API currently exposes pytest headline lines, not structured diagnostics.
 * Only recognise explicit messages; unfamiliar failures keep their raw report. */
export function manifestFeedback(headline: string) {
  const lines = headline.split("\n").map((line) => line.replace(/^E\s+/, "").trim());
  const fields = lines.flatMap((line) => {
    const match = /^(?:AssertionError:\s*)?(\/[^:]*):\s*(.+)$/.exec(line);
    return match ? [{ path: match[1], message: match[2] }] : [];
  });
  if (fields.length) return { title: "Check these manifest fields", fields, message: "Paths start at the top of your YAML file." };
  const assertion = lines.find((line) => line.startsWith("AssertionError:"))?.slice(15).trim();
  if (assertion) {
    const requirement: Record<string, string> = {
      name: "Check metadata.name against the name requested for this sitting.",
      replicas: "Check spec.replicas against the replica count requested for this sitting.",
      kind: "Check kind against the resource requested for this sitting.",
    };
    return { title: "Your manifest needs another look", fields: [], message: requirement[assertion] ?? assertion };
  }
  if (lines.some((line) => /^(?:yaml\.)?(?:parser\.ParserError|scanner\.ScannerError)/.test(line))) {
    return { title: "YAML could not be read", fields: [], message: "Check indentation, colons and quotes. The validator details below include the reported location." };
  }
  return { title: "The check did not complete successfully", fields: [], message: "Open the validator details for the reported reason. This may be a manifest problem or a checker problem." };
}

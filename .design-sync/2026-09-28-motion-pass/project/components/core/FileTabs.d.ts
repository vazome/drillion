/** One file of a task (a Helm chart, a Docker build context). Exactly one has `readOnly: false` — the learner's — and it
 *  comes first; the rest are read and never written. */
export interface FileTabsFile {
  /** as the chart has it: "values.yaml", "templates/deployment.yaml" */
  path: string;
  readOnly: boolean;
  /** the last run reported a problem in this file */
  marked?: boolean;
}
/** The files of a task above the editor (a Helm chart, a Docker build context): switches what the editor shows and nothing
 *  else. No tree, no add/close/rename/reorder, no file-type icons. 2–6 files; past the
 *  strip's width it scrolls inside itself. */
export interface FileTabsProps {
  files?: FileTabsFile[];
  /** the path the editor is showing */
  active?: string;
  onSelect?: (path: string) => void;
  /** the tablist's accessible name */
  label?: string;
  /** what the read-only files belong to, said in each locked tab's accessible name:
   *  "the chart" (default) for Helm, "the build context" for a Dockerfile task */
  partOf?: string;
  /** id of the element wrapping the editor, which carries role="tabpanel" */
  panelId?: string;
  className?: string;
  style?: React.CSSProperties;
}
export declare function FileTabs(props: FileTabsProps): JSX.Element;

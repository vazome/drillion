import { useMemo } from "react";
import CodeMirror from "@uiw/react-codemirror";
import { python } from "@codemirror/lang-python";
import { indentUnit } from "@codemirror/language";
import { EditorView, keymap } from "@codemirror/view";
import { createTheme } from "@uiw/codemirror-themes";
import { tags as t } from "@lezer/highlight";

const token = (name: string) => getComputedStyle(document.documentElement).getPropertyValue(name).trim();

/** One theme built from the design tokens, so the editor and the spec fences match exactly. */
function themeFromTokens(dark: boolean) {
  return createTheme({
    theme: dark ? "dark" : "light",
    settings: {
      background: token("--editor"), foreground: token("--text"),
      caret: token("--accent"), selection: token("--accent-tint"), selectionMatch: token("--accent-tint"),
      lineHighlight: token("--surface-2"), gutterBackground: token("--gutter"),
      gutterForeground: token("--text-faint"), gutterActiveForeground: token("--text-muted"),
      gutterBorder: token("--border"), fontFamily: token("--font-mono"),
    },
    styles: [
      { tag: [t.keyword, t.operatorKeyword, t.modifier], color: token("--syn-keyword"), fontWeight: "600" },
      { tag: [t.string, t.special(t.string)], color: token("--syn-string") },
      { tag: [t.number, t.bool, t.null], color: token("--syn-number") },
      { tag: [t.comment, t.lineComment, t.blockComment], color: token("--syn-comment"), fontStyle: "italic" },
      { tag: [t.function(t.variableName), t.definition(t.variableName)], color: token("--syn-function"), fontWeight: "600" },
      { tag: [t.variableName, t.propertyName], color: token("--text") },
    ],
  });
}

export function Editor({ value, onChange, onRun, readOnly, dark, height }: {
  value: string; onChange: (v: string) => void; onRun: () => void;
  readOnly?: boolean; dark: boolean; height: string;
}) {
  // Memoised: @uiw/react-codemirror reconfigures the whole editor whenever these change identity.
  const theme = useMemo(() => themeFromTokens(dark), [dark]);
  const extensions = useMemo(() => [
    python(),
    indentUnit.of("    "),
    EditorView.lineWrapping,
    keymap.of([{ key: "Mod-Enter", run: () => { onRun(); return true; } }]),
  ], [onRun]);

  return (
    <CodeMirror
      value={value} onChange={onChange} theme={theme} extensions={extensions}
      height={height} indentWithTab readOnly={readOnly}
      basicSetup={{ foldGutter: false, highlightActiveLine: !readOnly }}
      style={{ fontSize: "var(--fs-code)", border: "1px solid var(--border)", borderRadius: "var(--radius)", overflow: "hidden" }}
    />
  );
}

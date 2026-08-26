import React from "react";
import Markdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { remarkAlert } from "remark-github-blockquote-alert";

// The design system shipped a hand-rolled regex Markdown parser. It mis-renders real drill
// content: plain blockquotes (143/171 READMEs), _emphasis_ (113), ordered lists (17), h4+ (16)
// and nested lists (5) all fell through to paragraphs. Same visual decisions, real parser.
// ponytail: mermaid and assets/ video dropped — 0 of 171 drills use either; add the `img`
// override back if a drill ever ships one.

const KEYWORDS = /(#[^\n]*)|("[^"]*"|'[^']*')|\b(def|return|for|in|if|else|elif|from|import|lambda|None|True|False|not|and|or|while|class|raise|with|as|try|except|finally|yield|assert|pass|break|continue|global|nonlocal|del|is)\b|\b(\d+(?:\.\d+)?)\b/g;

/** Cosmetic Python colouring for spec fences. Worst case is a wrong colour, never wrong text. */
function highlight(code) {
  const out = [];
  let i = 0, k = 0, m;
  KEYWORDS.lastIndex = 0;
  while ((m = KEYWORDS.exec(code))) {
    if (m.index > i) out.push(code.slice(i, m.index));
    const [full, comment, str, kw] = m;
    const color = comment ? "var(--syn-comment)" : str ? "var(--syn-string)" : kw ? "var(--syn-keyword)" : "var(--syn-number)";
    out.push(<span key={k++} style={{ color, fontStyle: comment ? "italic" : "normal", fontWeight: kw ? 600 : 400 }}>{full}</span>);
    i = m.index + full.length;
  }
  if (i < code.length) out.push(code.slice(i));
  return out;
}

const label = { fontSize: "12px", fontWeight: 600, letterSpacing: "var(--ls-label)", textTransform: "uppercase", color: "var(--accent)" };
const fence = { margin: "2px 0 12px", fontFamily: "var(--font-mono)", fontSize: "13px", lineHeight: 1.55, background: "var(--editor)", border: "1px solid var(--border)", borderRadius: "var(--radius-sm)", padding: "10px 12px", overflowX: "auto", color: "var(--text)" };
const cellPad = { padding: "6px 12px", borderBottom: "1px solid var(--border)", fontSize: "13.5px", textAlign: "left", verticalAlign: "top" };

/** Renders a drill's spec_md (GitHub-flavoured Markdown). `slug` resolves relative asset links. */
export function SpecText({ text = "", hideTitle = true, slug, style }) {
  const components = React.useMemo(() => ({
    h1: hideTitle ? () => null : ({ children }) => <h1 style={{ font: "600 20px/1.3 var(--font-sans)", margin: "0 0 6px" }}>{children}</h1>,
    h2: ({ children }) => <h2 style={{ ...label, margin: "18px 0 6px" }}>{children}</h2>,
    h3: ({ children }) => <h3 style={{ font: "600 14px/1.4 var(--font-sans)", margin: "12px 0 4px" }}>{children}</h3>,
    h4: ({ children }) => <h4 style={{ font: "600 13px/1.4 var(--font-sans)", margin: "10px 0 4px", color: "var(--text-muted)" }}>{children}</h4>,
    p: ({ children }) => <p style={{ margin: "0 0 10px", maxWidth: "62ch" }}>{children}</p>,
    ul: ({ children }) => <ul style={{ margin: "0 0 10px", paddingLeft: 20 }}>{children}</ul>,
    ol: ({ children }) => <ol style={{ margin: "0 0 10px", paddingLeft: 22 }}>{children}</ol>,
    li: ({ children }) => <li style={{ marginBottom: 3, maxWidth: "58ch" }}>{children}</li>,
    blockquote: ({ children }) => <blockquote style={{ margin: "0 0 12px", paddingLeft: 12, borderLeft: "3px solid var(--border-strong)", color: "var(--text-muted)" }}>{children}</blockquote>,
    hr: () => <hr style={{ border: "none", borderTop: "1px solid var(--border)", margin: "16px 0" }} />,
    a: ({ href, children }) => <a href={href} target="_blank" rel="noreferrer">{children}</a>,
    img: ({ src, alt }) => <img src={src && slug && !/^\w+:/.test(src) ? `/api/ex/${slug}/${src}` : src} alt={alt} style={{ display: "block", maxWidth: "100%", borderRadius: "var(--radius-sm)", border: "1px solid var(--border)", margin: "4px 0 12px" }} />,
    table: ({ children }) => <table style={{ borderCollapse: "collapse", margin: "2px 0 12px", border: "1px solid var(--border)" }}>{children}</table>,
    th: ({ children }) => <th style={{ ...cellPad, fontSize: "12px", fontWeight: 600, letterSpacing: ".04em", textTransform: "uppercase", color: "var(--text-muted)", background: "var(--surface-2)" }}>{children}</th>,
    td: ({ children }) => <td style={cellPad}>{children}</td>,
    pre: ({ children }) => <>{children}</>,
    code: ({ className, children }) => {
      const source = String(children).replace(/\n$/, "");
      if (!className) {
        return <code style={{ fontFamily: "var(--font-mono)", fontSize: ".92em", background: "var(--surface-2)", border: "1px solid var(--border)", borderRadius: "3px", padding: "1px 4px" }}>{source}</code>;
      }
      return <pre style={fence}>{/python/.test(className) ? highlight(source) : source}</pre>;
    },
  }), [hideTitle, slug]);

  return (
    <div className="spec" style={{ fontFamily: "var(--font-sans)", fontSize: "var(--fs-body)", lineHeight: "var(--lh-body)", color: "var(--text)", ...style }}>
      <Markdown remarkPlugins={[remarkGfm, remarkAlert]} components={components}>{text}</Markdown>
    </div>
  );
}

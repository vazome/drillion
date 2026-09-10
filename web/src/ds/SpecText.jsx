import React from "react";
import s from "./SpecText.module.css";
import Markdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { remarkAlert } from "remark-github-blockquote-alert";

// The design system shipped a hand-rolled regex Markdown parser. It mis-renders real task
// content: plain blockquotes (143/171 READMEs), _emphasis_ (113), ordered lists (17), h4+ (16)
// and nested lists (5) all fell through to paragraphs. Same visual decisions, real parser.
// ponytail: mermaid and assets/ video dropped — 0 of 171 tasks use either; add the `img`
// override back if a task ever ships one.

const KEYWORDS = /(#[^\n]*)|("[^"]*"|'[^']*')|\b(def|return|for|in|if|else|elif|from|import|lambda|None|True|False|not|and|or|while|class|raise|with|as|try|except|finally|yield|assert|pass|break|continue|global|nonlocal|del|is)\b|\b(\d+(?:\.\d+)?)\b/g;

/** Cosmetic Python colouring for spec fences. Worst case is a wrong colour, never wrong text. */
function highlight(code) {
  const out = [];
  let i = 0, k = 0, m;
  KEYWORDS.lastIndex = 0;
  while ((m = KEYWORDS.exec(code))) {
    if (m.index > i) out.push(code.slice(i, m.index));
    const [full, comment, str, kw] = m;
    const token = comment ? "comment" : str ? "string" : kw ? "keyword" : "number";
    out.push(<span key={k++} className={s.tok} data-tok={token}>{full}</span>);
    i = m.index + full.length;
  }
  if (i < code.length) out.push(code.slice(i));
  return out;
}
/** Renders a task's spec_md (GitHub-flavoured Markdown). `slug` resolves relative asset links. */
export function SpecText({ text = "", hideTitle = true, slug, className: rootClassName, style }) {
  const components = React.useMemo(() => ({
    h1: hideTitle ? () => null : ({ children }) => <h1 className={s.h1}>{children}</h1>,
    h2: ({ children }) => <h2 className={s.h2}>{children}</h2>,
    h3: ({ children }) => <h3 className={s.h3}>{children}</h3>,
    h4: ({ children }) => <h4 className={s.h4}>{children}</h4>,
    // className has to survive: the alert plugin marks its label `<p class="markdown-alert-title">`,
    // and dropping the class left the label unstyled with the raw octicon showing through.
    p: ({ children, className }) => <p className={className || s.p}>{children}</p>,
    ul: ({ children }) => <ul className={s.ul}>{children}</ul>,
    ol: ({ children }) => <ol className={s.ol}>{children}</ol>,
    li: ({ children }) => <li className={s.li}>{children}</li>,
    blockquote: ({ children }) => <blockquote className={s.blockquote}>{children}</blockquote>,
    hr: () => <hr className={s.hr} />,
    a: ({ href, children }) => <a href={href} target="_blank" rel="noreferrer">{children}</a>,
    img: ({ src, alt }) => <img src={src && slug && !/^\w+:/.test(src) ? `/api/task/${slug}/assets/${src}` : src} alt={alt} className={s.img} />,
    table: ({ children }) => <table className={s.table}>{children}</table>,
    th: ({ children }) => <th className={s.th}>{children}</th>,
    td: ({ children }) => <td className={s.td}>{children}</td>,
    pre: ({ children }) => <>{children}</>,
    code: ({ className, children }) => {
      const source = String(children).replace(/\n$/, "");
      if (!className) {
        return <code className={s.code}>{source}</code>;
      }
      // a fence that scrolls sideways has to be reachable to be scrolled: without a tab
      // stop the code past its right edge exists for pointers only
      return <pre tabIndex={0} className={s.pre}>{/python/.test(className) ? highlight(source) : source}</pre>;
    },
  }), [hideTitle, slug]);

  return (
    <div className={[s.root, "spec", rootClassName].filter(Boolean).join(" ")} style={style}>
      <Markdown remarkPlugins={[remarkGfm, remarkAlert]} components={components}>{text}</Markdown>
    </div>
  );
}

"""The dict-of-runnables shape: one input fans out into several named fields."""

from langchain_core.runnables import Runnable, RunnableLambda, RunnablePassthrough

from _lib import rng

META = {"topic": 89, "title": "LCEL — a dict of runnables fans one input out",
        "tier": 4, "minutes": 20, "prereqs": [88]}


def solve(retrieve, render):
    """This is the shape that makes real LangChain code unreadable at first:

        {"context": ..., "question": RunnablePassthrough()} | render

    A plain dict on the left of `|` becomes a step of its own. It runs every
    value on the SAME input and returns a dict of the results under those key
    names. So one question goes in and a dict with several filled-in fields
    comes out, ready for the next step. RunnablePassthrough() is the
    do-nothing step: it hands its input straight through unchanged, which is
    how the original question survives next to the looked-up context.

    You are given two functions:

        retrieve(question)  ->  list of matching document strings
        render(fields)      ->  the final string, built from a dict

    Return a chain that takes ONE question string and returns render's output,
    where render is handed a dict with exactly these three keys:

        "question"   the question, unchanged
        "context"    retrieve's documents joined into one string, a newline
                     between each pair (empty string when there are none)
        "n_docs"     how many documents retrieve returned

    Worked example, with retrieve("restart") returning ["pod docs", "node docs"]:

        chain.invoke("restart")  hands render
            {"question": "restart",
             "context":  "pod docs" then a newline then "node docs",
             "n_docs":   2}

    Note that "context" and "n_docs" both start from retrieve. A dict value is
    allowed to be a small chain of its own, so RunnableLambda(retrieve) piped
    into something else is a legal value — the same input reaches both
    branches. The test inspects the dict render actually received, so the key
    names and their contents both have to be right. The chain must also work
    under .batch(list_of_questions).
    """
    raise NotImplementedError


HINTS = [
    "The confusing part is that the dict is not data being passed along — the "
    "dict IS the step, and its values are steps too. Whatever went into the "
    "dict step goes into every one of its values, and the outputs get "
    "reassembled under the same keys. Sketch it on paper: one arrow in, three "
    "arrows out, three results back into one dict, then one arrow onward.",
    "Build the dict literal first: keys 'question', 'context', 'n_docs'. Use "
    "RunnablePassthrough() for 'question'. For 'context' you need retrieve "
    "then a join, which is RunnableLambda(retrieve) | RunnableLambda(...) — a "
    "chain nested inside a dict value. 'n_docs' is retrieve then len. Then "
    "pipe the whole dict into RunnableLambda(render) and return that.",
    "Different data — one word fanned into three fields:\n"
    "    from langchain_core.runnables import RunnableLambda, RunnablePassthrough\n"
    "    show = RunnableLambda(lambda f: f\"{f['word']}/{f['upper']}/{f['size']}\")\n"
    "    chain = {\n"
    "        'word': RunnablePassthrough(),\n"
    "        'upper': RunnableLambda(str.upper),\n"
    "        'size': RunnableLambda(list) | RunnableLambda(len),\n"
    "    } | show\n"
    "    print(chain.invoke('pod'))    # pod/POD/3\n"
    "Notice 'size' is two steps stacked inside one dict value, and every "
    "value saw the same 'pod'.",
]


# ─────────────────────────────  below here is the machinery  ──────────────

def _gen(r):
    subjects = ["pod", "node", "disk", "cert", "dns", "quota", "token", "index"]
    picked = r.sample(subjects, r.randint(4, 6))
    corpus = []
    for subject in picked:
        for note in range(r.randint(1, 2)):
            action = r.choice(["restart", "drain", "rotate", "resize"])
            corpus.append(f"{subject}: {action} it, wait {r.randint(2, 30)}m (note {note})")
    asked = r.sample(picked, r.randint(2, 3)) + [r.choice(["sprocket", "widget"])]
    r.shuffle(asked)
    questions = [f"how do I fix the {subject}" for subject in asked]
    return corpus, questions


def _retriever(corpus):
    """Documents whose subject matches the last word of the question."""
    def retrieve(question):
        key = question.split()[-1]
        return [doc for doc in corpus if doc.startswith(key + ":")]
    return retrieve


def _renderer():
    """A render() that records every dict it was handed."""
    seen = []

    def render(fields):
        assert isinstance(fields, dict), (
            f"render expects a dict of fields, got {type(fields).__name__}"
        )
        seen.append(dict(fields))
        return " | ".join(f"{k}={fields[k]!r}" for k in sorted(fields))

    return render, seen


def _reference(retrieve, render):
    return {
        "question": RunnablePassthrough(),
        "context": RunnableLambda(retrieve) | RunnableLambda(lambda docs: "\n".join(docs)),
        "n_docs": RunnableLambda(retrieve) | RunnableLambda(len),
    } | RunnableLambda(render)


def test_solve():
    r = rng()
    for _ in range(4):
        corpus, questions = _gen(r)
        retrieve = _retriever(corpus)

        render, seen = _renderer()
        chain = solve(retrieve, render)
        assert isinstance(chain, Runnable), "return the chain itself, not a result"

        spare_render, _ = _renderer()
        for question in questions:
            docs = retrieve(question)
            want_fields = {"question": question,
                           "context": "\n".join(docs),
                           "n_docs": len(docs)}
            seen.clear()
            got = chain.invoke(question)
            assert seen, "render was never called — pipe the dict into it"
            assert seen[-1] == want_fields, (
                f"render got {seen[-1]!r}\n           expected {want_fields!r}"
            )
            assert got == spare_render(want_fields), "return what render returned"

        # same chain, many questions at once, answers in input order
        batch_render, _ = _renderer()
        ref_render, _ = _renderer()
        assert (solve(retrieve, batch_render).batch(questions)
                == _reference(retrieve, ref_render).batch(questions)), (
            ".batch must give the same answers, in input order"
        )

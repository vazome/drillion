def solve(retrieve, render):
    raise NotImplementedError


# ══ machinery — everything below is the grader's, not yours ══

from _lib import rng
from langchain_core.runnables import Runnable, RunnableLambda, RunnablePassthrough


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

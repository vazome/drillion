import assert from "node:assert/strict";
import { test } from "node:test";
import { createElement, useState } from "react";
import { renderToStaticMarkup } from "react-dom/server";
import { createServer } from "vite";

for (const action of ["reset", "takeDisk"]) {
  test(`${action} clears the diagnostic when replacing the rejected draft`, async () => {
    const server = await createServer({ root: new URL("../", import.meta.url).pathname, configFile: false, server: { middlewareMode: true, ws: false, watch: null } });
    const previous = globalThis.localStorage;
    globalThis.localStorage = { getItem: () => null, removeItem() {} };
    try {
      const { useDraft } = await server.ssrLoadModule("/src/useDraft.ts");
      const { ApiError } = await server.ssrLoadModule("/src/api.ts");
      const noop = () => {};
      function Probe() {
        const draft = useDraft("example", noop, noop);
        const [step, setStep] = useState(0);
        if (step === 0) {
          draft.absorb(new ApiError(400, { error: "bad YAML", line: 9 }));
          draft.absorb(new ApiError(409, { code: "valid", etag: "disk" }));
          setStep(1);
        } else if (step === 1) {
          assert.equal(draft.syntax.message, "bad YAML");
          assert.equal(draft.syntaxBad, true);
          if (action === "reset") draft.reset({ code: "valid", etag: "disk", note: "", attempt: null });
          else draft.takeDisk();
          setStep(2);
        } else {
          assert.equal(draft.code, "valid");
          assert.equal(draft.syntax, null);
          assert.equal(draft.syntaxBad, false);
        }
        return null;
      }
      renderToStaticMarkup(createElement(Probe));
    } finally {
      await server.close();
      if (previous === undefined) delete globalThis.localStorage;
      else globalThis.localStorage = previous;
    }
  });
}

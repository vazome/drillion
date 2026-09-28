Apply the drillion motion-pass hand-off to the drillion design system
(https://claude.ai/code/artifact/d4066cac-13e5-42b7-add8-b1b96d8c3075). The files are in
`.design-sync/2026-09-28-motion-pass/project/` in vazome/drillion; read that folder's
`README.md` first.

1. Read the system's `project/design-system.json`, then do a plain `read` of the system's url,
   so the publish counts as made on its latest version.
2. For each file under the hand-off's `project/`, read its namesake in the system. If the
   system's copy still matches version `1790454625-a34c` (the hand-off's base), take the
   hand-off's file as it is. If someone edited it since, apply the change the README's table
   describes to their newer copy instead, and say which files needed that.
3. `README.md` goes back with the system's current generated tail (from the last `---` before
   "## Consuming this system") byte for byte; only the hand-written part changes.
4. Publish every changed file in one call, `.jsx` and `.d.ts` as `text/plain`. Send the index
   last, read right before, with only `lastChange` set: by Daniel, via this session, and a
   note that it syncs the app's motion pass (#300).
5. Open the three task cards (ScreenTask, ScreenTaskHeaders, ScreenTaskReview) and FileTabs
   and PracticeHeatmap on the system's page, in light and dark, and compare with the
   hand-off's `screenshots/`. Report anything that differs.

Don't touch tokens, other components, or the generated `api/`, `tokens.css` and
`manifest.json`.

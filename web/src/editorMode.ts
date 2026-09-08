/** Vim or regular, remembered per browser rather than per practice history: it describes
 *  the person, not their cards, so it does not belong in a backup. Same shape as the theme
 *  in App.tsx, which is the other preference of this kind. */
const KEY = "drillion-editor-mode";

export function vimMode() {
  return localStorage.getItem(KEY) === "vim";
}

export function setVimMode(on: boolean) {
  localStorage.setItem(KEY, on ? "vim" : "regular");
}

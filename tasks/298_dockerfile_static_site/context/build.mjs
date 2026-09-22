// Writes the site into dist/: the page, and the script with its comments stripped.
import { cpSync, mkdirSync, readFileSync, writeFileSync } from "node:fs";

mkdirSync("dist", { recursive: true });
cpSync("index.html", "dist/index.html");
const js = readFileSync("src/main.js", "utf8").replace(/^\s*\/\/.*$/gm, "");
writeFileSync("dist/main.js", js);

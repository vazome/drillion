// The rendered frames, as the README's looping AVIF and its still poster. `pnpm render` first.
// AV1 in 4:4:4: full colour resolution keeps coloured UI text sharp, and inter-frame coding
// never leaves stale blocks through a fade, which lossy animated WebP does.
import { execFileSync } from "node:child_process";

const POSTER = 215; // Tracks, just after the Kubernetes pick: the whole app in view

const [crf = "18"] = process.argv.slice(2);
const ffmpeg = (...args) => execFileSync("ffmpeg", ["-loglevel", "error", "-y", ...args], { stdio: "inherit" });
const colour = ["-color_range", "pc", "-colorspace", "bt709", "-color_primaries", "bt709", "-color_trc", "iec61966-2-1"];

ffmpeg(
  "-framerate", "30", "-i", "out/frames/element-%04d.png",
  "-vf", "scale=out_color_matrix=bt709:out_range=full,format=yuv444p", ...colour,
  "-c:v", "libaom-av1", "-crf", crf, "-cpu-used", "4", "-row-mt", "1", "-tiles", "2x2",
  "-loop", "0", "-f", "avif", "../images/drillion-film.avif",
);
ffmpeg(
  "-i", `out/frames/element-${String(POSTER).padStart(4, "0")}.png`,
  "-compression_level", "9", "../images/drillion-film-still.png",
);

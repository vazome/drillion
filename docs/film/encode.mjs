// The rendered frames, as the looping WebP the README shows. `pnpm render` first.
// Lossless: lossy WebP skips blocks it judges unchanged, which leaves ghosts through slow fades.
import { execFileSync } from "node:child_process";

const [width = "1600", fps = "30"] = process.argv.slice(2);
execFileSync("ffmpeg", [
  "-loglevel", "error", "-y", "-framerate", "30", "-i", "out/frames/element-%04d.png",
  "-vf", `fps=${fps},scale=${width}:-1:flags=lanczos`,
  "-c:v", "libwebp_anim", "-lossless", "1", "-compression_level", "4", "-quality", "100", "-loop", "0",
  "../images/drillion-film.webp",
], { stdio: "inherit" });
